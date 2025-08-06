import uvicorn
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import Config
from exceptions.handlers import register_exception_handlers
from fido.service import (
    start_registration,
    finish_registration,
    start_authentication,
    finish_authentication,
)
from models import BeginResponse, CompleteResponse
from models import RegisterBeginRequest, RegisterCompleteRequest, AuthBeginRequest, AuthCompleteRequest

app = FastAPI()
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Security scheme for bearer token
security = HTTPBearer(auto_error=True)


# Dependency to verify bearer token is not empty
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing bearer token: Authorization header provided but token is empty"
        )
    return credentials.credentials


@app.post("/register/begin", response_model=BeginResponse)
def register_options(payload: RegisterBeginRequest):
    public_key, challenge_token = start_registration(payload.username)
    return JSONResponse(content={
        "publicKey": public_key['publicKey'],
        "challenge_token": challenge_token,
    })


@app.post("/register/complete", response_model=CompleteResponse)
def register_verify(payload: RegisterCompleteRequest, rp_account_token: str = Depends(verify_token)):
    finish_registration(payload.attestation, payload.challenge_token, rp_account_token)
    return {"status": "OK"}


@app.post("/authenticate/begin", response_model=BeginResponse)
def authenticate_begin(payload: AuthBeginRequest):
    public_key, challenge_token = start_authentication(payload.username)
    return JSONResponse(content={
        "publicKey": public_key['publicKey'],
        "challenge_token": challenge_token,
    })


@app.post("/authenticate/complete", response_model=CompleteResponse)
def authenticate_complete(payload: AuthCompleteRequest, rp_account_token: str = Depends(verify_token)):
    finish_authentication(payload.assertion, payload.challenge_token, rp_account_token)
    return JSONResponse(content={"status": "OK"})


if __name__ == "__main__":
    uvicorn.run(app, port=8000, log_level="info")
