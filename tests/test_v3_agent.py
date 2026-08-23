from fabricore.agent.handover_agent import HandoverAgent
from fabricore.config.settings import get_settings
from fabricore.data.loader import SyntheticDataLoader
from fabricore.retrieval.retriever import DocumentRetriever
from fabricore.tools.calculations import ProductionCalculationTool
from fabricore.tools.documents import DocumentSearchTool
from fabricore.tools.operational import OperationalDataTool
from fabricore.llm.base import LLMClient


def test_v3_agent_collects_evidence() -> None:
    settings = get_settings()

    data_loader = SyntheticDataLoader(settings.data_dir)

    operational_tool = OperationalDataTool(data_loader)

    document_retriever = DocumentRetriever(
        embedding_model=settings.embedding_model,
        vector_store_dir=settings.vector_store_dir,
    )

    document_tool = DocumentSearchTool(document_retriever)

    calculation_tool = ProductionCalculationTool()

    agent = HandoverAgent(
        llm_client=LLMClient,
        operational_tool=operational_tool,
        document_tool=document_tool,
        calculation_tool=calculation_tool,
    )

    context, documents, metrics = agent.collect_evidence(
        "SHIFT-S002"
    )

    assert context.shift.shift_id == "SHIFT-S002"
    assert documents
    assert metrics["target_quantity"] == 1000.0
    assert metrics["actual_quantity"] == 980.0
    assert metrics["loss_quantity"] == 20.0