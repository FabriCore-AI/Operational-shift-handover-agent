# Commands

## Commands used while developing and testing the project.

## Application

Run a handover for a shift:

```bash
uv run python -m fabricore.app --shift-id SHIFT-S001
```

> Change the shift ID when testing another scenario.

```bash
uv run python -m fabricore.app --shift-id SHIFT-S010
```

> Run this after each version to compare the output and see what changed and version wise progress.

## Tests

### Run the complete test suite:

```bash
uv run python -m pytest -v
```

### Run a specific test file:

```bash
uv run python -m pytest tests/test_retrieval.py -v
```

### V1 tests

#### Build the document index:

```bash
uv run python experiments/build_v1_index.py
```

#### Test document retrieval:

```bash
uv run python experiments/test_v1_retrieval.py
```

## Benchmarks V0

### Run the V0 baseline:

```bash
uv run python experiments/v0_baseline.py
```

### Review the V0 results:

```bash
uv run python experiments/review_v0.py
```

## V2 commands
### Run the final V2 test suite
```bash
uv run python -m pytest -v
```

### Run the V2 demo once more

```bash
uv run python experiments/demo_v2.py
```

### Verify the V2 application
```bash
uv run python -m fabricore.app --shift-id SHIFT-S002
uv run python -m fabricore.app --shift-id SHIFT-S010
```

## V3 — Agent + Approved Tools

### Run V3 demo

```bash
uv run python experiments/demo_v3.py
```

Use this to see the agent select approved tools and execute them for a shift handover request.

### Run all tests

```bash
uv run python -m pytest -v
```
## V4 — Validation

### Run the V4 demo

```bash
uv run python experiments/demo_v4.py
```

Demonstrates report generation followed by evidence-based validation.

### Run application with validation

```bash
uv run python -m fabricore.app --shift-id SHIFT-S001
uv run python -m fabricore.app --shift-id SHIFT-S002
```

Reports and validation results are saved under `outputs/handovers/`.

### Run tests

```bash
uv run python -m pytest -v
```

### Check code quality

```bash
uv run ruff check src/fabricore/app.py src/fabricore/handover/generator.py experiments/demo_v4.py src/fabricore/validation tests
```

## V5 — Evaluation

### Install evaluation dependencies

```bash
uv lock
uv sync --extra eval
```

Run `uv lock` after changing dependency groups so the tracked lock file matches `pyproject.toml`. The `eval` extra installs DeepEval without adding it to the normal application dependency set.

### Run the V5 benchmark

```bash
uv run --extra eval python experiments/evaluate_v5.py
```

The script evaluates all frozen scenarios in `data/synthetic/benchmarks/scenarios.json`. It writes one result per scenario and an aggregate summary to `experiments/results/v5/`. The run calls the configured Groq model for report generation and DeepEval judging, so API usage and latency depend on the provider.

### Check V5 code quality and tests

```bash
uv run ruff check src/fabricore/evaluation experiments/evaluate_v5.py tests
uv run python -m pytest -v
```
