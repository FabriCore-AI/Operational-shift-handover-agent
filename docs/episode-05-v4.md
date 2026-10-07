# Episode 05 — V4 Validation

## Goal

V3 introduced an agent that can select and execute approved tools.

The next limitation is that the generated handover still needs a deterministic validation step before it reaches human review.

V4 adds validation against the evidence collected by the system.

## V3 -> V4

```text
V3

Request
  ↓
Handover Agent
  ↓
Approved Tools
  ↓
Evidence
  ↓
Handover Report
```

V4 adds:

```text
Request
  ↓
Handover Agent
  ↓
Approved Tools
  ↓
Evidence
  ↓
Handover Report
  ↓
Validator
  ↓
Validation Result
  ↓
Human Review
```

## What Changed

V4 adds:

* `HandoverValidator`
* `ValidationIssue`
* `ValidationResult`
* `HandoverValidationService`
* V4 validation tests

The validator checks concrete properties that can be verified from the collected evidence.

## Validation Checks

### Shift identity

The report `shift_id` must match the shift in the collected operational context.

### Evidence references

Evidence IDs included in the report must exist in the collected evidence.

Missing evidence references are rejected.

Unknown evidence IDs are rejected.

### Production values

Production values in the generated report are compared with the operational production record.

### Production calculation

The reported production loss is checked against the production calculation result.

### Missing evidence

If production information is required but no production evidence exists, validation reports the problem.

## Validation Result

The validator returns a structured result:

```text
ValidationResult
├── valid
├── shift_id
└── issues
    ├── code
    ├── message
    └── field
```

Example:

```text
valid: false
shift_id: SHIFT-S001

issues:
  - code: UNKNOWN_EVIDENCE_ID
    field: key_events[0].evidence_ids
```

## Important Boundary

V4 validates facts that can be checked deterministically against structured evidence.

It does not attempt to automatically prove arbitrary natural-language statements in the executive summary or next-shift attention section.

The system continues to follow the existing rule:

```text
Operational Evidence
        ↓
Generated Handover
        ↓
Validation
        ↓
Human Review
```

V4 does not introduce autonomous equipment control or process changes.

## Tests

V4 validation tests cover:

* valid report
* shift ID mismatch
* unknown evidence ID
* missing evidence reference
* production value mismatch
* calculation mismatch
* missing production evidence
* validation service

Current result:

```text
8 passed
```

## Current V4 Scope

The validation layer and validation service are implemented and tested.

The next step is to connect validation to the actual handover execution/demo flow.

## Next Limitation

After validation is integrated, the system still needs a way to measure how well the handover performs across the fixed benchmark scenarios.

That becomes V5 — Evaluation.
