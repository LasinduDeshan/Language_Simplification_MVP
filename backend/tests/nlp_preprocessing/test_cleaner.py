"""
Unit tests for Conservative Cleaner
"""
from app.nlp_preprocessing.cleaner import ConservativeCleaner

def test_cleaner_removes_control_characters():
    cleaner = ConservativeCleaner()
    dirty = "Hello\x00World\x1F! \t\t How are you?"
    cleaned, audit = cleaner.clean(dirty)
    assert "\x00" not in cleaned
    assert "\x1F" not in cleaned
    assert "HelloWorld! How are you?" in cleaned
    assert len(audit) == 2

def test_cleaner_preserves_multiline_steps():
    cleaner = ConservativeCleaner()
    text = "1. Pick up ball.\n2. Put in box."
    cleaned, _ = cleaner.clean(text)
    assert "1. Pick up ball.\n2. Put in box." == cleaned
