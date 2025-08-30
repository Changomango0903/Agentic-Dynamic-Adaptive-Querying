from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from time import perf_counter
import asyncio
from app.controllers.planner import Planner
from app.controllers.critic import Critic
from app.controllers.synthesizer import Synthesizer
from app.readers.summarizer import Reader
from app.retrievers.web_api import WebRetriever
from app.retrievers.news_api import NewsRetriever
from app.policies.stop_policy import StopPolicy
from app.storage.db import Runs, Steps, Docs, StepDocs, async_session
from app.config import settings
from sqlalchemy import update
router = APIRouter(prefix="/research", tags=["research"])

class ResearchReq(BaseModel):
    question: str
    company: str | None = None
    year: int | None = None
    k: int = settings.TOP_K
    step_cap: int = settings.STEP_CAP
    budget_usd: float | None = None

class ResearchResp(BaseModel):
    final_answer: str
    trace_id: str

@router.post("", response_model=ResearchResp)
async def research(req: ResearchReq):
    t0 = perf_counter()

    planner = Planner()
    retrievers = [WebRetriever(), NewsRetriever()]
    reader = Reader()
    critic = Critic()
    synthesizer = Synthesizer()
    stop_policy = StopPolicy(marginal_threshold=settings.MARGINAL_COVERAGE_THRESHOLD,
                             step_cap=req.step_cap)

    # create run
    async with async_session() as s:
        run = Runs.new(question=req.question, step_cap=req.step_cap, k=req.k)
        s.add(run)
        await s.flush()
        trace_id = run.id
        await s.commit()
    queries = await planner.initial_queries(req.question, req.company, req.year)
    coverage = critic.init_coverage()

    for step_n in range(req.step_cap):
        # parallel fetch
        fetch_tasks = [r.fetch(queries, k=req.k) for r in retrievers]
        batches = await asyncio.gather(*fetch_tasks)
        docs = [d for b in batches for d in b]

        docs = await Docs.dedupe_and_rank(docs)
        notes = await reader.notes(docs)
        coverage_before = coverage.copy()
        coverage = critic.update_coverage(notes, coverage)

        decision = stop_policy.decide(coverage_before, coverage, step_n)

        # persist step + docs
        async with async_session() as s:
            step = Steps.new(run_id=trace_id, n=step_n, queries=queries,
                             notes=notes, coverage_delta=Critic.delta(coverage_before, coverage),
                             decision=decision)
            s.add(step)
            await s.flush()
            await StepDocs.attach(s, step.id, docs)
            await s.commit()

        if decision["stop"]:
            break

        queries = critic.next_queries(req.question, coverage, history_n=step_n+1)

    final_answer = await synthesizer.compose(trace_id)

    # finalize run
    async with async_session() as s:
        run = await s.get(Runs, trace_id)
        run.latency_ms = int((perf_counter() - t0) * 1000)
        await s.execute(
            update(Runs).where(Runs.id == trace_id).values(latency_ms=run.latency_ms)
        )
    await s.commit()

    return ResearchResp(final_answer=final_answer, trace_id=trace_id)