import os, sqlite3, json, time
from typing import List, Dict, Any

DB_PATH = os.getenv("DB_PATH", "./adaq.db")

def _c():
    return sqlite3.connect(DB_PATH)

def init():
    with _c() as c:
        c.execute("CREATE TABLE IF NOT EXISTS runs (run_id TEXT PRIMARY KEY, question TEXT, ts REAL, latency REAL, cost REAL)")
        c.execute("CREATE TABLE IF NOT EXISTS steps (run_id TEXT, n INTEGER, queries TEXT, doc_ids TEXT, notes TEXT, coverage TEXT, decision TEXT)")

def log_step(run_id: str, n: int, queries: List[str], doc_ids: List[str], notes: List[dict], coverage: Dict[str,float], decision: Dict[str,Any]):
    with _c() as c:
        c.execute("INSERT INTO steps VALUES (?,?,?,?,?,?,?)",
                  (run_id, n, json.dumps(queries), json.dumps(doc_ids), json.dumps(notes), json.dumps(coverage), json.dumps(decision)))

def finish_run(run_id: str, latency_s: float, cost_usd: float):
    with _c() as c:
        c.execute("INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?)", (run_id, "", time.time(), latency_s, cost_usd))

def get_trace(run_id: str) -> Dict[str, Any]:
    with _c() as c:
        c.row_factory = sqlite3.Row
        r = c.execute("SELECT * FROM runs WHERE run_id=?", (run_id,)).fetchone()
        if not r:
            return {}
        steps = c.execute("SELECT * FROM steps WHERE run_id=? ORDER BY n ASC", (run_id,)).fetchall()
        out = []
        for s in steps:
            out.append({
                "n": s["n"],
                "queries": json.loads(s["queries"]),
                "doc_ids": json.loads(s["doc_ids"]),
                "notes": json.loads(s["notes"]),
                "coverage": json.loads(s["coverage"]),
                "decision": json.loads(s["decision"]),
            })
        return {"run_id": run_id, "steps": out, "latency": r["latency"], "cost": r["cost"]}
