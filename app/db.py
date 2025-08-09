import json
import os
import time
from typing import Dict, Any
from .config import DB_FILE
from .security import hash_password

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