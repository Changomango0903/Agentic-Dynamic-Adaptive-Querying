from app.storage.db import Steps, Docs, async_session
from app.llm.provider import get_llm

SYSTEM_PROMPT = (
    "You are a careful analyst. Synthesize an answer strictly from the retrieved notes and docs. "
    "Cite using [#] indices matching the provided sources list; do not invent sources."
)

class Synthesizer:
    async def compose(self, trace_id: str) -> str:
        async with async_session() as s:
            steps = await Steps.list_for_run(s, trace_id)
            doc_ids = set()
            notes_all = []
            for st in steps:
                notes_all.append(st.notes)
                for d_id in (await s.execute(Steps.doc_ids_q(st.id))).scalars():
                    doc_ids.add(d_id)
            docs = await Docs.by_ids(s, list(doc_ids))

        numbered = [f"[{i+1}] {d.title} — {d.url}" for i, d in enumerate(docs)]
        sources_map = {d.id: i+1 for i, d in enumerate(docs)}

        content = (
            "\n\n".join(notes_all) +
            "\n\n---\nSources:\n" + "\n".join(numbered)
        )
        llm = get_llm()
        prompt = (
            "Write a concise, well-structured answer with bullet points and short paragraphs. "
            "Include inline citations like [1], [2] that refer to the Sources list below.\n\n" + content
        )
        return await llm.complete(SYSTEM_PROMPT, prompt)