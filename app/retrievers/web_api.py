from .base import BaseRetriever
from app.config import settings
import httpx, asyncio

class WebRetriever(BaseRetriever):
    async def _search(self, q: str, k: int):
        if not settings.TAVILY_API_KEY:
            return []
        url = "https://api.tavily.com/search"
        payload = {"api_key": settings.TAVILY_API_KEY, "query": q, "max_results": k}
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            results = data.get("results", [])
            out = []
            for it in results:
                out.append({
                    "url": it.get("url"),
                    "title": it.get("title"),
                    "snippet": it.get("content", "")[:500],
                    "source": "web",
                })
            return out

    async def fetch(self, queries, k):
        tasks = [self._search(q, k) for q in queries]
        batches = await asyncio.gather(*tasks)
        return [d for b in batches for d in b]