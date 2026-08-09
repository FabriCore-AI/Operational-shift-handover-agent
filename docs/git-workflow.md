# Git Workflow

## Version Map

```text
v0.1.0  Episode 01 — Baseline LLM
v1.0.0  Episode 02 — RAG
v2.0.0  Episode 03 — Operational Data
v3.0.0  Episode 04 — Agent + Tools
v4.0.0  Episode 05 — Validation
v5.0.0  Episode 06 — Evaluation
v6.0.0  Episode 07 — Observability
v7.0.0  Episode 08 — Guardrails
v8.0.0  Episode 09 — Production Architecture
final   Episode 10 — Complete System
```

## Episode Flow

```text
Implement -> Test -> Review -> Commit -> Tag -> Next Episode
```

## Commit Examples

```text
feat(v0): implement baseline handover generator
test(v0): add benchmark scenarios
docs(v0): document baseline architecture
```

## Package Management

```bash
uv add <package>
uv add --dev <package>
uv sync
uv run <command>
```

Do not use `pip install`. uv package manager is a very good package manager

## Never Commit

```text
.env
API keys
credentials
real operational data

## keep these things in .gitignore file
```
