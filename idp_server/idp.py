import base64
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import Config
from database.users_stub import USERS
from models import TokenRequest, TokenResponse
from utils import create_jwt_token

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/token/generate", response_model=TokenResponse)
def generate_token(payload: TokenRequest):
    user = USERS.get(payload.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not payload.password:
        raise HTTPException(status_code=400, detail="Password required")
    if not payload.account_id:
        raise HTTPException(status_code=400, detail="Account Id required")

    # Encode the input password and compare against stored token
    encoded_input = base64.b64encode(payload.password.encode()).decode()
    stored_encoded = user.get("token")
    if encoded_input != stored_encoded:
        raise HTTPException(status_code=401, detail="Invalid password")

    if payload.account_id not in user["accounts"]:
        raise HTTPException(status_code=403, detail="Invalid account access")

    # Create base token data
    issued_at = int(datetime.now(timezone.utc).timestamp())
    base_token_data = {
        Config.USER_KEY: payload.username,  # Unique user ID (substitute for 'sub')
        Config.ACCOUNT_ID_KEY: payload.account_id,  # Org or tenant scoping
        "sub": user["id"],
        "iss": Config.JWT_ISSUER,  # 'iss': trusted issuing domain
        "iat": issued_at,  # Issued at (Unix timestamp)
        "exp": issued_at + Config.JWT_EXPIRY_SECONDS,  # Expiration (60s from iat)
    }

    # Create tokens for RP and extension
    encoded_jwt_rp = create_jwt_token(base_token_data.copy(), Config.JWT_AUDIENCE_RP)
    encoded_jwt_extn = create_jwt_token(base_token_data.copy(), Config.JWT_AUDIENCE_EXTN)

    return {"token_rp": encoded_jwt_rp, "token_extn": encoded_jwt_extn}


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


if __name__ == "__main__":
    uvicorn.run(app, port=8001, log_level="info")
