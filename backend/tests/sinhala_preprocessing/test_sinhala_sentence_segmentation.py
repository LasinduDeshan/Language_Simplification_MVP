"""
Tests for Stage 30 Sentence Segmentation.
"""

from app.sinhala_preprocessing.sentence_segmenter import segment_sentences

def test_western_full_stop_and_questions():
    text = "මම පාසල් යමි. ඔබට කොහොමද? ඉතා හොඳයි!"
    sentences = segment_sentences(text)
    assert len(sentences) == 3
    assert sentences[0].text == "මම පාසල් යමි."
    assert sentences[0].boundary_rule == "FULL_STOP"
    assert sentences[1].text == "ඔබට කොහොමද?"
    assert sentences[1].boundary_rule == "QUESTION_MARK"
    assert sentences[2].text == "ඉතා හොඳයි!"
    assert sentences[2].boundary_rule == "EXCLAMATION_MARK"

def test_decimal_protection():
    text = "පොතේ මිල රු. 12.50 කි. එය මිලදී ගන්න."
    sentences = segment_sentences(text)
    assert len(sentences) == 2
    assert "12.50" in sentences[0].text
    assert sentences[1].text == "එය මිලදී ගන්න."

def test_abbreviation_protection():
    text = "වෛ. පෙරේරා මහතා රෝහලට ගියේය. ඔහු ලෙඩුන් බැලීය."
    sentences = segment_sentences(text)
    assert len(sentences) == 2
    assert "වෛ." in sentences[0].text

def test_kunddaliya_boundary():
    text = "සිංහල පාඩම මෙතෙකින් නිමයි෴"
    sentences = segment_sentences(text)
    assert len(sentences) == 1
    assert sentences[0].boundary_rule == "KUNDDALIYA"
