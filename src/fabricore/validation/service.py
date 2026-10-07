from collections.abc import Iterable
from typing import Any

from fabricore.models.schemas import HandoverReport, ShiftContext
from fabricore.validation.schemas import ValidationResult
from fabricore.validation.validator import HandoverValidator


class HandoverValidationService:
    """Run V4 validation against a generated handover and its evidence."""

    def __init__(
        self,
        validator: HandoverValidator | None = None,
    ) -> None:
        self.validator = validator or HandoverValidator()

    def validate(
        self,
        report: HandoverReport,
        context: ShiftContext,
        documents: Iterable[Any] | None = None,
        metrics: dict[str, float] | None = None,
    ) -> ValidationResult:
        return self.validator.validate(
            report=report,
            context=context,
            documents=documents,
            metrics=metrics,
        )