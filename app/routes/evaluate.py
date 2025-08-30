from fastapi import APIRouter
from pydantic import BaseModel
from app.eval.harness import run_harness

router = APIRouter(prefix="/evaluate", tags=["evaluate"])

class EvalReq(BaseModel):
    dataset_path: str = "eval/datasets/finance_v0.1.jsonl"
    methods: list[str] = ["bm25", "static_rag", "multiquery", "adaq"]

@router.post("")
async def evaluate(req: EvalReq):
    return await run_harness(req.dataset_path, req.methods)