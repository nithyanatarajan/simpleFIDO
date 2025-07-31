# 🧭 FIDO2 + Passkey + WebAuthn Extensions – Architecture Overview

This document describes the architecture and flow of a Passkey + FIDO2 authentication system that integrates
**standard** and **custom WebAuthn extensions** using a **Vanilla JS client**, **FastAPI relying party backend**,
and a **FastAPI stub extension server**.

## 🎯 Goal

Build a working full-cycle **passkey-based authentication** system with:

- Stateless challenge validation (via **JWTs**)
- Simple **in-memory** credential storage
- No databases or persistent state
- Support for real or virtual authenticators (e.g. Chrome DevTools)
- Demonstrate real + custom WebAuthn extensions
- Cleanly separate **authenticator logic**, **relying party validation**, and **custom domain-specific checks**

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

- Form-based UI for passkey registration & login
- Calls `navigator.credentials.create()` and `navigator.credentials.get()`
- Injects standard + custom extensions into `publicKeyCredential` options
- Sends attestation/assertion and client extension results to RP server

### 2. Relying Party Server (FastAPI)

- Endpoints:
    - `/register/begin` → Generates challenge and publicKey options
    - `/register/complete` → Verifies attestation
    - `/authenticate/begin` → Generates challenge and publicKey options
    - `/authenticate/complete` → Verifies assertion
- Challenge is embedded as a signed JWT
- Validates `clientExtensions` during `/complete` flows
- Calls Extension Server for custom validation (to validate `accountProps.token`)

### 3. Extension Server (FastAPI Stub)

- Endpoint: `/extensions/validate`
- Validates JWT token passed via `accountProps`
- Returns claims like `account_id`, `sub` used by RP to bind credential

### 4. Identity Provider (FastAPI Stub)

- Authenticates the user based on `username/password`
- Issues runtime JWT used in custom extension
- Acts as a stand-in for a real IdP (e.g. Auth0, Keycloak)

---

## ✅ Why Use JWTs for Challenge and Extensions?

- **Challenge JWT**: Encapsulates registration/authentication challenge details securely and verifiably
- **Account JWT**: Injected at runtime into the `accountProps` extension by the client
    - Represents the domain-specific user context
    - Prevents hardcoding or static configuration of contextual metadata
- **Extension Server**: Independently verifies JWT signature and performs validation logic without coupling with core
  authentication

---

## 🔗 Flow Overview

### 🧾 **Pre-authentication Step – Runtime Token Issuance**

> 🔐 *Mandatory prior to both registration and authentication*

1. **Client** sends a request to the **Identity Provider (IdP)** via `/token/generate`, supplying:

    - User credentials (e.g., `username`, `password`)
2. **IdP** authenticates the user and responds with an **`account_token` (JWT)** containing:

    - Claims like `sub` (subject) and `account_id`
3. **Client** injects this `account_token` into the WebAuthn custom extension:

    - `accountProps: { token }`

---

### 🔐 **Registration Flow**

1. **User** initiates registration from the client.
2. **Client** sends a `username` to the **Relying Party (RP)** via `/register/begin`.
3. **RP** responds with:

    - `publicKeyCredentialCreationOptions` (WebAuthn registration options)
    - `challenge_token` (JWT protecting the challenge state)
4. **Client** builds the `publicKey` and adds extensions:

    - `credProps` — requests credential discoverability info
    - `accountProps: { token }` — embeds the JWT from IdP
5. **User** completes biometric gesture using authenticator.
6. **Browser** returns:

    - Credential
    - `clientExtensionResults` (includes `accountProps`)

7. **RP**:

    - Verifies challenge and attestation
    - Extracts `accountProps.token`
    - Validates the token with **extension server** via `/extensions/validate`
    - Associates credential with the validated user context (`username`, `account_id`)

---

### 🔐 **Authentication Flow**

1. **User** initiates login from the client.
2. **Client** sends a `username` to **RP** via `/authenticate/begin`.
3. **RP** responds with:

    - `publicKeyCredentialRequestOptions`
    - `challenge_token` (JWT encoding the state)
4. **Client** invokes `navigator.credentials.get()` with extensions:
    - `credProps`
    - `accountProps: { token }` (same as before)
5. **Browser** returns:

    - WebAuthn assertion
    - `clientExtensionResults.accountProps.token`
6. **RP**:

    - Validates the challenge and signature
    - Retrieves and verifies `accountProps.token` via extension server
    - Verifies subject (`sub`) matches expected user
    - Grants access if all checks pass

---

## 🧩 Custom Extension: `accountProps`

- Injected by the client during registration/authentication
- Carries a runtime-issued JWT token
- Not processed by browser or authenticator
- Parsed and validated by the RP server via the Extension Server

```js
function withExtensions(publicKey, token) {
  return {
    ...publicKey,
    extensions: {
      credProps: true,
      accountProps: { token } // 🔒 custom JWT passed to RP
    }
  };
}
```

#### Example of clientExtensionResults:

```json
{
  "credProps": {
    "rk": true
  },
  "accountProps": {
    "token": "eyJhbGciOi..."
  }
}
```

---

## 🧠 What Is the Extension Server?

- The "extension server" is **not** a FIDO component
- It is a backend-only validation layer for custom extensions like `accountProps`
- This separation supports domain-specific identity validation without affecting core WebAuthn ceremony

---

## 📦 Benefits of This Architecture

- ✅ Fully **compliant with WebAuthn Level 2+** extension specifications
- ✅ Cleanly separates **authentication responsibilities** from **business/domain validation**
- ✅ Demonstrates practical integration of:

    - **Standard extensions** (`credProps`)
    - **Custom extensions** (`accountProps`)
- ✅ Enables secure, extensible, and testable WebAuthn extension handling — ideal for real-world passkey adoption and
  experimentation

---

## ✅ Summary Table

| Extension ID   | Type     | Injected By | Processed By            | Validated Where                    |
|----------------|----------|-------------|-------------------------|------------------------------------|
| `credProps`    | Standard | Client      | Browser / Authenticator | RP (informational)                 |
| `accountProps` | Custom   | Client      | ❌ Not processed         | ✅ RP server (via Extension Server) |

