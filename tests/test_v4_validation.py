from fabricore.models.schemas import (
    AlarmEvent,
    EquipmentReading,
    HandoverEvent,
    HandoverReport,
    ProductionRecord,
    ProductionSummary,
    ShiftContext,
    ShiftRecord,
)
from fabricore.validation.validator import HandoverValidator


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
            operator_summary="Normal shift with reduced production.",
        ),
        equipment=[
            EquipmentReading(
                reading_id="READ-001",
                timestamp="2025-01-01T10:00:00",
                equipment_id="P-101",
                status="Warning",
                temperature_c=80.0,
                pressure_bar=5.0,
                vibration_mm_s=4.2,
            )
        ],
        alarms=[
            AlarmEvent(
                event_id="ALARM-001",
                timestamp="2025-01-01T10:05:00",
                equipment_id="P-101",
                event_type="HIGH_VIBRATION",
                severity="Warning",
                description="High vibration detected.",
                state="Open",
            )
        ],
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


def build_valid_report() -> HandoverReport:
    return HandoverReport(
        shift_id="SHIFT-S001",
        executive_summary="Production finished below target.",
        key_events=[
            HandoverEvent(
                event="High vibration detected on P-101.",
                severity="Warning",
                evidence_ids=["ALARM-001"],
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
        next_shift_attention=["Review P-101 vibration condition."],
        evidence_limitations=[],
    )


def test_valid_report_passes_validation() -> None:
    validator = HandoverValidator()

    result = validator.validate(
        report=build_valid_report(),
        context=build_context(),
        metrics={"loss_quantity": 8.0},
    )

    assert result.valid is True
    assert result.shift_id == "SHIFT-S001"
    assert result.issues == []


def test_wrong_shift_id_is_rejected() -> None:
    validator = HandoverValidator()
    report = build_valid_report()
    report.shift_id = "SHIFT-S999"

    result = validator.validate(
        report=report,
        context=build_context(),
        metrics={"loss_quantity": 8.0},
    )

    assert result.valid is False
    assert any(
        issue.code == "SHIFT_ID_MISMATCH"
        for issue in result.issues
    )


def test_unknown_evidence_id_is_rejected() -> None:
    validator = HandoverValidator()
    report = build_valid_report()
    report.key_events[0].evidence_ids = ["UNKNOWN-001"]

    result = validator.validate(
        report=report,
        context=build_context(),
        metrics={"loss_quantity": 8.0},
    )

    assert result.valid is False
    assert any(
        issue.code == "UNKNOWN_EVIDENCE_ID"
        for issue in result.issues
    )


def test_missing_evidence_reference_is_rejected() -> None:
    validator = HandoverValidator()
    report = build_valid_report()
    report.key_events[0].evidence_ids = []

    result = validator.validate(
        report=report,
        context=build_context(),
        metrics={"loss_quantity": 8.0},
    )

    assert result.valid is False
    assert any(
        issue.code == "MISSING_EVIDENCE_REFERENCE"
        for issue in result.issues
    )


def test_production_mismatch_is_rejected() -> None:
    validator = HandoverValidator()
    report = build_valid_report()
    report.production_status.actual_quantity = 80.0

    result = validator.validate(
        report=report,
        context=build_context(),
        metrics={"loss_quantity": 8.0},
    )

    assert result.valid is False
    assert any(
        issue.code == "PRODUCTION_VALUE_MISMATCH"
        for issue in result.issues
    )


def test_calculation_mismatch_is_rejected() -> None:
    validator = HandoverValidator()

    result = validator.validate(
        report=build_valid_report(),
        context=build_context(),
        metrics={"loss_quantity": 20.0},
    )

    assert result.valid is False
    assert any(
        issue.code == "CALCULATION_MISMATCH"
        for issue in result.issues
    )


def test_missing_production_evidence_is_rejected() -> None:
    validator = HandoverValidator()
    context = build_context()
    context.production = []

    result = validator.validate(
        report=build_valid_report(),
        context=context,
        metrics={"loss_quantity": 8.0},
    )

    assert result.valid is False
    assert any(
        issue.code == "MISSING_PRODUCTION_EVIDENCE"
        for issue in result.issues
    )