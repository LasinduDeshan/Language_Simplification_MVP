"""
Integration error hierarchy for cross-component contracts.
"""

class IntegrationError(Exception):
    """Base exception for cross-component integration issues."""
    pass

class InvalidMockFixtureError(IntegrationError):
    """Raised when a mock fixture violates simulated data requirements."""
    pass

class ComponentDisabledError(IntegrationError):
    """Raised when an external API route is invoked while in mock mode."""
    pass

class ContractValidationError(IntegrationError):
    """Raised when an integration payload violates the agreed schema."""
    pass
