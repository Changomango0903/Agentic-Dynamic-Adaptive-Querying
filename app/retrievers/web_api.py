from typing import List, Dict
import hashlib, os
from app.storage import cache

def _h(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()[:12]

def fetch(queries: List[str], k: int = 6) -> List[Dict]:
    key = "ret:" + _h("|".join(queries)) + f":k={k}"
    hit = cache.get(key)
    if hit:
        return hit
    # Mock provider (replace with Bing/SerpAPI/NewsAPI)
    docs = []
    for i, q in enumerate(queries):
        docs.append({
            "id": _h(q+str(i)),
            "url": f"https://example.com/search?q={i}",
            "title": f"Result for: {q[:60]}",
            "snippet": f"Snippet about {q}...",
            "source": f"https://example.com/article/{_h(q)}",
        })
    # Deduplicate by source then cache
    seen, out = set(), []
    for d in docs:
        s = d.get("source") or d.get("url")
        if s not in seen:
            seen.add(s); out.append(d)
    cache.set(key, out[:k], ttl=int(os.getenv("CACHE_TTL_SECS","86400")))
    return out[:k]
