import json, asyncio, time
from pathlib import Path
from typing import Dict
from app.routes.research import research, ResearchReq
from app.config import settings


async def _judge_quality(notes: str) -> Dict[str, float]:
    # Lightweight proxy: length & unique source refs -> pseudo coverage; replace with LLM judge later
    uniq_refs = len(set([p for p in notes.split() if p.startswith("[") and p.endswith("]")]))
    return {"coverage_proxy": min(1.0, uniq_refs / 6.0)}


async def run_harness(dataset_path: str, methods: list[str]):
    ds = [json.loads(l) for l in Path(dataset_path).read_text().strip().splitlines()]
    results = []
    t0 = time.time()
    for case in ds:
        q = case["question"]
        row = {"id": case["id"], "question": q}
        if "adaq" in methods:
            resp = await research(ResearchReq(question=q, company=case.get("company"), year=case.get("year")))
            row["adaq_trace_id"] = resp.trace_id
        results.append(row)
    return {"dataset": dataset_path, "n": len(ds), "seconds": time.time() - t0, "results": results}