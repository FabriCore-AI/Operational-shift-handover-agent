from fabricore.models.schemas import ShiftContext
from fabricore.data.loader import SyntheticDataLoader


class OperationalDataTool:
    """Retrieve structured operational evidence for a shift."""

    def __init__(self, data_loader: SyntheticDataLoader) -> None:
        self.data_loader = data_loader

    def run(self, shift_id: str) -> ShiftContext:
        if not shift_id.strip():
            raise ValueError("shift_id must not be empty.")

        return self.data_loader.load_shift(shift_id)