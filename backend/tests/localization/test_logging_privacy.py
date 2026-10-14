"""
Privacy and security tests: ensure raw child text and control characters are escaped in logs.
"""
from app.localization.invisible_characters import escape_controls_for_log

def test_escaped_controls_in_logging():
    # Invisible controls and directional overrides must be escaped
    log_msg = "User action: \u200B\u200D\u202E"
    escaped = escape_controls_for_log(log_msg)
    assert "\u200B" not in escaped
    assert "\u200D" not in escaped
    assert "\u202E" not in escaped
    assert "\\u200b" in escaped
    assert "\\u200d" in escaped
    assert "\\u202e" in escaped

def test_ascii_and_clean_text_unchanged():
    clean_msg = "Task started successfully."
    assert escape_controls_for_log(clean_msg) == clean_msg
