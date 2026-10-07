from fabricore.config.settings import get_settings
from fabricore.data.loader import SyntheticDataLoader
from fabricore.data.retriever import OperationalDataRetriever
from fabricore.handover.generator import HandoverGenerator
from fabricore.llm.groq_client import GroqLLMClient
from fabricore.retrieval.retriever import DocumentRetriever
from fabricore.tools.calculations import ProductionCalculationTool
from fabricore.validation import HandoverValidationService


def main() -> None:
    shift_id = "SHIFT-S002"
    settings = get_settings()

    loader = SyntheticDataLoader(settings.data_dir)
    context = OperationalDataRetriever(loader).retrieve(shift_id)

    retriever = DocumentRetriever(
        embedding_model=settings.embedding_model,
        vector_store_dir=settings.vector_store_dir,
    )
    generator = HandoverGenerator(
        llm_client=GroqLLMClient(),
        retriever=retriever,
    )

    print("=" * 60)
    print("V4 — HANDOVER VALIDATION")
    print("=" * 60)

    report, documents = generator.generate_with_evidence(context)

    metrics = None
    if context.production:
        production = context.production[0]
        metrics = ProductionCalculationTool().production_deviation(
            target_quantity=production.target_qty,
            actual_quantity=production.actual_qty,
        )

    result = HandoverValidationService().validate(
        report=report,
        context=context,
        documents=documents,
        metrics=metrics,
    )

    print(f"\nShift: {report.shift_id}")
    print(f"Validation valid: {result.valid}")
    print(f"Validation issues: {len(result.issues)}")

    for issue in result.issues:
        print(f"- {issue.code} [{issue.field}]: {issue.message}")

    print("\nHuman review is still required.")


if __name__ == "__main__":
    main()