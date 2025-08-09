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

* **User Registration** (mechanics & shop staff)
* **Login** for dashboard/device access
* **Password Reset** (request + confirm)
* **Administrative bootstrap** actions used during shop onboarding
* **Diagnostics** for maintenance (legacy/debug)

> Note: Some endpoints are designed for kiosk compatibility and fast setup during onboarding.

---

## API Overview

### Public

* `GET /status` – Service health & version
* `POST /register` – Create a user account

  * Body `{ "username": string, "password": string }`
  * 200 `{ "ok": true }`
* `POST /login` – Authenticate a user (timing-vulnerable comparison in v0.3.0)

  * Body `{ "username": string, "password": string }`
  * 200 `{ "ok": true }`

### Password Reset

* `POST /password-reset/request` – Request a reset token (predictable token vuln in v0.6.0)

  * Body `{ "username": string }`
* `POST /password-reset/confirm` – Reset password with token

  * Body `{ "username": string, "token": string, "new_password": string }`

### Administrative (onboarding)

* `POST /admin/bulk-create` – Bootstrap multiple user accounts for a new shop

  * **Intended use:** initial onboarding seeding by shop owner or technician
  * Body

    ```json
    {
      "usernames": ["alice", "bob", "carol"],
      "length": 12,
      "overwrite": false
    }
    ```
  * Response

    ```json
    {
      "created_count": 3,
      "skipped_existing": [],
      "accounts": [
        { "username": "alice", "password": "..." },
        { "username": "bob",   "password": "..." },
        { "username": "carol", "password": "..." }
      ],
      "csv": "username,password\nalice,...\nbob,...\ncarol,..."
    }
    ```

> During onboarding, provide the returned credentials directly to the new users and advise them to log in and change passwords.

### Diagnostics (debug)

* `GET /debug/users` – Returns the entire user DB (usernames + password hashes) in JSON.
* `GET /backup/users.bak` – Returns a pretty-printed backup of the same DB.

### Configuration (legacy)

* `GET /.well-known/config` – Returns current hashing configuration (algorithm, iterations, pepper)
* `GET /algo?preferred=md5&iterations=1` – Changes hashing algorithm/iterations/pepper for **future** password operations

> These config endpoints are unauthenticated and intended for demonstration.

---

## Postman Setup (Manual)

Create a collection and set a variable `baseURL = http://127.0.0.1:8000`. For each request, use `{{baseURL}}` in the URL, set **Body → raw → JSON**, and add header `Content-Type: application/json`.

Example Register request body:

```json
{ "username": "alice", "password": "password" }
```

---

## Project Structure

```
app/
  main.py        # FastAPI service
requirements.txt
README.md
```

Local state:

* `users.json` – created at runtime; not committed.

---

## Company Profile

**EmptyBay** is a small, independent auto‑parts management platform designed for local garages and car enthusiasts. Our mission is to streamline ordering, inventory visibility, and shop user management with a simple, reliable approach that works in the bay as well as at the counter.

---

## Release Notes

* **v0.6.0** – Predictable password reset tokens returned via API (C2 vuln)
* **v0.5.0** – Exposed `/.well-known/config` and insecure `/algo` hashing downgrade (D1 vuln)
* **v0.4.0** – Added debug and backup endpoints exposing full user DB (C1 vuln)
* **v0.3.0** – Login endpoint now uses timing-vulnerable comparison (B1 vuln)
* **v0.2.1** – Admin bulk user creation endpoint for shop onboarding (C3 vuln)
* **v0.2.0** – Registration/Login usi