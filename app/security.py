import hashlib
import secrets
import time
from .config import CONFIG

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
    from .db import load_db, save_db
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