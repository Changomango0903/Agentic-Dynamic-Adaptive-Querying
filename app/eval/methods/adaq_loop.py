from typing import Dict
from app.controllers import planner, critic
from app.retrievers import web_api
from app.readers import summarizer
def run(case: Dict):
    qs = planner.generate_initial_queries(case["question"], case.get("company"), case.get("year"))
    facets = critic.init_facets(["regulation","supply","competition","macro","legal"])
    all_notes = []
    for step in range(case.get("step_cap",3)):
        docs = web_api.fetch(qs, k=case.get("k",6))
        notes = summarizer.summarize(docs); all_notes.extend(notes)
        cov = critic.update_coverage(notes, facets)
        if sum(cov.values())/5 >= 0.85: break
        qs = critic.next_queries(case["question"], cov, history=[])
    return {"answer": "adaq answer (stub)", "sources": list({n["source"] for n in all_notes})}