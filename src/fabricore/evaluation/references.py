import json
from typing import Any

from fabricore.models.schemas import ShiftContext


def build_reference_facts(
    context: ShiftContext,
    scenario: dict[str, Any],
) -> str:
    """Build report-oriented expected facts from frozen source records."""
    production = context.production[0] if context.production else None

    facts = {
        "scenario_id": scenario["scenario_id"],
        "shift_id": context.shift.shift_id,
        "scenario": scenario["name"],
        "scenario_purpose": scenario["purpose"],
        "operator_summary": context.shift.operator_summary,
        "production": None,
        "operational_events": [],
        "equipment_conditions": [],
        "maintenance": [],
        "operating_notes": [],
        "evaluation_rules": [
            "Include material facts relevant to the shift handover.",
            "Do not require raw source records or scenario metadata in the report.",
            "Do not invent facts, causes, thresholds, or completed actions.",
            "Preserve alarm state and severity as supported by the evidence.",
            "Identify conflicting or missing information when supported by evidence.",
            "Keep production quantities and downtime consistent with source records.",
            "Human review remains required.",
        ],
        "production_source_record": (
            production.model_dump(mode="json") if production else None
        ),
        "evaluation_guidance": [
            "Do not claim evidence that is absent from the source records.",
            "Do not invent facts, causes, thresholds, or completed actions.",
            "Preserve alarm state and severity as supported by the evidence.",
            "Identify conflicting or missing information when supported by evidence.",
            "Keep production quantities and downtime consistent with source records.",
            "Include material facts relevant to the shift handover.",
            "Human review remains required.",
        ],
    }

    if production is not None:
        facts["production"] = {
            "target_quantity": production.target_qty,
            "actual_quantity": production.actual_qty,
            "loss_quantity": production.loss_qty,
            "downtime_minutes": production.downtime_minutes,
            "status": production.status,
        }

    for alarm in context.alarms:
        facts["operational_events"].append(
            {
                "event_id": alarm.event_id,
                "timestamp": alarm.timestamp,
                "equipment_id": alarm.equipment_id,
                "event_type": alarm.event_type,
                "severity": alarm.severity,
                "description": alarm.description,
                "state": alarm.state,
            }
        )

    for reading in context.equipment:
        facts["equipment_conditions"].append(
            {
                "reading_id": reading.reading_id,
                "timestamp": reading.timestamp,
                "equipment_id": reading.equipment_id,
                "status": reading.status,
                "temperature_c": reading.temperature_c,
                "pressure_bar": reading.pressure_bar,
                "vibration_mm_s": reading.vibration_mm_s,
            }
        )

    for event in context.maintenance:
        facts["maintenance"].append(
            {
                "maintenance_id": event.maintenance_id,
                "equipment_id": event.equipment_id,
                "type": event.type,
                "issue": event.issue,
                "action": event.action,
                "status": event.status,
            }
        )

    for note in context.operating_notes:
        facts["operating_notes"].append(
            {
                "note_id": note.note_id,
                "timestamp": note.timestamp,
                "author_role": note.author_role,
                "note": note.note,
            }
        )

def build_expected_handover_facts(context: ShiftContext) -> str:
    """Build concise, report-oriented expectations from source evidence."""
    facts: list[str] = [
        f"Shift ID: {context.shift.shift_id}",
    ]

    if context.shift.operator_summary:
        facts.append(
            f"Operator-reported summary: {context.shift.operator_summary}"
        )

    for production in context.production:
        facts.extend(
            [
                f"Production target: {production.target_qty}",
                f"Actual production: {production.actual_qty}",
                f"Production loss: {production.loss_qty}",
                f"Downtime in minutes: {production.downtime_minutes}",
                f"Source production status: {production.status}",
            ]
        )

    for alarm in context.alarms:
        facts.append(
            "Operational event: "
            f"equipment={alarm.equipment_id}; "
            f"type={alarm.event_type}; "
            f"severity={alarm.severity}; "
            f"state={alarm.state}; "
            f"description={alarm.description}"
        )

    for reading in context.equipment:
        facts.append(
            "Equipment condition: "
            f"equipment={reading.equipment_id}; "
            f"status={reading.status}; "
            f"temperature_c={reading.temperature_c}; "
            f"pressure_bar={reading.pressure_bar}; "
            f"vibration_mm_s={reading.vibration_mm_s}"
        )

    for event in context.maintenance:
        facts.append(
            "Maintenance evidence: "
            f"equipment={event.equipment_id}; "
            f"issue={event.issue}; "
            f"action={event.action}; "
            f"status={event.status}"
        )

    for note in context.operating_notes:
        facts.append(f"Operating note: {note.note}")

    return json.dumps(
        {"required_source_facts": facts},
        indent=2,
        ensure_ascii=False,
    )


    return json.dumps(facts, indent=2, ensure_ascii=False)