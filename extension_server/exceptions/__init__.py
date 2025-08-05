class TokenValidationError(Exception):
    """Raised when jwt token validation fails."""

    def __init__(self, reason: str, status_code: int = 401):
        self.reason = reason
        self.status_code = status_code
