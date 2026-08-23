import json

from fabricore.llm.base import LLMClient
from fabricore.models.schemas import HandoverReport, ShiftContext
from fabricore.tools.calculations import ProductionCalculationTool
from fabricore.tools.documents import DocumentSearchTool
from fabricore.tools.operational import OperationalDataTool


from fabricore.agent.tool_plan import (
    DocumentSearchArguments,
    OperationalDataArguments,
    ProductionCalculationArguments,
    ToolPlan,
)
TOOL_SELECTION_PROMPT = """
You are selecting tools for an industrial shift handover system.

Available tools:

1. operational_data
   - Retrieves structured operational records for a shift.
   - Required when operational facts are needed.

2. document_search
   - Searches approved industrial reference documents.
   - Use when procedures, guidelines, limits, or reference information
     are relevant.

3. production_calculation
   - Calculates production loss and deviation percentage.
   - Use when production performance needs to be quantified.

Return only the tool calls required for the request.

Do not invent tool names or arguments.
"""


class HandoverAgent:
    """Select and execute approved tools for shift handover generation."""

    def __init__(
        self,
        llm_client: LLMClient,
        operational_tool: OperationalDataTool,
        document_tool: DocumentSearchTool,
        calculation_tool: ProductionCalculationTool,
    ) -> None:
        self.llm_client = llm_client
        self.operational_tool = operational_tool
        self.document_tool = document_tool
        self.calculation_tool = calculation_tool

    def select_tools(self, request: str) -> ToolPlan:
        if not request.strip():
            raise ValueError("Request must not be empty.")

        response = self.llm_client.generate_structured(
            system_prompt=TOOL_SELECTION_PROMPT,
            user_prompt=request,
            response_schema=ToolPlan.model_json_schema(),
        )

        try:
            payload = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError("LLM returned invalid tool plan JSON.") from exc

        return ToolPlan.model_validate(payload)

    def execute_tools(
        self,
        plan: ToolPlan,
    ) -> dict:
        results: dict = {}

        for call in plan.calls:
            if call.tool == "operational_data":
                arguments = OperationalDataArguments.model_validate(
                    call.arguments
                )

                results["operational_data"] = (
                    self.operational_tool.run(
                        arguments.shift_id
                    )
                )

            elif call.tool == "document_search":
                arguments = DocumentSearchArguments.model_validate(
                    call.arguments
                )

                results["document_search"] = (
                    self.document_tool.run(
                        arguments.query
                    )
                )

            elif call.tool == "production_calculation":
                arguments = ProductionCalculationArguments.model_validate(
                    call.arguments
                )

                results["production_calculation"] = (
                    self.calculation_tool.production_deviation(
                        target_quantity=float(
                            arguments.target_quantity
                        ),
                        actual_quantity=float(
                            arguments.actual_quantity
                        ),
                    )
                )

        return results

    def collect_evidence(
        self,
        shift_id: str,
    ) -> tuple[ShiftContext, list, dict[str, float]]:
        """Collect the standard evidence set used by the V2 flow."""

        operational_context = self.operational_tool.run(shift_id)

        query = self._build_document_query(operational_context)

        documents = self.document_tool.run(
            query=query,
            top_k=3,
        )

        production = operational_context.production

        if production:
            production_record = production[0]

            metrics = self.calculation_tool.production_deviation(
                target_quantity=production_record.target_qty,
                actual_quantity=production_record.actual_qty,
            )
        else:
            metrics = {
                "target_quantity": 0.0,
                "actual_quantity": 0.0,
                "loss_quantity": 0.0,
                "deviation_percent": 0.0,
            }

        return operational_context, documents, metrics

    def _build_document_query(
        self,
        context: ShiftContext,
    ) -> str:
        parts = [
            "shift handover",
            context.shift.operator_summary,
        ]

        for alarm in context.alarms:
            parts.append(
                f"{alarm.equipment_id} "
                f"{alarm.event_type} "
                f"{alarm.description}"
            )

        for equipment in context.equipment:
            parts.append(
                f"{equipment.equipment_id} "
                f"status {equipment.status}"
            )

        return " ".join(parts)

    def run(self, request: str) -> dict:
        """Select and execute the tools required for the request."""

        plan = self.select_tools(request)

        return self.execute_tools(plan)