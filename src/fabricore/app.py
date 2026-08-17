"""
Run:
uv run python -m fabricore.app --shift-id SHIFT-S002
uv run python -m fabricore.app --shift-id SHIFT-S001
"""

import argparse
import json
from pathlib import Path

from fabricore.retrieval.retriever import DocumentRetriever
from fabricore.data.retriever import OperationalDataRetriever

from fabricore.config.settings import get_settings
from fabricore.data.loader import SyntheticDataLoader
from fabricore.handover.generator import HandoverGenerator
from fabricore.llm.groq_client import GroqLLMClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="FabriCore AI V0 Shift Handover Generator"
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

    loader = SyntheticDataLoader(
        settings.data_dir
    )

    operational_retriever = OperationalDataRetriever(
        loader
    )

    context = operational_retriever.retrieve(
        args.shift_id
    )

    print("✓ Shift loaded")
    print(f"✓ Operational context retrieved for the shift_id {args.shift_id}")

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

    report = generator.generate(context)

    print("✓ Handover generated")

    output_dir = Path("outputs/handovers")
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = output_dir / f"{args.shift_id}.json"

    output_path.write_text(
        json.dumps(
            report.model_dump(mode="json"),
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"✓ Saved: {output_path}")

    print("\n" + "=" * 60)
    print("SHIFT HANDOVER")
    print("=" * 60)
    print(
        json.dumps(
            report.model_dump(mode="json"),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()