import pytest
from app.datasets.common.schema_registry import SchemaRegistry
from app.datasets.common.versions import is_compatible_schema_version

def test_unsupported_major_version_fails_safely():
    reg = SchemaRegistry()
    
    # 2.0.0 is an unsupported future version
    with pytest.raises(ValueError, match="Unsupported future major schema version 2.0.0"):
        reg.validate_schema_version("adaptation_record", "2.0.0")

def test_is_compatible_schema_version():
    assert is_compatible_schema_version("1.0.0", "1.0.0") is True
    assert is_compatible_schema_version("1.0.1", "1.1.0") is True
    assert is_compatible_schema_version("2.0.0", "1.0.0") is False
    assert is_compatible_schema_version("0.9.0", "1.0.0") is False
