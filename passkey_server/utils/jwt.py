from typing import Optional

from jose import JWTError
from jwt import ExpiredSignatureError, InvalidTokenError

from config import Config
import jwt
from datetime import datetime, timezone


def encode_challenge_token(payload: dict) -> str:
    issued_at = int(datetime.now(timezone.utc).timestamp())
    payload = {
        **payload,
        "aud": Config.JWT_AUDIENCE,  # Audience for the token
        "iss": Config.JWT_ISSUER,  # 'iss': trusted issuing domain
        "iat": issued_at,  # Issued at (Unix timestamp)
        "exp": issued_at + Config.JWT_EXPIRY_SECONDS,  # Expiration (60s from iat)
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)


def decode_token(token: str, issuer: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
            options={"require": ["exp", "iat", "iss"]},
            leeway=Config.JWT_LEEWAY_SECONDS,
            issuer=issuer,
            audience=Config.JWT_AUDIENCE,
        )

        return payload

    except ExpiredSignatureError:
        raise ExpiredSignatureError("Token expired")

    except JWTError as e:
        # Catch all PyJWT errors here
        raise InvalidTokenError(f"Token validation error: {str(e)}")


def decode_challenge_token(token: str) -> dict:
    return decode_token(token, Config.JWT_ISSUER)


def validate_account_token(token: str) -> dict:
    return decode_token(token, Config.JWT_ORIGINAL_ISSUER)
