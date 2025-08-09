from fastapi import APIRouter
import time
from ..models import BulkCreateIn
from ..db import load_db, save_db
from ..security import hash_password
from ..utils import generate_random_password

router = APIRouter()

@router.post("/admin/bulk-create")
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