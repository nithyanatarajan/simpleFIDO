# 🛡️ FIDO2 + Passkey + WebAuthn Extension POC

This proof-of-concept demonstrates a complete full-stack implementation of secure, passkey-based authentication using
the **FIDO2/WebAuthn standards**, including custom extensions and JWT-based stateless flows. The system cleanly
separates responsibilities across four cooperating services:

- 🧠 **Identity Provider (IdP)** — authenticates users and issues scoped JWTs
- 🔐 **Relying Party (RP)** — handles WebAuthn ceremonies and verification
- 🧩 **Extension Server** — signs challenges and validates custom domain context (`accountProps`)
- 🌐 **Web Client** — interacts with platform authenticators via the WebAuthn API

## ✅ Highlights

- Stateless challenge verification using signed JWTs (no backend session storage)
- Clean separation of auth logic vs domain/business logic
- Browser-compatible demonstration of **custom WebAuthn extensions** (even if unrecognized)
- Standards-compliant flow across **registration**, **authentication**, and **custom extension usage**

## 🧱 Components

### 🔹 1. `passkey_web` (Client)

A Vanilla JS frontend powered by Vite. Handles:

- Credential registration/authentication using the WebAuthn API
- Injecting standard (e.g., `credProps`) and custom extensions (e.g., `accountProps`)
- Posting results to RP and Extension servers

### 🔹 2. `passkey_server` (Relying Party)

A FastAPI service that:

- Issues signed JWT challenges for registration and authentication
- Verifies attestation and assertion responses
- Stores credential metadata in-memory
- Delegates domain-specific validation to the Extension Server

### 🔹 3. `extension_server` (Custom Extension Verifier)

A FastAPI microservice that:

- Issues signed challenge tokens for WebAuthn
- Verifies assertions and checks `accountProps` token
- Operates independently of RP to enforce business-specific rules

### 🔹 4. `idp_server` (IdP)

A basic identity provider that:

- Authenticates users via username/password
- Issues scoped JWTs:
    - `access_token_rp` for the RP Server
    - `access_token_ext` for the Extension Server

---

## 🧩 Supported Extensions

| Extension      | Type     | Purpose                           |
|----------------|----------|-----------------------------------|
| `credProps`    | Standard | Indicates whether key is resident |
| `accountProps` | Custom   | JWT representing business context |

> Note: `accountProps` is **browser-unrecognized** — it must be manually passed to the extension server after the
> WebAuthn ceremony.

---

## 📦 Project Structure

```bash
.
├── README.md                # ← Root documentation (this file)
├── Overview.md              # Architecture + detailed walkthrough
├── passkey_web/             # Vanilla JS frontend (uses Vite)
├── passkey_server/          # FastAPI RP server
├── extension_server/        # FastAPI custom extension validator
├── idp_server/  # Optional IdP stub
````

---

## 🚀 Getting Started

> Ensure you have **Python 3.12+**, **Node.js**, and [`uv`](https://github.com/astral-sh/uv) installed.
> All servers use `uv` as the dependency manager. Client uses `npm`.

### 1. Install All Dependencies

```bash
task install
```

### 2. Start All Services (Dev Mode)

> Use the provided `Taskfile.yml` to spin up all components in parallel

```bash
task dev
```

This runs the following tasks in parallel:

* `idp_server` at [http://localhost:8001](http://localhost:8001)
* `extension_server` at [http://localhost:9000](http://localhost:9000)
* `passkey_server` (RP) at [http://localhost:8000](http://localhost:8000)
* `passkey_web` (web frontend) at [http://localhost:5173](http://localhost:5173)

### 3. Test the Flow

Open your browser at:
[http://localhost:5173](http://localhost:5173)

#### 🧪 Testing Tips

Use **Chrome DevTools > WebAuthn Panel** to simulate passkeys:

* Protocol: `CTAP2`
* Transport: `internal` or `USB`
* Enable user verification if desired
* Add RP ID: `localhost`

---

## ⚠️ Known Limitations

* `accountProps` will **not appear** in `clientExtensionResults` — this is expected.
* JWTs are short-lived and context-bound — no session state is stored.
* Browser extensions are **not modified** or polyfilled — this is purely WebAuthn compliant.

---

## ✅ Standards Alignment

This POC complies with:

* [WebAuthn Level 2 Spec](https://www.w3.org/TR/webauthn-2/)
* [FIDO2 CTAP2 Spec](https://fidoalliance.org/specs/fido-v2.1-rd-20220125/)
* W3C best practices around:

    * Challenge entropy
    * Context binding (origin, RP ID)
    * Key attestation and assertion verification
    * Authenticator-agnostic compatibility

---

## 📚 See Also

- [Overview.md](./Overview.md)

---

## 📄 References

* [WebAuthn Spec (W3C)](https://www.w3.org/TR/webauthn-3/)
* [MDN: WebAuthn Extensions](https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API/WebAuthn_extensions)
* [SimpleWebAuthn](https://simplewebauthn.dev)
* [FIDO2: Server Guidance](https://developers.google.com/identity/passkeys/developer-guides/server-introduction)

