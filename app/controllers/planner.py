from typing import List, Optional

def generate_initial_queries(question: str, company: Optional[str]=None, year: Optional[int]=None) -> List[str]:
    base = " ".join([x for x in [question, company or "", str(year or "")] if x])
    variants = [
        base,
        f"{base} key risks",
        f"{base} regulation watchdog actions",
        f"{base} supply chain vulnerabilities",
        f"{base} competition landscape",
        f"{base} macro headwinds",
    ]
    seen, out = set(), []
    for q in variants:
        if q and q not in seen:
            seen.add(q); out.append(q)
    return out[:6]
