import json
from datetime import datetime, timezone
from fastapi import HTTPException
from jose.utils import base64url_decode
from config import Config
from store.challenge import generate_challenge, store_challenge, pop_stored_challenge
from validations.validate import validate_runtime_token


async def handle_extension_prepare(username: str, token: str) -> dict:
    user, account_id = await validate_runtime_token(token)

    if user != username:
        raise HTTPException(
            status_code=403,
            detail="Username mismatch: The provided username does not match the token's user"
        )

    challenge = generate_challenge()
    store_challenge(user, challenge)
    issued_at = int(datetime.now(timezone.utc).timestamp())

    return {
        "status": "valid",
        Config.USER_KEY: user,
        Config.ACCOUNT_ID_KEY: account_id,
        "challenge": challenge,
        "issued_at": issued_at,
        "registered": True
    }


async def handle_extension_validation(username: str, token: str, credential: dict) -> dict:
    user, account_id = await validate_runtime_token(token)

    if user != username:
        raise HTTPException(
            status_code=403,
            detail="Username mismatch: The provided username does not match the token's user"
        )

    stored_challenge = pop_stored_challenge(user)
    if not stored_challenge:
        raise HTTPException(status_code=400, detail="Missing or expired challenge")

    try:
        client_data_b64 = credential.get("response", {}).get("clientDataJSON")
        if not client_data_b64:
            raise ValueError("Missing clientDataJSON")

        client_data_json = json.loads(base64url_decode(client_data_b64).decode("utf-8"))
        received_challenge = client_data_json.get("challenge")

        if received_challenge != stored_challenge:
            raise ValueError("Challenge mismatch")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    return {
        "status": "valid",
        Config.USER_KEY: user,
        Config.ACCOUNT_ID_KEY: account_id,
        "authenticated": True
    }
