# 🚀 Running & Testing the Passkey Web Client (Vite)

This guide walks through running the **frontend only** code.

---

## ✅ Requirements

- Node.js >= 22
- Backend API must be reachable from browser

---

## 🛠️ Run Steps

### 1. Have an environment variable setup

```bash
cp .env.example .env
```   

### 2. Install dependencies

```bash
npm install
```

### 3. Run development server

```bash
npm run dev
```

---

## 🧪 Test

- Open browser at deployed URL
- Register with passkey
- Authenticate with `account_token` JWT
