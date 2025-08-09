"""
EmptyBay Manager - Authentication API (Starter Version)
--------------------------------------------------------
This is the starting point for the EmptyBay Manager authentication system.
It contains basic endpoints and example features for demonstration purposes.

Run:
    uvicorn app.main:app --reload
Docs:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI, HTTPException, Header, Query
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
app = FastAPI(title="EmptyBay Manager API", version="0.10.0")

# Simple file-based data store
DB_FILE = "users.json"

# -----------------------------------------------------------
# Runtime configuration (modifies hashing and other behaviors)
# -----------------------------------------------------------
CONFIG = {
    "hash_algo": "md5",      # md5 | sha1 | pbkdf2
    "iterations": 1,
    "pepper": "pepper"
}
CONFIG.setdefault("reuse_salt", True)
CONFIG.setdefault("predictable_salt", True)

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
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)

def hash_password(password: str, username: str | None = None) -> str:
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

    digest = hashlib.md5(material).hexdigest()
    return f"md5${salt}${digest}"

def generate_random_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))

def insecure_equal(a: str, b: str) -> bool:
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if a[i] != b[i]:
            return False
    return True

def weak_reset_token(username: str) -> str:
    minute_epoch = int(time.time() // 60)
    material = f"{username}{minute_epoch}".encode()
    return hashlib.md5(material).hexdigest()

def make_session_token(username: str) -> str:
    material = (username + CONFIG["pepper"]).encode()
    return hashlib.md5(material).hexdigest()

def get_user_by_token(token: str, db: dict) -> str | None:
    for uname in db.get("users", {}):
        if make_session_token(uname) == token:
            return uname
    return None

def get_salt(username: str) -> str:
    db = load_db()

    if CONFIG.get("reuse_salt", True):
        if "global" not in db["salts"]:
            db["salts"]["global"] = "globalsalt"
            save_db(db)
        return db["salts"]["global"]

    if CONFIG.get("predictable_salt", True):
        salt = (username[:3] + "123")
        if db["salts"].get(username) != salt:
            db["salts"][username] = salt
            save_db(db)
        return salt

    rnd = secrets.token_hex(8)
    db["salts"][username] = rnd
    save_db(db)
    return rnd

# -----------------------------------------------------------
# Seed a default admin account
# -----------------------------------------------------------
def ensure_default_admin():
    db = load_db()
    if "admin" not in db["users"]:
        pw = "EmptyBay!123"
        db["users"]["admin"] = {
            "hash": hash_password(pw, "admin"),
            "role": "admin",
            "created_at": int(time.time())
        }
        save_db(db)

ensure_default_admin()

# -----------------------------------------------------------
# Data models
# -----------------------------------------------------------
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
    length: int = 12
    overwrite: bool = False

# -----------------------------------------------------------
# Public / Company endpoints
# -----------------------------------------------------------
@app.get("/status")
def status():
    return {
        "service": "EmptyBay Auth",
        "version": "0.10.0",
        "note": "pre-alpha build"
    }

# -----------------------------------------------------------
# Auth endpoints
# -----------------------------------------------------------
@app.post("/register")
def register(body: RegisterIn):
    db = load_db()

    if body.username in db["users"]:
        raise HTTPException(status_code=409, detail="username exists")

    db["users"][body.username] = {
        "hash": hash_password(body.password, body.username),
        "role": "user",
        "created_at": int(time.time())
    }
    save_db(db)
    return {"ok": True, "username": body.username, "stored_hash": db["users"][body.username]["hash"]}

@app.post("/login")
def login(body: LoginIn):
    db = load_db()
    user = db["users"].get(body.username)
    if not user:
        raise HTTPException(status_code=401, detail="bad creds")

    expected = hash_password(body.password, body.username)
    stored = user["hash"]
    if not insecure_equal(stored, expected):
        raise HTTPException(status_code=401, detail="Incorrect login")

    return {
        "ok": True,
        "token": make_session_token(body.username),
        "stored_hash": stored
    }

@app.get("/me")
def me(authorization: str | None = Header(default=None), token: str | None = Query(default=None)):
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
    db = load_db()
    if body.username in db["users"]:
        token = weak_reset_token(body.username)
        return {"reset_token": token}
    return {"ok": True}

@app.post("/password-reset/confirm")
def reset_confirm(body: ResetConfirmIn):
    db = load_db()
    user = db["users"].get(body.username)
    if not user:
        raise HTTPException(status_code=404, detail="no such user")

    expected = weak_reset_token(body.username)
    if body.token != expected:
        raise HTTPException(status_code=400, detail="invalid token")

    user["hash"] = hash_password(body.new_password, body.username)
    save_db(db)
    return {"ok": True, "username": body.username, "new_hash": user["hash"]}

# -----------------------------------------------------------
# Misc endpoints
# -----------------------------------------------------------
@app.get("/debug/users")
def debug_users():
    db = load_db()
    return JSONResponse(db)

@app.get("/backup/users.bak", response_class=PlainTextResponse)
def backup_dump():
    db = load_db()
    return json.dumps(db, indent=2)

@app.get("/.well-known/config")
def well_known_config():
    return CONFIG

@app.get("/.well-known/salts")
def dump_salts():
    db = load_db()
    if not db["salts"]:
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
    CONFIG["hash_algo"] = preferred.lower()
    CONFIG["iterations"] = max(1, int(iterations))
    if pepper is not None:
        CONFIG["pepper"] = pepper
    return CONFIG

@app.post("/admin/bulk-create")
def bulk_create_users(body: BulkCreateIn):
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

    csv_lines = ["username,password"]
    csv_lines += [f"{row['username']},{row['password']}" for row in created]
    csv_blob = " ".join(csv_lines)

    return {
        "created_count": len(created),
        "skipped_existing": skipped,
        "accounts": created,
        "csv": csv_blob
    }

# -----------------------------------------------------------
# End of file
# -----------------------------------------------------------
