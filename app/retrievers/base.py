from typing import List, Dict

class BaseRetriever:
    async def fetch(self, queries: List[str], k: int) -> List[Dict]:
        raise NotImplementedError