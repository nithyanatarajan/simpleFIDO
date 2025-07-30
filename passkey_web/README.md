# 🔐 WebAuthn + Passkey Client (Vite)

This is a minimal frontend built with **Vanilla JS** and **Vite**, demonstrating **passkey-based registration and
authentication** using WebAuthn APIs. It integrates with a FastAPI backend that supports stateless FIDO2 flows and a
custom extension token validation.

---

## 🚀 Features

- ✅ WebAuthn registration using `navigator.credentials.create()`
- ✅ Authentication using `navigator.credentials.get()`
- ✅ Supports **custom extension token** (JWT) for domain-specific logic
- ✅ Clean modular structure using ES Modules
- ✅ Live-reload via Vite Dev Server

---

## 📂 Project Structure

```
📁 public/          # Static assets (if needed)
📁 src/
  ├── auth.js       # Handles login with passkey
  ├── register.js   # Handles passkey registration
  ├── utils.js      # Buffer <-> base64url helpers
  ├── main.js       # Entry point + form handler
📄 index.html        # Demo UI with login & register forms
```

---

## 🧪 End-to-End Flow

| Step | Action                                                 |
|------|--------------------------------------------------------|
| 1️⃣  | Enter username, click **Register** – creates a passkey |
| 2️⃣  | Enter username + account token (JWT), click **Login**  |
| 3️⃣  | Auth data sent to backend for verification             |
| 4️⃣  | If token and WebAuthn checks pass → ✅ success message  |

---

## 📦 Requirements

- Node.js >= 22
- Backend running at same origin (or configure `VITE_API_BASE_URL`)

---

## 🔧 Configuration

You can optionally override the backend API via `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```
