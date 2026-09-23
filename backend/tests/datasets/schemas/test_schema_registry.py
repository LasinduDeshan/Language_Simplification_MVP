import pytest
from app.datasets.common.schema_registry import SchemaRegistry

def test_schema_registry_loads_default_and_validates():
    reg = SchemaRegistry()
    assert reg.validate_schema_version("adaptation_record", "1.0.0") is True
    assert reg.validate_schema_version("simplification_pair", "1.0.0") is True

def test_unsupported_future_version_raises():
    reg = SchemaRegistry()
    with pytest.raises(ValueError, match="Unsupported future major schema version"):
        reg.validate_schema_version("adaptation_record", "2.0.0")
