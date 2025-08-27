from typing import Dict
from app.retrievers import web_api
from app.readers import summarizer
def run(case: Dict):
    docs = web_api.fetch([case["question"]], k=case.get("k",6))
    notes = summarizer.summarize(docs)
    return {"answer": "static_rag answer (stub)", "sources": [n["source"] for n in notes]}
