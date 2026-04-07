print(">>> RUNNING server.py FROM THIS FOLDER <<<")
import datetime
from fastapi import FastAPI, HTTPException, Header

from auth import login as auth_login, validate_token
from prompt_engine import load_all_text_files, assemble_prompt



app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ============================================
# 1. Auth helpers
# ============================================

def require_token(authorization: str | None):
    """
    Expect header: Authorization: Bearer <token>
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header"
        )

    token = authorization.split(" ", 1)[1].strip()
    validate_token(token)


# ============================================
# 2. Endpoint: Login
# ============================================

@app.post("/login")
def login_endpoint(payload: dict):
    """
    Expected payload:
    {
        "password": "string"
    }
    """
    password = payload.get("password", "")
    token = auth_login(password)
    return {"token": token}


# ============================================
# 3. Endpoint: List Available Modules
# ============================================

@app.get("/modules")
def get_modules(authorization: str = Header(None)):
    require_token(authorization)

    modules = load_all_text_files(".")
    return {
        "success": True,
        "modules": list(modules.keys()),
        "errors": []
    }


# ============================================
# 4. Endpoint: Generate Prompt
# ============================================

@app.post("/generate")
def generate_prompt(payload: dict, authorization: str = Header(None)):
    require_token(authorization)

    try:
        selection = payload.get("selection", [])
        modules = load_all_text_files(".")
        prompt = assemble_prompt(modules, selection, debug=False)

        return {
            "success": True,
            "prompt": prompt,
            "modulesUsed": selection,
            "count": len(selection),
            "timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0",
            "images": [],
            "errors": []
        }

    except Exception as e:
        return {
            "success": False,
            "prompt": "",
            "modulesUsed": [],
            "count": 0,
            "timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0",
            "images": [],
            "errors": [str(e)]
        }


# ============================================
# 5. Endpoint: Generate Images (stub)
# ============================================

@app.post("/images")
def generate_images(payload: dict, authorization: str = Header(None)):
    """
    Expected payload shape:
    {
        "prompt": "string",
        "modulesUsed": ["list", "of", "modules"],
        "count": int,
        "style": "string",
        "size": "string"
    }
    """
    require_token(authorization)

    try:
        return {
            "success": True,
            "images": [],
            "count": 0,
            "timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0",
            "errors": []
        }

    except Exception as e:
        return {
            "success": False,
            "images": [],
            "count": 0,
            "timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0",
            "errors": [str(e)]
        }
