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