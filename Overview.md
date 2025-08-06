# Overview: WebAuthn Passkey POC with Custom Extension Server

This proof-of-concept demonstrates how to extend the WebAuthn passkey-based registration and authentication flow with a
secure client-to-extension-server interaction — **without misusing the `extensions` mechanism** and fully aligned with
FIDO2/WebAuthn specifications.

---

## 🎯 Goal

Build a fully working, standards-compliant **passkey-based authentication** system that:

- Uses **stateless JWT-based challenges** to simplify validation and avoid server-side storage
- Stores credentials in **in-memory structures**, with no persistent database
- Supports **real or virtual authenticators** (e.g., Chrome DevTools, YubiKey)
- Separates concerns cleanly across:
    - **Identity Provider** (JWT issuance)
    - **Relying Party (RP) Server** (WebAuthn registration/authentication)
    - **Extension Server** (custom domain logic)
- Demonstrates a secure client → extension-server interaction using WebAuthn ceremony
- Injects **custom business context** (`accountProps`) outside of the WebAuthn API — without misusing `extensions`
- Adheres strictly to **FIDO2/WebAuthn standards** and avoids assumptions unsupported by browser APIs

---

## 🧩 Architectural Principles

- **Stateless by Design**: No server-side storage — challenges are JWT-based and self-contained
- **Extension-Oriented**: Supports both **standard extensions** (e.g., `credProps`) and **custom extensions** (
  `accountProps`)
- **Modular and Realistic**: Each responsibility is cleanly split across the Client, RP, Identity Provider, and
  Extension Server — mirroring production-level design

---

## 🧱 System Components

### 1. Web Client (Vanilla JS + Vite)

- Handles UI for registration, login, and extension-based signing
- Calls `navigator.credentials.create()` and `navigator.credentials.get()` for WebAuthn ceremonies
- Sends attestation and assertion data to RP endpoints
- Fetches a signed challenge via `/extensions/prepare` for custom signing
- Injects that challenge in a second WebAuthn call
- Logs `credProps` (standard extension) to demonstrate browser-supported extension handling
- Manually includes `accountProps` (JWT) in the final call to `/extensions/validate` — not passed through the browser

### 2. Relying Party Server (FastAPI)

- Endpoints:
    - `POST /register/begin` → Generates publicKeyCredentialCreationOptions (JWT not verified here)
    - `POST /register/complete` → Verifies attestation and validates `access_token_rp`
    - `POST /authenticate/begin` → Generates publicKeyCredentialRequestOptions (JWT not verified here)
    - `POST /authenticate/complete` → Verifies assertion and validates `access_token_rp`
- Uses FIDO2-compliant libraries for challenge and signature verification
- Maintains in-memory credential store for the POC (no persistent state)

### 3. Extension Server (FastAPI Stub)

- Endpoints:
    - `POST /extensions/prepare` → Verifies `access_token_ext`, returns signed challenge + metadata
    - `POST /extensions/validate` → Validates signature over the challenge, verifies `accountProps`
- Validates:
    - Challenge authenticity and expiry
    - Signature over `authenticatorData` + `clientDataHash`
    - RP origin from `clientDataJSON.origin`
    - Custom claims in `accountProps` JWT (roles, tenant, scopes, etc.)
- Uses credential ID to fetch the correct public key

### 4. Identity Provider (FastAPI Stub)

- Endpoint: `POST /token/generate`
- Performs user authentication using `username` and `password`
- Issues two scoped, signed JWTs:
    - `access_token_rp` → for the RP Server (`aud: rp-server`)
    - `access_token_ext` → for the Extension Server (`aud: extension-server`)

---

## 🔐 Trust Model

- JWTs are short-lived, audience-restricted, and signed using secure keys
- The client derives `accountProps` from `access_token_ext` claims — these are not transmitted via WebAuthn APIs
- All signature and token validations are done at the point of **final submission**, not at challenge generation
- Only the **extension server** handles business context (`accountProps`) — the RP is agnostic to it

---

