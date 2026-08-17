from fabricore.data.loader import SyntheticDataLoader
from fabricore.data.retriever import OperationalDataRetriever


def test_operational_data_retrieval() -> None:
    loader = SyntheticDataLoader("data/synthetic")
    retriever = OperationalDataRetriever(loader)

    context = retriever.retrieve("SHIFT-S002")

    assert context.shift.shift_id == "SHIFT-S002"
    assert context.production
    assert context.alarms
    assert context.equipment