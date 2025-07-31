import base64
from datetime import datetime
from datetime import timezone

import jwt
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import Config
from database.users_stub import USERS
from models import TokenRequest, TokenResponse

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

    issued_at = int(datetime.now(timezone.utc).timestamp())
    token_data = {
        Config.USER_KEY: payload.username,
        Config.USER_NAME_KEY: user["name"],
        Config.ACCOUNT_ID_KEY: payload.account_id,
        Config.ISSUER_KEY: Config.JWT_ISSUER,
        "iat": issued_at,
        "exp": issued_at + Config.JWT_EXPIRY_SECONDS
    }

    encoded_jwt = jwt.encode(token_data, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
    return {"token": encoded_jwt}


@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


if __name__ == "__main__":
    uvicorn.run(app, port=8001, log_level="info")
