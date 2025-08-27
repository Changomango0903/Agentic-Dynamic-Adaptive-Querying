import os, sqlite3, json, time

DB_PATH = os.getenv("DB_PATH", "./adaq.db")

def _c():
    return sqlite3.connect(DB_PATH)

def _init():
    with _c() as c:
        c.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT, exp REAL)")

def get(key: str):
    _init()
    with _c() as c:
        row = c.execute("SELECT v, exp FROM kv WHERE k=?", (key,)).fetchone()
        if not row: return None
        v, exp = row
        if exp and exp < time.time():
            c.execute("DELETE FROM kv WHERE k=?", (key,))
            return None
        return json.loads(v)

def set(key: str, value, ttl: int=86400):
    _init()
    exp = time.time() + ttl if ttl else None
    with _c() as c:
        c.execute("INSERT OR REPLACE INTO kv VALUES (?,?,?)", (key, json.dumps(value), exp))
