# FabriCore AI — Series Roadmap

```text
V0 -> V1 -> V2 -> V3 -> V4 -> V5 -> V6 -> V7 -> V8 -> FINAL
```

| Episode | Version | Change |
|---|---|---|
| 01 | V0 | Plain LLM baseline |
| 02 | V1 | RAG / document grounding |
| 03 | V2 | Operational data retrieval |
| 04 | V3 | Agent + approved tools |
| 05 | V4 | Validation |
| 06 | V5 | Evaluation |
| 07 | V6 | Observability |
| 08 | V7 | Guardrails |
| 09 | V8 | Production architecture |
| 10 | FINAL | Full system + comparison |

## Episode Loop

```text
Current System -> Limitation -> Engineering Change
        -> New Architecture -> Implement -> Test
        -> Git Version -> Next Limitation
```

## Frozen Principles

- Synthetic industrial data.
- Same benchmark scenarios across versions.
- Decision support, not autonomous control.
- No unsupported operational claims.
- Human review is the final operational boundary.
- Use `uv` for Python environment and dependencies.
