from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.storage import db
from app.controllers import planner, critic, synthesizer
from app.retrievers import web_api
from app.readers import summarizer
from app.policies import stop_policy
import os, time, uuid

router = APIRouter()

class ResearchRequest(BaseModel):
    question: str = Field(..., description="User research question")
    company: Optional[str] = None
    year: Optional[int] = None
    k: int = int(os.getenv("TOP_K", "6"))
    step_cap: int = int(os.getenv("STEP_CAP", "5"))
    budget_usd: float = float(os.getenv("BUDGET_USD", "0.5"))

class ResearchResponse(BaseModel):
    final_answer: str
    trace_id: str

@router.post("/research", response_model=ResearchResponse)
def research(req: ResearchRequest):
    db.init()
    run_id = f"run_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    facets = critic.init_facets(["regulation","supply","competition","macro","legal"])
    queries = planner.generate_initial_queries(req.question, req.company, req.year)

    for step in range(req.step_cap):
        docs = web_api.fetch(queries, k=req.k)
        notes = summarizer.summarize(docs)
        coverage = critic.update_coverage(notes, facets)
        decision = stop_policy.decide(coverage, step, req.step_cap)
        db.log_step(run_id, step, queries, [d["id"] for d in docs], notes, coverage, decision)
        if decision["stop"]:
            break
        queries = critic.next_queries(req.question, coverage, history=[])

    answer = synthesizer.compose(req.question, db.get_trace(run_id))
    db.finish_run(run_id, latency_s=0.0, cost_usd=0.0)
    return ResearchResponse(final_answer=answer, trace_id=run_id)
