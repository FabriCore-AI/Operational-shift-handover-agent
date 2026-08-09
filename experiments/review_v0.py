import json
from pathlib import Path


RESULTS_DIR = Path("experiments/results/v0")


def load_results() -> list[dict]:
    results = []

    for path in sorted(
        RESULTS_DIR.glob("S[0-9][0-9][0-9].json")
    ):
        results.append(
            json.loads(
                path.read_text(encoding="utf-8")
            )
        )

    return results


def main() -> None:
    results = load_results()

    print()
    print("=" * 80)
    print("FABRICORE AI — V0 BASELINE REVIEW")
    print("=" * 80)

    for result in results:
        report = result.get("report", {})

        print()
        print("-" * 80)
        print(
            f"{result['scenario_id']} — "
            f"{result['scenario_name']}"
        )
        print("-" * 80)

        print(f"Status       : {result['status']}")
        print(
            f"Latency      : "
            f"{result['latency_seconds']:.2f}s"
        )

        print(
            f"Key events   : "
            f"{len(report.get('key_events', []))}"
        )

        print(
            f"Equipment    : "
            f"{len(report.get('equipment_issues', []))}"
        )

        print(
            f"Actions      : "
            f"{len(report.get('outstanding_actions', []))}"
        )

        print(
            f"Attention    : "
            f"{len(report.get('next_shift_attention', []))}"
        )

        print(
            f"Limitations  : "
            f"{len(report.get('evidence_limitations', []))}"
        )

        production = report.get(
            "production_status",
            {},
        )

        print(
            "Production   : "
            f"{production.get('actual_quantity')} / "
            f"{production.get('target_quantity')}"
        )

        print(
            "Summary      : "
            f"{report.get('executive_summary', '')}"
        )


if __name__ == "__main__":
    main()