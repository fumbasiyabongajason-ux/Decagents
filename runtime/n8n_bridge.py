#!/usr/bin/env python3
"""
n8n tool bridge — free, self-hosted tools for Decagent (instead of Composio).
=============================================================================
Each "tool" your agents can use is an n8n workflow exposed as a Webhook node.
You define the tools in runtime/n8n_tools.json (copy n8n_tools.example.json).

Flow when an agent uses a tool:
  agent decides to call e.g. send_email(to, subject, body)
    -> this bridge POSTs those args to your n8n webhook URL
    -> n8n runs the workflow (sends the email via its own Gmail credential)
    -> n8n returns a result, which the agent reads and continues.

Your credentials live INSIDE n8n (not in this app). Self-hosted n8n is free.

Env vars:
  N8N_BASE_URL     prefix for relative webhook paths, e.g. https://n8n.yoursite.com
  N8N_TOOLS_FILE   override path to the tools JSON (default runtime/n8n_tools.json)
  N8N_AUTH_HEADER  optional; sent as the Authorization header to your webhooks
"""
import json, os, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _tools_path() -> str:
    return os.getenv("N8N_TOOLS_FILE", str(ROOT / "runtime" / "n8n_tools.json"))


def load_tools():
    """Return (openai_tools, name->url map), or (None, None) if not configured."""
    path = _tools_path()
    if not os.path.exists(path):
        return None, None
    try:
        defs = json.loads(pathlib.Path(path).read_text())
    except Exception as e:
        print(f"! could not read n8n tools file {path}: {e}")
        return None, None
    base = os.getenv("N8N_BASE_URL", "").rstrip("/")
    single = os.getenv("N8N_WEBHOOK_URL", "").strip()  # ONE router webhook for ALL tools
    tools, wmap = [], {}
    for d in defs:
        name = d["name"]
        if single:                       # all tools flow through one router workflow
            url = single
        else:                            # or one webhook per tool
            wh = d.get("webhook", "")
            url = base + wh if (wh.startswith("/") and base) else wh
        wmap[name] = url
        tools.append({"type": "function", "function": {
            "name": name,
            "description": d.get("description", ""),
            "parameters": d.get("parameters", {"type": "object", "properties": {}}),
        }})
    return (tools or None), (wmap or None)


def execute_one(name, args, wmap):
    """Run a single tool by POSTing {tool, args} to its n8n webhook. Returns a result string."""
    import requests
    headers = {}
    if os.getenv("N8N_AUTH_HEADER"):
        headers["Authorization"] = os.getenv("N8N_AUTH_HEADER")
    url = (wmap or {}).get(name)
    if not url:
        return f"(no n8n webhook configured for tool '{name}')"
    try:
        r = requests.post(url, json={"tool": name, "args": args}, headers=headers, timeout=90)
        return r.text[:6000] if r.text else f"(n8n returned status {r.status_code})"
    except Exception as e:
        return f"(n8n call failed: {e})"


def handle(resp, wmap):
    """Run the tool calls in an OpenAI-style response via n8n webhooks.
    Returns a list of tool-role messages to append to the conversation."""
    import requests  # honors HTTPS_PROXY; pip install requests
    headers = {}
    if os.getenv("N8N_AUTH_HEADER"):
        headers["Authorization"] = os.getenv("N8N_AUTH_HEADER")
    out = []
    for tc in (getattr(resp.choices[0].message, "tool_calls", None) or []):
        name = tc.function.name
        try:
            args = json.loads(tc.function.arguments or "{}")
        except Exception:
            args = {}
        url = (wmap or {}).get(name)
        if not url:
            content = f"(no n8n webhook configured for tool '{name}')"
        else:
            try:
                r = requests.post(url, json={"tool": name, "args": args}, headers=headers, timeout=90)
                content = r.text[:6000] if r.text else f"(n8n returned status {r.status_code})"
            except Exception as e:
                content = f"(n8n call failed: {e})"
        out.append({"role": "tool", "tool_call_id": tc.id, "content": content})
    return out
