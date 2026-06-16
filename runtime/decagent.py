#!/usr/bin/env python3
"""
Decagent runtime — provider-flexible (use a FREE LLM).
=====================================================
Runs any of the 10 agents on whatever model you point it at:
  • Google Gemini   — best free tier (no card needed)   aistudio.google.com
  • Groq            — free + very fast (Llama etc.)      console.groq.com
  • OpenRouter      — many free models, one key          openrouter.ai
  • OpenAI / local / Anthropic — also supported

How the provider is chosen (see runtime/.env.example):
  OpenAI-compatible (covers Gemini, Groq, OpenRouter, OpenAI, local Ollama):
      LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
  Anthropic (Claude):
      ANTHROPIC_API_KEY, DECAGENT_MODEL
If the LLM_* vars are set, they win; otherwise Anthropic; otherwise it explains how to set one.

Composio (COMPOSIO_API_KEY) gives the agents their tools. Without it, agents still
run as plain chat assistants.

Usage:
    python runtime/decagent.py --list
    python runtime/decagent.py --agent scout -m "Research the EV market"
"""
from __future__ import annotations
import argparse, json, os, pathlib

try:
    from dotenv import load_dotenv
    load_dotenv(pathlib.Path(__file__).parent / ".env")
    load_dotenv()
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / "agents"
MAX_TURNS = int(os.getenv("DECAGENT_MAX_TURNS", "12"))


# --------------------------------------------------------------------------- #
# Loading agents
# --------------------------------------------------------------------------- #
def find_agent_dir(agent_id: str) -> pathlib.Path:
    for d in sorted(AGENTS_DIR.iterdir()):
        if d.is_dir() and d.name.split("-", 1)[-1] == agent_id:
            return d
    raise SystemExit(f"Unknown agent '{agent_id}'. Run with --list to see all agents.")


def load_agent(agent_id: str) -> dict:
    d = find_agent_dir(agent_id)
    manifest = json.loads((d / "agent.json").read_text())
    manifest["system_prompt"] = (d / manifest["system_prompt_file"]).read_text()
    manifest["_dir"] = str(d)
    return manifest


def list_agents() -> list:
    return json.loads((ROOT / "catalog.json").read_text())["agents"]


# --------------------------------------------------------------------------- #
# Which LLM provider?  (set by env vars — point this at a FREE provider)
# --------------------------------------------------------------------------- #
def provider_config() -> dict:
    key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if key:  # OpenAI-compatible: Gemini, Groq, OpenRouter, OpenAI, local…
        return {"kind": "openai", "key": key,
                "base_url": os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
                "model": os.getenv("LLM_MODEL", "gpt-4o-mini")}
    if os.getenv("ANTHROPIC_API_KEY"):
        return {"kind": "anthropic", "key": os.getenv("ANTHROPIC_API_KEY"),
                "base_url": None, "model": os.getenv("DECAGENT_MODEL", "claude-opus-4-8")}
    return {"kind": None}


NO_PROVIDER_MSG = (
    "No LLM provider is configured yet. Add a FREE one to your .env:\n\n"
    "  LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/\n"
    "  LLM_API_KEY=<your free Google AI Studio key>\n"
    "  LLM_MODEL=gemini-2.0-flash\n\n"
    "Get the free key at https://aistudio.google.com  (no card needed). "
    "Groq and OpenRouter work too — see runtime/.env.example."
)


# --------------------------------------------------------------------------- #
# Tools (Composio) — provider-specific formatting
# --------------------------------------------------------------------------- #
def _openai_tools(toolkits: list):
    if not os.getenv("COMPOSIO_API_KEY"):
        return None, None
    try:
        from composio_openai import ComposioToolSet
    except ImportError:
        print("! composio-openai not installed — running without tools (pip install composio-openai)")
        return None, None
    ts = ComposioToolSet(api_key=os.getenv("COMPOSIO_API_KEY"))
    try:
        return ts.get_tools(apps=[t.upper() for t in toolkits]), ts
    except Exception as e:
        print(f"! could not load tools {toolkits}: {e}")
        return None, None


def _anthropic_tools(toolkits: list):
    if not os.getenv("COMPOSIO_API_KEY"):
        return None, None
    try:
        from composio_claude import ComposioToolSet
    except ImportError:
        print("! composio-claude not installed — running without tools (pip install composio-claude)")
        return None, None
    ts = ComposioToolSet(api_key=os.getenv("COMPOSIO_API_KEY"))
    try:
        return ts.get_tools(apps=[t.upper() for t in toolkits]), ts
    except Exception as e:
        print(f"! could not load tools {toolkits}: {e}")
        return None, None


# --------------------------------------------------------------------------- #
# Run loops
# --------------------------------------------------------------------------- #
def _history_msgs(history):
    out = []
    for h in (history or []):
        if h.get("role") in ("user", "assistant") and h.get("content"):
            out.append({"role": h["role"], "content": h["content"]})
    return out


