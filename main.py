# main.py

from fastapi import FastAPI
from pydantic import BaseModel

from auth import login, validate_token
from gpu_client import generate_image

app = FastAPI()


# ============================================
# 1. Request Models
# ============================================

class LoginRequest(BaseModel):
    password: str


class ImageRequest(BaseModel):
    token: str
    prompt: str
    seed: int | None = None
    size: str | None = None


# ============================================
# 2. Login Endpoint
# ============================================

@app.post("/login")
def login_endpoint(req: LoginRequest):
    token = login(req.password)
    return {"token": token}


# ============================================
# 3. Image Generation Endpoint
# ============================================

@app.post("/generate-image")
async def generate_image_endpoint(req: ImageRequest):
    # Validate session token
    validate_token(req.token)

    # Forward request to GPU server
    result = await generate_image(
        prompt=req.prompt,
        seed=req.seed,
        size=req.size
    )

    return result
