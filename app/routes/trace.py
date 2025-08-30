from fastapi import APIRouter, HTTPException
from app.storage.db import Runs, Steps, StepDocs, Docs, async_session

router = APIRouter(prefix="/trace", tags=["trace"])

@router.get("/{trace_id}")
async def get_trace(trace_id: str):
    async with async_session() as s:
        run = await s.get(Runs, trace_id)
        if not run:
            raise HTTPException(404, "trace not found")
        steps = await Steps.list_for_run(s, trace_id)
        step_dicts = []
        for st in steps:
            doc_ids = await StepDocs.docs_for_step(s, st.id)
            docs = await Docs.by_ids(s, doc_ids)
            step_dicts.append({
                "n": st.n,
                "queries": st.queries,
                "notes": st.notes,
                "coverage_delta": st.coverage_delta,
                "decision": st.decision,
                "docs": [d.as_public() for d in docs],
            })
        return {
            "run": {"id": run.id, "question": run.question, "created_at": run.created_at,
                     "latency_ms": run.latency_ms, "k": run.k, "step_cap": run.step_cap},
            "steps": step_dicts
        }