print(">>> RUNNING server.py FROM THIS FOLDER <<<")

import datetime
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

from auth import login as auth_login, validate_token
from prompt_engine import load_all_text_files, assemble_prompt


# ============================================
# FastAPI App + CORS
# ============================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Frontend served locally or anywhere
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Auth Helper
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
# Helper: Filter module files
# ============================================

def filter_module_files(modules: dict) -> dict:
    """
    Removes unwanted .txt files such as requirements.txt or project notes.
    Keeps only the actual module files used for prompt generation.
    """
    blocked = {
        "requirements.txt",
        "ProjectInstructions.txt",
        "README.txt",
    }

    return {
        name: content
        for name, content in modules.items()
        if name not in blocked
    }


# ============================================
# Endpoint: Login
# ============================================

@app.post("/login")
def login_endpoint(payload: dict):
    password = payload.get("password", "")
    token = auth_login(password)
    return {"token": token}


# ============================================
# Endpoint: List Available Modules
# ============================================

@app.get("/modules")
def get_modules(authorization: str = Header(None)):
    require_token(authorization)

    modules = load_all_text_files(".")
    modules = filter_module_files(modules)

    return {
        "success": True,
        "modules": list(modules.keys()),
        "errors": []
    }


# ============================================
# Endpoint: Generate Prompt
# ============================================

@app.post("/generate")
def generate_prompt(payload: dict, authorization: str = Header(None)):
    require_token(authorization)

    try:
        selection = payload.get("selection", [])
        modules = load_all_text_files(".")
        modules = filter_module_files(modules)

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
# Endpoint: Generate Images (stub)
# ============================================

@app.post("/images")
def generate_images(payload: dict, authorization: str = Header(None)):
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
