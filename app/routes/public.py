from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
def status():
    return {
        "service": "EmptyBay Auth",
        "version": "0.10.0",
        "note": "pre-alpha build"
    }