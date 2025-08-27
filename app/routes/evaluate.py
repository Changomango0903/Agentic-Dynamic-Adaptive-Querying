from fastapi import APIRouter
from app.eval import harness

router = APIRouter()

@router.post("/evaluate")
def evaluate():
    return harness.run_all()
