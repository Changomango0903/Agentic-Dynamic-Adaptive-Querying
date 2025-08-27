# ROADMAP.md — ADAQ Delivery Plan

> **Timeline overview:** MVP (Weeks 1–3) → Core Pro Upgrades (Weeks 4–8) → Stretch (Weeks 9–10)

## Milestones & Acceptance Criteria

### M1 — MVP: ADAQ‑Lite (Week 3)

**Objective:** Beat Static RAG and ship a polished, reproducible demo.

**Done when**

* [ ] `/research` endpoint implements adaptive loop with step cap & stop policy.
* [ ] Web/news retriever, dedupe (URL + SimHash), summarizer, synthesizer with citations.
* [ ] Trace persisted (SQLite) and viewable in UI (`/trace/{id}` + Streamlit page).
* [ ] Baselines: BM25/dense only; Static RAG; MultiQuery RAG.
* [ ] Evaluation on 30–50 prompts with report (Coverage, NDCG\@5, cost/latency).
* [ ] README with one‑click Docker Compose + demo GIF of Tesla run.

**Targets**

* Coverage: **+15–25%** vs Static RAG.
* NDCG\@5: **+10–20%** vs Static RAG.
* Cost: **≤3×** Static RAG for ≥20% quality lift.

---

### M2 — Facet Coverage & Better Ranking (Weeks 4–5)

**Objective:** Increase recall without runaway cost.

**Scope**

* [ ] Facet coverage map module (regulation, supply, competition, macro, legal).
* [ ] Critic targets *holes* explicitly in next‑query generation.
* [ ] Cross‑encoder re‑ranker (optional toggle) + ablation.

**Acceptance**

* [ ] Ablation report: ±facet map, ±reranker, step caps {2,4,6}.
* [ ] Improve Coverage by ≥5 pts over MVP at ≤20% extra cost.

---

### M3 — Budget Manager & Model Tiering (Weeks 6–7)

**Objective:** Maintain QoS under latency/\$ constraints.

**Scope**

* [ ] Per‑run budget config; enforce early stop when marginal gain < threshold.
* [ ] Route planner/critic to small model when confident; fallback to larger model.
* [ ] Parallelize retrieval & reading; prefetch top‑k.

**Acceptance**

* [ ] Cost‑quality frontier chart shows ≥10% cost reduction at same quality.

---

### M4 — Evaluation at Scale & Experiment Cards (Week 8)

**Objective:** Make research‑grade evidence easy to share.

**Scope**

* [ ] 100+ prompt dataset across multiple firms and at least 1 extra domain.
* [ ] LLM‑assisted judging with human spot‑checks (10–20%).
* [ ] Automated experiment cards (JSON/MD) + plots.

**Acceptance**

* [ ] Reproducible `eval/harness.py` runs all methods and emits cards/plots.
* [ ] README “Results” section with tables and cost‑quality charts.

---

### M5 — Pro UX & Dossier Export (Weeks 9–10)

**Objective:** Portfolio polish and stakeholder usability.

**Scope**

* [ ] Trace Explorer: filter by facet; show *newly covered* facets per step; compare baseline vs ADAQ side‑by‑side.
* [ ] Export Research Dossier (PDF/HTML) with references and trace appendix.
* [ ] Public leaderboard (CSV in repo) with badge image.

**Acceptance**

* [ ] Usability test: 5 users replicate the Tesla demo and interpret the trace.
* [ ] Dossier export passes a light peer‑review checklist.

---

## Workstreams & Owners (suggested)

1. **Core Engine** — planner, critic, synthesizer, stop policy.
2. **Retrieval & Ranking** — web/news/Reddit, dedupe, reranker.
3. **UI/UX** — Trace Explorer, compare view, dossier export.
4. **Eval/Science** — datasets, baselines, metrics, ablations, experiment cards.
5. **Infra/DevEx** — Docker, caching, logging, telemetry, CI.

(If solo, tackle in that order; if a team, assign owners per stream.)

---

## Backlog (prioritized)

**P0 (MVP‑critical)**

* [ ] Implement loop controller; SQLite schemas; caching & dedupe.
* [ ] Static RAG & MultiQuery baselines; harness scripts; 30–50 prompt dataset.
* [ ] Streamlit Trace viewer; Docker Compose; README + demo GIF.

**P1 (Performance & Quality)**

* [ ] Facet coverage map; coverage‑aware next‑query generator.
* [ ] Cross‑encoder re‑ranker; rerank ablations; parallel retrieval.
* [ ] Budget manager; model tiering; early stop heuristics.

**P2 (Scale & Research)**

* [ ] 100+ prompt multi‑domain dataset; LLM‑assisted judging; human spot‑checks.
* [ ] Experiment cards; cost‑quality dashboard; public results.

**P3 (Polish & Outreach)**

* [ ] Trace Explorer v2 (filters, compare view); Dossier export; leaderboard.
* [ ] Short demo video; blog‑style README; badge images.

---

## Acceptance Rubrics

**Faithfulness (0–5)**: All claims traceable to cited sources; no unsupported statements.
**Completeness (0–5)**: Captures major facets; minimal omissions.
**Relevance (0–5)**: Sources are domain‑appropriate and timely.
**Trace Quality (0–5)**: Clear query evolution; rationale logged; stop decision justified.

---

## Risks & Mitigations

* **Source volatility / paywalls** → Layer multiple APIs; cache aggressively; graceful degradation.
* **Eval bias** → Dual LLM judges + human spot‑checks; inter‑rater stats.
* **Latency** → Async IO; parallel fetch; step caps; prefetch; reranker batching.
* **Cost overruns** → Budget manager; small‑model routing; strict TTL caches.

---

## Operating Principles

* Evidence‑first; cite everything you synthesize.
* Measure before optimizing; always keep a strong baseline.
* Prefer simple heuristics that are measurable; iterate to learned policies.

---

## Templates

**Experiment Card (JSON)**

```json
{
  "run_id": "m2_facetmap_v1",
  "date": "2025-08-27",
  "dataset": "finance_v0.3",
  "methods": ["bm25","static_rag","multiquery","adaq"],
  "config": {"k":8, "step_cap":5, "reranker": true},
  "metrics": {"coverage@all":0.71, "ndcg@5":0.62, "cost_usd":0.19, "latency_s":38.4},
  "notes": "Facet map improved coverage by +6 pts at +12% cost."
}
```

**Decision Log (MD)**

```
## 2025‑08‑27 — Enable cross‑encoder reranker by default
Context: Static RAG still missing regulation facet ~30% of the time.
Decision: Turn on reranker with top‑20 → top‑5 re‑rank.
Consequences: +9% NDCG@5, +8% latency.
```

---

## Definition of Done (per feature)

* Tests exist and pass (unit + integration where relevant).
* Logs/metrics added; config documented.
* README updated; UI demoable; examples reproducible.
* If it affects quality/cost: add an experiment card.
