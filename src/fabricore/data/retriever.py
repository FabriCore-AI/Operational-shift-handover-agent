from fabricore.data.loader import SyntheticDataLoader
from fabricore.models.schemas import ShiftContext


class OperationalDataRetriever:
    def __init__(
        self,
        loader: SyntheticDataLoader,
    ) -> None:
        self.loader = loader

    def retrieve(
        self,
        shift_id: str,
    ) -> ShiftContext:
        context = self.loader.load_shift(shift_id)

        return context