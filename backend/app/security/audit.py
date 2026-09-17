import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger("audit_logger")
logger.setLevel(logging.INFO)

# Formatter
handler = logging.StreamHandler()
formatter = logging.Formatter('{"timestamp": "%(asctime)s", "event": %(message)s}')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)

def log_audit_event(event_type: str, details: Dict[str, Any]):
    """
    Logs system and security events without sensitive personal data.
    """
    payload = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details
    }
    logger.info(str(payload).replace("'", '"'))
