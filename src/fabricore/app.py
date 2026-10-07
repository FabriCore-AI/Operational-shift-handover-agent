"""
Run:
uv run python -m fabricore.app --shift-id SHIFT-S002
uv run python -m fabricore.app --shift-id SHIFT-S001
"""

import argparse
import json
from pathlib import Path

from fabricore.config.settings import get_settings
from fabricore.data.loader import SyntheticDataLoader
from fabricore.data.retriever import OperationalDataRetriever
from fabricore.handover.generator import HandoverGenerator
from fabricore.llm.groq_client import GroqLLMClient
from fabricore.retrieval.retriever import DocumentRetriever
from fabricore.tools.calculations import ProductionCalculationTool
from fabricore.validation import HandoverValidationService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FabriCore AI Shift Handover Generator"
    )
    parser.add_argument(
        "--shift-id",
        required=True,
        help="Shift ID to generate a handover for.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()

    print(f"Loading shift: {args.shift_id}")

    loader = SyntheticDataLoader(settings.data_dir)
    operational_retriever = OperationalDataRetriever(loader)
    context = operational_retriever.retrieve(args.shift_id)

    print("✓ Operational context retrieved")

    llm_client = GroqLLMClient()
    retriever = DocumentRetriever(
        embedding_model=settings.embedding_model,
        vector_store_dir=settings.vector_store_dir,
    )
    generator = HandoverGenerator(
        llm_client=llm_client,
        retriever=retriever,
    )

    print("→ Generating handover...")
    report, documents = generator.generate_with_evidence(context)
    print("✓ Handover generated")

    calculation_tool = ProductionCalculationTool()
    metrics = None

    if context.production:
        production_record = context.production[0]
        metrics = calculation_tool.production_deviation(
            target_quantity=production_record.target_qty,
            actual_quantity=production_record.actual_qty,
        )

    validation = HandoverValidationService().validate(
        report=report,
        context=context,
        documents=documents,
        metrics=metrics,
    )

    output_dir = Path("outputs/handovers")
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / f"{args.shift_id}.json"
    validation_path = output_dir / f"{args.shift_id}.validation.json"

    report_path.write_text(
        json.dumps(report.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )
    validation_path.write_text(
        json.dumps(validation.model_dump(mode="json"), indent=2),
        encoding="utf-8",
    )

    print(f"✓ Saved report: {report_path}")
    print(f"✓ Saved validation: {validation_path}")

    print("\n" + "=" * 60)
    print("SHIFT HANDOVER")
    print("=" * 60)
    print(json.dumps(report.model_dump(mode="json"), indent=2))

    print("\n" + "=" * 60)
    print("V4 VALIDATION")
    print("=" * 60)
    print(f"Valid: {validation.valid}")
    print(f"Issues: {len(validation.issues)}")

    for issue in validation.issues:
        location = f" [{issue.field}]" if issue.field else ""
        print(f"- {issue.code}{location}: {issue.message}")

    print("\nHuman review is still required.")
    if not validation.valid:
        print("⚠ Validation failed. Review the issues before using this report.")


if __name__ == "__main__":
    main()