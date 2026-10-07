from fabricore.models.schemas import (
    HandoverEvent,
    HandoverReport,
    ProductionRecord,
    ProductionSummary,
    ShiftContext,
    ShiftRecord,
)
from fabricore.validation.service import HandoverValidationService


def build_context() -> ShiftContext:
    return ShiftContext(
        shift=ShiftRecord(
            shift_id="SHIFT-S001",
            date="2025-01-01",
            start_time="06:00",
            end_time="14:00",
            shift="A",
            team="Team-A",
            unit="Unit-1",
            product="Product-A",
            target_qty=100.0,
            actual_qty=92.0,
            status="Completed",
            operator_summary="Normal shift.",
        ),
        production=[
            ProductionRecord(
                production_id="PROD-001",
                scenario_id="S001",
                unit="Unit-1",
                product="Product-A",
                target_qty=100.0,
                actual_qty=92.0,
                loss_qty=8.0,
                downtime_minutes=20.0,
                status="Below Target",
            )
        ],
    )


def build_report() -> HandoverReport:
    return HandoverReport(
        shift_id="SHIFT-S001",
        executive_summary="Production finished below target.",
        key_events=[
            HandoverEvent(
                event="Production was below target.",
                severity="Warning",
                evidence_ids=["PROD-001"],
            )
        ],
        equipment_issues=[],
        production_status=ProductionSummary(
            target_quantity=100.0,
            actual_quantity=92.0,
            loss_quantity=8.0,
            downtime_minutes=20.0,
            status="Below Target",
            evidence_ids=["PROD-001"],
        ),
        outstanding_actions=[],
        next_shift_attention=[],
        evidence_limitations=[],
    )


def test_validation_service_returns_valid_result() -> None:
    service = HandoverValidationService()

    result = service.validate(
        report=build_report(),
        context=build_context(),
        metrics={"loss_quantity": 8.0},
    )

    assert result.valid is True
    assert result.shift_id == "SHIFT-S001"
    assert result.issues == []