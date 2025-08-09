"""
EmptyBay Manager - Authentication API (Skeleton Version)
--------------------------------------------------------
This is the *starting point* for the EmptyBay vulnerable authentication system.
We will be adding features and intentionally insecure implementations step-by-step.

Right now:
- Only the structure of endpoints is present.
- No real authentication logic or vulnerabilities yet.
- Lots of comments to guide future edits.

Run:
    uvicorn app.main:app --reload
Docs:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from typing import Dict, Any
import json, os, time
import hashlib
import secrets
import string

# -----------------------------------------------------------
# App setup
# -----------------------------------------------------------
# title & version appear in auto-generated docs at /docs
app = FastAPI(title="EmptyBay Manager API", version="0.2.0")

# The "database" file we'll read/write. Later we can make this part of a vulnerability.
DB_FILE = "users.json"

# -----------------------------------------------------------
# Helper functions for reading/writing our "database"
# -----------------------------------------------------------
def load_db() -> Dict[str, Any]:
    """
    Loads the JSON database file if it exists, otherwise returns an empty structure.
    Later: We might 'accidentally' leak this file somewhere.
    """
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db: Dict[str, Any]) -> None:
    """
    Saves the in-memory DB dictionary back to disk as JSON.
    """
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)

def hash_password_md5(password: str) -> str:
    """
    Intentionally weak hash: MD5 with no salt, one iteration.
    Stored as 'md5$<digest>' so it's easy to identify in the DB.
    """
    digest = hashlib.md5(password.encode()).hexdigest()
    return f"md5${digest}"

def generate_random_password(length: int = 12) -> str:
    """
    Generates a random password.
    NOTE: We include only letters+digits to keep demo-friendly.
    For a real system you'd include punctuation and enforce policy.
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

# -----------------------------------------------------------
# Data models (for request bodies)
# -----------------------------------------------------------
# These help FastAPI auto-validate incoming JSON and generate docs.

class RegisterIn(BaseModel):
    username: str
    password: str

class LoginIn(BaseModel):
    username: str
    password: str

class ResetRequestIn(BaseModel):
    username: str

class ResetConfirmIn(BaseModel):
    username: str
    token: str
    new_password: str

class BulkCreateIn(BaseModel):
    usernames: list[str]
    length: int = 12        # password length
    overwrite: bool = False # if True, replace existing users' passwords

# -----------------------------------------------------------
# Public / "Company" endpoints
# -----------------------------------------------------------

@app.get("/status")
def status():
    """
    Public status endpoint for EmptyBay Manager.
    This simulates what a real company might expose for uptime checks.
    """
    return {
        "service": "EmptyBay Auth",
        "version": "0.1.0",
        "note": "pre-alpha build"
    }

# -----------------------------------------------------------
# Auth endpoints (currently safe placeholders)
# -----------------------------------------------------------

@app.post("/register")
def register(body: RegisterIn):
    """
    Creates a new user in our database.
    Vulnerability (A1): hashes with MD5, no salt (see hash_password_md5).
    """
    db = load_db()

    if body.username in db["users"]:
        raise HTTPException(status_code=409, detail="username exists")

    db["users"][body.username] = {
        "hash": hash_password_md5(body.password),  # intentionally weak
        "role": "user",
        "created_at": int(time.time())
    }
    save_db(db)
    return {"ok": True}

@app.post("/login")
def login(body: LoginIn):
    """
    Attempts to authenticate a user.
    Currently uses MD5(no salt) to recompute and compares directly.
    """
    db = load_db()
    user = db["users"].get(body.username)
    if not user:
        raise HTTPException(status_code=401, detail="bad creds")

    expected = hash_password_md5(body.password)
    stored = user["hash"]

    if stored != expected:
        raise HTTPException(status_code=401, detail="bad creds")

    return {"ok": True}

@app.post("/password-reset/request")
def reset_request(body: ResetRequestIn):
    """
    Requests a password reset token for a username.
    Currently unimplemented.
    Later:
        - Will generate predictable/weak tokens.
        - May 'accidentally' expose them in the response.
    """
    return {"detail": "not implemented yet"}

@app.post("/password-reset/confirm")
def reset_confirm(body: ResetConfirmIn):
    """
    Confirms a password reset with a token and sets a new password.
    Currently unimplemented.
    """
    raise HTTPException(status_code=501, detail="not implemented yet")

# -----------------------------------------------------------
# Recon / Leak endpoints (disabled for now)
# -----------------------------------------------------------

@app.get("/debug/users")
def debug_users():
    """
    Will later dump the entire user DB (intentional vulnerability).
    Disabled in v0.1.0.
    """
    return JSONResponse({"detail": "disabled in 0.1.0"})

@app.get("/backup/users.bak", response_class=PlainTextResponse)
def backup_dump():
    """
    Will later simulate a stray backup file with sensitive data.
    Disabled in v0.1.0.
    """
    return "not available in 0.1.0"

@app.get("/.well-known/config")
def well_known_config():
    """
    Will later expose sensitive configuration (intentional vulnerability).
    Disabled in v0.1.0.
    """
    return {"detail": "coming soon"}

@app.get("/algo")
def set_algo(preferred: str = "md5", iterations: int = 1):
    """
    Will later allow changing hash algorithm & iteration count at runtime.
    This will be an intentional 'downgrade attack' vulnerability.
    Disabled in v0.1.0.
    """
    return {"detail": "disabled in 0.1.0"}

@app.post("/admin/bulk-create")
def bulk_create_users(body: BulkCreateIn):
    """
    ADMIN (INTENTIONALLY UNPROTECTED) — Bulk create users with random passwords.
    Vulnerability C3:
      - No authentication or authorization.
      - Returns plaintext credentials in the response (and a CSV string).
    Behavior:
      - For each username:
          * If user exists and overwrite=False, skip.
          * Else, generate password, store MD5 hash, record plaintext in response.
    """
    db = load_db()
    created = []
    skipped = []

    for uname in body.usernames:
        uname = uname.strip()
        if not uname:
            continue

        if uname in db["users"] and not body.overwrite:
            skipped.append(uname)
            continue

        pw = generate_random_password(body.length)
        db["users"][uname] = {
            "hash": hash_password_md5(pw),  # intentionally weak
            "role": "user",
            "created_at": int(time.time())
        }
        created.append({"username": uname, "password": pw})

    save_db(db)

    # Convenience CSV block for quick copy-paste into your report
    # format: username,password
    csv_lines = ["username,password"]
    csv_lines += [f"{row['username']},{row['password']}" for row in created]
    csv_blob = "\n".join(csv_lines)

    return {
        "created_count": len(created),
        "skipped_existing": skipped,
        "accounts": created,
        "csv": csv_blob
    }

# -----------------------------------------------------------
# End of file
# -----------------------------------------------------------
