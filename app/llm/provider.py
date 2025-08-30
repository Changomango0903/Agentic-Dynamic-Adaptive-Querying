from app.config import settings
import httpx, json

class OpenAIProvider:
    async def complete(self, system: str, user: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": 0.2,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()

class OllamaProvider:
    async def complete(self, system: str, user: str) -> str:
        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {"temperature": 0.1},
            "stream": False,  # <<< important: return a single JSON object
        }
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            try:
                data = r.json()
            except Exception:
                # helpful error when Ollama still streams or returns non-JSON
                body = (r.text or "")[:800]
                raise RuntimeError(f"Ollama returned non-JSON: {body}") from None

        # Handle both known shapes
        if isinstance(data, dict):
            # /api/chat with stream=false (current)
            if isinstance(data.get("message"), dict):
                return (data["message"].get("content") or "").strip()
            # some variants include a top-level 'response'
            if "response" in data:
                return (data["response"] or "").strip()

        # Fallback
        return (str(data) or "").strip()

def get_llm():
    if settings.LLM_PROVIDER == "ollama":
        return OllamaProvider()
    return OpenAIProvider()