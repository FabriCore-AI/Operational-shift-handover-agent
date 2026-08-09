from pathlib import Path

import pandas as pd

from fabricore.models.schemas import (
    AlarmEvent,
    EquipmentReading,
    MaintenanceEvent,
    OperatingNote,
    ProductionRecord,
    ShiftContext,
    ShiftRecord,
)


class SyntheticDataLoader:
    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)

    def load_shift(self, shift_id: str) -> ShiftContext:
        shifts = pd.read_csv(self.data_dir / "shifts.csv")
        equipment = pd.read_csv(self.data_dir / "equipment.csv")
        alarms = pd.read_csv(self.data_dir / "alarms.csv")
        production = pd.read_csv(self.data_dir / "production.csv")
        maintenance = pd.read_csv(self.data_dir / "maintenance.csv")
        notes = pd.read_csv(self.data_dir / "operating_notes.csv")

        shift_row = shifts.loc[shifts["shift_id"] == shift_id]

        if shift_row.empty:
            raise ValueError(f"Shift not found: {shift_id}")

        shift = ShiftRecord(**shift_row.iloc[0].to_dict())

        scenario_id = shift_id.replace("SHIFT-", "")

        production_rows = production.loc[
            production["scenario_id"] == scenario_id
        ]

        note_rows = notes.loc[
            notes["scenario_id"] == scenario_id
        ]

        # Equipment and alarm records use scenario-specific IDs.
        equipment_rows = equipment.loc[
            equipment["reading_id"].str.startswith(f"EQ-{scenario_id}-")
        ]

        alarm_rows = alarms.loc[
            alarms["event_id"].str.startswith(f"EVT-{scenario_id}-")
        ]

        maintenance_rows = maintenance.loc[
            maintenance["maintenance_id"].str.startswith(f"MNT-{scenario_id}-")
        ]

        return ShiftContext(
            shift=shift,
            equipment=[
                EquipmentReading(**row.to_dict())
                for _, row in equipment_rows.iterrows()
            ],
            alarms=[
                AlarmEvent(**row.to_dict())
                for _, row in alarm_rows.iterrows()
            ],
            production=[
                ProductionRecord(**row.to_dict())
                for _, row in production_rows.iterrows()
            ],
            maintenance=[
                MaintenanceEvent(**row.to_dict())
                for _, row in maintenance_rows.iterrows()
            ],
            operating_notes=[
                OperatingNote(**row.to_dict())
                for _, row in note_rows.iterrows()
            ],
        )