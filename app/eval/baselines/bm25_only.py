from app.ranking.bm25 import rank


def run(query: str, docs: list[dict]) -> list[dict]:
return rank(docs, query)