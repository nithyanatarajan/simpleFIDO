# extension_server.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import jwt
from accounts import VALID_ACCOUNTS
from config import Config
from models import ExtensionRequest

app = APIRouter()


@app.post("/extensions/validate")
async def validate_extension(req: ExtensionRequest):
    try:
        # 1. Decode and verify the JWT (signature + expiry)
        payload = jwt.decode(req.account_token, Config.JWT_SECRET, algorithms=['HS256'])
        user = payload.get(Config.USER_KEY)
        account_id = payload.get(Config.ACCOUNT_ID_KEY)

        if not user or not account_id:
            return JSONResponse(
                status_code=400,
                content={'status': 'invalid', 'reason': 'Missing required claims in token'}
            )

        # 2. Domain-specific check
        allowed_accounts = VALID_ACCOUNTS.get(user, [])
        if account_id not in allowed_accounts:
            return JSONResponse(
                status_code=403,
                content={'status': 'invalid', 'reason': 'Unauthorized account access'}
            )

        # Validated
        return JSONResponse(
            status_code=200,
            content={'status': 'valid', Config.USER_KEY: user, Config.ACCOUNT_ID_KEY: account_id}
        )

    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=401,
            content={'status': 'invalid', 'reason': 'Token expired'}
        )

    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=401,
            content={'status': 'invalid', 'reason': 'Invalid token'}
        )
