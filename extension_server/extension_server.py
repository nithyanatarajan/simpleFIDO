# extension_server.py
import json
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose.utils import base64url_decode

from config import Config
from exceptions.errors import InvalidTokenError, ChallengeMismatchError, InvalidCredentialFormatError
from exceptions.handlers import register_exception_handlers
from models \
    import ExtensionRegistrationResponse, ExtensionValidationResponse, ExtensionValidationRequest, \
    ExtensionRegistrationRequest
from store.challenge import store_challenge, generate_challenge, pop_stored_challenge
from utils.encoding import b64url_decode
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
        raise InvalidTokenError("Missing bearer token: Authorization header provided but token is empty")
    return credentials.credentials


@app.post("/extensions/prepare", response_model=ExtensionRegistrationResponse)
async def prepare_registration_context(payload: ExtensionRegistrationRequest,
                                       extn_account_token: str = Depends(verify_token)):
    user, account_id = await validate_runtime_token(extn_account_token, payload.username)

    # Generate challenge (base64url-encoded)
    challenge = generate_challenge()

    # Store
    store_challenge(user, challenge)

    issued_at = int(datetime.now(timezone.utc).timestamp())
    return {
        "status": "valid",
        Config.USER_KEY: user,
        Config.ACCOUNT_ID_KEY: account_id,
        "challenge": challenge,
        "issued_at": issued_at,  # Unix timestamp
        "registered": True,  # example additional claim
    }


@app.post("/extensions/validate", response_model=ExtensionValidationResponse)
async def validation_context(payload: ExtensionValidationRequest,
                             extn_account_token: str = Depends(verify_token)):
    user, account_id = await validate_runtime_token(extn_account_token, payload.username)

    stored_challenge = pop_stored_challenge(user)
    if not stored_challenge:
        raise ChallengeMismatchError()

    # Bare-minimum validation: Check challenge round-trip
    client_data_b64 = (payload.credential.get("response", {}).get("clientDataJSON"))
    if not client_data_b64:
        raise InvalidCredentialFormatError()

    client_data_json = json.loads(b64url_decode(client_data_b64))
    received_challenge = client_data_json.get("challenge")

    if received_challenge != stored_challenge:
        raise ChallengeMismatchError()

    return {
        "status": "valid",
        Config.USER_KEY: user,
        Config.ACCOUNT_ID_KEY: account_id,
        "authenticated": True  # example additional claim
    }


if __name__ == "__main__":
    uvicorn.run(app, port=9000, log_level="info")
