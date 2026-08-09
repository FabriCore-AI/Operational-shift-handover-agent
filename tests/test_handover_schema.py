from fabricore.models.schemas import HandoverReport


def test_handover_schema_is_strict():
    schema = HandoverReport.model_json_schema()

    assert schema["additionalProperties"] is False

    for definition_name, definition in schema.get("$defs", {}).items():
        if definition.get("type") == "object":
            assert definition.get("additionalProperties") is False, (
                f"{definition_name} is not strict"
            )