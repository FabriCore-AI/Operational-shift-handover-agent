from fabricore.agent.handover_agent import HandoverAgent
from fabricore.agent.tool_plan import ToolPlan
from fabricore.config.settings import get_settings
from fabricore.data.loader import SyntheticDataLoader
from fabricore.llm.groq_client import GroqLLMClient
from fabricore.retrieval.retriever import DocumentRetriever
from fabricore.tools.calculations import ProductionCalculationTool
from fabricore.tools.documents import DocumentSearchTool
from fabricore.tools.operational import OperationalDataTool


def build_agent() -> HandoverAgent:
    settings = get_settings()

    data_loader = SyntheticDataLoader(settings.data_dir)

    document_retriever = DocumentRetriever(
        embedding_model=settings.embedding_model,
        vector_store_dir=settings.vector_store_dir,
    )

    return HandoverAgent(
        llm_client=GroqLLMClient(),
        operational_tool=OperationalDataTool(data_loader),
        document_tool=DocumentSearchTool(document_retriever),
        calculation_tool=ProductionCalculationTool(),
    )


def test_v3_tool_selection() -> None:
    agent = build_agent()

    plan = agent.select_tools(
        "Prepare a handover for SHIFT-S010 and investigate "
        "the reactor protection trip using the relevant procedure."
    )

    assert isinstance(plan, ToolPlan)
    assert plan.calls

    tool_names = {call.tool for call in plan.calls}

    assert "operational_data" in tool_names
    assert "document_search" in tool_names


def test_v3_tool_execution() -> None:
    agent = build_agent()

    plan = ToolPlan(
        calls=[
            {
                "tool": "operational_data",
                "arguments": {
                    "shift_id": "SHIFT-S010",
                },
            },
            {
                "tool": "production_calculation",
                "arguments": {
                    "target_quantity": "1000",
                    "actual_quantity": "820",
                },
            },
        ]
    )

    results = agent.execute_tools(plan)

    assert results["operational_data"].shift.shift_id == "SHIFT-S010"
    assert results["production_calculation"]["loss_quantity"] == 180.0