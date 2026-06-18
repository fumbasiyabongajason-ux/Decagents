#!/usr/bin/env python3
"""
Decagent API server
====================
Exposes the ten agents over HTTP so your subscription website can call them.
This is the backend the website talks to.

Run the Console:
    pip install -r runtime/requirements.txt
    cp runtime/.env.example runtime/.env     # add your keys
    uvicorn runtime.server:app --reload --port 8000
    # then open http://localhost:8000  ->  chat with all 10 agents

Endpoints:
    GET  /                          -> the Console chat UI (app/index.html)
    POST /chat {agent, message, history}
                                    -> chat; agent="auto" routes automatically
    GET  /agents                    -> list all agents
    GET  /agents/{id}               -> one agent's full manifest
    POST /run  {agent, message}     -> run an agent once (no history)

NOTE: This is the open scaffold. Before going live you must add (see billing/):
    - authentication (who is calling)
    - subscription checks (is this user's plan allowed to use this agent)
    - rate limiting and usage metering
The middleware stub `require_active_subscription` shows where that goes.
"""
from __future__ import annotations
import json, os, pathlib
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from . import decagent  # reuse the runtime

ROOT = pathlib.Path(__file__).resolve().parent.parent
APP_HTML = ROOT / "app" / "index.html"  # the Console chat UI

# Optional shared password. If set (recommended for any public/cloud URL), the
# Console requires it before chatting — protects your API spend + connected tools.
ACCESS_PASSWORD = (os.getenv("DECAGENT_PASSWORD") or "eiziee").strip()
app = FastAPI(title="Decagent API", version="0.1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


class RunRequest(BaseModel):
    agent: str
    message: str


class ChatRequest(BaseModel):
    agent: str = "auto"          # an agent id, or "auto" to route automatically
    message: str
    history: list[dict] = []     # prior [{role, content}] turns from the Console


class AuthRequest(BaseModel):
    password: str = ""


def require_active_subscription(authorization: Optional[str], agent_id: str) -> str:
    """STUB — replace with real auth + Stripe subscription check.

    1. Resolve the API key / session token in `authorization` to a user.
    2. Look up that user's Stripe subscription and plan tier.
    3. Confirm the requested agent is included in their tier (see catalog tiers).
    4. Meter the call for usage-based billing if you use it.
    Raise HTTPException(402) if their plan doesn't cover this agent.
    """
    # Demo mode: allow everything. DO NOT ship to production like this.
    return "demo-user"


@app.get("/agents")
def agents():
    return decagent.list_agents()


@app.get("/agents/{agent_id}")
def agent_detail(agent_id: str):
    try:
        a = decagent.load_agent(agent_id)
    except SystemExit:
        raise HTTPException(404, f"No agent '{agent_id}'")
    a.pop("_dir", None)
    return a


@app.post("/run")
def run(req: RunRequest, authorization: Optional[str] = Header(default=None)):
    user = require_active_subscription(authorization, req.agent)
    try:
        text = decagent.run(req.agent, req.message)
    except SystemExit as e:
        raise HTTPException(400, str(e))
    return {"agent": req.agent, "user": user, "response": text}


@app.get("/", response_class=HTMLResponse)
def home():
    """Serve the Decagent Console (the ChatGPT-style chat UI)."""
    if APP_HTML.exists():
        return FileResponse(str(APP_HTML), headers={"Cache-Control": "no-store, max-age=0"})
    return HTMLResponse("<h1>Decagent Console</h1><p>UI file <code>app/index.html</code> not found.</p>")


@app.get("/api")
def api_info():
    return {"product": "Decagent Console", "console": "/", "agents": "/agents",
            "chat": "POST /chat", "run": "POST /run"}


@app.get("/auth")
def auth_status():
    """Tells the Console whether a password is required."""
    return {"protected": bool(ACCESS_PASSWORD)}


@app.post("/auth")
def auth_check(req: AuthRequest):
    """Verify a password attempt."""
    return {"ok": (not ACCESS_PASSWORD) or req.password == ACCESS_PASSWORD}


@app.post("/chat")
def chat(req: ChatRequest, x_decagent_password: Optional[str] = Header(default=None)):
    """Console chat endpoint. agent='auto' routes to the best specialist,
    then runs it with the conversation history."""
    if ACCESS_PASSWORD and (x_decagent_password or "") != ACCESS_PASSWORD:
        raise HTTPException(401, "unauthorized")
    agent_id = req.agent or "auto"
    try:
        if agent_id == "auto":
            agent_id = decagent.route(req.message)
        text = decagent.run(agent_id, req.message,
                             history=req.history[-10:], verbose=False)
        return {"agent": agent_id, "response": text}
    except (Exception, SystemExit) as e:  # missing keys/deps, bad id, API errors — report cleanly
        return {"agent": agent_id, "response": None, "error": str(e) or "agent runtime error"}
