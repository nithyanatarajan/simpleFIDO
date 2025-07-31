# extension_server.py
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import jwt
from config import Config
from models import ExtensionRequest
import uvicorn

app = APIRouter()


@app.post("/extensions/validate")
async def validate_extension(req: ExtensionRequest):
    try:
        # Decode and verify the JWT (signature + expiry)
        payload = jwt.decode(
            req.account_token,
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
            return JSONResponse(
                status_code=403,
                content={'status': 'invalid', 'reason': 'Invalid token issuer'}
            )

        # Validate required claims
        if not user or not account_id:
            return JSONResponse(
                status_code=400,
                content={'status': 'invalid', 'reason': 'Missing required claims in token'}
            )

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


if __name__ == "__main__":
    uvicorn.run(app, port=9000, log_level="info")
