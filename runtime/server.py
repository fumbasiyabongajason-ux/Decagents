#!/usr/bin/env python3
"""
Decagent API server
====================
Exposes the ten agents over HTTP so your subscription website can call them.
This is the backend the website talks to.

Run:
    pip install -r runtime/requirements.txt
    uvicorn runtime.server:app --reload --port 8000

Endpoints:
    GET  /agents                 -> list all agents (id, name, tier, tagline)
    GET  /agents/{id}            -> one agent's full manifest
    POST /run  {agent, message}  -> run an agent, return its response

NOTE: This is the open scaffold. Before going live you must add (see billing/):
    - authentication (who is calling)
    - subscription checks (is this user's plan allowed to use this agent)
    - rate limiting and usage metering
The middleware stub `require_active_subscription` shows where that goes.
"""
from __future__ import annotations
import json, pathlib
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import decagent  # reuse the runtime

ROOT = pathlib.Path(__file__).resolve().parent.parent
app = FastAPI(title="Decagent API", version="0.1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


class RunRequest(BaseModel):
    agent: str
    message: str


def require_active_subscription(authorization: str | None, agent_id: str) -> str:
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
def run(req: RunRequest, authorization: str | None = Header(default=None)):
    user = require_active_subscription(authorization, req.agent)
    try:
        text = decagent.run(req.agent, req.message)
    except SystemExit as e:
        raise HTTPException(400, str(e))
    return {"agent": req.agent, "user": user, "response": text}


@app.get("/")
def root():
    return {"product": "Decagent", "agents": "/agents", "run": "POST /run"}
