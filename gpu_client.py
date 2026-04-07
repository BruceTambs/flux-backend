# gpu_client.py

import httpx
from fastapi import HTTPException

# ============================================
# 1. GPU Server Endpoint
# ============================================

# Replace this with your actual GPU server endpoint when ready
GPU_SERVER_URL = "http://your-gpu-server-endpoint/run"


# ============================================
# 2. Generate Image (core GPU call)
# ============================================

async def generate_image(prompt: str, seed: int | None, size: str | None):
    payload = {
        "prompt": prompt,
        "seed": seed,
        "size": size
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(GPU_SERVER_URL, json=payload)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="GPU server error")

        return response.json()

    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="GPU server offline")

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="GPU server timeout")