def _run_openai(agent, message, history, cfg):
    try:
        from openai import OpenAI
    except ImportError:
        return "The OpenAI client isn't installed. Run:  pip install openai"
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["key"])
    tools, ts = _openai_tools(agent["composio_toolkits"])

    messages = [{"role": "system", "content": agent["system_prompt"]}]
    messages += _history_msgs(history)
    messages.append({"role": "user", "content": message})

    final_text = ""
    for _ in range(MAX_TURNS):
        kwargs = {"model": cfg["model"], "messages": messages}
        if tools:
            kwargs["tools"] = tools
        try:
            resp = client.chat.completions.create(**kwargs)
        except Exception as e:
            if tools:  # some free models reject tool schemas — fall back to plain chat
                tools = ts = None
                resp = client.chat.completions.create(model=cfg["model"], messages=messages)
            else:
                raise
        m = resp.choices[0].message
        if getattr(m, "tool_calls", None) and ts:
            messages.append(m.model_dump(exclude_none=True))
            messages.extend(ts.handle_tool_calls(resp))
            continue
        final_text = m.content or ""
        break
    return (final_text or "").strip()


def _run_anthropic(agent, message, history, cfg):
    try:
        from anthropic import Anthropic
    except ImportError:
        return "The Anthropic client isn't installed. Run:  pip install anthropic"
    client = Anthropic(api_key=cfg["key"])
    tools, ts = _anthropic_tools(agent["composio_toolkits"])

    messages = _history_msgs(history)
    messages.append({"role": "user", "content": message})

    final_text = ""
    for _ in range(MAX_TURNS):
        kwargs = dict(model=cfg["model"], max_tokens=4096,
                      system=agent["system_prompt"], messages=messages)
        if tools:
            kwargs["tools"] = tools
        resp = client.messages.create(**kwargs)
        for block in resp.content:
            if getattr(block, "type", None) == "text":
                final_text += block.text
        if resp.stop_reason == "tool_use" and ts:
            messages.append({"role": "assistant", "content": resp.content})
            messages.append({"role": "user", "content": ts.handle_tool_calls(resp)})
            continue
        break
    return final_text.strip()


def run(agent_id: str, message: str, history: list | None = None,
        verbose: bool = True) -> str:
    """Run one agent on a message. `history` is optional prior [{role, content}] turns."""
    agent = load_agent(agent_id)
    if verbose:
        print(f"\n{agent['emoji']}  {agent['name']} — {agent['tagline']}\n" + "-" * 60)
    cfg = provider_config()
    if cfg["kind"] == "openai":
        text = _run_openai(agent, message, history, cfg)
    elif cfg["kind"] == "anthropic":
        text = _run_anthropic(agent, message, history, cfg)
    else:
        text = NO_PROVIDER_MSG
    if verbose:
        print(text or "(no response)")
    return text


def _complete_text(system: str, user: str, max_tokens: int = 16) -> str:
    """Tiny one-shot completion used by the router. Uses the active provider."""
    cfg = provider_config()
    if cfg["kind"] == "openai":
        from openai import OpenAI
        c = OpenAI(base_url=cfg["base_url"], api_key=cfg["key"])
        r = c.chat.completions.create(model=cfg["model"], max_tokens=max_tokens,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
        return r.choices[0].message.content or ""
    if cfg["kind"] == "anthropic":
        from anthropic import Anthropic
        c = Anthropic(api_key=cfg["key"])
        r = c.messages.create(model=cfg["model"], max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": user}])
        return "".join(getattr(b, "text", "") for b in r.content)
    return ""


def route(message: str) -> str:
    """Pick the best agent id for a message (the Console's 'Auto' mode)."""
    agents = [a for a in list_agents() if a["id"] != "auto"]
    ids = [a["id"] for a in agents]
    menu = "\n".join(f"- {a['id']}: {a['tagline']}" for a in agents)
    try:
        txt = _complete_text(
            "You are a router for a team of AI agents. Reply with ONLY the single best agent id.",
            f"Agents:\n{menu}\n\nRequest: {message}\n\nBest agent id:", 16).strip().lower()
    except Exception:
        return ids[0]
    for i in ids:
        if i in txt:
            return i
    return ids[0]


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main():
    p = argparse.ArgumentParser(description="Run a Decagent agent in plain language.")
    p.add_argument("--agent", help="agent id, e.g. builder, scout, outreach")
    p.add_argument("--message", "-m", help="what you want the agent to do")
    p.add_argument("--list", action="store_true", help="list all agents")
    args = p.parse_args()

    if args.list or not args.agent:
        cfg = provider_config()
        prov = cfg["kind"] or "none — set a free provider (see .env.example)"
        print("\nDecagent — 10 plain-language AI agents")
        print("provider:", prov, "| model:", cfg.get("model", "—"))
        print("=" * 44)
        for a in list_agents():
            print(f"  {a['emoji']}  {a['id']:11} {a['tier']:8} {a['tagline']}")
        print("\nRun one:  python runtime/decagent.py --agent <id> -m \"your request\"\n")
        return

    message = args.message
    if not message:
        try:
            message = input("What do you want this agent to do?\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            return
    if message:
        run(args.agent, message)


if __name__ == "__main__":
    main()
