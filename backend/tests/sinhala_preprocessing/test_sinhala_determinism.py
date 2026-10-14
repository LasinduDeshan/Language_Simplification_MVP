"""
Property test asserting Pipeline Determinism across repeated runs.
"""

from app.sinhala_preprocessing.pipeline import preprocess_sinhala_text
from app.sinhala_preprocessing.serialization import record_to_dict

SAMPLES = [
    "අම්මා මට ආදරෙයි.",
    "Grade 1: කියවීම සහ ගණිතය.",
    "පොතේ මිල රු. 12.50 කි.",
    "වෛ. පෙරේරා රෝහලට ගියේය.",
    "ශ්‍රී ලංකා ප්‍රජාතාන්ත්‍රික සමාජවාදී ජනරජය"
]

def test_pipeline_determinism_property():
    for text in SAMPLES:
        run1 = preprocess_sinhala_text(text, record_id="TEST-001")
        run2 = preprocess_sinhala_text(text, record_id="TEST-001")
        run3 = preprocess_sinhala_text(text, record_id="TEST-001")

        d1 = record_to_dict(run1)
        d2 = record_to_dict(run2)
        d3 = record_to_dict(run3)

        assert d1 == d2, f"Determinism failure between run 1 and run 2 for: {text}"
        assert d2 == d3, f"Determinism failure between run 2 and run 3 for: {text}"
        assert run1.normalized_text_sha256 == run2.normalized_text_sha256
