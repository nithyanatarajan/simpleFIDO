# 📜 FIDO2 + Passkey Flow (with `accountProps` Custom Extension)

## 🔐 1. Pre-Authentication: `POST /token/generate` (IdP)

| **Step** | **Actor**  | **Responsibility** | **Details**                                                                                       |
|----------|------------|--------------------|---------------------------------------------------------------------------------------------------|
| 1        | **Client** | Send credentials   | Sends `username`, `password`, and `account_id` to IdP                                             |
| 2        | **IdP**    | Validate user      | Validates user from in-memory DB (`users_stub.py`) by base64-checking password and account\_id    |
| 3        | **IdP**    | Generate JWTs      | Issues two scoped JWTs:<br/>`access_token_rp` for RP,<br/>`access_token_ext` for Extension Server |
| 4        | **IdP**    | Return to Client   | Returns `{ access_token_rp, access_token_ext }` to client                                         |

> These tokens are short-lived and **stateless**, used to drive downstream flows securely.

---

## 📝 2. Registration Flow

### `POST /register/begin` (RP)

| **Step** | **Actor**     | **Responsibility**      | **Details**                                                                                       |
|----------|---------------|-------------------------|---------------------------------------------------------------------------------------------------|
| 1        | **Client**    | Sends username          | Sends `username` only. Tokens not used here.                                                      |
| 2        | **RP Server** | Generate challenge      | Generates a random challenge.                                                                     |
| 3        | **RP Server** | Derive `user_handle`    | Derived from `username`, e.g., `sha256(username)`, base64-encoded                                 |
| 4        | **RP Server** | Create challenge token  | JWT-encodes `{ username, challenge, user_handle }`                                                |
| 5        | **RP Server** | Return to client        | Returns `{ publicKey, challenge_token }`. `publicKey` is used in `navigator.credentials.create()` |
| 6        | **Client**    | Start WebAuthn creation | Calls `navigator.credentials.create({ publicKey })`                                               |

### `POST /register/complete` (RP)

| **Step** | **Actor**            | **Responsibility**            | **Details**                                                      |
|----------|----------------------|-------------------------------|------------------------------------------------------------------|
| 1        | **Client**           | Submit attestation + token    | Sends `{ credential, challenge_token }` to RP                    |
| 2        | **RP Server**        | Decode challenge              | Extracts and verifies challenge from token                       |
| 3        | **RP Server**        | Validate WebAuthn attestation | Validates attestationObject + clientDataJSON                     |
| 4        | **RP Server**        | Extract extension values      | Looks for `accountProps` in `clientExtensionResults` (optional)  |
| 5        | **RP Server**        | Validate `accountProps` (opt) | If present, extracts `token` and POSTs to `/extensions/validate` |
| 6        | **Extension Server** | Validate extension token      | Checks JWT: `user`, `account_id`, `iss`, `aud`, expiry           |
| 7        | **RP Server**        | Finalize                      | Saves credential and user\_handle                                |
| 8        | **RP Server**        | Respond                       | Sends `{ status: ok }` to client                                 |

---

## 🔁 3. Authentication Flow

### `POST /authenticate/begin` (RP)

| **Step** | **Actor**     | **Responsibility**          | **Details**                                                                   |
|----------|---------------|-----------------------------|-------------------------------------------------------------------------------|
| 1        | **Client**    | Send user + account token   | Sends `username` and `account_token`                                          |
| 2        | **RP Server** | Validate `account_token`    | Checks signature, `exp`, `aud`, `iss`, and claims                             |
| 3        | **RP Server** | Retrieve stored credentials | Fetches credentials using `username`                                          |
| 4        | **RP Server** | Generate challenge          | Generates fresh challenge                                                     |
| 5        | **RP Server** | Create challenge token      | JWT-encodes `{ username, challenge }`                                         |
| 6        | **RP Server** | Return publicKey            | Returns `{ publicKey, challenge_token }` for `navigator.credentials.get()`    |
| 7        | **Client**    | Call `navigator.get()`      | Triggers authenticator UI and sends `accountProps` via clientExtensionResults |

### `POST /authenticate/complete` (RP)

| **Step** | **Actor**            | **Responsibility**              | **Details**                                                                 |
|----------|----------------------|---------------------------------|-----------------------------------------------------------------------------|
| 1        | **Client**           | Send assertion + token          | Sends `{ credential, challenge_token }`, with `accountProps.token` embedded |
| 2        | **RP Server**        | Decode challenge token          | Extracts `username`, `challenge`, etc.                                      |
| 3        | **RP Server**        | Validate WebAuthn assertion     | Verifies `authenticatorData` + `clientDataJSON` signature                   |
| 4        | **RP Server**        | Validate extension (if present) | If `accountProps.token` is present, POSTs to `/extensions/validate`         |
| 5        | **Extension Server** | Verify token                    | Validates JWT: `user`, `account_id`, expiry, issuer                         |
| 6        | **RP Server**        | Final validation + sign count   | Verifies credential ID, updates sign counter                                |
| 7        | **RP Server**        | Respond                         | Returns `{ status: ok }` or relevant error                                  |

---

## 🧩 4. Extension Flow

### `POST /extensions/prepare` (Extension Server)

| **Step** | **Actor**            | **Responsibility**            | **Details**                                                                                    |
|----------|----------------------|-------------------------------|------------------------------------------------------------------------------------------------|
| 1        | **Client**           | Send ext access token         | Sends `access_token_ext` (from IdP)                                                            |
| 2        | **Extension Server** | Validate token                | Checks JWT: `iss == identity-provider`, `aud == extension-server`, `exp`, `user`, `account_id` |
| 3        | **Extension Server** | Generate challenge            | Signs and returns short-lived challenge and optional context metadata                          |
| 4        | **Client**           | Begin WebAuthn with challenge | Uses `navigator.credentials.get({ challenge: ..., ... })`                                      |

### `POST /extensions/validate` (Extension Server)

| **Step** | **Actor**            | **Responsibility**       | **Details**                                                                                    |
|----------|----------------------|--------------------------|------------------------------------------------------------------------------------------------|
| 1        | **Client**           | Submit signed assertion  | Sends `{ credentials }` and `access_token_ext` (from IdP)                                      |
| 2        | **Extension Server** | Validate token           | Checks JWT: `iss == identity-provider`, `aud == extension-server`, `exp`, `user`, `account_id` |
| 3        | **Extension**        | Decode `clientDataJSON`  | Parse challenge                                                                                |
| 4        | **Extension**        | Rebuild `clientDataHash` | `SHA256(clientDataJSON)`                                                                       |
| 5        | **Extension**        | Check challenge          | Ensures challenge match expected context                                                       |
| 6        | **Extension**        | Respond                  | `{ status: valid }` or `{ status: invalid, reason }`                                           |

