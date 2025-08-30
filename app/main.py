"""FastAPI entrypoint for ADAQ-lite M1.
Exposes /research, /trace/{id}, /evaluate endpoints and wires DI singletons.
"""
from fastapi import FastAPI
from app.utils.logging import setup_logging
from app.storage.db import init_db
from app.routes.research import router as research_router
from app.routes.trace import router as trace_router
from app.routes.evaluate import router as evaluate_router

app = FastAPI(title="ADAQ-lite", version="0.1.0")

@app.on_event("startup")
async def _startup():
    setup_logging()
    await init_db()

app.include_router(research_router)
app.include_router(trace_router)
app.include_router(evaluate_router)