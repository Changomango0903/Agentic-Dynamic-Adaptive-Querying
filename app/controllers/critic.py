from typing import Dict, List
from app.policies.facet_seed import FACETS

class Critic:
    @staticmethod
    def delta(before: Dict[str, float], after: Dict[str, float]) -> Dict[str, float]:
        return {k: max(0.0, after.get(k, 0.0) - before.get(k, 0.0)) for k in FACETS}

    def init_coverage(self) -> Dict[str, float]:
        return {f: 0.0 for f in FACETS}

    def update_coverage(self, notes: str, coverage: Dict[str, float]) -> Dict[str, float]:
        text = notes.lower()
        updated = coverage.copy()
        for facet, kws in FACETS.items():
            score = updated[facet]
            hits = sum(1 for kw in kws if kw in text)
            if hits:
                # capped incremental score for M1
                score = min(1.0, score + 0.25 + 0.05 * min(hits, 3))
            updated[facet] = score
        return updated

    def next_queries(self, question: str, coverage: Dict[str, float], history_n: int) -> List[str]:
        # aim at least-covered facet with 2 targeted rewrites
        target = min(coverage, key=coverage.get)
        return [f"{question} {target}", f"{question} {target} risks analysis"]