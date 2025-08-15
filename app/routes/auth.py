from fastapi import APIRouter, HTTPException, Header, Query
import time
from ..models import RegisterIn, LoginIn
from ..db import load_db, save_db
from ..security import hash_password, insecure_equal, make_session_token, get_user_by_token

router = APIRouter()

@router.post("/register")
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

@router.post("/login")
def login(body: LoginIn):
    db = load_db()
    user = db["users"].get(body.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Username or Password")

    expected = hash_password(body.password, body.username)
    stored = user["hash"]
    if not insecure_equal(stored, expected):
        raise HTTPException(status_code=401, detail="Invalid Username or Password")

    return {
        "ok": True,
        "token": make_session_token(body.username),
        "stored_hash": stored
    }

@router.get("/me")
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