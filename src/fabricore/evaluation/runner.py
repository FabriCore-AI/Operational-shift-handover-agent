import json
import statistics
import time
from pathlib import Path
from typing import Any

from fabricore.config.settings import get_settings
from fabricore.data.loader import SyntheticDataLoader
from fabricore.evaluation.groq_judge import build_groq_judge
from fabricore.evaluation.references import (
    build_expected_handover_facts,
    build_reference_facts,
)
from fabricore.handover.generator import HandoverGenerator
from fabricore.llm.groq_client import GroqLLMClient
from fabricore.retrieval.context import format_retrieved_context
from fabricore.retrieval.retriever import DocumentRetriever
from fabricore.tools.calculations import ProductionCalculationTool
from fabricore.validation import HandoverValidationService


def _report_text(report: Any) -> str:
    return json.dumps(report.model_dump(mode="json"), indent=2, ensure_ascii=False)


def _retrieval_context(context: Any, documents: list[Any]) -> list[str]:
    return [
        "STRUCTURED OPERATIONAL EVIDENCE\n"
        + json.dumps(context.model_dump(mode="json"), indent=2, ensure_ascii=False),
        "RETRIEVED REFERENCE DOCUMENTS\n" + format_retrieved_context(documents),
    ]


def _measure_metric(metric: Any, test_case: Any) -> dict[str, Any]:
    metric.measure(test_case)
    score = metric.score
    return {
        "score": round(float(score), 4) if score is not None else None,
        "threshold": metric.threshold,
        "passed": metric.is_successful(),
        "reason": metric.reason,
    }


