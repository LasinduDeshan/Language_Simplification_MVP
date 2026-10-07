"""
Semantic version definitions and compatibility validators for Stage 14 datasets.
"""
import re

SEMVER_REGEX = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

CURRENT_SCHEMA_VERSION = "1.0.0"
CURRENT_DATASET_VERSION = "0.1.0"
SUPPORTED_SCHEMA_VERSIONS = ["1.0.0"]

def parse_semver(v_str: str):
    m = SEMVER_REGEX.match(v_str)
    if not m:
        raise ValueError(f"Invalid SemVer string: {v_str}")
    return tuple(map(int, m.groups()))

def is_compatible_schema_version(record_version: str, reader_version: str = CURRENT_SCHEMA_VERSION) -> bool:
    """
    Checks if a record's schema version is compatible with reader version.
    Major versions must match. Record minor version must not exceed reader minor version.
    """
    try:
        rec_major, rec_minor, _ = parse_semver(record_version)
        read_major, read_minor, _ = parse_semver(reader_version)
    except ValueError:
        return False

    if rec_major != read_major:
        return False
    if rec_minor > read_minor:
        return False
    return True
