from typing import Literal

from pydantic import BaseModel, ConfigDict


class OperationalDataArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    shift_id: str


class DocumentSearchArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str


class ProductionCalculationArguments(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_quantity: str
    actual_quantity: str


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: Literal[
        "operational_data",
        "document_search",
        "production_calculation",
    ]
    arguments: (
        OperationalDataArguments
        | DocumentSearchArguments
        | ProductionCalculationArguments
    )


class ToolPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    calls: list[ToolCall]