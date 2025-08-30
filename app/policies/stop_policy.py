from typing import Dict

class StopPolicy:
    def __init__(self, marginal_threshold: float, step_cap: int):
        self.marginal_threshold = marginal_threshold
        self.step_cap = step_cap

    def decide(self, before: Dict[str, float], after: Dict[str, float], step_n: int) -> Dict:
        gain = sum(max(0.0, after[k] - before[k]) for k in after) / max(1, len(after))
        should_stop = (step_n + 1 >= self.step_cap) or (gain < self.marginal_threshold)
        return {"stop": should_stop, "reason": f"marginal={gain:.3f}", "gain": gain}