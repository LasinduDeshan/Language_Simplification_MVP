"""
Property test asserting NFC Normalization Idempotence: NFC(NFC(x)) == NFC(x).
"""

import unicodedata

SAMPLES = [
    "අම්මා මට ආදරෙයි.",
    "ශ්‍රී ලංකා ප්‍රජාතාන්ත්‍රික සමාජවාදී ජනරජය",
    "ක\u0DCA\u200Dරමය",
    "Grade 1: කියවීම",
    "පොතේ මිල රු. 12.50 කි.",
    "වෛ. පෙරේරා මහතා රෝහලට ගියේය.",
    "අංකය ෧ වේ.",
    "සිංහල පාඩම මෙතෙකින් නිමයි෴",
    "   හිස්තැන් සහිත පාඨය   "
]

def test_nfc_idempotence_property():
    for text in SAMPLES:
        first_pass = unicodedata.normalize("NFC", text)
        second_pass = unicodedata.normalize("NFC", first_pass)
        third_pass = unicodedata.normalize("NFC", second_pass)

        assert first_pass == second_pass, f"Idempotence failed on second pass for: {text}"
        assert second_pass == third_pass, f"Idempotence failed on third pass for: {text}"
