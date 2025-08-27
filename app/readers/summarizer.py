from typing import List, Dict

def summarize(docs: List[Dict]) -> List[Dict]:
    return [{
        "doc_id": d["id"],
        "summary": f"{d['title']} — {d['snippet']}",
        "source": d.get("source") or d.get("url")
    } for d in docs]
