from typing import Dict
from app.retrievers import web_api
def run(case: Dict): 
    docs = web_api.fetch([case["question"]], k=case.get("k",6))
    return {"answer": "bm25_only answer (stub)", "sources": [d["source"] for d in docs]}
