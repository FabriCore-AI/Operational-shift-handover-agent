import json
import time
from pathlib import Path

from fabricore.config.settings import get_settings
from fabricore.data.loader import SyntheticDataLoader
from fabricore.handover.generator import HandoverGenerator
from fabricore.llm.groq_client import GroqLLMClient


def run_v0_benchmark() -> None:
    settings = get_settings()

    loader = SyntheticDataLoader(
        data_dir=settings.data_dir,
    )

    llm_client = GroqLLMClient()

    generator = HandoverGenerator(
        llm_client=llm_client,
    )

    scenarios_path = (
        Path(settings.data_dir)
        / "benchmarks"
        / "scenarios.json"
    )

    scenarios = json.loads(
        scenarios_path.read_text(
            encoding="utf-8",
        )
    )

    results_dir = Path("experiments/results/v0")
    results_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = []

    for scenario in scenarios:
        scenario_id = scenario["scenario_id"]
        shift_id = f"SHIFT-{scenario_id}"

        print()
        print("=" * 60)
        print(f"Running {scenario_id} - {scenario['name']}")
        print("=" * 60)

        start_time = time.perf_counter()

        try:
            context = loader.load_shift(shift_id)

            report = generator.generate(context)

            latency = time.perf_counter() - start_time

            result = {
                "scenario_id": scenario_id,
                "scenario_name": scenario["name"],
                "shift_id": shift_id,
                "status": "SUCCESS",
                "latency_seconds": round(latency, 3),
                "report": report.model_dump(mode="json"),
            }

            print(f"✓ Completed in {latency:.2f}s")

        except Exception as exc:
            latency = time.perf_counter() - start_time

            result = {
                "scenario_id": scenario_id,
                "scenario_name": scenario["name"],
                "shift_id": shift_id,
                "status": "FAILED",
                "latency_seconds": round(latency, 3),
                "error": str(exc),
            }

            print(f"✗ Failed: {exc}")

        output_path = results_dir / f"{scenario_id}.json"

        output_path.write_text(
            json.dumps(
                result,
                indent=2,
            ),
            encoding="utf-8",
        )

        summary.append(
            {
                "scenario_id": scenario_id,
                "scenario_name": scenario["name"],
                "shift_id": shift_id,
                "status": result["status"],
                "latency_seconds": result["latency_seconds"],
            }
        )

    summary_path = results_dir / "summary.json"

    summary_path.write_text(
        json.dumps(
            summary,
            indent=2,
        ),
        encoding="utf-8",
    )

    successful = sum(
        item["status"] == "SUCCESS"
        for item in summary
    )

    failed = len(summary) - successful

    print()
    print("=" * 60)
    print("V0 BENCHMARK COMPLETE")
    print("=" * 60)
    print(f"Total scenarios : {len(summary)}")
    print(f"Successful      : {successful}")
    print(f"Failed          : {failed}")
    print(f"Results         : {results_dir}")


if __name__ == "__main__":
    run_v0_benchmark()