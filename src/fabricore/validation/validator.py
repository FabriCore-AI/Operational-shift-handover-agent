from collections.abc import Iterable
from typing import Any

from fabricore.models.schemas import HandoverReport, ShiftContext
from fabricore.validation.schemas import ValidationIssue, ValidationResult


class HandoverValidator:
    """Validate a generated handover report against collected evidence."""

    def validate(
        self,
        report: HandoverReport,
        context: ShiftContext,
        documents: Iterable[Any] | None = None,
        metrics: dict[str, float] | None = None,
    ) -> ValidationResult:
        issues: list[ValidationIssue] = []

        evidence_ids = self._collect_evidence_ids(
            context=context,
            documents=documents or [],
        )

        self._validate_shift_id(
            report=report,
            context=context,
            issues=issues,
        )

        self._validate_evidence_references(
            report=report,
            evidence_ids=evidence_ids,
            issues=issues,
        )

        self._validate_production(
            report=report,
            context=context,
            metrics=metrics,
            issues=issues,
        )

        return ValidationResult(
            valid=not issues,
            shift_id=report.shift_id,
            issues=issues,
        )

    def _validate_shift_id(
        self,
        report: HandoverReport,
        context: ShiftContext,
        issues: list[ValidationIssue],
    ) -> None:
        if report.shift_id != context.shift.shift_id:
            issues.append(
                ValidationIssue(
                    code="SHIFT_ID_MISMATCH",
                    message=(
                        f"Report shift_id '{report.shift_id}' does not "
                        f"match evidence shift_id '{context.shift.shift_id}'."
                    ),
                    field="shift_id",
                )
            )

    def _validate_evidence_references(
        self,
        report: HandoverReport,
        evidence_ids: set[str],
        issues: list[ValidationIssue],
    ) -> None:
        for index, event in enumerate(report.key_events):
            self._check_reference_list(
                evidence_ids=event.evidence_ids,
                available_ids=evidence_ids,
                issues=issues,
                field=f"key_events[{index}].evidence_ids",
            )

        for index, issue in enumerate(report.equipment_issues):
            self._check_reference_list(
                evidence_ids=issue.evidence_ids,
                available_ids=evidence_ids,
                issues=issues,
                field=f"equipment_issues[{index}].evidence_ids",
            )

        self._check_reference_list(
            evidence_ids=report.production_status.evidence_ids,
            available_ids=evidence_ids,
            issues=issues,
            field="production_status.evidence_ids",
        )

        for index, action in enumerate(report.outstanding_actions):
            self._check_reference_list(
                evidence_ids=action.evidence_ids,
                available_ids=evidence_ids,
                issues=issues,
                field=f"outstanding_actions[{index}].evidence_ids",
            )

    def _check_reference_list(
        self,
        evidence_ids: list[str],
        available_ids: set[str],
        issues: list[ValidationIssue],
        field: str,
    ) -> None:
        if not evidence_ids:
            issues.append(
                ValidationIssue(
                    code="MISSING_EVIDENCE_REFERENCE",
                    message="At least one evidence ID is required.",
                    field=field,
                )
            )
            return

        for evidence_id in evidence_ids:
            if evidence_id not in available_ids:
                issues.append(
                    ValidationIssue(
                        code="UNKNOWN_EVIDENCE_ID",
                        message=(
                            f"Evidence ID '{evidence_id}' was not found "
                            "in the collected evidence."
                        ),
                        field=field,
                    )
                )

    def _validate_production(
        self,
        report: HandoverReport,
        context: ShiftContext,
        metrics: dict[str, float] | None,
        issues: list[ValidationIssue],
    ) -> None:
        production = context.production

        if not production:
            issues.append(
                ValidationIssue(
                    code="MISSING_PRODUCTION_EVIDENCE",
                    message=(
                        "The report contains production status but no "
                        "production record is available in the evidence."
                    ),
                    field="production_status",
                )
            )
            return

        record = production[0]

        expected_values = {
            "target_quantity": record.target_qty,
            "actual_quantity": record.actual_qty,
            "loss_quantity": record.loss_qty,
            "downtime_minutes": record.downtime_minutes,
            "status": record.status,
        }

        for field, expected in expected_values.items():
            actual = getattr(report.production_status, field)

            if actual != expected:
                issues.append(
                    ValidationIssue(
                        code="PRODUCTION_VALUE_MISMATCH",
                        message=(
                            f"Production field '{field}' contains "
                            f"'{actual}', expected '{expected}'."
                        ),
                        field=f"production_status.{field}",
                    )
                )

        if metrics is not None:
            expected_loss = metrics.get("loss_quantity")

            if (
                expected_loss is not None
                and report.production_status.loss_quantity != expected_loss
            ):
                issues.append(
                    ValidationIssue(
                        code="CALCULATION_MISMATCH",
                        message=(
                            "Reported loss quantity does not match "
                            "the production calculation evidence."
                        ),
                        field="production_status.loss_quantity",
                    )
                )

    def _collect_evidence_ids(
        self,
        context: ShiftContext,
        documents: Iterable[Any],
    ) -> set[str]:
        evidence_ids: set[str] = set()

        evidence_ids.add(context.shift.shift_id)

        for record in context.equipment:
            evidence_ids.add(record.reading_id)

        for alarm in context.alarms:
            evidence_ids.add(alarm.event_id)

        for production in context.production:
            evidence_ids.add(production.production_id)

        for maintenance in context.maintenance:
            evidence_ids.add(maintenance.maintenance_id)

        for note in context.operating_notes:
            evidence_ids.add(note.note_id)

        for document in documents:
            document_id = self._extract_id(
                document,
                "document_id",
            )

            if document_id:
                evidence_ids.add(document_id)

        return evidence_ids

    @staticmethod
    def _extract_id(
        value: Any,
        field: str,
    ) -> str | None:
        if hasattr(value, field):
            result = getattr(value, field)
            return str(result) if result is not None else None

        if isinstance(value, dict):
            result = value.get(field)
            return str(result) if result is not None else None

        return None