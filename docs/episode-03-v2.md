# Episode 03 — V2: RAG + Operational Data Retrieval

## Goal

Extend V1 so the handover system can retrieve structured operational
data together with reference documents.

## V1

```text
Shift
  ↓
Operational Context
  ↓
Document Retrieval
  ↓
LLM
  ↓
Handover
```

## V2
```text
                    ┌── Operational Data
                    │
Shift Request ──────┤
                    └── Reference Documents
                              ↓
                       Combined Evidence
                              ↓
                             LLM
                              ↓
                         Handover
```
## What changed
- Added OperationalDataRetriever
- Kept document RAG from V1
- Combined operational context with retrieved reference information
- Added V2 integration test
- Added V2 demonstration script

## Validation
- Full test suite: 12 passed


## V2 demo:
  SHIFT-S002  ✓
  SHIFT-S010  ✓


## Current limitation

Operational data is still retrieved from the synthetic project dataset.
No production database or external operational system is connected yet.

## Next

V3 — Agent + Tools