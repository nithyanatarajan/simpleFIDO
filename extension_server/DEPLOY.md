# 🚀 Running & Testing the Stub Extension Server

This document outlines how to install, run, and test the extension server locally.
This stub server can now be integrated into your FIDO2 authentication flow

---

## 📁 Directory Structure

```
extension-server/
├── extension_server.py     # Main API logic
├── accounts.py             # List of valid accounts
└── config.py               # Configuration (e.g., secret key)
```

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
