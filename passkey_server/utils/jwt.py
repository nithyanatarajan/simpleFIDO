from typing import Optional

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from config import Config


def encode_challenge_token(token: str) -> str:
    return jwt.encode(token, Config.JWT_SECRET, algorithm="HS256")


def decode_challenge_token(token: str) -> dict:
    return jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])


def validate_token(token: str) -> Optional[dict]:
    """
    Validates and decodes a JWT token used for account validation.

    Returns the payload if valid, else raises an appropriate exception.
    """
    try:
        payload = jwt.decode(
            token,
            Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
            options={"require": ["exp", "iat", "iss"]},
            leeway=Config.JWT_LEEWAY_SECONDS
        )

        if payload.get("iss") != Config.JWT_ISSUER:
            raise InvalidTokenError("Invalid issuer")

        return payload

    except ExpiredSignatureError:
        raise ExpiredSignatureError("Account token expired")

    except InvalidTokenError as e:
        raise InvalidTokenError(f"Invalid account token: {str(e)}")
