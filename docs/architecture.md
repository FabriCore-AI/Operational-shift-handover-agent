# Operational Shift Handover Agent — Architecture

## Flow Diagram of the Project:


                       USER / SHIFT SUPERVISOR
                                 │
                                 ▼
                       Shift Handover Request
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │   Agent / Orchestrator   │
                    └────────────┬─────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       Document RAG       Operational Data      Tools
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 ▼
                       Evidence / Context
                                 │
                                 ▼
                         LLM Reasoning Layer
                                 │
                                 ▼
                       Generated Handover
                                 │
                                 ▼
                          Claim Validation
                                 │
                                 ▼
                           Evaluation
                                 │
                                 ▼
                         Guardrails / Policy
                                 │
                                 ▼
                           Human Review
                                 │
                                 ▼
                       Final Shift Handover
                                 │
                                 ▼
                           Observability



## Target

```text
User
  |
  v
API / Application
  |
  v
Agent / Orchestrator
  |
  +--> RAG
  +--> Operational Data
  +--> Tools
  |
  v
Evidence / Context
  |
  v
LLM Reasoning
  |
  v
Validation
  |
  v
Guardrails
  |
  v
Human Review
  |
  v
Final Handover

Evaluation + Observability
          
```

## Evidence Flow

```text
Observed Data
     |
Retrieved Evidence
     |
AI Interpretation
     |
Validation
     |
Human Review
     |
Final Handover
```

## Evolution

```text
V0  Data -> Prompt -> LLM -> Handover
V1  Data + Docs -> Retrieval -> LLM -> Handover
V2  Docs + Operational Data -> Context -> LLM
V3  Agent -> RAG + Data + Tools -> Handover
V4  Agent -> Claims -> Validation -> Handover
V5  System -> Evaluation -> Improvement
V6  System -> Traces / Cost / Latency / Errors
V7  Guardrails -> Agent -> Guardrails
V8  API -> Agent -> RAG/Data/Tools -> Validation
    -> Guardrails -> Human Review
    -> Observability + Evaluation
```

**Rule:** each version adds only what is needed to solve the previous version's demonstrated limitation.

---

## Version Evolution

### V0

```text
Shift Data
    ↓
   LLM
    ↓
Handover
```
### V1
```
                 ┌── Documents
                 ↓
Shift Data → Retrieval
                 ↓
              Context
                 ↓
                LLM
                 ↓
             Handover
```
## V2 — RAG + Operational Data Retrieval
```text
                    ┌── Operational Data
                    │
Shift Request ──────┤
                    │
                    └── Reference Documents
                              ↓
                       Combined Evidence
                              ↓
                             LLM
                              ↓
                         Handover
```


## V3 — Agent + Approved Tools

V3 adds an agent that selects and executes approved tools before the handover is generated.

```text
User Request
     ↓
Handover Agent
     ↓
Tool Selection
     ↓
Approved Tools
 ┌───────────────┬─────────────────┬──────────────────────┐
 ↓               ↓                 ↓
Operational      Document          Production
Data             Search            Calculation
Tool             Tool              Tool
 └───────────────┴─────────────────┴──────────────────────┘
                         ↓
                      Evidence
```

### V3 Components

* `HandoverAgent`
* `OperationalDataTool`
* `DocumentSearchTool`
* `ProductionCalculationTool`
* `ToolPlan`
* Tool argument schemas

### V3 Flow

```text
Request
  ↓
LLM selects required tools
  ↓
Validate tool plan
  ↓
Execute only approved tools
  ↓
Collect evidence
  ↓
Generate handover
```

The agent can only execute registered tools. Tool names and arguments are validated before execution.

V3 remains a decision-support system. It does not control equipment or change process conditions.

### Target Architecture
```
            ┌── Documents
            ├── Operational Data
            ├── Tools
            ├── Validation
            ├── Evaluation
            ├── Observability
            └── Guardrails
                    ↓
                  Agent
                    ↓
              Human Review
                    ↓
              Final Handover
```
