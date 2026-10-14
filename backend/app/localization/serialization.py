"""
UTF-8 serialization, export services, and byte-level SHA-256 verification.
"""
import io
import csv
import json
import hashlib
from typing import List, Dict, Any, Tuple

def serialize_to_utf8_json(data: Any, indent: int = 2) -> Tuple[bytes, str]:
    """
    Serialize data to UTF-8 bytes and return (bytes, sha256_hex).
    Ensures ensure_ascii=False for native Unicode characters.
    """
    json_str = json.dumps(data, ensure_ascii=False, indent=indent)
    raw_bytes = json_str.encode("utf-8")
    sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
    return raw_bytes, sha256_hash

def serialize_to_utf8_csv(
    rows: List[Dict[str, Any]], 
    fieldnames: List[str], 
    use_bom: bool = False
) -> Tuple[bytes, str]:
    """
    Serialize tabular data to UTF-8 CSV bytes and return (bytes, sha256_hex).
    Optionally prepends UTF-8 BOM (0xEF, 0xBB, 0xBF) for spreadsheet compatibility.
    """
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    
    csv_str = output.getvalue()
    raw_bytes = csv_str.encode("utf-8")
    if use_bom:
        raw_bytes = b"\xef\xbb\xbf" + raw_bytes
        
    sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
    return raw_bytes, sha256_hash

def verify_export_bytes(raw_bytes: bytes, expected_hash: str) -> Tuple[bool, str]:
    """
    Verify exact SHA-256 byte hash of exported artifact.
    """
    actual_hash = hashlib.sha256(raw_bytes).hexdigest()
    return (actual_hash == expected_hash, actual_hash)
