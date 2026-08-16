# Episode 02 — V1 RAG

## Goal

> Can reference-document retrieval improve the V0 shift handover?

## V0

```text
Shift Data
    ↓
  Prompt
    ↓
   LLM
    ↓
 Handover
```

## V1

```text
                 ┌── Reference Documents
                 ↓
Shift Data → Retrieval
                 ↓
          Retrieved Context
                 ↓
               Prompt
                 ↓
                LLM
                 ↓
             Handover
```

## New Capability

```text
V0 → Closed context

V1 → Shift data + retrieved reference knowledge
```

## Knowledge Base

```text
Equipment Guidelines
        +
Response Procedures
        +
Operations Guidance
        ↓
    Document Store
```

## Evidence Boundary

```text
Operational Records
        ↓
Prove what happened

Reference Documents
        ↓
Explain approved guidance
```

Reference documents must not be treated as proof that an operational event occurred.

## V1 Does Not Include

```text
Agent              X
Tool selection     X
Validation         X
Evaluation         X
Observability      X
Guardrails         X
```

## Target Flow

```text
Shift Data
    +
Reference Documents
    ↓
  Retrieval
    ↓
Relevant Context
    ↓
     LLM
    ↓
Handover
```

## V1 Success Criteria

```text
-  Retrieve relevant documents
-  Ground the LLM response
-  Preserve V0 structured output
-  Keep operational evidence separate
-  Avoid unsupported claims
```

## Next

> Implement the document ingestion and retrieval layer.


## V1 COMPLETE

### Added:
- Industrial reference documents
- Document chunking
- Sentence-transformer embeddings
- FAISS vector index
- Semantic retrieval
- Retrieved context in LLM prompt

### Validated:
- 10 automated tests
- Retrieval across vibration, temperature,
  equipment trip, and handover queries

### Remaining limitation:
- Operational data is still assembled directly
- Retrieval is deterministic
- No structured database/tool access
- No validation of generated claims
- No agent/tool selection

### Next:
> V2 — RAG + Structured Operational Data Retrieval