"""
J.A.R.V.I.S — Vercel Serverless API
====================================
FastAPI backend that runs automatically on Vercel when the app is deployed.
No separate server process needed — the API starts with every request.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from intents import IntentRouter
from logger import get_logger

log = get_logger("api_index")

app = FastAPI(
    title="J.A.R.V.I.S API",
    description="Serverless backend for J.A.R.V.I.S — auto-runs on Vercel",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = IntentRouter()


class QueryRequest(BaseModel):
    text: str


async def _process_chat(text: str) -> dict:
    log.info(f"API received query: {text[:60]}")
    result = await router.route(text)
    result["type"] = "response"
    return result


@app.post("/api/chat")
@app.post("/chat")
async def chat_endpoint(request: QueryRequest):
    try:
        return await _process_chat(request.text)
    except Exception as e:
        log.error(f"API routing error: {e}")
        return {
            "response": "I encountered an unexpected error. Please try again.",
            "tool": "llm",
            "log": f"Error: {str(e)[:80]}",
            "type": "response",
        }


@app.get("/api/health")
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "J.A.R.V.I.S API is online.",
        "mode": "serverless",
    }


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public")

# Explicit route for the root to serve index.html directly
@app.get("/")
async def serve_index():
    import glob
    
    # Check a few possible locations
    possible_paths = [
        os.path.join(os.getcwd(), "public", "index.html"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "index.html"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public", "index.html"),
        os.path.join(os.getcwd(), "index.html"),
    ]
    
    for p in possible_paths:
        if os.path.exists(p):
            return FileResponse(p)
            
    # If not found, return debug info so we can see the filesystem!
    try:
        root_files = os.listdir(os.getcwd())
        parent_files = os.listdir(os.path.dirname(os.getcwd()))
        file_dir_files = os.listdir(os.path.dirname(os.path.abspath(__file__)))
        file_parent_files = os.listdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    except Exception as e:
        root_files = [str(e)]
        parent_files = []
        file_dir_files = []
        file_parent_files = []
        
    return {
        "detail": "Frontend index.html not found",
        "debug_cwd": os.getcwd(),
        "debug_cwd_files": root_files,
        "debug_parent_files": parent_files,
        "debug_file_dir": os.path.dirname(os.path.abspath(__file__)),
        "debug_file_dir_files": file_dir_files,
        "debug_file_parent": os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "debug_file_parent_files": file_parent_files
    }

# Mount the rest of the public directory for all other static files
for p in [os.path.join(os.getcwd(), "public"), os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public")]:
    if os.path.exists(p):
        app.mount("/", StaticFiles(directory=p), name="static")
        break
