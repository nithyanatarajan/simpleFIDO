# validate.py
import jwt

from config import Config
from exceptions.errors import TokenExpiredError, MissingClaimsError, InvalidTokenError, UsernameMismatchError


async def validate_runtime_token(token, current_user: str) -> tuple[str, str]:
    try:
        # Decode and verify the JWT (signature + expiry)
        payload = jwt.decode(
            token,
            Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
            leeway=Config.JWT_LEEWAY_SECONDS,  # allows 30 seconds skew
            issuer=Config.JWT_ORIGINAL_ISSUER,
            audience=Config.JWT_AUDIENCE,
        )

        # Extract claims
        payload_user = payload.get(Config.USER_KEY)
        account_id = payload.get(Config.ACCOUNT_ID_KEY)

        # Validate required claims
        if not payload_user or not account_id:
            raise MissingClaimsError()

        if payload_user != current_user:
            raise UsernameMismatchError()

        return payload_user, account_id

    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()

    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token")
