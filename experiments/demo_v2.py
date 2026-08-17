import json

from fabricore.config.settings import get_settings
from fabricore.data.loader import SyntheticDataLoader
from fabricore.data.retriever import OperationalDataRetriever
from fabricore.handover.generator import HandoverGenerator
from fabricore.llm.groq_client import GroqLLMClient
from fabricore.retrieval.context import format_retrieved_context
from fabricore.retrieval.query_builder import build_retrieval_query
from fabricore.retrieval.retriever import DocumentRetriever


def main() -> None:
    settings = get_settings()

    shift_id = "SHIFT-S002"

    print("=" * 60)
    print("V2 — RAG + OPERATIONAL DATA RETRIEVAL")
    print("=" * 60)
    print()
    print(f"Shift: {shift_id}")
    print()

    # ---------------------------------------------------------
    # 1. Retrieve operational data
    # ---------------------------------------------------------
    loader = SyntheticDataLoader(settings.data_dir)

    operational_retriever = OperationalDataRetriever(
        loader
    )

    context = operational_retriever.retrieve(
        shift_id
    )

    print("Operational evidence")
    print("--------------------")
    print(
        f"Production : "
        f"{context.production[0].actual_qty} / "
        f"{context.production[0].target_qty}"
    )
    print(
        f"Downtime   : "
        f"{context.production[0].downtime_minutes} min"
    )

    if context.alarms:
        print(
            f"Alarm      : "
            f"{context.alarms[0].event_id}"
        )

    if context.equipment:
        equipment_ids = sorted(
            {
                item.equipment_id
                for item in context.equipment
            }
        )
        print(
            f"Equipment  : "
            f"{', '.join(equipment_ids)}"
        )

    if context.maintenance:
        maintenance_ids = [
            item.maintenance_id
            for item in context.maintenance
        ]
        print(
            f"Maintenance: "
            f"{', '.join(maintenance_ids)}"
        )

    print()

    # ---------------------------------------------------------
    # 2. Retrieve reference documents
    # ---------------------------------------------------------
    document_retriever = DocumentRetriever(
        embedding_model=settings.embedding_model,
        vector_store_dir=settings.vector_store_dir,
    )

    query = build_retrieval_query(context)

    retrieved_documents = document_retriever.search(
        query=query,
        top_k=3,
    )

    retrieved_context = format_retrieved_context(
        retrieved_documents
    )

    print("Reference evidence")
    print("------------------")

    for document in retrieved_documents:
        print(
            f"{document.document_id} "
            f"(score={document.score:.4f})"
        )

    print()

    # ---------------------------------------------------------
    # 3. Generate handover using both evidence sources
    # ---------------------------------------------------------
    print("Generating handover...")
    print()

    llm_client = GroqLLMClient()

    generator = HandoverGenerator(
        llm_client=llm_client,
        retriever=document_retriever,
    )

    report = generator.generate(
        context
    )

    print("=" * 60)
    print("SHIFT HANDOVER")
    print("=" * 60)

    print(
        json.dumps(
            report.model_dump(),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()