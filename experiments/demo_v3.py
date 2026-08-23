from fabricore.agent.handover_agent import HandoverAgent
from fabricore.config.settings import get_settings
from fabricore.data.loader import SyntheticDataLoader
from fabricore.llm.groq_client import GroqLLMClient
from fabricore.retrieval.retriever import DocumentRetriever
from fabricore.tools.calculations import ProductionCalculationTool
from fabricore.tools.documents import DocumentSearchTool
from fabricore.tools.operational import OperationalDataTool


def build_agent() -> HandoverAgent:
    settings = get_settings()

    data_loader = SyntheticDataLoader(
        settings.data_dir
    )

    document_retriever = DocumentRetriever(
        embedding_model=settings.embedding_model,
        vector_store_dir=settings.vector_store_dir,
    )

    return HandoverAgent(
        llm_client=GroqLLMClient(),
        operational_tool=OperationalDataTool(
            data_loader
        ),
        document_tool=DocumentSearchTool(
            document_retriever
        ),
        calculation_tool=ProductionCalculationTool(),
    )


def main() -> None:
    agent = build_agent()

    request = (
        "Prepare the shift handover for SHIFT-S010. "
        "Investigate the reactor protection trip and "
        "use the relevant operating procedure."
    )

    print("=" * 60)
    print("V3 — AGENT + TOOLS")
    print("=" * 60)

    print("\nRequest")
    print("-------")
    print(request)

    print("\nAgent executing approved tools...")

    results = agent.run(request)

    print("\nTool results")
    print("------------")

    for name, result in results.items():
        print(f"\n{name}")

        if isinstance(result, list):
            for item in result:
                print(item)
        else:
            print(result)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()