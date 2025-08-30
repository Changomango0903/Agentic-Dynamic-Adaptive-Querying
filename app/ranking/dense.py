"""Optional dense retriever (local HF). Install sentence-transformers to enable.
Falls back to identity ranking if not installed. Set EMBEDDINGS_PROVIDER=hf to use.
"""
from typing import List

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
except Exception:
    _model = None
    np = None


def rerank_dense(docs: List[dict], query: str) -> List[dict]:
    if not _model:
        return docs
    texts = [d.get("title", "") + " " + d.get("snippet", "") for d in docs]
    qv = _model.encode([query], normalize_embeddings=True)
    dv = _model.encode(texts, normalize_embeddings=True)
    sims = (dv @ qv.T).ravel()
    idx = sims.argsort()[::-1]
    out = []
    for i in idx:
        d = docs[i].copy()
        d.setdefault("scores", {})["dense"] = float(sims[i])
        out.append(d)
    return out