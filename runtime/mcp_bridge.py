#!/usr/bin/env python3
"""
MCP tool bridge — connect your agents to ANY MCP server (Pipedream, Zapier, …).
===============================================================================
The "thousands of apps" path. An MCP server exposes app tools; this bridge
discovers them (tools/list) and lets agents call them (tools/call). The provider
(Pipedream / Zapier) handles auth + execution. Any failure falls back to plain
chat — it never crashes the Console.

Env:
  MCP_SERVER_URL   the MCP endpoint (streamable HTTP). Pipedream Connect:
                   https://remote.mcp.pipedream.net/v3
  MCP_HEADERS      JSON of auth headers. Pipedream example:
                   {"Authorization":"Bearer <token>","x-pd-project-id":"proj_xxx",
                    "x-pd-environment":"development","x-pd-external-user-id":"me"}
  MCP_APP_SLUGS    (Pipedream only, optional) comma list of apps to expose, e.g.
                   "gmail,github,slack". The bridge connects per app (sending
                   x-pd-app-slug) and merges their tools. Leave unset for a single
                   server that already returns all its tools (e.g. Zapier).

Active when TOOLS_BACKEND=mcp (or auto when MCP_SERVER_URL is set).
"""
import json, os, re, uuid

PROTOCOL_VERSION = "2025-06-18"


_PD_TOKEN = {"value": None, "exp": 0}   # cached Pipedream access token


def _pipedream_token(client_id, client_secret):
    """Mint/refresh a Pipedream Connect access token (client_credentials). Cached ~1h."""
    import time, requests
    now = time.time()
    if _PD_TOKEN["value"] and now < _PD_TOKEN["exp"] - 60:
        return _PD_TOKEN["value"]
    r = requests.post("https://api.pipedream.com/v1/oauth/token",
                      json={"grant_type": "client_credentials",
                            "client_id": client_id, "client_secret": client_secret},
                      timeout=30)
    d = r.json()
    _PD_TOKEN["value"] = d.get("access_token")
    _PD_TOKEN["exp"] = now + int(d.get("expires_in", 3600))
    return _PD_TOKEN["value"]


def _base_headers(app_slug=None):
    """Build request headers. If Pipedream creds are set, auto-mint the bearer token and
    add the x-pd-* headers; otherwise fall back to raw MCP_HEADERS JSON (e.g. for Zapier)."""
    h = {"Content-Type": "application/json",
         "Accept": "application/json, text/event-stream"}
    cid, sec = os.getenv("PIPEDREAM_CLIENT_ID"), os.getenv("PIPEDREAM_CLIENT_SECRET")
    if cid and sec:
        h["Authorization"] = f"Bearer {_pipedream_token(cid, sec)}"
        h["x-pd-project-id"] = os.getenv("PIPEDREAM_PROJECT_ID", "")
        h["x-pd-environment"] = os.getenv("PIPEDREAM_ENVIRONMENT", "development")
        h["x-pd-external-user-id"] = os.getenv("PIPEDREAM_EXTERNAL_USER_ID", "me")
    else:
        raw = os.getenv("MCP_HEADERS", "").strip()
        if raw:
            try:
                h.update(json.loads(raw))
            except Exception as e:
                print("! MCP_HEADERS is not valid JSON:", e)
    if app_slug:
        h["x-pd-app-slug"] = app_slug
    return h


def _parse(text, content_type):
    """Extract the JSON-RPC message (with 'result' or 'error') from a JSON or SSE body."""
    if not text:
        return None
    ct = (content_type or "").lower()
    if "text/event-stream" in ct or text.lstrip().startswith(("event:", "data:")):
        msg = None
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                payload = line[5:].strip()
                if not payload or payload == "[DONE]":
                    continue
                try:
                    obj = json.loads(payload)
                except Exception:
                    continue
                if isinstance(obj, dict) and ("result" in obj or "error" in obj):
                    msg = obj            # keep the last result/error frame
        return msg
    try:
        return json.loads(text)
    except Exception:
        return None


