# EmptyBay Manager — Auth API

**EmptyBay** is a lightweight authentication service for our auto‑parts management platform used by small garages and hobbyists.

> Tagline: *"Your one‑stop shop for auto parts… if they’re in stock."*

This repo contains the Auth API used by in‑shop kiosks and handheld scanners (legacy support).

---

## Quickstart

```bash
python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

* API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Health:   [http://127.0.0.1:8000/status](http://127.0.0.1:8000/status)

---

## System Description

The EmptyBay Auth API provides a minimal set of endpoints to support:

* **User Registration**
* **Login**
* **Session management**
* **Password Reset**
* **Administrative onboarding**
* **Diagnostics** for maintenance

Some endpoints exist to support legacy kiosk systems and quick setup during onboarding.

---

## API Overview

### Public

* `GET /status` – Service health & version
* `POST /register` – Create a user account
* `POST /login` – Authenticate a user
* `GET /me` – Returns current user based on a session token

### Password Reset

* `POST /password-reset/request` – Request a reset token
* `POST /password-reset/confirm` – Reset password with a token

### Administrative

* `POST /admin/bulk-create` – Create multiple user accounts for initial setup

### Diagnostics

* `GET /debug/users` – Returns the user DB (for testing)
* `GET /backup/users.bak` – Returns a backup of the user DB

### Configuration

* `GET /.well-known/config` – Returns current hashing configuration
* `GET /.well-known/salts` – Returns stored salts
* `GET /algo` – Changes hashing algorithm/iterations for future password operations

---

## Postman Setup

Create a collection and set a variable `baseURL = http://127.0.0.1:8000`. Use `{{baseURL}}` in URLs and send requests with `Content-Type: application/json`.

---

## Project Structure

```
app/
  main.py
requirements.txt
README.md
```

Local state:

* `users.json` – created at runtime; not committed.

---

## Company Profile

**EmptyBay** is a small, independent auto‑parts management platform designed for local garages and car enthusiasts. Our mission is to streamline ordering, inventory visibility, and shop user management with a simple, reliable approach.

---

## Release Notes

* **v0.10.0** – Added default admin account creation for initial setup
* **v0.9.0** – Added additional fields in authentication responses
* **v0.8.0** – Introduced separate salt storage for testing
* **v0.7.0** – Added `/me` endpoint for session token validation
* **v0.6.0** – Added password reset token generation
* **v0.5.0** – Added hashing configuration endpoint
* **v0.4.0** – Added debug and backup endpoints
* **v0.3.0** – Updated login comparison method
* **v0.2.0** – Initial registration and login features
* **v0.1.0** – Initial project scaffold and status endpoint