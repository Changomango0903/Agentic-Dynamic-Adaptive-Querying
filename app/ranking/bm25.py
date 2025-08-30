from rank_bm25 import BM25Okapi
import numpy as np

def rank(docs, query):
    texts = [d.get("title", "") + " " + d.get("snippet", "") for d in docs]
    tokenized = [t.lower().split() for t in texts]
    bm25 = BM25Okapi(tokenized)
    scores = bm25.get_scores(query.lower().split())
    order = np.argsort(-scores)
    return [docs[i] | {"scores": {"bm25": float(scores[i])}} for i in order]