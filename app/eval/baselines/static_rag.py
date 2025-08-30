from app.retrievers.web_api import WebRetriever
from app.retrievers.news_api import NewsRetriever
from app.readers.summarizer import Reader
from app.controllers.synthesizer import Synthesizer


async def run(question: str, k: int):
retrievers = [WebRetriever(), NewsRetriever()]
docs = []
for r in retrievers:
docs += await r.fetch([question], k)
reader = Reader()
notes = await reader.notes(docs)
# For baseline, skip iterative refinement; persist minimal in-memory context
synth = Synthesizer()
# reuse synth compose by faking a single-step trace would require DB; for harness,
# return notes + docs and let harness judge.
return {"docs": docs, "notes": notes}