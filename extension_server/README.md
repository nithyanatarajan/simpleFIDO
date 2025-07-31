# 🔌 Stub Extension Server – Developer Guide

A minimal, standalone service that acts as a **custom WebAuthn extension authority**, validating `account_token` JWTs
passed during authentication.

---

## 🎯 Purpose

This service is required during authentication to validate domain-specific JWTs (e.g., account identifiers). It is a
trusted part of the security architecture and enforces business logic before allowing FIDO2 assertions to succeed.

---

## ✅ Responsibilities

| Step | Task                                   | Description                                             |
|------|----------------------------------------|---------------------------------------------------------|
| 1️⃣  | Expose API endpoint                    | `POST /extensions/validate`                             |
| 2️⃣  | Accept JWT input via JSON              | `{ "token": "<JWT>" }`                                  |
| 3️⃣  | Verify JWT signature and decode claims | HMAC (HS256) validation                                 |
| 4️⃣  | Enforce validation rules               | E.g., check if `account_id` is in `VALID_ACCOUNTS` list |
| 5️⃣  | Return structured response             | `200 OK` or `401 Unauthorized`                          |

---

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

---

## ▶️ Run the Server

```bash
uvicorn extension_server:app --host 0.0.0.0 --port 9000 --reload
```

Server will be live at: [http://localhost:9000](http://localhost:9000)

---

## 🧪 Generate a Test JWT

Use [generate_token.py](generate_token.py) to create a JWT token for testing.

```bash
# valid account
TOKEN=$(python generate_token.py --user user1@example.com --account acc001)

# invalid account
TOKEN=$(python generate_token.py --user user1@example.com --account acc003)

# invalid account
TOKEN=$(python generate_token.py --account acc003)
```

---

## 📤 Test the API

```bash
curl -X POST http://localhost:9000/extensions/validate \
  -H "Content-Type: application/json" \
  -d "{\"account_token\": \"$TOKEN\"}"

```

Expected: 200 OK with status `valid` if the account is authorized.
