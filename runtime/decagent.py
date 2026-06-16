#!/usr/bin/env python3
"""
Decagent runtime
================
Loads any agent from the /agents folder, connects the Composio tools it needs,
and runs it against an LLM. One engine runs all ten agents.

Usage:
    python runtime/decagent.py --agent builder
    python runtime/decagent.py --agent scout --message "Research the EV charging market"
    python runtime/decagent.py --list

Environment (see runtime/.env.example):
    ANTHROPIC_API_KEY   your LLM key
    COMPOSIO_API_KEY    your Composio key (provides the tools)

This is intentionally small and readable so you can extend it. The hard parts
(tool calling, auth) are handled by Composio.
"""
from __future__ import annotations
import argparse, json, os, sys, pathlib

try:
    from dotenv import load_dotenv
    load_dotenv(pathlib.Path(__file__).parent / ".env")
    load_dotenv()  # also read a root .env if present
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / "agents"
MODEL = os.getenv("DECAGENT_MODEL", "claude-opus-4-8")
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


def list_agents() -> list[dict]:
    catalog = json.loads((ROOT / "catalog.json").read_text())
    return catalog["agents"]


# --------------------------------------------------------------------------- #
# Composio tools
# --------------------------------------------------------------------------- #
def get_tools(toolkits: list[str]):
    """Return Composio tools for the given toolkit slugs, plus the toolset
    handle used to execute tool calls. Returns (None, None) if Composio is not
    configured, so the agent can still run as a plain chat assistant."""
    if not os.getenv("COMPOSIO_API_KEY"):
        print("! COMPOSIO_API_KEY not set — running without external tools.\n")
        return None, None
    try:
        from composio_claude import ComposioToolSet
    except ImportError:
        print("! composio-claude not installed — running without external tools.")
        print("  Install with: pip install composio-claude\n")
        return None, None

    toolset = ComposioToolSet(api_key=os.getenv("COMPOSIO_API_KEY"))
    apps = [t.upper() for t in toolkits]
    try:
        tools = toolset.get_tools(apps=apps)
    except Exception as e:  # unknown toolkit names, auth issues, etc.
        print(f"! Could not load tools for {apps}: {e}\n  Running without tools.\n")
        return None, None
    return tools, toolset


# --------------------------------------------------------------------------- #
# Run loop
# --------------------------------------------------------------------------- #
def run(agent_id: str, message: str) -> str:
    agent = load_agent(agent_id)
    print(f"\n{agent['emoji']}  {agent['name']} — {agent['tagline']}\n" + "-" * 60)

    try:
        from anthropic import Anthropic
    except ImportError:
        raise SystemExit("Please install the LLM client: pip install anthropic")

    client = Anthropic()  # reads ANTHROPIC_API_KEY
    tools, toolset = get_tools(agent["composio_toolkits"])

    messages = [{"role": "user", "content": message}]
    final_text = ""

    for _ in range(MAX_TURNS):
        kwargs = dict(model=MODEL, max_tokens=4096,
                      system=agent["system_prompt"], messages=messages)
        if tools:
            kwargs["tools"] = tools
        resp = client.messages.create(**kwargs)

        # collect any text the model produced this turn
        for block in resp.content:
            if getattr(block, "type", None) == "text":
                final_text += block.text

        if resp.stop_reason == "tool_use" and toolset:
            # Composio executes the requested tool calls and returns results
            tool_results = toolset.handle_tool_calls(resp)
            messages.append({"role": "assistant", "content": resp.content})
            messages.append({"role": "user", "content": tool_results})
            continue
        break

    print(final_text.strip() or "(no response)")
    return final_text.strip()


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
        print("\nDecagent — 10 plain-language AI agents\n" + "=" * 40)
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
