# Episode 06 — V5 Evaluation

## Goal

V4 added deterministic validation for concrete report properties. The next limitation is that validation alone does not measure how faithful or complete the handover is across different operating scenarios.

V5 adds an evaluation run using DeepEval and deterministic checks over the existing S001–S010 benchmark.

## V4 → V5

```text
Frozen Scenarios (S001–S010)
          ↓
Generate Handover + Collect Evidence
          ↓
DeepEval Metrics
  ├── Faithfulness
  └── Handover Completeness
          +
Deterministic Validation
          ↓
Per-Scenario Results
          ↓
Aggregate Summary
```

## What Changed

- Added DeepEval as an optional `eval` dependency group.
- Added a Groq-backed DeepEval judge adapter so evaluation uses the configured provider.
- Added source-derived reference facts for each scenario.
- Added per-scenario results and an aggregate evaluation summary.
- Kept evaluation separate from the normal application path.

## Metrics

### Faithfulness

Measures whether the generated report is supported by the collected operational evidence and retrieved reference documents.

### Handover completeness

Uses DeepEval GEval to assess whether the report covers relevant events, equipment conditions, production status, open actions, next-shift attention, and evidence limitations without rewarding invented facts.

### Deterministic checks

The existing V4 validator checks shift identity, evidence references, production values, and production calculation consistency. These checks remain separate from LLM-judge scores.

## Reference Data

Expected facts are assembled from the frozen scenario metadata and the corresponding operational records. The project does not treat the V0 generated report as ground truth, and does not invent a single reference handover for each scenario.

## Run

Install the optional evaluation dependency group:

```bash
uv lock
uv sync --extra eval
```

Run the benchmark:

```bash
uv run --extra eval python experiments/evaluate_v5.py
```

Results are written to `experiments/results/v5/`, with one JSON file per scenario and a `summary.json` aggregate.

## Important Boundary

DeepEval metrics use an LLM judge and can vary between runs. Their scores are evaluation signals, not deterministic facts and not operational approval. Production values and evidence references continue to use deterministic validation. The system remains decision support, with human review required.

## Next Limitation

V5 provides evaluation results, but it does not yet explain the execution path, latency breakdown, model usage, or failures in a consistent operational trace. That becomes V6 — Observability.
