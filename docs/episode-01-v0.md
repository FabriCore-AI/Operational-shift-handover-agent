# Episode 01 — V0 Baseline

## Objective

> Can a plain LLM generate a useful shift handover from structured operational data?

---

## Architecture

```text
Synthetic Data
      |
      v
Data Loader
      |
      v
Shift Context
      |
      v
Prompt Builder
      |
      v
Groq LLM
      |
      v
Structured Output
      |
      v
Handover Report
```

---

## LLM

```text
Provider : Groq
Model    : openai/gpt-oss-120b
```

---

## V0 Includes

```text
- Pydantic data models
- Synthetic data loader
-  Prompt builder
-  Groq LLM integration
-  Strict structured output
-  HandoverReport validation
-  CLI execution
-  10-scenario benchmark
```

---

## V0 Does NOT Include

```text
RAG              
Vector DB        
Agent            
Tools            
Validation       
Evaluation       
Observability    
Guardrails       
Production API  
```

---

# V0 Baseline Result

```text
10 / 10 scenarios executed successfully
```

### What Worked

```text
Structured output       
Operational extraction  
Evidence references     
Missing-data awareness  
Basic event handling    
Maintenance extraction  
```

### Observed Limitations

```text
Conflicting evidence       ⚠
AI interpretation/advice   ⚠
Independent validation     X
Reference retrieval        X
Closed prompt context      X
Quality measurement        X
```

---

## Key Observation

```text
                    V0
                     |
          ┌──────────┴──────────┐
          |                     |
       SUCCESS               LIMITATION
          |                     |
   Good baseline          Closed context
                                |
                                v
                       No external knowledge
                                |
                                v
                       No independent checking
```

The LLM can summarize and interpret the operational data supplied to it, but it cannot independently retrieve or verify supporting operational knowledge.

---

## Evidence Boundary

```text
Observed Data
      |
      v
LLM Interpretation
      |
      v
Generated Handover
      |
      v
Human Review
```

Some generated `next_shift_attention` items may be reasonable interpretations or recommendations rather than directly observed actions.

This becomes an important limitation for future validation and guardrail layers.

---

## V0 Lesson

```text
A plain LLM can produce a useful baseline
handover from structured operational data.

But the context is closed.

The model cannot independently retrieve
approved reference knowledge or verify claims.
```

---

## Why V1?

```text
V0
 |
 | Closed context
 | No document retrieval
 v
Need grounded reference knowledge
 |
 v
V1 — RAG
```

### V1 Goal

> Ground the handover in approved operational documents and reference information.
