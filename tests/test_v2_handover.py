from unittest.mock import Mock

from fabricore.data.loader import SyntheticDataLoader
from fabricore.data.retriever import OperationalDataRetriever
from fabricore.handover.generator import HandoverGenerator
from fabricore.models.schemas import HandoverReport
from fabricore.retrieval.schemas import RetrievedDocument


def test_v2_handover_combines_operational_context_with_rag() -> None:
    loader = SyntheticDataLoader("data/synthetic")
    operational_retriever = OperationalDataRetriever(loader)

    context = operational_retriever.retrieve("SHIFT-S002")

    document_retriever = Mock()

    document_retriever.search.return_value = [
        RetrievedDocument(
            chunk_id="CHUNK-001",
            document_id="DOC-P101-VIBRATION-001",
            source="P-101_vibration_guideline.md",
            title="P-101 Vibration Guideline",
            content=(
                "A high-vibration alarm requires operator attention. "
                "Repeated or increasing vibration should be reviewed "
                "by maintenance or engineering personnel."
            ),
            score=0.78,
        )
    ]

    llm_client = Mock()

    llm_client.generate_structured.return_value = (
        HandoverReport(
            shift_id="SHIFT-S002",
            executive_summary=(
                "Production was below target and a high-vibration "
                "alarm was recorded on P-101."
            ),
            key_events=[
                {
                    "event": "High vibration alarm on pump P-101",
                    "severity": "WARNING",
                    "evidence_ids": ["EVT-S002-01"],
                }
            ],
            equipment_issues=[
                {
                    "equipment_id": "P-101",
                    "issue": "High vibration detected",
                    "status": "ACKNOWLEDGED",
                    "evidence_ids": ["EVT-S002-01"],
                }
            ],
            production_status={
                "target_quantity": 1000.0,
                "actual_quantity": 980.0,
                "loss_quantity": 20.0,
                "downtime_minutes": 15.0,
                "status": "BELOW_TARGET",
                "evidence_ids": ["PROD-S002"],
            },
            outstanding_actions=[],
            next_shift_attention=[
                "Monitor vibration on P-101"
            ],
            evidence_limitations=[],
        ).model_dump_json()
    )

    generator = HandoverGenerator(
        llm_client=llm_client,
        retriever=document_retriever,
    )

    report = generator.generate(context)

    assert report.shift_id == "SHIFT-S002"
    assert report.production_status.actual_quantity == 980.0
    assert report.key_events
    assert report.equipment_issues

    document_retriever.search.assert_called_once()
    llm_client.generate_structured.assert_called_once()