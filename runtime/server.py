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
import concurrent.futures, hmac, json, os, pathlib
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, PlainTextResponse
from pydantic import BaseModel

from . import decagent  # reuse the runtime

ROOT = pathlib.Path(__file__).resolve().parent.parent
APP_HTML = ROOT / "app" / "index.html"  # the Console chat UI

# Optional shared password. If set (recommended for any public/cloud URL), the
# Console requires it before chatting — protects your API spend + connected tools.
ACCESS_PASSWORD = (os.getenv("DECAGENT_PASSWORD") or "Love").strip()
app = FastAPI(title="Decagent API", version="0.1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)


# Keep the Console INVISIBLE to the public web: every response tells search engines not to index
# or follow it. Combined with /robots.txt and the noindex <meta> in the page, the app stays
# reachable by anyone with the link + password, but won't show up in Google/Bing or be archived.
@app.middleware("http")
async def _no_index_header(request, call_next):
    resp = await call_next(request)
    resp.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive, nosnippet"
    return resp


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots():
    """Tell every crawler to stay out — the console is private."""
    return "User-agent: *\nDisallow: /\n"

# Hard wall-clock ceiling for a single agent run. A slow web search or a stuck
# connected-app (Pipedream/MCP) call can otherwise hang the request forever; the
# in-loop budget only checks between turns, so one slow turn can overshoot badly.
# This guarantees /chat returns BEFORE the Console's 115s client abort.
HARD_TIMEOUT_SEC = float(os.getenv("DECAGENT_HARD_TIMEOUT_SEC", "150"))  # room for async video (~1 min)
_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=8)


def _run_with_deadline(fn, *args, **kwargs):
    """Run fn in a worker thread; abandon it if it exceeds HARD_TIMEOUT_SEC."""
    return _EXECUTOR.submit(fn, *args, **kwargs).result(timeout=HARD_TIMEOUT_SEC)


def _keep_warm():
    """Self-ping the PUBLIC URL every ~10 min so Render's free tier never spins the
    app down (15-min idle = cold start / 'needs refresh'). Inbound traffic to the
    external URL resets the idle timer; an internal localhost ping would NOT. Render
    sets RENDER_EXTERNAL_URL automatically. Disable with DECAGENT_KEEPWARM=0."""
    import time, requests
    if os.getenv("DECAGENT_KEEPWARM", "1") == "0":
        return
    url = (os.getenv("RENDER_EXTERNAL_URL") or os.getenv("DECAGENT_PUBLIC_URL") or "").rstrip("/")
    if not url:
        return
    time.sleep(45)  # let the app finish booting first
    while True:
        try:
            requests.get(url + "/api", timeout=20)
        except Exception:
            pass
        time.sleep(600)  # 10 min < Render's 15-min idle window


import threading as _kw_threading
_kw_threading.Thread(target=_keep_warm, daemon=True).start()


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
    except Exception as e:
        raise HTTPException(500, f"could not load agent '{agent_id}': {e}")
    a.pop("_dir", None)
    return a


@app.post("/run")
def run(req: RunRequest, authorization: Optional[str] = Header(default=None)):
    user = require_active_subscription(authorization, req.agent)
    try:
        text = _run_with_deadline(decagent.run, req.agent, req.message)
    except concurrent.futures.TimeoutError:
        raise HTTPException(504, f"agent timed out after {int(HARD_TIMEOUT_SEC)}s")
    except SystemExit as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, f"agent error: {e}")
    return {"agent": req.agent, "user": user, "response": text}


@app.get("/p/{pid}", response_class=HTMLResponse)
def page(pid: str):
    """Serve a webpage published by create_webpage/build_site — a live URL on this site. Reads the
    durable store (local /tmp first, then Supabase) so links survive a free-tier restart/redeploy."""
    safe = os.path.basename(pid or "")
    if not safe or not all(c.isalnum() or c in "_-" for c in safe):
        raise HTTPException(404, "not found")
    try:
        from . import builtin_tools as _bt
        html = _bt.page_html(safe)
    except Exception:
        html = None
    if html is not None:
        return HTMLResponse(html, headers={"Cache-Control": "no-store"})
    path = os.path.join(os.getenv("DECAGENT_PAGES_DIR", "/tmp/dgpages"), safe + ".html")
    if os.path.exists(path):
        return FileResponse(path, media_type="text/html", headers={"Cache-Control": "no-store"})
    raise HTTPException(404, "not found")


