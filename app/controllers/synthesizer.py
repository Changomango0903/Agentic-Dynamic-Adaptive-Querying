from app.storage import db

def compose(question: str, trace: dict) -> str:
    bullets, seen = [], set()
    for s in trace.get("steps", []):
        for note in s.get("notes", []):
            src = note.get("source","")
            if src and src not in seen:
                bullets.append(f"- {note.get('summary','')} (source: {src})")
                seen.add(src)
    if not bullets:
        bullets = ["- No evidence collected."]
    return "Answer to: " + question + "\n\nTop findings:\n" + "\n".join(bullets[:12])
