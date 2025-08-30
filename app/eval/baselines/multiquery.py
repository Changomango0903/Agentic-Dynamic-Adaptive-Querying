from app.controllers.planner import Planner
from app.retrievers.web_api import WebRetriever
from app.retrievers.news_api import NewsRetriever
from app.readers.summarizer import Reader


async def run(question: str, k: int):
planner = Planner()
queries = await planner.initial_queries(question, None, None)
retrievers = [WebRetriever(), NewsRetriever()]
docs = []
for r in retrievers:
docs += await r.fetch(queries, k)
reader = Reader()
notes = await reader.notes(docs)
return {"docs": docs, "notes": notes}