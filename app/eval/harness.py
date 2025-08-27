from typing import Dict, List
from pathlib import Path
import json
from app.eval.methods import bm25_only, static_rag, multiquery, adaq_loop

DATA = Path(__file__).resolve().parent / "datasets" / "finance.sample.jsonl"

def load_dataset() -> List[Dict]:
    with open(DATA, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def run_all():
    ds = load_dataset()[:5]
    results = {}
    for name, fn in [("bm25", bm25_only.run),
                     ("static_rag", static_rag.run),
                     ("multiquery", multiquery.run),
                     ("adaq", adaq_loop.run)]:
        results[name] = [fn(x) for x in ds]
    # Toy metric = avg #sources per answer (replace with Coverage/NDCG@5 later)
    metrics = {k: sum(len(vv["sources"]) for vv in v)/max(1,len(v)) for k,v in results.items()}
    return {"cases": len(ds), "avg_sources": metrics, "notes": "Toy metric = avg #sources per answer"}