def run_v5_evaluation() -> dict[str, Any]:
    try:
        from deepeval.metrics import FaithfulnessMetric, GEval
        from deepeval.test_case import LLMTestCase, SingleTurnParams
    except ImportError as exc:
        raise RuntimeError(
            "DeepEval is required. Run `uv sync` after adding the V5 dependency."
        ) from exc

    settings = get_settings()
    data_loader = SyntheticDataLoader(settings.data_dir)
    retriever = DocumentRetriever(
        embedding_model=settings.embedding_model,
        vector_store_dir=settings.vector_store_dir,
    )
    generator = HandoverGenerator(GroqLLMClient(), retriever=retriever)
    calculation_tool = ProductionCalculationTool()
    validation_service = HandoverValidationService()
    judge = build_groq_judge()

    faithfulness = FaithfulnessMetric(
        threshold=0.7,
        model=judge,
        include_reason=True,
        async_mode=False,
    )
    completeness = GEval(
        name="Handover Completeness",
        criteria=(
            "Evaluate the completeness of the generated shift handover, "
            "not the completeness of its underlying source-data dump. "
            "Check whether the report captures material source-supported "
            "events, relevant equipment conditions, production target and "
            "actual output, production loss and downtime when available, "
            "outstanding actions when supported, next-shift attention, "
            "and material evidence limitations. Assess each section only "
            "when relevant to the scenario and available evidence. "
            "Do not require internal scenario metadata or raw source-record "
            "structures to be reproduced in the report. Do not reward "
            "unsupported claims or unnecessary repetition. Use the expected "
            "source facts and retrieval context to judge omissions."
        ),
        evaluation_params=[
            SingleTurnParams.ACTUAL_OUTPUT,
            SingleTurnParams.EXPECTED_OUTPUT,
            SingleTurnParams.RETRIEVAL_CONTEXT,
        ],
        threshold=0.7,
        model=judge,
        async_mode=False,
    )

    scenarios_path = Path(settings.data_dir) / "benchmarks" / "scenarios.json"
    scenarios = json.loads(scenarios_path.read_text(encoding="utf-8"))
    results_dir = Path("experiments/results/v5")
    results_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []

    for scenario in scenarios:
        scenario_id = scenario["scenario_id"]
        shift_id = f"SHIFT-{scenario_id}"
        started = time.perf_counter()
        print(f"\nEvaluating {scenario_id} — {scenario['name']}")

        try:
            context = data_loader.load_shift(shift_id)
            report, documents = generator.generate_with_evidence(context)
            production = context.production[0] if context.production else None
            metrics = (
                calculation_tool.production_deviation(
                    target_quantity=production.target_qty,
                    actual_quantity=production.actual_qty,
                )
                if production
                else None
            )
            validation = validation_service.validate(
                report=report,
                context=context,
                documents=documents,
                metrics=metrics,
            )

            actual_output = _report_text(report)
            expected_output = build_expected_handover_facts(context)
            retrieval_context = _retrieval_context(context, documents)
            test_case = LLMTestCase(
                input=(
                    f"Prepare a shift handover for {shift_id}. "
                    f"Scenario: {scenario['name']}. Purpose: {scenario['purpose']}."
                ),
                actual_output=actual_output,
                expected_output=expected_output,
                retrieval_context=retrieval_context,
            )

            metric_results: dict[str, Any] = {}
            for name, metric in (
                ("faithfulness", faithfulness),
                ("completeness", completeness),
            ):
                try:
                    metric_results[name] = _measure_metric(metric, test_case)
                except Exception as exc:  # noqa: BLE001
                # Keep evaluating other metrics if one metric fails.
                    metric_results[name] = {
                        "score": None,
                        "threshold": metric.threshold,
                        "passed": False,
                        "error": f"{type(exc).__name__}: {exc}",
                    }

            result = {
                "scenario_id": scenario_id,
                "scenario_name": scenario["name"],
                "shift_id": shift_id,
                "status": "SUCCESS",
                "latency_seconds": round(time.perf_counter() - started, 3),
                "validation": validation.model_dump(mode="json"),
                "deterministic_checks": {
                    "validation_passed": validation.valid,
                    "validation_issue_count": len(validation.issues),
                    "production_values_match": not any(
                        issue.code in {"PRODUCTION_VALUE_MISMATCH", "CALCULATION_MISMATCH"}
                        for issue in validation.issues
                    ),
                    "evidence_references_valid": not any(
                        issue.code in {
                            "UNKNOWN_EVIDENCE_ID",
                            "MISSING_EVIDENCE_REFERENCE",
                        }
                        for issue in validation.issues
                    ),
                },
                "deepeval": metric_results,
                "report": report.model_dump(mode="json"),
            }
            print(
                f"✓ validation={validation.valid}; "
                f"faithfulness={metric_results['faithfulness'].get('score')}; "
                f"completeness={metric_results['completeness'].get('score')}"
            )
        except Exception as exc:  # noqa: BLE001
        # Record the failed scenario and continue the benchmark.
            result = {
                "scenario_id": scenario_id,
                "scenario_name": scenario["name"],
                "shift_id": shift_id,
                "status": "FAILED",
                "latency_seconds": round(time.perf_counter() - started, 3),
                "error": f"{type(exc).__name__}: {exc}",
            }
            print(f"✗ Failed: {result['error']}")

        (results_dir / f"{scenario_id}.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        results.append(result)

    successful = [item for item in results if item["status"] == "SUCCESS"]
    summary: dict[str, Any] = {
        "version": "V5",
        "evaluation_framework": "DeepEval",
        "judge_model": judge.get_model_name(),
        "total_scenarios": len(results),
        "successful_scenarios": len(successful),
        "failed_scenarios": len(results) - len(successful),
        "validation_pass_rate": round(
            sum(item["deterministic_checks"]["validation_passed"] for item in successful)
            / len(successful),
            4,
        ) if successful else None,
        "metrics": {},
    }
    for metric_name in ("faithfulness", "completeness"):
        scored = [
            item["deepeval"][metric_name]["score"]
            for item in successful
            if item["deepeval"][metric_name].get("score") is not None
        ]
        passed = sum(
            item["deepeval"][metric_name].get("passed") is True
            for item in successful
        )
        summary["metrics"][metric_name] = {
            "scored_scenarios": len(scored),
            "mean_score": round(statistics.mean(scored), 4) if scored else None,
            "passed_scenarios": passed,
        }

    summary_path = results_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print("\nV5 EVALUATION COMPLETE")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Results saved to: {results_dir}")
    return summary
