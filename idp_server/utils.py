import secrets
import uuid

import jwt

from config import Config


def create_jwt_token(data: dict, audience: str) -> str:
    """
    Helper function to create a JWT token with the given data and audience.

    Args:
        data: Dictionary containing the token payload data
        audience: The audience for the token

    Returns:
        str: The encoded JWT token
    """
    # Set the audience in the data
    data["aud"] = audience

    # Generate a unique JWT ID and nonce
    data["jti"] = str(uuid.uuid4())
    data["nonce"] = secrets.token_urlsafe(16)

    # Encode and return the JWT token
    return jwt.encode(data, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
