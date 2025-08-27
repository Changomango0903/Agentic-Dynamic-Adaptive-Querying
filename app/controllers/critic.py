from typing import Dict, List

def init_facets(names: List[str]) -> Dict[str, float]:
    return {n: 0.0 for n in names}

def update_coverage(notes: List[dict], facets: Dict[str, float]) -> Dict[str, float]:
    text = " ".join(n.get("summary","").lower() for n in notes)
    keys = {
        "regulation": ["sec","doj","regulator","fine","recall","esg","antitrust"],
        "supply": ["supplier","factory","production","shortage","logistics","capacity"],
        "competition": ["competitor","market share","pricing","rival","china"],
        "macro": ["rates","inflation","recession","fx","oil","tariff","demand"],
        "legal": ["lawsuit","litigation","class action","settlement","probe"],
    }
    for facet, words in keys.items():
        hits = sum(1 for w in words if w in text)
        facets[facet] = min(1.0, facets.get(facet,0.0) + 0.15*hits)
    return facets.copy()

def next_queries(question: str, coverage: Dict[str, float], history: List[dict]) -> List[str]:
    holes = sorted([k for k,v in coverage.items() if v < 0.5], key=lambda k: coverage[k])
    return [f"{question} {h} risks 2025 analysis" for h in holes][:3]
