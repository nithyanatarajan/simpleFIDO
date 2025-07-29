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

## 📦 Input & Output

### 🔹 Sample Request

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR..."
}
```

### 🔸 Success Response

```json
{
  "status": "valid",
  "account_id": "acc_12345",
  "user": "user@example.com"
}
```

### 🔸 Error Response

```json
{
  "status": "invalid",
  "reason": "Signature verification failed"
}
```

---

## 🧱 Why Keep It Separate?

- ✅ **Security Boundary** – Isolates auth logic from FIDO2 protocol
- 🧪 **Testability** – Can be stubbed or mocked in test suites
- 📦 **Modular** – Can be replaced with production-grade microservice later