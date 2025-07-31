# 🚀 passkey_server

FastAPI backend to handle WebAuthn registration and authentication flow, including extension handling.

## 🧩 Features

- WebAuthn Registration & Authentication APIs
- Extension validation:
    - `appid` (standard read extension)
    - `credProps` (standard)
    - `accountProps` (custom extension validated against a separate service)

## 📂 Endpoints

| Method | Endpoint                 | Description                                             |
|--------|--------------------------|---------------------------------------------------------|
| POST   | `/register/begin`        | Begin passkey registration                              |
| POST   | `/register/complete`     | Complete passkey registration                           |
| POST   | `/authenticate/begin`    | Begin authentication                                    |
| POST   | `/authenticate/complete` | Complete authentication (includes extension validation) |

## 🛠️ Setup

### 1. Setup Python Environment

```bash
uv venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
uv sync --all-extras --dev
```

### 3. Copy Environment Variables

```bash
cp .env.example .env
```

---

## ▶️ Run the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Server will be live at: [http://localhost:8000](http://localhost:8000)

---

## 📤 Test the API

```bash
curl -X POST http://localhost:8000/register/begin \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"user1@example.com\"}"
```

Expected: 200 OK with public key and challenge token.
