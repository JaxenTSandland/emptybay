from fastapi import APIRouter, HTTPException
from ..models import ResetRequestIn, ResetConfirmIn
from ..db import load_db, save_db
from ..security import weak_reset_token, hash_password

router = APIRouter()

@router.post("/password-reset/request")
def reset_request(body: ResetRequestIn):
    db = load_db()
    if body.username in db["users"]:
        token = weak_reset_token(body.username)
        return {"reset_token": token}
    return {"ok": True}

@router.post("/password-reset/confirm")
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