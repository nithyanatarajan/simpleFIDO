# 🔐 idp_stub

Lightweight Identity Provider stub for issuing short-lived JWTs used in custom WebAuthn extension flows.

## 🧩 Features

- Issues JWTs for use in WebAuthn `accountProps` extension
- Uses mock user store (`users_stub.py`)
- Passwords are verified via base64-encoded comparison
- Stateless and suitable for local testing

## 📂 Endpoints

| Method | Endpoint           | Description                            |
|--------|--------------------|----------------------------------------|
| POST   | `/token/generate`  | Generates a JWT for a given user       |

## 🛠️ Setup

### 1. Setup Python Environment

```bash
uv venv
source .venv/bin/activate
````

### 2. Install Dependencies

```bash
uv sync --all-extras --dev
```

---

## ▶️ Run the Server

```bash
uvicorn idp:app --host 0.0.0.0 --port 8001 --reload
```

Server will be live at: [http://localhost:8001](http://localhost:8001)

---

## 📤 Test the API

```bash
curl -X POST http://localhost:8001/token/generate \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user1@example.com",
    "password": "UserOne",
    "account_id": "acc001"
  }'
```

Expected: 200 OK with a JWT token in response.

