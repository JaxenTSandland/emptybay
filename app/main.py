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
import hmac
import secrets
import string

# -----------------------------------------------------------
# App setup
# -----------------------------------------------------------
# title & version appear in auto-generated docs at /docs
app = FastAPI(title="EmptyBay Manager API", version="0.8.0")

# The "database" file we'll read/write. Later we can make this part of a vulnerability.
DB_FILE = "users.json"

# -----------------------------------------------------------
# Insecure runtime configuration (exposed + mutable)
# -----------------------------------------------------------
CONFIG = {
    "hash_algo": "md5",      # md5 | sha1 | pbkdf2
    "iterations": 1,         # tiny counts by default
    "pepper": "pepper"       # weak pepper, publicly exposed
}
CONFIG.setdefault("reuse_salt", True)           # if True, everyone shares one salt
CONFIG.setdefault("predictable_salt", True)     # if True, per-user salt = username[:3] + "123"


# -----------------------------------------------------------
# Helper functions for reading/writing our "database"
# -----------------------------------------------------------
def load_db() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        return {"users": {}, "salts": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
    except json.JSONDecodeError:
        db = {"users": {}, "salts": {}}
    db.setdefault("users", {})
    db.setdefault("salts", {})
    return db

def save_db(db: Dict[str, Any]) -> None:
    """
    Saves the in-memory DB dictionary back to disk as JSON.
    """
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)

def hash_password(password: str, username: str | None = None) -> str:
    """
    Uses CONFIG and an intentionally weak salt policy.
    Salt is stored separately in DB and exposed via API.
    Format: "<algo>$<salt>$<digest-or-hex>"
    """
    # choose salt (username required for predictable salt)
    salt = get_salt(username or "")
    material = (salt + password + CONFIG["pepper"]).encode()

    if CONFIG["hash_algo"].lower() == "md5":
        digest = hashlib.md5(material).hexdigest()
        for _ in range(CONFIG["iterations"] - 1):
            digest = hashlib.md5(digest.encode()).hexdigest()
        return f"md5${salt}${digest}"

    if CONFIG["hash_algo"].lower() == "sha1":
        digest = hashlib.sha1(material).hexdigest()
        for _ in range(CONFIG["iterations"] - 1):
            digest = hashlib.sha1(digest.encode()).hexdigest()
        return f"sha1${salt}${digest}"

    if CONFIG["hash_algo"].lower() == "pbkdf2":
        dk = hashlib.pbkdf2_hmac("sha256", material, b"", max(1, CONFIG["iterations"]))
        return f"pbkdf2${salt}${dk.hex()}"

    # fallback
    digest = hashlib.md5(material).hexdigest()
    return f"md5${salt}${digest}"

