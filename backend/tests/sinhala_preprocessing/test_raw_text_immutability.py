"""
Property test asserting Raw Text Immutability.
Verifies raw_text and raw_text_sha256 are never altered regardless of transformations.
"""

import hashlib
from app.sinhala_preprocessing.pipeline import preprocess_sinhala_text

TEST_INPUTS = [
    "අම්මා මට ආදරෙයි.",
    "   අක්‍රමවත්   හිස්තැන් සහිත පාඨය.   \r\nනව පේළිය.",
    "Grade 2: සිංහල කියවීම.",
    "මම \uFFFD යමි.",
    "මම\u0000පාසල් යමි.",
    "\u0DCFම්මා"
]

def test_raw_text_immutability_property():
    for text in TEST_INPUTS:
        original_copy = str(text)
        original_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()

        rec = preprocess_sinhala_text(raw_text=text)

        # Raw text in record must equal original
        assert rec.raw_text == original_copy
        assert rec.raw_text_sha256 == original_sha
        assert rec.raw_utf8_byte_count == len(original_copy.encode("utf-8"))
        assert rec.raw_code_point_count == len(original_copy)

        # Original variable must not be mutated
        assert text == original_copy
