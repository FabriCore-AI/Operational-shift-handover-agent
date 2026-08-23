# Episode 04 — V3: Agent + Tools

## Goal

Introduce an agent layer that can select and execute approved tools
based on the user's request.

## V2

```text
Shift Request
     ↓
Operational Data + RAG
     ↓
Combined Evidence
     ↓
LLM
     ↓
Handover
```

## V3
```text
User Request
     ↓
Handover Agent
     ↓
Tool Selection
     ↓
Approved Tools
 ┌───────────────┬────────────────┬────────────────────┐
 │               │                │                    │
Operational   Document       Production
Data          Search         Calculation
 │               │                │
 └───────────────┴────────────────┘
                 ↓
              Evidence

```

### What changed
- Added HandoverAgent
- Added LLM-based tool selection
- Added approved tool execution
- Added operational data tool
- Added document search tool
- Added production calculation tool
- Added V3 agent tests
- Added tool selection and execution tests
- Added V3 demonstration

### Example

#### Request:

>Prepare the shift handover for SHIFT-S010. Investigate the reactor
protection trip and use the relevant operating procedure.


#### The agent selected and executed the required tools and returned:

>operational shift data
reactor protection trip information
relevant equipment-trip procedure
evidence-boundary information
Validation

