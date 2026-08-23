class ProductionCalculationTool:
    """Calculate basic production metrics from supplied values."""

    def production_deviation(
        self,
        target_quantity: float,
        actual_quantity: float,
    ) -> dict[str, float]:
        if target_quantity < 0:
            raise ValueError("target_quantity must not be negative.")

        if actual_quantity < 0:
            raise ValueError("actual_quantity must not be negative.")

        loss_quantity = target_quantity - actual_quantity

        deviation_percent = (
            (loss_quantity / target_quantity) * 100
            if target_quantity > 0
            else 0.0
        )

        return {
            "target_quantity": target_quantity,
            "actual_quantity": actual_quantity,
            "loss_quantity": loss_quantity,
            "deviation_percent": deviation_percent,
        }