@app.get("/debug/video")
def debug_video(pw: Optional[str] = None):
    """TEMP — reports which video keys the app actually sees (NEVER the values). Remove after."""
    if ACCESS_PASSWORD and not hmac.compare_digest(pw or "", ACCESS_PASSWORD):
        raise HTTPException(401, "add ?pw=YOUR_PASSWORD")
    pol = os.getenv("POLLINATIONS_API_KEY") or os.getenv("POLLINATIONS_TOKEN") or ""
    gem = os.getenv("GEMINI_API_KEY") or ""
    related = sorted(n for n in os.environ
                     if any(s in n.upper() for s in ("POLLINAT", "GEMINI", "GOOGLE", "VEO")))
    return {"pollinations_key_detected": bool(pol.strip()), "pollinations_key_len": len(pol),
            "pollinations_key_prefix": (pol.strip()[:3] if pol.strip() else ""),
            "gemini_key_detected": bool(gem.strip()),
            "related_env_var_names": related}


@app.get("/debug/persist")
def debug_persist(pw: Optional[str] = None):
    """TEMP — verify Supabase persistence end-to-end: env vars set? tables exist? can we
    write+read+delete? Never returns secret values. Remove once confirmed working."""
    if ACCESS_PASSWORD and not hmac.compare_digest(pw or "", ACCESS_PASSWORD):
        raise HTTPException(401, "add ?pw=YOUR_PASSWORD")
    import requests, time as _t
    url = (os.getenv("SUPABASE_URL") or "").rstrip("/")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY") or ""
    out = {"supabase_url_detected": bool(url), "supabase_key_detected": bool(key)}
    if not (url and key):
        out["status"] = "Supabase env NOT set — add SUPABASE_URL and SUPABASE_KEY in Render → Environment."
        return out
    hdr = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    tag = "__persist_selftest__"

    def round_trip(table, row, filt):
        try:
            w = requests.post(f"{url}/rest/v1/{table}",
                              headers={**hdr, "Prefer": "resolution=merge-duplicates,return=minimal"},
                              json=row, timeout=12)
            if not w.ok:
                return {"ok": False, "error": f"write {w.status_code}: {(w.text or '')[:140]}"}
            r = requests.get(f"{url}/rest/v1/{table}?{filt}&select=*&limit=1", headers=hdr, timeout=12)
            got = bool(r.ok and r.json())
            requests.delete(f"{url}/rest/v1/{table}?{filt}", headers=hdr, timeout=12)  # clean up
            return {"ok": got} if got else {"ok": False, "error": "wrote but could not read back"}
        except Exception as e:
            return {"ok": False, "error": str(e)[:140]}

    txt = tag + str(int(_t.time()))
    out["decagent_pages"] = round_trip("decagent_pages",
                                       {"pid": tag, "html": "<i>selftest</i>", "title": "selftest"},
                                       f"pid=eq.{tag}")
    out["decagent_memories"] = round_trip("decagent_memories", {"text": txt}, f"text=eq.{txt}")
    ok = out["decagent_pages"].get("ok") and out["decagent_memories"].get("ok")
    out["status"] = ("✅ PERSISTENCE WORKING — pages & memory survive restarts." if ok else
                     "⚠️ Not fully working — see per-table error (usually: run the CREATE TABLE SQL once).")
    return out


@app.get("/", response_class=HTMLResponse)
def home():
    """Serve the Decagent Console (the ChatGPT-style chat UI)."""
    if APP_HTML.exists():
        return FileResponse(str(APP_HTML), headers={"Cache-Control": "no-store, max-age=0"})
    return HTMLResponse("<h1>Decagent Console</h1><p>UI file <code>app/index.html</code> not found.</p>")


@app.get("/api")
def api_info():
    return {"product": "Decagent Console", "console": "/", "agents": "/agents",
            "chat": "POST /chat", "run": "POST /run", "connect": "GET /connect"}


@app.get("/media/{name}")
def media(name: str):
    """Serve a generated video (mp4) saved by the generate_video tool."""
    safe = os.path.basename(name or "")
    if "/" in (name or "") or ".." in (name or "") or not safe.endswith(".mp4"):
        raise HTTPException(404, "not found")
    path = os.path.join("/tmp/dgmedia", safe)
    if not os.path.exists(path):
        raise HTTPException(404, "not found")
    return FileResponse(path, media_type="video/mp4")


