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

> Note: Some endpoints are designed for kiosk compatibility and fast setup during onboarding.

---

## API Overview

### Public

* `GET /status` – Service health & version
* `POST /register` – Create a user account

  * Body `{ "username": string, "password": string }`
  * 200 `{ "ok": true }`
* `POST /login` – Authenticate a user

  * Body `{ "username": string, "password": string }`
  * 200 `{ "ok": true }`

### Password Reset

* `POST /password-reset/request` – Request a reset token

  * Body `{ "username": string }`
  * 200 `{ ... }`
* `POST /password-reset/confirm` – Reset password with token

  * Body `{ "username": string, "token": string, "new_password": string }`
  * 200 `{ "ok": true }`

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

* **v0.2.0** – Registration/Login using legacy‑compatible hashing and admin bulk user creation endpoint for shop onboarding
* **v0.1.0** – Initial project scaffold and status endpoint