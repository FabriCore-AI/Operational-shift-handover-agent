from fabricore.models.schemas import ShiftContext


def build_retrieval_query(context: ShiftContext) -> str:
    parts = [
        context.shift.operator_summary,
        context.shift.status,
    ]

    for equipment in context.equipment:
        parts.extend(
            [
                equipment.equipment_id,
                equipment.status,
                f"temperature {equipment.temperature_c}",
                f"pressure {equipment.pressure_bar}",
                f"vibration {equipment.vibration_mm_s}",
            ]
        )

    for alarm in context.alarms:
        parts.extend(
            [
                alarm.equipment_id,
                alarm.event_type,
                alarm.severity,
                alarm.description,
                alarm.state,
            ]
        )

    for maintenance in context.maintenance:
        parts.extend(
            [
                maintenance.equipment_id,
                maintenance.issue,
                maintenance.action,
                maintenance.status,
            ]
        )

    for note in context.operating_notes:
        parts.append(note.note)

    return " ".join(
        part
        for part in parts
        if part
    )