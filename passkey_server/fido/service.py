import base64

from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, \
    PublicKeyCredentialUserEntity, PublicKeyCredentialDescriptor, PublicKeyCredentialType

from config import Config
from exceptions import ExtensionValidationError
from fido.store import store_credential, get_credentials_for_username, get_credential, update_sign_count
from utils.encoding import b64url_decode
from utils.handle import get_user_handle
from utils.jwt import decode_challenge_token, encode_challenge_token, validate_token
from utils.retry import verify_extension_token_with_retries

rp_entity = PublicKeyCredentialRpEntity(id=Config.RP_ID, name=Config.RP_NAME)
server = Fido2Server(rp_entity)


# ---- Registration ----
def start_registration(username: str):
    user_handle = get_user_handle(username)
    user = PublicKeyCredentialUserEntity(
        id=user_handle,
        name=username,
        display_name=username
    )
    options, state = server.register_begin(user=user,
                                           credentials=[],
                                           user_verification="discouraged",
                                           authenticator_attachment="cross-platform")

    # Embed username + user_handle in challenge token
    state["username"] = username
    state["user_handle"] = base64.urlsafe_b64encode(user_handle).decode("utf-8")
    return dict(options), (encode_challenge_token(state))


def finish_registration(attestation: dict, challenge_token: str):
    # 1. Decode challenge JWT
    state = decode_challenge_token(challenge_token)

    # 2. Complete registration
    auth_data = server.register_complete(state, attestation)

    # 3. Retrieve user_handle from stored state
    user_handle = base64.urlsafe_b64decode(state["user_handle"].encode("utf-8"))

    # 4. Extension Validation
    extensions = attestation.get("extensions", {})

    # 4a. Handle accountProps.token
    account_token = extensions.get("accountProps", {}).get("token")
    if account_token:
        validate_token(account_token)

    # 4b. Log credProps (e.g., rk - resident key support)
    cred_props = auth_data.extensions.get("credProps") if auth_data.extensions else {}
    if cred_props:
        print(f"credProps from authenticator: {cred_props}")

    # 5. Print registration details
    print("Registered Credential ID:", auth_data.credential_data.credential_id)
    print("Public Key:", auth_data.credential_data.public_key)

    # 6. Save credential to in-memory store
    store_credential(
        credential_id=auth_data.credential_data.credential_id,
        user_handle=user_handle,
        public_key=auth_data.credential_data.public_key,
        sign_count=0,
        username=state["username"],
        rp_id=Config.RP_ID,
        credential_data=auth_data.credential_data,
        is_resident_key=(cred_props.get("rk", False))
    )

    return True


# ---- Authentication ----
def start_authentication(username: str):
    # 1. Load registered credentials for this user
    credentials = get_credentials_for_username(username)
    if not credentials:
        raise ValueError("User Not Found or No Credentials Registered")

    # 2. Prepare allowCredentials list
    allow_credentials = [
        PublicKeyCredentialDescriptor(
            id=cred["credential_id"],
            type=PublicKeyCredentialType.PUBLIC_KEY
        )
        for cred in credentials
    ]

    # 3. Begin authentication ceremony
    options, state = server.authenticate_begin(allow_credentials)
    state["username"] = username  # needed later for verification

    # 4. Return publicKey options + JWT-encoded state
    return dict(options), encode_challenge_token(state)


def finish_authentication(assertion: dict, challenge_token: str, account_token: str) -> bool:
    # 1. Decode challenge token (contains username + challenge)
    state = decode_challenge_token(challenge_token)
    username = state["username"]

    # 2. Lookup credential from store
    credential_id = b64url_decode(assertion["rawId"])
    stored = get_credential(credential_id)
    if not stored:
        raise ValueError("Credential not found for ID")

    # 3. Extract extension input (account_token)
    client_extensions = assertion["response"].get("clientExtensionResults", {})
    account_token_from_extension = client_extensions.get("accountProps", {}).get("token")
    print(f"Account Token: {account_token_from_extension}")

    # 3a. Use account_token from extension if available, else fallback to provided token
    account_token = account_token_from_extension or account_token
    if not account_token:
        raise ExtensionValidationError("Missing extension input: account_token")

    # 4. Verify extension token with stub server (with retries + timeout)
    result = verify_extension_token_with_retries(account_token)

    # 4a. Check if extension server returned a valid response
    if result.get("status") != "valid":
        raise ExtensionValidationError("Extension server rejected token")

    # 4b. Cross-check username with `sub` from extension server
    if result.get("user") != username:
        raise ExtensionValidationError("Username in extension token does not match")

    # 5. Match account_id if your RP is multi-tenant
    if "account_id" in stored and result.get("account_id") != stored["account_id"]:
        raise ExtensionValidationError("Account ID mismatch")

    # 6. Validate the assertion
    auth_data = server.authenticate_complete(
        state,  # from JWT
        [stored["credential_data"]],
        assertion  # raw browser response (WebAuthn assertion)
    )

    # 7. Update signature counter
    if hasattr(auth_data, "new_sign_count"):
        update_sign_count(credential_id, auth_data.new_sign_count)

    print("✅ AUTHENTICATION SUCCESS for", username)
    return True
