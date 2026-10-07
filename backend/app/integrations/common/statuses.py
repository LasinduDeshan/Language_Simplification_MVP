"""
Standard integration status constants for Stage 12 responsibility boundaries.
"""

STATUS_MOCK = "mock"
STATUS_NOT_CONNECTED = "not_connected"
STATUS_READY_FOR_INTEGRATION = "ready_for_integration"
STATUS_CONNECTED = "connected"
STATUS_CONNECTION_FAILED = "connection_failed"

VALID_INTEGRATION_STATUSES = {
    STATUS_MOCK,
    STATUS_NOT_CONNECTED,
    STATUS_READY_FOR_INTEGRATION,
    STATUS_CONNECTED,
    STATUS_CONNECTION_FAILED,
}
