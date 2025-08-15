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
from fastapi.middleware.cors import CORSMiddleware
from .routes import public, auth, reset, leaks, admin
from .db import ensure_default_admin

app = FastAPI(title="EmptyBay Manager API", version="0.10.0")

# Add CORS middleware - must be added before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://61fa7680fec0.ngrok-free.app",  # Frontend ngrok URL
        "https://cb9ed81ee21a.ngrok-free.app",  # Backend ngrok URL
        "http://localhost:3000",                 # Local development
        "http://127.0.0.1:3000"                 # Local development alternative
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add explicit OPTIONS handler to bypass ngrok issues
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return {"message": "OK"}

app.include_router(public.router)
app.include_router(auth.router)
app.include_router(reset.router)
app.include_router(leaks.router)
app.include_router(admin.router)

ensure_default_admin()