"""
J.A.R.V.I.S — Vercel Serverless API
====================================
FastAPI backend that runs automatically on Vercel when the app is deployed.
No separate server process needed — the API starts with every request.
"""

import os
import sys
import base64
from fastapi.responses import HTMLResponse, Response

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from intents import IntentRouter
from logger import get_logger

try:
    from api.frontend_assets import INDEX_HTML, APP_JS, STYLE_CSS, SPACE_CSS, FAVICON_ICO, FAVICON_PNG
except ImportError:
    INDEX_HTML = "<h1>Build Error: frontend_assets.py missing</h1>"
    APP_JS = ""
    STYLE_CSS = ""
    SPACE_CSS = ""
    FAVICON_ICO = ""
    FAVICON_PNG = ""

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

@app.get("/")
async def serve_index():
    return HTMLResponse(content=INDEX_HTML)

@app.get("/app.js")
async def serve_app_js():
    return Response(content=APP_JS, media_type="application/javascript")

@app.get("/style.css")
async def serve_style_css():
    return Response(content=STYLE_CSS, media_type="text/css")

@app.get("/space.css")
async def serve_space_css():
    return Response(content=SPACE_CSS, media_type="text/css")

@app.get("/favicon.ico")
async def serve_favicon_ico():
    return Response(content=base64.b64decode(FAVICON_ICO) if FAVICON_ICO else b"", media_type="image/x-icon")

@app.get("/favicon.png")
async def serve_favicon_png():
    return Response(content=base64.b64decode(FAVICON_PNG) if FAVICON_PNG else b"", media_type="image/png")
