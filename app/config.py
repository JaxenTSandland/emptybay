CONFIG = {
    "hash_algo": "md5",
    "iterations": 1,
    "pepper": "pepper"
}
CONFIG.setdefault("reuse_salt", True)
CONFIG.setdefault("predictable_salt", True)

DB_FILE = "users.json"