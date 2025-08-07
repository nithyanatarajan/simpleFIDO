# errors.py
class ExtensionValidationError(Exception):
    """Base exception for all validation errors in the extension server."""

    def __init__(self, reason: str, status_code: int = 400):
        self.reason = reason
        self.status_code = status_code


class InvalidTokenError(ExtensionValidationError):
    def __init__(self, reason: str = None):
        super().__init__(
            reason=reason or "Invalid or missing token: The provided token is either invalid or not present",
            status_code=401
        )


class TokenExpiredError(ExtensionValidationError):
    """Raised when JWT is expired."""

    def __init__(self):
        super().__init__("Token expired", status_code=401)


class ChallengeMismatchError(ExtensionValidationError):
    def __init__(self):
        super().__init__(
            reason="Missing or expired challenge",
            status_code=401
        )

class MissingClaimsError(ExtensionValidationError):
    """Raised when required claims are missing from the token."""

    def __init__(self):
        super().__init__("Missing required claims", status_code=400)


class InvalidCredentialFormatError(ExtensionValidationError):
    def __init__(self):
        super().__init__(
            reason="Invalid credential format",
            status_code=400
        )


class UsernameMismatchError(ExtensionValidationError):
    def __init__(self):
        super().__init__(
            reason="Username mismatch: The provided username does not match the token's user",
            status_code=403
        )
