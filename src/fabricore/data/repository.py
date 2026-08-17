from fabricore.models.schemas import ShiftContext


class OperationalDataRepository:
    def __init__(self, loader) -> None:
        self.loader = loader

    def get_shift_context(
        self,
        shift_id: str,
    ) -> ShiftContext:
        return self.loader.load_shift_context(
            shift_id
        )