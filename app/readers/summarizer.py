from app.llm.provider import get_llm
from typing import List

class Reader:
    async def notes(self, docs: List[dict]) -> str:
        """Summarize retrieved docs into bullet notes with source tags [#]."""
        llm = get_llm()
        items = []
        for i, d in enumerate(docs):
            items.append(f"[{i+1}] {d['title']} — {d['snippet']}")
        prompt = (
            "Summarize the following sources into concise bullet points. "
            "Each point should reference one or more sources using [#] numbers.\n\n" +
            "\n".join(items)
        )
        return await llm.complete("You compress information faithfully.", prompt)