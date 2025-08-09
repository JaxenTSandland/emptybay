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

from fastapi import FastAPI
from .routes import public, auth, reset, leaks, admin
from .db import ensure_default_admin

app = FastAPI(title="EmptyBay Manager API", version="0.10.0")

app.include_router(public.router)
app.include_router(auth.router)
app.include_router(reset.router)
app.include_router(leaks.router)
app.include_router(admin.router)

ensure_default_admin()