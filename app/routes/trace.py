from fastapi import APIRouter, HTTPException
from app.storage import db

router = APIRouter()

@router.get("/trace/{run_id}")
def get_trace(run_id: str):
    t = db.get_trace(run_id)
    if not t:
        raise HTTPException(404, "Trace not found")
    return t
