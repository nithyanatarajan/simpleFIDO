# 🔐 Simple FIDO2 + Passkey POC

A minimal **proof-of-concept** that demonstrates how to build a modern **passwordless authentication system** using:

- ✅ **FastAPI backend** (stateless JWT-based challenge, in-memory credential store)
- ✅ **Vanilla JavaScript frontend** (WebAuthn API)
- ✅ **FIDO2-compliant flows** for **registration** and **authentication**

---

## 🎯 Goal

Build a working full-cycle **passkey-based authentication** system with:

- Stateless challenge validation (via **JWTs**)
- Simple **in-memory** credential storage
- No databases or persistent state
- Support for real or virtual authenticators (e.g. Chrome DevTools)

---

## 🧩 Backend Highlights

- Uses `python-fido2`'s `Fido2Server` for handling WebAuthn protocol logic
- Stores credentials in an in-memory dictionary keyed by credential ID
- Challenge states (`register_begin`, `authenticate_begin`) are encoded into signed JWTs
- FastAPI endpoints for:
  - **Begin registration**
  - **Complete registration**
  - **Begin authentication**
  - **Complete authentication**

---

## 🔐 Challenge Structure (JWT)

Every `/begin` step returns a signed JWT (`challenge_token`) that encapsulates:

- The **challenge** itself (from `python-fido2`)
- User metadata (e.g., `username`, `user_handle`)
- RP information (`rp_id`)
- Flow type (`registration` or `authentication`)
- Expiry (e.g., 60 seconds)

This removes the need for server-side sessions.

---

## 💡 Registration Flow

1. **Client** calls `/register/begin` with their username.
2. **Server** responds with `publicKey` options and `challenge_token`.
3. **Browser** uses WebAuthn API (`navigator.credentials.create(...)`) to generate a new credential.
4. **Client** posts result to `/register/complete` with attestation + challenge token.
5. **Server** validates and stores credential in memory.

---

## 🔐 Authentication Flow

1. **Client** calls `/authenticate/begin` with their username.
2. **Server** responds with `publicKey` options and `challenge_token`.
3. **Browser** uses WebAuthn API (`navigator.credentials.get(...)`) to generate assertion.
4. **Client** posts result to `/authenticate/complete` with assertion + challenge token.
5. **Server** verifies signature and optionally returns a login token.

---

## 🧪 Testing Tips

- Use **Chrome DevTools > WebAuthn panel** to simulate passkeys:

  - Protocol: `CTAP2`
  - Transport: `internal` or `USB`
  - Enable user verification (optional)

- Works with physical authenticators (like YubiKey) or platform ones (on supported devices/browsers).

---

## 📦 Project Layout

```
.
├── passkey_server/ # FastAPI backend
│ ├── main.py
│ ├── fido/
│ ├── utils/
│ └── config.py
├── passkey_web/ # Vanilla JS frontend
│ ├── index.html
│ └── src/
│     ├── auth.js
│     └── register.js
└── README.md
```

---

## 🚧 Limitations

- In-memory store: credentials are lost on restart
- No user registration or identity provider logic
- No session/login persistence (beyond validation)

---

## ✅ What This POC Demonstrates

- Stateless FIDO2 registration and login using JWTs
- How to bridge WebAuthn API responses to a Python backend
- Full working flows with minimal code and no DBs

---

## 🔜 Possible Extensions

- Add database support (e.g., SQLite/PostgreSQL)
- Implement login sessions after authentication
- Add metadata (browser, platform info) to stored credentials
- Integrate real platform passkeys via macOS, iCloud, Android, etc.
