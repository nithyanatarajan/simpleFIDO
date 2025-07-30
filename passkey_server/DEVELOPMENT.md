# 🚀 Running & Testing the FIDO Server

This document outlines how to install, run, and test the FIDO server locally.

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
