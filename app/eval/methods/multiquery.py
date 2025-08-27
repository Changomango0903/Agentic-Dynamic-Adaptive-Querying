from typing import Dict
from app.controllers import planner
from app.retrievers import web_api
from app.readers import summarizer
def run(case: Dict):
    qs = planner.generate_initial_queries(case["question"], case.get("company"), case.get("year"))
    docs = web_api.fetch(qs, k=case.get("k",6))
    notes = summarizer.summarize(docs)
    return {"answer": "multiquery answer (stub)", "sources": [n["source"] for n in notes]}
