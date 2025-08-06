import base64

from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, \
    PublicKeyCredentialUserEntity, PublicKeyCredentialDescriptor, PublicKeyCredentialType

from config import Config
from exceptions import ExtensionValidationError
from fido.store import store_credential, get_credentials_for_username, get_credential, update_sign_count
from utils.encoding import b64url_decode
from utils.handle import get_user_handle
from utils.jwt import decode_challenge_token, encode_challenge_token, validate_account_token

rp_entity = PublicKeyCredentialRpEntity(id=Config.RP_ID, name=Config.RP_NAME)
server = Fido2Server(rp_entity)


# ---- Registration ----
def start_registration(username: str) -> tuple[dict, str]:
    """
    Begins the WebAuthn registration ceremony for a given username.

    Returns:
        - publicKeyCredentialCreationOptions (dict)
        - challenge_token (JWT-encoded state)
    """
    # 1. Generate user handle (should be stable across logins)
    user_handle = get_user_handle(username)

    # 2. Create user entity
    user = PublicKeyCredentialUserEntity(
        id=user_handle,
        name=username,
        display_name=username
    )

    # 3. Begin registration ceremony
    options, state = server.register_begin(user=user,
                                           credentials=[],
                                           resident_key_requirement="preferred",
                                           user_verification="discouraged",
                                           authenticator_attachment="cross-platform")

    # 4. Embed state metadata into token (for stateless verification)
    state["username"] = username
    state["user_handle"] = base64.urlsafe_b64encode(user_handle).decode("utf-8")

    # 5. Return as tuple (options, challenge_token)
    return dict(options), encode_challenge_token(state)


def finish_registration(attestation: dict, challenge_token: str, rp_account_token: str) -> bool:
    """
    Completes the WebAuthn registration process.

    Validates the signed challenge, attestation response, and account-level token.
    Saves credential to in-memory store on success.
    """

    # 1. Decode and validate challenge token (issued during /register/begin)
    state = decode_challenge_token(challenge_token)
    username = state.get("username")
    user_handle_b64 = state.get("user_handle")
    if not (username and user_handle_b64):
        raise ValueError("Malformed challenge token")

    # 2. Complete FIDO2/WebAuthn registration
    auth_data = server.register_complete(state, attestation)

    # 3. Decode user handle from base64
    try:
        user_handle = base64.urlsafe_b64decode(user_handle_b64.encode("utf-8"))
    except Exception as e:
        raise ValueError("Invalid user handle encoding") from e

    # 4. Validate account token (from IdP), restrict to extension server
    claims = validate_account_token(rp_account_token)
    if claims.get(Config.USER_KEY) != username:
        raise ValueError("Account token does not match user")

    # 5. Inspect standard extension `credProps` (optional)
    cred_props = attestation.get('extensions', {}).get('credProps') if attestation.get('extensions') else {}
    if cred_props:
        print(f"credProps from authenticator: {cred_props}")
    else:
        print("No credProps extension found in authenticator response")

    # 6. Store credential in in-memory DB
    store_credential(
        credential_id=auth_data.credential_data.credential_id,
        user_handle=user_handle,
        public_key=auth_data.credential_data.public_key,
        sign_count=0,
        username=username,
        rp_id=Config.RP_ID,
        credential_data=auth_data.credential_data,
        is_resident_key=cred_props.get("rk", False),
    )

    print("✅ REGISTRATION SUCCESS for", username)
    return True


# ---- Authentication ----
def start_authentication(username: str):
    # 1. Load registered credentials for this user
    credentials = get_credentials_for_username(username)
    if not credentials:
        raise ValueError("User not found or no credentials registered")

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
    state["username"] = username  # Required later during verification

    # 4. Return publicKey options + JWT-encoded state
    return dict(options), encode_challenge_token(state)


def finish_authentication(assertion: dict, challenge_token: str, rp_access_token: str) -> bool:
    """
    Completes the WebAuthn authentication ceremony.

    :param assertion: WebAuthn assertion from the browser
    :param challenge_token: Encoded JWT state from /authenticate/begin
    :param rp_access_token: JWT issued by IdP (aud: rp-server)
    :return: True if successful, raises on failure
    """
    # 1. Decode challenge token and extract session state
    state = decode_challenge_token(challenge_token)
    username = state["username"]

    # 2. Lookup credential in server-side store
    credential_id = b64url_decode(assertion["rawId"])
    stored = get_credential(credential_id)
    if not stored:
        raise ValueError("Credential not found for ID")

    # 3. Validate RP access token (audience should be rp-server)
    claims = validate_account_token(rp_access_token)
    if claims.get(Config.USER_KEY) != username:
        raise ValueError("Account token does not match user")

    # 4. Match account_id if your system is multi-tenant
    if "account_id" in stored and claims.get(Config.ACCOUNT_ID_KEY) != stored["account_id"]:
        raise ExtensionValidationError("Account ID mismatch")

    # 5. Complete authentication ceremony (validates signature, challenge, origin)
    auth_data = server.authenticate_complete(
        state,  # from JWT
        [stored["credential_data"]],
        assertion  # raw browser response (WebAuthn assertion)
    )

    # 6. Update stored signature counter (prevents cloned credential replay)
    if hasattr(auth_data, "new_sign_count"):
        update_sign_count(credential_id, auth_data.new_sign_count)

    print("✅ AUTHENTICATION SUCCESS for", username)
    return True
