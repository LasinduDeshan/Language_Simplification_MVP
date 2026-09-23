import pytest
from app.datasets.lexicons.schemas import LexiconEntryV1
from app.datasets.common.enums import LanguageCode

def test_valid_lexicon_entry():
    entry = LexiconEntryV1(
        entry_id="LEX-EN-000001",
        language=LanguageCode.EN,
        word="purchase",
        normalized_form="purchase",
        part_of_speech="verb",
        difficulty_tier=2,
        simpler_alternatives=["buy"],
        child_friendly_definition="To get something by paying money."
    )
    assert entry.entry_id == "LEX-EN-000001"
    assert entry.difficulty_tier == 2
    assert "buy" in entry.simpler_alternatives

def test_invalid_lexicon_id():
    with pytest.raises(ValueError, match="Invalid entry_id format"):
        LexiconEntryV1(
            entry_id="INVALID-ID",
            word="purchase",
            normalized_form="purchase"
        )
