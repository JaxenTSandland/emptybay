from fastapi import APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse
import json
from ..db import load_db, save_db
from ..config import CONFIG

router = APIRouter()

@router.get("/debug/users")
def debug_users():
    db = load_db()
    return JSONResponse(db)

@router.get("/backup/users.bak", response_class=PlainTextResponse)
def backup_dump():
    db = load_db()
    return json.dumps(db, indent=2)

@router.get("/.well-known/config")
def well_known_config():
    return CONFIG

@router.get("/.well-known/salts")
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

@router.get("/algo")
def set_algo(preferred: str = "md5", iterations: int = 1, pepper: str | None = None):
    CONFIG["hash_algo"] = preferred.lower()
    CONFIG["iterations"] = max(1, int(iterations))
    if pepper is not None:
        CONFIG["pepper"] = pepper
    return CONFIG