class MCPClient:
    """One connection to an MCP endpoint (optionally pinned to one app via headers)."""
    def __init__(self, url, headers):
        self.url = url
        self.base_headers = headers
        self.session_id = None

    def _rpc(self, method, params=None, notify=False):
        import requests  # honors HTTPS_PROXY
        body = {"jsonrpc": "2.0", "method": method}
        if not notify:
            body["id"] = str(uuid.uuid4())
        if params is not None:
            body["params"] = params
        headers = dict(self.base_headers)
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        r = requests.post(self.url, json=body, headers=headers, timeout=90)
        sid = r.headers.get("Mcp-Session-Id") or r.headers.get("mcp-session-id")
        if sid:
            self.session_id = sid
        if notify:
            return None
        return _parse(r.text, r.headers.get("Content-Type"))

    def connect(self):
        res = self._rpc("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "decagent", "version": "0.1.0"},
        })
        try:
            self._rpc("notifications/initialized", notify=True)
        except Exception:
            pass
        return res

    def list_tools(self):
        res = self._rpc("tools/list", {})
        if not res or "result" not in res:
            return []
        return res["result"].get("tools", [])

    def call_tool(self, name, arguments):
        res = self._rpc("tools/call", {"name": name, "arguments": arguments or {}})
        if not res:
            return "(no response from MCP server)"
        if "error" in res:
            return f"(MCP error: {res['error'].get('message', 'unknown')})"
        content = res.get("result", {}).get("content", [])
        texts = [c.get("text", "") for c in content
                 if isinstance(c, dict) and c.get("type") == "text"]
        return "\n".join(t for t in texts if t) or json.dumps(res.get("result", {}))[:4000]


class ToolRouter:
    """Maps the (sanitized) tool name the model sees -> the client + real name."""
    def __init__(self):
        self.byname = {}   # safe_name -> (MCPClient, real_name)

    def add(self, safe, client, real):
        self.byname[safe] = (client, real)

    def call(self, safe, args):
        client, real = self.byname.get(safe, (None, safe))
        if client is None:
            return f"(unknown tool '{safe}')"
        return client.call_tool(real, args)


def _safe_name(orig, seen, prefix=""):
    raw = f"{prefix}_{orig}" if prefix else orig
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", raw)[:64] or "tool"
    base, i = safe, 1
    while safe in seen:
        safe = f"{base[:60]}_{i}"
        i += 1
    seen.add(safe)
    return safe


def _collect(client, tools, router, seen, prefix=""):
    for t in client.list_tools():
        orig = t.get("name")
        if not orig:
            continue
        safe = _safe_name(orig, seen, prefix)
        router.add(safe, client, orig)
        tools.append({"type": "function", "function": {
            "name": safe,
            "description": (t.get("description") or "")[:1024],
            "parameters": t.get("inputSchema") or {"type": "object", "properties": {}},
        }})


def load_tools():
    """Return (openai_tools, ToolRouter) or (None, None)."""
    url = os.getenv("MCP_SERVER_URL", "").strip()
    if not url and os.getenv("PIPEDREAM_CLIENT_ID"):
        url = "https://remote.mcp.pipedream.net/v3"   # Pipedream default endpoint
    if not url:
        return None, None
    slugs = [s.strip() for s in os.getenv("MCP_APP_SLUGS", "").split(",") if s.strip()]
    tools, router, seen = [], ToolRouter(), set()
    try:
        if slugs:  # Pipedream multi-app: one connection per app slug
            for slug in slugs:
                client = MCPClient(url, _base_headers(slug))
                client.connect()
                _collect(client, tools, router, seen, prefix=slug)
        else:      # single server returns its full tool set (Zapier, etc.)
            client = MCPClient(url, _base_headers())
            client.connect()
            _collect(client, tools, router, seen)
    except Exception as e:
        print("! MCP connect/list failed:", e)
        return None, None
    return (tools or None), (router if tools else None)


def handle(resp, router):
    """Execute the model's tool calls against the MCP server(s); return tool messages."""
    out = []
    for tc in (getattr(resp.choices[0].message, "tool_calls", None) or []):
        safe = tc.function.name
        try:
            args = json.loads(tc.function.arguments or "{}")
        except Exception:
            args = {}
        try:
            content = router.call(safe, args)
        except Exception as e:
            content = f"(MCP call failed: {e})"
        out.append({"role": "tool", "tool_call_id": tc.id, "content": content})
    return out
