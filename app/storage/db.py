from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Text, JSON, select
from datetime import datetime
import hashlib, json
from app.config import settings
from app.utils.hashing import norm_url
from app.ranking.bm25 import rank as bm25_rank
from app.ranking.dense import rerank_dense

engine = create_async_engine(f"sqlite+aiosqlite:///{settings.SQLITE_PATH}")
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class Runs(Base):
    __tablename__ = "runs"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    question: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String, default=lambda: datetime.utcnow().isoformat())
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    k: Mapped[int] = mapped_column(Integer, default=8)
    step_cap: Mapped[int] = mapped_column(Integer, default=5)

    @staticmethod
    def new(question: str, step_cap: int, k: int):
        rid = hashlib.sha1(f"{datetime.utcnow().isoformat()}|{question}".encode()).hexdigest()[:12]
        r = Runs(id=rid, question=question, step_cap=step_cap, k=k)
        return r

class Docs(Base):
    __tablename__ = "docs"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    url: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    snippet: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String)
    dedupe_hash: Mapped[str] = mapped_column(String)
    scores: Mapped[dict] = mapped_column(JSON, default={})

    def as_public(self):
        return {"id": self.id, "url": self.url, "title": self.title, "snippet": self.snippet, "source": self.source, "scores": self.scores}

    @staticmethod
    async def dedupe_and_rank(raw_docs: list[dict]) -> list[dict]:
        # normalize + dedupe by url + title
        seen = {}
        uniques = []
        for d in raw_docs:
            key = norm_url(d.get("url") or "") + "|" + (d.get("title") or "").strip().lower()
            if key in seen:
                continue
            seen[key] = True
            uniques.append(d)
        # rank by bm25 then optional dense rerank on the concatenated queries
        if not uniques:
            return []
        ranked = bm25_rank(uniques, " ".join([d.get("title") or "" for d in uniques])[:256])
        ranked = rerank_dense(ranked, ranked[0].get("title", ""))
        # attach ids
        out = []
        for d in ranked:
            did = hashlib.sha1((d.get("url") or d.get("title") or "").encode()).hexdigest()[:12]
            d["id"] = did
            out.append(d)
        return out

    @staticmethod
    async def by_ids(s, ids: list[str]):
        res = await s.execute(select(Docs).where(Docs.id.in_(ids)))
        return list(res.scalars())

class Steps(Base):
    __tablename__ = "steps"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String)
    n: Mapped[int] = mapped_column(Integer)
    queries: Mapped[list] = mapped_column(JSON)
    notes: Mapped[str] = mapped_column(Text)
    coverage_delta: Mapped[dict] = mapped_column(JSON)
    decision: Mapped[dict] = mapped_column(JSON)

    @staticmethod
    async def list_for_run(s, run_id: str):
        res = await s.execute(select(Steps).where(Steps.run_id == run_id).order_by(Steps.n))
        return list(res.scalars())

    @staticmethod
    def doc_ids_q(step_id: int):
        from sqlalchemy import select
        return select(StepDocs.doc_id).where(StepDocs.step_id == step_id)

    @staticmethod
    def new(run_id: str, n: int, queries: list[str], notes: str, coverage_delta: dict, decision: dict):
        return Steps(run_id=run_id, n=n, queries=queries, notes=notes, coverage_delta=coverage_delta, decision=decision)

class StepDocs(Base):
    __tablename__ = "step_docs"
    step_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doc_id: Mapped[str] = mapped_column(String, primary_key=True)

    @staticmethod
    async def attach(s, step_id: int, docs: list[dict]):
        # 1) dedupe incoming docs by id
        uniq = {}
        for d in docs:
            did = d.get("id")
            if not did:
                continue
            uniq[did] = d

        # 2) upsert Docs (insert only if missing)
        for did, d in uniq.items():
            if not await s.get(Docs, did):
                s.add(Docs(
                    id=did,
                    url=d.get("url") or "",
                    title=d.get("title") or "",
                    snippet=d.get("snippet") or "",
                    source=d.get("source") or "web",
                    dedupe_hash=""
                ))

        # 3) bulk attach step↔doc with SQLite OR IGNORE (idempotent)
        rows = [{"step_id": step_id, "doc_id": did} for did in uniq.keys()]
        if rows:
            stmt = sqlite_insert(StepDocs).values(rows).prefix_with("OR IGNORE")
            await s.execute(stmt)
    
    @staticmethod
    async def docs_for_step(s, step_id: int) -> list[str]:
        res = await s.execute(select(StepDocs.doc_id).where(StepDocs.step_id == step_id))
        return list(res.scalars())

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)