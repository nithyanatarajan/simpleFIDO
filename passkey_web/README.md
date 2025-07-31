# 🚀 Running & Testing the Passkey Web Client (Vite)

This guide walks through running the **frontend only** code.

---

## ✅ Requirements

- Node.js >= 22
- Backend API must be reachable from browser

---

## 🛠️ Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Have an environment variable setup

```bash
cp .env.example .env
```   

### 3. Run development server

```bash
npm run dev
```

Then open http://localhost:5173

**Notes:**

- You’ll need to pass a valid `account_token` JWT in the login form
- JWT is injected into `accountProps` extension for domain-specific validation


---

## 🧪 Test

- Open browser at deployed URL
- Register with passkey
- Authenticate with `account_token` JWT
