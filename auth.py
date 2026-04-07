# auth.py

import secrets
from fastapi import HTTPException

# Hardcoded for now; later you can move this to env vars
DEMO_PASSWORD = "changeme"

# In-memory token store
active_tokens = set()

def login(password: str) -> str:
    if password != DEMO_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")

    token = secrets.token_hex(16)
    active_tokens.add(token)
    return token

def validate_token(token: str):
    if token not in active_tokens:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
