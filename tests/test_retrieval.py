from pathlib import Path

import pytest

from fabricore.config.settings import get_settings
from fabricore.retrieval.retriever import DocumentRetriever


@pytest.fixture(scope="module")
def retriever() -> DocumentRetriever:
    settings = get_settings()

    vector_store = Path(
        settings.vector_store_dir
    )

    if not (
        vector_store / "documents.faiss"
    ).exists():
        pytest.fail(
            "FAISS index not found. "
            "Run: uv run python "
            "experiments/build_v1_index.py"
        )

    return DocumentRetriever(
        embedding_model=settings.embedding_model,
        vector_store_dir=settings.vector_store_dir,
    )


def test_p101_vibration_retrieval(
    retriever: DocumentRetriever,
) -> None:
    results = retriever.search(
        "high vibration on P-101",
        top_k=3,
    )

    document_ids = [
        result.document_id
        for result in results
    ]

    assert "DOC-P101-VIBRATION-001" in document_ids


def test_r101_temperature_retrieval(
    retriever: DocumentRetriever,
) -> None:
    results = retriever.search(
        "high temperature on reactor R-101",
        top_k=3,
    )

    document_ids = [
        result.document_id
        for result in results
    ]

    assert "DOC-R101-TEMPERATURE-001" in document_ids

def test_empty_query_rejected(
    retriever: DocumentRetriever,
) -> None:
    with pytest.raises(ValueError):
        retriever.search("")



def test_invalid_top_k_rejected(
    retriever: DocumentRetriever,
) -> None:
    with pytest.raises(ValueError):
        retriever.search(
            "high vibration",
            top_k=0,
        )


def test_equipment_trip_retrieval(
    retriever: DocumentRetriever,
) -> None:
    results = retriever.search(
        "equipment protection trip response",
        top_k=3,
    )

    document_ids = [
        result.document_id
        for result in results
    ]

    assert "DOC-PROC-TRIP-001" in document_ids


def test_shift_handover_retrieval(
    retriever: DocumentRetriever,
) -> None:
    results = retriever.search(
        "what should be included in shift handover",
        top_k=3,
    )

    document_ids = [
        result.document_id
        for result in results
    ]

    assert "DOC-OPS-HANDOVER-001" in document_ids