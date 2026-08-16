from fabricore.handover.generator import HandoverGenerator
from fabricore.models.schemas import ShiftContext, ShiftRecord
from fabricore.llm.base import LLMClient



class FakeRetriever:
    def search(
        self,
        query: str,
        top_k: int = 3,
    ):
        return []
    

class FakeLLMClient(LLMClient):
    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_schema: dict,
    ) -> str:
        return """
        {
            "shift_id": "SHIFT-TEST",
            "executive_summary": "Test shift completed normally.",
            "key_events": [],
            "equipment_issues": [],
            "production_status": {
                "target_quantity": 1000,
                "actual_quantity": 995,
                "loss_quantity": 5,
                "downtime_minutes": 0,
                "status": "ACHIEVED",
                "evidence_ids": [
                    "PROD-TEST"
                ]
            },
            "outstanding_actions": [],
            "next_shift_attention": [],
            "evidence_limitations": []
        }
        """


def test_handover_generator_returns_handover_report():
    context = ShiftContext(
        shift=ShiftRecord(
            shift_id="SHIFT-TEST",
            date="2026-07-01",
            start_time="06:00",
            end_time="14:00",
            shift="Morning",
            team="Team-A",
            unit="UNIT-A",
            product="Product-X",
            target_qty=1000,
            actual_qty=995,
            status="Normal",
            operator_summary="Normal production.",
        )
    )

    llm_client = FakeLLMClient()
    generator = HandoverGenerator(
        llm_client=llm_client,
        retriever=FakeRetriever(),
    )

    report = generator.generate(context)

    assert report.shift_id == "SHIFT-TEST"
    assert report.executive_summary == "Test shift completed normally."
    assert report.production_status.actual_quantity == 995