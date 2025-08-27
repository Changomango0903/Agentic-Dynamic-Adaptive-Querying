from fastapi import FastAPI
from app.routes import research, trace, evaluate

app = FastAPI(title="ADAQ-lite", version="0.1.0")
app.include_router(research.router)
app.include_router(trace.router)
app.include_router(evaluate.router)

@app.get("/")
def root():
    return {"ok": True, "service": "adaq-lite", "routes": ["/research", "/trace/{id}", "/evaluate"]}
