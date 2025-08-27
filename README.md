# PROJECT.md — ADAQ: Agentic Dynamic Adaptive Querying

> **Elevator pitch:** ADAQ turns an LLM into an *active researcher*. Instead of "search once, read top‑k," the agent plans → searches → reads → *critiques its own coverage* → refines the next query, and stops when evidence is sufficient. You get higher coverage, better relevance, transparent traces, and reproducible evaluations.

---

## 1. Vision & Goals

* **Vision:** Build a general‑purpose *agentic retrieval* system that adaptively issues and refines queries, producing transparent, well‑cited syntheses.
* **Primary goal (MVP):** On a focused task (e.g., *“Top risks facing Tesla in 2025”*), demonstrate a **+15–25% improvement** in Coverage and NDCG\@5 vs Static RAG at ≤3× cost.
* **Secondary goals (Pro):**

  * Multi‑domain research (finance, policy/regulation, tech/science).
  * Learning loops (bandit/RL for search policy), re‑ranking, and budget control.
  * Trace Explorer UI, experiment tracking, and exportable research dossiers.

---

## 2. Why this matters

* Complex questions require *multiple facets* (regulation, supply chain, competition, macro, legal). Static retrieval misses facets that aren’t obvious from the initial query.
* Recruiters and admissions panels care about **transparency** and **measurement**: ADAQ provides a **search trace** and a **rigorous evaluation harness** with baselines.

---

## 3. Scope

### In (MVP)

* Domain: financial news (company risk analysis) in English.
* Sources: Web search + 1–2 news APIs; optional Reddit.
* Loop: plan → retrieve → read → critique → refine (≤5 steps) → synthesize.
* Trace logging + simple UI.

### Out (MVP)

* PDF heavy parsing, table extraction, complex toolchains.
* RL training; multi‑domain; multilingual.

---

## 4. System Architecture (high level)

**Components**

* **Planner**: Converts the user problem into initial query set.
* **Retriever(s)**: Web/news/Reddit APIs; BM25/dense retrieval for re‑ranking.
* **Reader**: Summarizes evidence, extracts claims, anchors citations.
* **Critic**: Maintains a *facet coverage map*; decides *stop vs refine*; proposes next query.
* **Synthesizer**: Produces final, cited answer and risk taxonomy.
* **Trace Logger**: Persists queries, docs, notes, decisions, costs.
* **Budget Manager** (Pro): Tracks latency/\$; model tiering; early stop.

**Data flow**
User Q → Planner → Retriever(k) → Reader (notes/citations) → Critic (coverage & next query) → \[loop] → Synthesizer → Trace saved → UI.

---

## 5. Core Loop (pseudocode)

```python
state = init_state(question, step_cap=5, budget=cfg.budget)
facets = init_facets(["regulation","supply","competition","macro","legal"])  # configurable
queries = planner.generate_initial_queries(question)

for step in range(step_cap):
    docs = retriever.fetch(queries, k=cfg.k)
    notes = reader.summarize(docs)  # bullets + citations
    coverage = critic.update_coverage(notes, facets)
    decision = critic.decide(coverage, budget, step)
    trace.log(step, queries, docs, notes, decision)

    if decision.stop:
        break
    queries = critic.next_queries(question, coverage, history=trace)

answer = synthesizer.compose(trace)
return answer, trace.id
```

Stopping criteria (MVP): step cap, marginal coverage gain < threshold, or budget/latency cap.

---

## 6. Data Model

* **Run**: `{id, question, timestamp, cost_usd, latency_ms, steps[], final_answer}`
* **Step**: `{n, queries[], retrieved_doc_ids[], notes, coverage_delta, decision:{stop|refine, reason}}`
* **Doc**: `{id, url, title, snippet, source, dedupe_hash, scores:{bm25?, dense?, rerank?}}`
* **Coverage**: `{facet -> completeness_score ∈ [0,1]}`
* **EvalCase**: `{id, question, gold_factors[]}`

---

## 7. API (MVP)

### POST `/research`

* **Body**

```json
{
  "question": "Top risks facing Tesla in 2025",
  "company": "TSLA",
  "year": 2025,
  "k": 8,
  "step_cap": 5,
  "budget_usd": 0.50
}
```

* **Response**

```json
{
  "final_answer": "…with citations…",
  "trace_id": "run_2025_08_27_001"
}
```

### GET `/trace/{id}`

Returns the full search trace (queries → docs → notes → decisions → synthesis).