@app.get("/connect")
def connect(app: Optional[str] = None, pw: Optional[str] = None):
    """One-click helper to connect your Pipedream app accounts (no curl needed).
    Visit /connect?pw=YOUR_PASSWORD to see a button per app in MCP_APP_SLUGS,
    or /connect?app=gmail&pw=... to jump straight to authorizing one app."""
    if ACCESS_PASSWORD and not hmac.compare_digest(pw or "", ACCESS_PASSWORD):
        return HTMLResponse("<h3>Add <code>?pw=YOUR_PASSWORD</code> to the URL.</h3>", status_code=401)
    cid = os.getenv("PIPEDREAM_CLIENT_ID")
    sec = os.getenv("PIPEDREAM_CLIENT_SECRET")
    proj = os.getenv("PIPEDREAM_PROJECT_ID")
    if not (cid and sec and proj):
        return HTMLResponse("<h3>Set PIPEDREAM_CLIENT_ID, PIPEDREAM_CLIENT_SECRET and "
                            "PIPEDREAM_PROJECT_ID in Render → Environment first, then reload.</h3>")
    env = os.getenv("PIPEDREAM_ENVIRONMENT", "development")
    uid = os.getenv("PIPEDREAM_EXTERNAL_USER_ID", "me")
    import requests
    try:
        tok = requests.post("https://api.pipedream.com/v1/oauth/token",
                            json={"grant_type": "client_credentials", "client_id": cid, "client_secret": sec},
                            timeout=30).json().get("access_token")
        r = requests.post(f"https://api.pipedream.com/v1/connect/{proj}/tokens",
                          headers={"Authorization": f"Bearer {tok}", "X-PD-Environment": env,
                                   "Content-Type": "application/json"},
                          json={"external_user_id": uid}, timeout=30).json()
    except Exception as e:
        return HTMLResponse(f"<h3>Could not reach Pipedream: {e}</h3>", status_code=502)
    link = r.get("connect_link_url")
    token = r.get("token") or r.get("connect_token")
    if not (link or token):
        return HTMLResponse(f"<h3>Pipedream did not return a connect token.</h3><pre>{json.dumps(r)[:600]}</pre>",
                            status_code=502)

    def app_url(slug):
        if link:
            return link + ("&" if "?" in link else "?") + "app=" + slug
        return f"https://pipedream.com/_static/connect.html?token={token}&connectLink=true&app={slug}"

    if app:
        return RedirectResponse(app_url(app))
    slugs = [s.strip() for s in os.getenv("MCP_APP_SLUGS", "").split(",") if s.strip()] or ["gmail", "github"]
    btns = "".join(
        f'<a href="/connect?app={s}&pw={pw}" style="display:block;margin:10px 0;padding:13px 16px;'
        f'background:#6E56F8;color:#0a0a0f;border-radius:11px;text-decoration:none;font-weight:600">'
        f'Connect {s} &rarr;</a>' for s in slugs)
    return HTMLResponse(
        "<html><body style='font-family:system-ui,sans-serif;max-width:440px;margin:48px auto;"
        "padding:0 20px;background:#0d0d13;color:#ececf1'>"
        f"<h2 style='font-family:Space Grotesk,sans-serif'>Connect your apps</h2>"
        f"<p style='color:#9a9aac'>Authorizing as user <b>{uid}</b> (environment: {env}). "
        "Tap each app to connect it — then your agents can use it.</p>"
        f"{btns}</body></html>")


@app.get("/auth")
def auth_status():
    """Tells the Console whether a password is required."""
    return {"protected": bool(ACCESS_PASSWORD)}


@app.post("/auth")
def auth_check(req: AuthRequest):
    """Verify a password attempt."""
    return {"ok": (not ACCESS_PASSWORD) or hmac.compare_digest(req.password or "", ACCESS_PASSWORD)}


@app.post("/chat")
def chat(req: ChatRequest, x_decagent_password: Optional[str] = Header(default=None)):
    """Console chat endpoint. agent='auto' routes to the best specialist,
    then runs it with the conversation history."""
    if ACCESS_PASSWORD and not hmac.compare_digest(x_decagent_password or "", ACCESS_PASSWORD):
        raise HTTPException(401, "unauthorized")
    agent_id = req.agent or "auto"

    def _work():
        aid = decagent.route(req.message) if agent_id == "auto" else agent_id
        text, steps = decagent.run_traced(aid, req.message, history=req.history[-10:])
        return aid, text, steps

    try:
        agent_id, text, steps = _run_with_deadline(_work)
        return {"agent": agent_id, "response": text, "steps": steps}
    except concurrent.futures.TimeoutError:
        return {"agent": agent_id, "response": None,
                "error": (f"The agent took longer than {int(HARD_TIMEOUT_SEC)}s and was stopped. "
                          "This is usually a slow web search or a stuck connected-app call — try "
                          "again or simplify. If searches always stall, set a free TAVILY_API_KEY.")}
    except (Exception, SystemExit) as e:  # missing keys/deps, bad id, API errors — report cleanly
        return {"agent": agent_id, "response": None, "error": str(e) or "agent runtime error"}