def generate_random_password(length: int = 12) -> str:
    """
    Generates a random password.
    NOTE: We include only letters+digits to keep demo-friendly.
    For a real system you'd include punctuation and enforce policy.
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def insecure_equal(a: str, b: str) -> bool:
    """
    Intentionally timing-vulnerable comparison:
    - Compares byte-by-byte and RETURNS EARLY on first mismatch.
    - Longer shared prefix => longer runtime => information leak.

    WARNING: Do NOT do this in real systems. Use hmac.compare_digest on fixed-length data.
    """
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if a[i] != b[i]:
            return False
    return True

def weak_reset_token(username: str) -> str:
    """
    Predictable, time-bucketed reset token:
    md5(username + minuteEpoch). Valid for the current minute only.
    This is intentionally weak and easy to brute/guess.
    """
    minute_epoch = int(time.time() // 60)
    material = f"{username}{minute_epoch}".encode()
    return hashlib.md5(material).hexdigest()

def make_session_token(username: str) -> str:
    """
    Deterministic, predictable token:
    md5(username + pepper). No expiry. Not stored server-side.
    """
    material = (username + CONFIG["pepper"]).encode()
    return hashlib.md5(material).hexdigest()

def get_user_by_token(token: str, db: dict) -> str | None:
    """
    Recompute expected token for each user and compare.
    O(n) scan; no index. Returns username or None.
    """
    for uname in db.get("users", {}):
        if make_session_token(uname) == token:
            return uname
    return None

def get_salt(username: str) -> str:
    db = load_db()

    # Reused global salt (default bad path)
    if CONFIG.get("reuse_salt", True):
        if "global" not in db["salts"]:
            db["salts"]["global"] = "globalsalt"  # fixed & predictable
            save_db(db)
        return db["salts"]["global"]

    # Predictable per-user salt (second bad path)
    if CONFIG.get("predictable_salt", True):
        salt = (username[:3] + "123")
        if db["salts"].get(username) != salt:
            db["salts"][username] = salt
            save_db(db)
        return salt

    # (unused “good” path)
    rnd = secrets.token_hex(8)
    db["salts"][username] = rnd
    save_db(db)
    return rnd



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
        "version": "0.8.0",
        "note": "pre-alpha build"
    }

# -----------------------------------------------------------
# Auth endpoints (currently safe placeholders)
# -----------------------------------------------------------

@app.post("/register")
def register(body: RegisterIn):
    """
    Creates a new user in our database.
    Vulnerability (A1): hashes with MD5, no salt (see hash_password).
    """
    db = load_db()

    if body.username in db["users"]:
        raise HTTPException(status_code=409, detail="username exists")

    db["users"][body.username] = {
        "hash": hash_password(body.password, body.username),
        "role": "user",
        "created_at": int(time.time())
    }
    save_db(db)
    return {"ok": True}

@app.post("/login")
def login(body: LoginIn):
    """
    Attempts to authenticate a user.

    Vulnerabilities so far:
      - A1: MD5 (no salt) for password hashing (hash_password)
      - B1: Timing-vulnerable compare via insecure_equal()

    Later:
      - We'll add session token behavior and other vulns.
    """
    db = load_db()
    user = db["users"].get(body.username)
    if not user:
        # keep identical status code to avoid easy user enumeration,
        # but timing will still leak existence later in the assignment.
        raise HTTPException(status_code=401, detail="bad creds")

    expected = hash_password(body.password, body.username)
    stored = user["hash"]
    if not insecure_equal(stored, expected):
        raise HTTPException(status_code=401, detail="Incorrect login")

    # TODO: issue a weak/predictable session token
    return {"ok": True, "token": make_session_token(body.username)}

from fastapi import Header, Query

@app.get("/me")
def me(authorization: str | None = Header(default=None), token: str | None = Query(default=None)):
    """
    Returns the current user derived from a token.
    Vulnerabilities:
      - Accepts token via header OR query param (easy interception/reuse).
      - Token is predictable and non-expiring.
      - No server-side invalidation/rotation.
    Header example: Authorization: Bearer <token>
    Query example:  /me?token=<token>
    """
    supplied = None
    if authorization and authorization.lower().startswith("bearer "):
        supplied = authorization.split(" ", 1)[1].strip()
    if token and not supplied:
        supplied = token

    if not supplied:
        raise HTTPException(status_code=401, detail="missing token")

    db = load_db()
    uname = get_user_by_token(supplied, db)
    if not uname:
        raise HTTPException(status_code=401, detail="invalid token")

    return {"username": uname, "role": db["users"][uname]["role"]}

@app.post("/password-reset/request")
def reset_request(body: ResetRequestIn):
    """
    Requests a password reset token for a username.

    Vulnerability (C2):
      - Predictable token = md5(username + minuteEpoch)
      - Token is directly returned in the response (leak)
      - Side-channel: timing + response shape can leak user existence

    Behavior:
      - If user exists: return { reset_token: <token> }
      - If user does not exist: still return { ok: true } to *try* to hide existence (timing will vary anyway)
    """
    db = load_db()
    if body.username in db["users"]:
        token = weak_reset_token(body.username)
        return {"reset_token": token}
    return {"ok": True}


@app.post("/password-reset/confirm")
def reset_confirm(body: ResetConfirmIn):
    """
    Confirms a password reset with a token and sets a new password.

    Vulnerability (C2):
      - Token is predictable and valid for the current minute only.
      - No rate limiting or additional checks.

    On success:
      - Sets the user's password to the NEW one using our weak hash (MD5 no salt).
    """
    db = load_db()
    user = db["users"].get(body.username)
    if not user:
        raise HTTPException(status_code=404, detail="no such user")

    expected = weak_reset_token(body.username)
    if body.token != expected:
        raise HTTPException(status_code=400, detail="invalid token")

    user["hash"] = hash_password(body.new_password, body.username)
    save_db(db)
    return {"ok": True}


# -----------------------------------------------------------
# Recon / Leak endpoints (disabled for now)
# -----------------------------------------------------------

@app.get("/debug/users")
def debug_users():
    """
    DEBUG/DIAGNOSTIC (INTENTIONALLY INSECURE)
    C1: Leaks the entire user database including password hashes.
    NOTE: No auth. This is a classic 'left enabled in prod' mistake.
    """
    db = load_db()
    return JSONResponse(db)  # usernames + hashes

@app.get("/backup/users.bak", response_class=PlainTextResponse)
def backup_dump():
    """
    BACKUP LEAK (INTENTIONALLY INSECURE)
    C1: Simulates a stray backup file left on the server.
    Pretty-prints the same DB so it's easy to harvest.
    """
    db = load_db()
    return json.dumps(db, indent=2)

@app.get("/.well-known/config")
def well_known_config():
    """
    INTENTIONALLY EXPOSED CONFIG (D1)
    Attackers can read pepper, algorithm, and iteration count.
    """
    return CONFIG

@app.get("/.well-known/salts")
def dump_salts():
    """
    INTENTIONALLY EXPOSED SALTS (A/B vuln)
    Returns the 'salts' map from the DB. If empty, backfill from stored hashes.
    """
    db = load_db()
    if not db["salts"]:
        # Backfill from users' hash format: "<algo>$<salt>$<digest>"
        for uname, rec in db.get("users", {}).items():
            parts = str(rec.get("hash", "")).split("$")
            if len(parts) == 3:
                _, salt, _ = parts
                if CONFIG.get("reuse_salt", True):
                    db["salts"]["global"] = salt
                else:
                    db["salts"][uname] = salt
        save_db(db)
    return db.get("salts", {})

@app.get("/algo")
def set_algo(preferred: str = "md5", iterations: int = 1, pepper: str | None = None):
    """
    INTENTIONALLY UNPROTECTED DOWNGRADE ENDPOINT (D1)
    Anyone can change hashing parameters for *future* operations
    (e.g., registration, bulk-create).
    """
    CONFIG["hash_algo"] = preferred.lower()
    CONFIG["iterations"] = max(1, int(iterations))
    if pepper is not None:
        CONFIG["pepper"] = pepper  # also mutable (very bad)
    return CONFIG


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
            "hash": hash_password(pw, uname),
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
