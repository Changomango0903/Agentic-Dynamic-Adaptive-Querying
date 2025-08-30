from typing import List

class Planner:
    """Heuristic initial query generator.
    Keeps it simple for M1; can be replaced by learned policy later.
    """
    async def initial_queries(self, question: str, company: str | None, year: int | None) -> List[str]:
        q = question.strip()
        if company:
            q += f" {company}"
        if year:
            q += f" {year}"
        seeds = [q]
        # a couple of facet-aimed rewrites
        seeds += [f"{q} regulation", f"{q} supply chain", f"{q} competition", f"{q} macro"]
        return seeds