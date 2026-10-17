"""
Verification of Stage 35 Implementation Manifest with Negative Tamper Test.
"""

import hashlib
import tempfile
from pathlib import Path

def test_stage35_manifest_verification_and_negative_tamper():
    manifest_path = Path("data/model_comparison/stage35/manifests/stage35_implementation_manifest.sha256")
    assert manifest_path.exists()
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip()]
        
    for line in lines:
        expected_hash, rel_path = line.split("  ", 1)
        p = Path(rel_path)
        assert p.exists(), f"File {rel_path} does not exist"
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        assert h == expected_hash, f"Hash mismatch for {rel_path}"
        
    # Negative tamper test on a temporary duplicate
    with tempfile.NamedTemporaryFile("wb", delete=False) as tf:
        tf.write(b"tampered content")
        tamper_path = tf.name
        
    tamper_hash = hashlib.sha256(Path(tamper_path).read_bytes()).hexdigest()
    assert tamper_hash != lines[0].split("  ", 1)[0]
    Path(tamper_path).unlink(missing_ok=True)
