from .base import BaseRetriever
from app.config import settings
import httpx

class NewsRetriever(BaseRetriever):
    async def fetch(self, queries, k):
        if not settings.NEWSAPI_KEY:
            return []
        url = "https://newsapi.org/v2/everything"
        out = []
        async with httpx.AsyncClient(timeout=20) as client:
            for q in queries[:3]:  # cap calls
                r = await client.get(url, params={
                    "q": q,
                    "pageSize": k,
                    "language": "en",
                    "apiKey": settings.NEWSAPI_KEY,
                })
                if r.status_code != 200:
                    continue
                for art in r.json().get("articles", []):
                    out.append({
                        "url": art.get("url"),
                        "title": art.get("title"),
                        "snippet": (art.get("description") or "")[:500],
                        "source": "newsapi",
                    })
        return out