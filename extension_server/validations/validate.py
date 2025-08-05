# validate.py
import jwt

from config import Config
from exceptions import TokenValidationError


async def validate_runtime_token(token):
    try:
        # Decode and verify the JWT (signature + expiry)
        payload = jwt.decode(
            token,
            Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
            leeway=Config.JWT_LEEWAY_SECONDS  # allows 30 seconds skew
        )

        # Extract claims
        user = payload.get(Config.USER_KEY)
        account_id = payload.get(Config.ACCOUNT_ID_KEY)
        issuer = payload.get(Config.ISSUER_KEY)

        # Validate issuer
        if issuer != Config.JWT_ISSUER:
            raise TokenValidationError("Invalid token issuer", status_code=403)

        # Validate required claims
        if not user or not account_id:
            raise TokenValidationError("Missing required claims", status_code=400)

        return user, account_id

    except jwt.ExpiredSignatureError:
        raise TokenValidationError("Token expired", status_code=401)

    except jwt.InvalidTokenError:
        raise TokenValidationError("Invalid token", status_code=401)
