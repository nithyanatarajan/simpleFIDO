# extension_server.py
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import Config
from exceptions.handlers import register_exception_handlers
from models import RegResponse, AuthResponse
from validations.validate import validate_runtime_token

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


@app.post("/extensions/prepare", response_model=RegResponse)
async def prepare_registration_context(extn_account_token: str = Depends(verify_token)):
    user, account_id = await validate_runtime_token(extn_account_token)
    return {
        "status": "valid",
        Config.USER_KEY: user,
        Config.ACCOUNT_ID_KEY: account_id,
        "org": "example_corp",  # optional extras
        "region": "IN",
        "registered": True,  # example additional claim
    }


@app.post("/extensions/validate", response_model=AuthResponse)
async def validation_context(extn_account_token: str = Depends(verify_token)):
    user, account_id = await validate_runtime_token(extn_account_token)
    return {
        "status": "valid",
        Config.USER_KEY: user,
        Config.ACCOUNT_ID_KEY: account_id,
        "org": "example_corp",  # optional extras
        "region": "IN",
        "authenticated": True  # example additional claim
    }


if __name__ == "__main__":
    uvicorn.run(app, port=9000, log_level="info")