### POST `/evaluate`

Runs baselines and ADAQ on a dataset and returns metrics.

---

## 8. Evaluation

**Baselines**

1. BM25 or Dense retriever only
2. Static RAG (single-shot retrieve → answer)
3. MultiQuery RAG (parallel rewrites; no adaptivity)
4. **ADAQ** (iterative; facet-aware; stop policy)

**Metrics**

* **Coverage**: fraction of gold factors retrieved (Recall/Hit‑Rate).
* **Relevance**: NDCG\@5, Precision\@5 (LLM/human judges).
* **Answer Quality**: Faithfulness & Completeness (0–5 rubric).
* **Efficiency**: steps, latency, \$ cost. Report quality‑vs‑cost curves.

**Datasets**

* Finance (MVP): 30–50 prompts covering 5–8 firms (e.g., risks 2025).
* Pro: 100+ prompts, multi‑domain (finance, policy, tech/science).

**Ablations (Pro)**

* With/without facet coverage map; with/without cross‑encoder re‑ranker; step caps {2,4,6}; model size sweeps.

**Reports**

* Experiment cards (JSON/Markdown): who/what/when/config/metrics/cost + plots.

---

## 9. UX & Deliverables

**Trace Explorer (MVP → Pro)**

* Timeline of steps; expand queries; show retrieved docs and notes; highlight newly covered facets; side‑by‑side baseline vs ADAQ (Pro).

**Deliverables**

* Demo GIF of a Tesla run; README with one‑click Docker Compose; notebooks for eval; exportable “Research Dossier” (PDF/HTML, Pro).

---

## 10. Engineering

* **Stack**: Python (FastAPI), async HTTP; simple UI (Streamlit/Next.js).
* **Retrieval**: Web/news APIs; BM25/dense; optional cross‑encoder re‑ranker (Pro).
* **Storage**: SQLite (MVP) → Postgres + pgvector/FAISS (Pro).
* **Caching**: URL content cache; query result cache with TTL; dedupe via URL + SimHash/MinHash.
* **Observability**: Structured JSON logs; metrics (Prometheus); OpenTelemetry traces (Pro).
* **Testing**: Unit tests (parsers, scoring, policies) + integration tests (loop).
* **Configs**: `.env` for API keys; per‑run budget/step caps.

**Example Env**

```
SEARCH_API_KEY=...
NEWS_API_KEY=...
OPENAI_API_KEY=...
CACHE_TTL_SECS=86400
STEP_CAP=5
TOP_K=8
BUDGET_USD=0.50
```

---

## 11. Repository Layout

```
adaq/
├─ app/
│  ├─ routes/            # /research, /trace, /evaluate
│  ├─ controllers/       # planner, critic, synthesizer
│  ├─ retrievers/        # web_api.py, news_api.py, reddit_api.py
│  ├─ readers/           # summarizer.py, quote_attribution.py
│  ├─ ranking/           # bm25.py, dense.py, cross_encoder.py
│  ├─ policies/          # facet_map.py, stop_policy.py, budget.py
│  └─ storage/           # db.py, cache.py, schemas.py
├─ ui/                   # Streamlit/Next.js Trace Explorer
├─ eval/
│  ├─ datasets/          # finance.jsonl, general.jsonl
│  ├─ baselines/         # static_rag.py, multiquery.py
│  ├─ harness.py         # runs methods, outputs tables/plots
│  └─ reports/           # experiment cards
├─ notebooks/
├─ tests/
├─ docker/
└─ README.md
```

---

## 12. Road to Production (Pro)

* Budget Manager (model tiering, early stop).
* Facet Controller with explicit *coverage map*.
* Cross‑encoder re‑ranker; learned search policy (bandit/RL).
* Multi‑domain datasets + LLM/human judging; automated experiment cards.
* Research Dossier export; public leaderboard; demo video.

---

## 13. Risks & Mitigations

* **API rate/cost:** Aggressive caching, step caps, batch judging, retries/backoff.
* **Hallucinated citations:** Only cite retrieved set; optional quote‑level verification.
* **Eval subjectivity:** Dual LLM judges + human spot‑checks; inter‑rater agreement.
* **Latency:** Parallel retrieval/reading; async; prefetch top‑k.

---

## 14. License & Ethics

* Respect robots.txt, API ToS, and rate limits.
* Provide source attribution; avoid misrepresenting speculative claims.
* Default to permissive OSS (MIT/Apache‑2.0) unless data licenses require otherwise.

---