import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import Config
from exceptions.handlers import register_exception_handlers
from fido.service import (
    start_registration,
    finish_registration,
    start_authentication,
    finish_authentication,
)
from models import RegisterBeginRequest, RegisterCompleteRequest, AuthBeginRequest, AuthCompleteRequest

app = FastAPI()
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.post("/register/begin")
def register_options(payload: RegisterBeginRequest):
    public_key, challenge_token = start_registration(payload.username, payload.account, payload.org_id)
    return JSONResponse(content={
        "publicKey": public_key['publicKey'],
        "challenge_token": challenge_token,
    })


@app.post("/register/complete")
def register_verify(payload: RegisterCompleteRequest):
    finish_registration(payload.attestation, payload.challenge_token)
    return {"status": "OK"}


@app.post("/authenticate/begin")
def authenticate_begin(payload: AuthBeginRequest):
    try:
        print('auth begin')
        public_key, challenge_token = start_authentication(payload.username, payload.org_id)
        return JSONResponse(content={
            "publicKey": public_key['publicKey'],
            "challenge_token": challenge_token,
        })
    except ValueError:
        raise HTTPException(status_code=404, detail="User Not Found, No credentials registered")


@app.post("/authenticate/complete")
def authenticate_complete(payload: AuthCompleteRequest):
    finish_authentication(payload.assertion, payload.challenge_token, payload.account_token)
    return JSONResponse(content={"status": "OK"})


if __name__ == "__main__":
    uvicorn.run(app, port=8000, log_level="info")