## 🧾 Flow Summary

### 1. Pre-authentication (JWT Issuance)

- The browser authenticates with the Identity Provider (`/token/generate`) using `username`, `password`, and
  `account_id`.
- IdP issues two scoped JWTs:
    - `access_token_rp` → with `aud: rp-server`
    - `access_token_ext` → with `aud: extension-server`
- The client derives `accountProps` from `access_token_ext` claims for custom extension usage.

### 2. Passkey Registration

- Client initiates registration via `POST /register/begin` (no token verified at this stage).
- RP returns `publicKeyCredentialCreationOptions`, optionally injecting standard extensions like `credProps`.
- Browser invokes:
  ```js
  navigator.credentials.create({ publicKey: options });
  ```

* Authenticator returns an attestation response (`clientDataJSON`, `attestationObject`).
* Client submits attestation to `POST /registration/complete` along with `access_token_rp`.
* RP verifies:

    * Attestation integrity
    * `access_token_rp` (issuer, audience, expiry)
    * Registers and binds the credential to the user

### 3. Passkey Authentication

* Client initiates login via `POST /authenticate/begin` (no token verified at this stage).
* RP returns `publicKeyCredentialRequestOptions`.
* Browser invokes:

  ```js
  navigator.credentials.get({ publicKey: options });
  ```
* Authenticator returns signed assertion (`authenticatorData`, `clientDataJSON`, `signature`).
* Client submits assertion to `POST /authentication/complete` along with `access_token_rp`.
* RP verifies:

    * Assertion signature
    * `access_token_rp` (issuer, audience, expiry)
    * Issues a session on success

### 4. Extension Challenge Preparation

* Client calls `POST /extensions/prepare` with `access_token_ext`.
* Extension server verifies the JWT and returns a time-limited, signed challenge.
* Optional: The server may also return extension metadata or context claims.

### 5. Challenge Signing via WebAuthn

* Client calls `navigator.credentials.get()` again — this time with the challenge from the extension server.
* Example:

  ```js
  navigator.credentials.get({
    publicKey: {
      challenge: fromExtensionServer,
      allowCredentials: [...],
      userVerification: 'required'
    }
  });
  ```
* Authenticator signs the challenge securely.

### 6. Extension Validation

* Client calls `POST /extensions/validate` with:

    * `authenticatorData`, `clientDataJSON`, `signature`
    * `credentialId`
    * `accountProps` JWT (manually added)
    * (optional) extension metadata

* Extension server verifies:

    * JWT (`accountProps`) validity: issuer, audience, expiry
    * Signature over `authenticatorData` + `clientDataHash`
    * Challenge match with `clientDataJSON.challenge`
    * RP origin consistency from `clientDataJSON.origin`
    * Credential binding by looking up public key for `credentialId`

![sequence.png](diagrams/sequence.png)
---

## ✅ Why Use JWTs for Challenge and Extensions?

- **Challenge JWT**: Encapsulates challenge metadata securely and verifiably
- **Account JWT**: Injected by client manually into validation step
    - Represents domain-specific user context (e.g., accountId, tenantId, scopes)
    - Avoids misuse of WebAuthn extension interface
- **Extension Server**: Independently validates everything without affecting RP

---

## 🚫 Why Not Use clientExtensionResults?

- `accountProps` is **not a browser-recognized extension**
- WebAuthn ignores unrecognized keys in extensions object
- They are neither sent to authenticator nor echoed back to client
- Instead: pass them manually via secure, client-controlled POST

---

## 🧪 Security Notes

- Do not trust unsigned or unverified claims (`accountProps`)
- Validate all tokens (audience, issuer, expiry)
- Always compare challenge from JWT with `clientDataJSON.challenge`
- Always verify origin from `clientDataJSON.origin`

---

## 📎 Optional Enhancements (Future Work)

- Add challenge replay protection (store nonce hash server-side)
- Support token refresh flow for long-lived sessions
- Add rate limiting or IP-bound tokens for extension flows
- Add UI visibility into step-by-step flows