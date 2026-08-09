from pydantic import BaseModel, ConfigDict, Field


class ShiftRecord(BaseModel):
    shift_id: str
    date: str
    start_time: str
    end_time: str
    shift: str
    team: str
    unit: str
    product: str
    target_qty: float
    actual_qty: float
    status: str
    operator_summary: str


class EquipmentReading(BaseModel):
    reading_id: str
    timestamp: str
    equipment_id: str
    status: str
    temperature_c: float
    pressure_bar: float
    vibration_mm_s: float


class AlarmEvent(BaseModel):
    event_id: str
    timestamp: str
    equipment_id: str
    event_type: str
    severity: str
    description: str
    state: str


class ProductionRecord(BaseModel):
    production_id: str
    scenario_id: str
    unit: str
    product: str
    target_qty: float
    actual_qty: float
    loss_qty: float
    downtime_minutes: float
    status: str


class MaintenanceEvent(BaseModel):
    maintenance_id: str
    timestamp: str
    equipment_id: str
    type: str
    issue: str
    action: str
    status: str


class OperatingNote(BaseModel):
    note_id: str
    scenario_id: str
    timestamp: str
    author_role: str
    note: str


class ShiftContext(BaseModel):
    shift: ShiftRecord
    equipment: list[EquipmentReading] = Field(default_factory=list)
    alarms: list[AlarmEvent] = Field(default_factory=list)
    production: list[ProductionRecord] = Field(default_factory=list)
    maintenance: list[MaintenanceEvent] = Field(default_factory=list)
    operating_notes: list[OperatingNote] = Field(default_factory=list)




class HandoverEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event: str
    severity: str
    evidence_ids: list[str]


class EquipmentIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    equipment_id: str
    issue: str
    status: str
    evidence_ids: list[str]


class ProductionSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_quantity: float
    actual_quantity: float
    loss_quantity: float
    downtime_minutes: float
    status: str
    evidence_ids: list[str]


class OutstandingAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action: str
    owner_or_role: str
    status: str
    evidence_ids: list[str]


class HandoverReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    shift_id: str
    executive_summary: str
    key_events: list[HandoverEvent]
    equipment_issues: list[EquipmentIssue]
    production_status: ProductionSummary
    outstanding_actions: list[OutstandingAction]
    next_shift_attention: list[str]
    evidence_limitations: list[str]