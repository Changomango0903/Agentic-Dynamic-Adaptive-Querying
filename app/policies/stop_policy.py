from typing import Dict

def decide(coverage: Dict[str, float], step: int, step_cap: int) -> Dict:
    avg = sum(coverage.values())/max(1,len(coverage))
    return {"stop": step+1 >= step_cap or avg >= 0.85,
            "reason": "step_cap" if step+1>=step_cap else "coverage>=0.85"}
