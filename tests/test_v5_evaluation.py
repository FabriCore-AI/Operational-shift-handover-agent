import json

from fabricore.evaluation.references import build_reference_facts
from fabricore.models.schemas import (
    OperatingNote,
    ProductionRecord,
    ShiftContext,
    ShiftRecord,
)


def test_reference_facts_come_from_scenario_and_source_records() -> None:
    context = ShiftContext(
        shift=ShiftRecord(
            shift_id="SHIFT-S001",
            date="2026-07-01",
            start_time="06:00",
            end_time="14:00",
            shift="Morning",
            team="Team-A",
            unit="UNIT-A",
            product="Product-X",
            target_qty=1000,
            actual_qty=995,
            status="Normal",
            operator_summary="Normal production; no significant events.",
        ),
        production=[
            ProductionRecord(
                production_id="PROD-S001",
                scenario_id="S001",
                unit="UNIT-A",
                product="Product-X",
                target_qty=1000,
                actual_qty=995,
                loss_qty=5,
                downtime_minutes=0,
                status="ACHIEVED",
            )
        ],
        operating_notes=[
            OperatingNote(
                note_id="NOTE-S001",
                scenario_id="S001",
                timestamp="2026-07-01T13:00:00",
                author_role="Operator",
                note="No significant events.",
            )
        ],
    )
    scenario = {
        "scenario_id": "S001",
        "name": "Normal Shift",
        "purpose": "baseline normal operation",
    }

    facts = json.loads(build_reference_facts(context, scenario))

    assert facts["scenario_id"] == "S001"
    assert facts["scenario_purpose"] == "baseline normal operation"
    assert facts["shift_id"] == "SHIFT-S001"
    assert facts["production_source_record"]["loss_qty"] == 5
    assert facts["operating_notes"][0]["note_id"] == "NOTE-S001"
    assert any("Do not claim evidence" in item for item in facts["evaluation_guidance"])
