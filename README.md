# 🛡️ FIDO2 + Passkey + WebAuthn Extension POC

This project demonstrates a standards-compliant, modular proof-of-concept implementation of **Passkey-based
authentication** using **FIDO2 + WebAuthn**, enriched with **standard and custom extensions**.

## 🎯 Goal

Build a working full-cycle **FIDO2 + Passkey authentication** system with:

- Standards-compliant **WebAuthn credential registration and login**
- Stateless architecture using **JWT-backed challenge validation**
- Use of **WebAuthn extensions**:
    - 🟢 `credProps` (standard)
    - 🔵 `accountProps` (custom, domain-specific)
- Clean separation of concerns across:
    - Web client (Vanilla JS + WebAuthn APIs)
    - Relying Party server (FastAPI-based passkey backend)
    - Extension server (FastAPI stub for token validation)
- Minimal setup with **in-memory storage** and **no persistent database**
- Compatible with **real or virtual authenticators** (e.g., Chrome DevTools)

---

## 📦 Project Structure

```bash
.
├── README.md                # ← Root documentation (this file)
├── passkey_web/             # Vanilla JS frontend (uses Vite)
├── passkey_server/          # FastAPI backend (Relying Party server)
├── extension_server/        # Stub extension verifier (FastAPI)
└── ...
```

---

## 🧱 Components

### 🔹 1. `passkey_web` (Client)

- Written in Vanilla JS + Vite
- Interfaces with the browser's WebAuthn APIs:
    - `navigator.credentials.create()` for registration
    - `navigator.credentials.get()` for authentication
- Injects **standard extensions** (`credProps`)
- Injects **custom extension** (`accountProps`) containing a JWT
- Sends WebAuthn response + `clientExtensionResults` to the backend

```js
function withExtensions(publicKey, token) {
  return {
    ...publicKey,
    extensions: {
      credProps: true,
      accountProps: { token }
    }
  };
}
```

### 🔹 2. `passkey_server` (Relying Party)

* FastAPI-based server exposing:

```http
POST /register/begin
POST /register/complete
POST /authenticate/begin
POST /authenticate/complete
```

- Issues WebAuthn challenges and options
- Validates attestation / assertion
- Extracts and verifies standard + custom extensions
- For `accountProps`, delegates token validation to `extension_server`

**Example `clientExtensionResults`:**

```json
{
  "credProps": {
    "rk": true
  },
  "accountProps": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### 🔹 3. `extension_server` (Custom Extension Handler)

- FastAPI service for JWT validation
- Endpoint: `POST /extensions/validate`
- Verifies signature using `EXTENSION_JWT_SECRET`
- On success, returns user identity claims (`sub`, `account_id`)
- On failure, returns 401 Unauthorized

### 🔹 4. Identity Provider (IdP)

- Optional stub that:
    - Accepts `username/password`
    - Returns a short-lived signed JWT (`account_token`)
- The token is injected into `accountProps`

---

## 🧪 Supported Extensions

| Extension      | Type     | Purpose                               |
|----------------|----------|---------------------------------------|
| `credProps`    | Standard | Returns whether key is resident       |
| `accountProps` | Custom   | JWT token for domain-specific context |

---

## 🔹 Custom Extension: `accountProps`

* Client-side only injection
* **Not processed** by browser or authenticator
* Parsed from `clientExtensionResults` by RP
* Validated by a dedicated extension server

### 🔧 Token Flow

1. Client calls `/token/generate` from IdP
2. Receives a JWT (e.g. `eyJhbGciOi...`)
3. Injects this token into `accountProps`
4. RP reads it, and sends it to `/extensions/validate`
5. The response is used to bind credential or validate identity

---

## ✨ Getting Started

### 1. Start Extension Server

Also see [extension_server/README.md](./extension_server/README.md) for more details.

```bash
cd extension_server
uvicorn main:app --reload --port 9000
```

### 2. Start passkey server

Also see [passkey_server/README.md](./passkey_server/README.md) for more details.

```bash
cd passkey_server
uvicorn main:app --reload --port 8000
```

### 3. Start Web Client

Also see [passkey_web/README.md](./passkey_web/README.md) for more details.

```bash
cd passkey_web
npm install
npm run dev
```

### 4. Register and Login

Open [http://localhost:5173](http://localhost:5173) in Google Chrome or a compatible browser.
Use tools like Chrome Virtual Authenticator to simulate passkeys or test with physical devices like YubiKey.

#### 🧪 Testing Tips

- Use **Chrome DevTools > WebAuthn panel** to simulate passkeys:
    - Protocol: `CTAP2`
    - Transport: `internal` or `USB`
    - Enable user verification (optional)

---

## 🚧 Limitations

- In-memory store: credentials are lost on restart
- No user registration or identity provider logic
- No session/login persistence (beyond validation)

---

## 📚 See Also

- [Overview.md](./Overview.md)

---

## 📄 References

* [WebAuthn Spec (W3C)](https://www.w3.org/TR/webauthn-3/)
* [MDN: WebAuthn Extensions](https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API/WebAuthn_extensions)
* [SimpleWebAuthn](https://simplewebauthn.dev)
* [FIDO2: Server Guidance](https://developers.google.com/identity/passkeys/developer-guides/server-introduction)
