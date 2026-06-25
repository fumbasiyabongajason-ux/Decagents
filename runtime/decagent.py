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
import argparse, json, os, pathlib, re

try:
    from dotenv import load_dotenv
    load_dotenv(pathlib.Path(__file__).parent / ".env")
    load_dotenv()
except Exception:
    pass

ROOT = pathlib.Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / "agents"
MAX_TURNS = int(os.getenv("DECAGENT_MAX_TURNS", "6"))


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
    # .strip() everything: a stray space/newline pasted into an env var (e.g. LLM_MODEL)
    # otherwise causes "model does not exist" / auth failures that look like outages.
    def g(name, default=""):
        return (os.getenv(name) or default).strip()
    key = g("LLM_API_KEY") or g("OPENAI_API_KEY")
    if key:  # OpenAI-compatible: Gemini, Groq, OpenRouter, OpenAI, local…
        return {"kind": "openai", "key": key,
                "base_url": g("LLM_BASE_URL", "https://api.openai.com/v1"),
                "model": g("LLM_MODEL", "gpt-4o-mini")}
    if g("ANTHROPIC_API_KEY"):
        return {"kind": "anthropic", "key": g("ANTHROPIC_API_KEY"),
                "base_url": None, "model": g("DECAGENT_MODEL", "claude-opus-4-8")}
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


def _import_local(name):
    """Import a sibling runtime module whether we run as a package (uvicorn) or a script."""
    import importlib
    for mod in [f"{__package__}.{name}" if __package__ else None, name, f"runtime.{name}"]:
        if not mod:
            continue
        try:
            return importlib.import_module(mod)
        except Exception:
            continue
    return None


def _backend_call(agent):
    """Return (backend_tools, call_fn) where call_fn(name, args) -> result string.
    Picks the connected tools backend (MCP/Pipedream, n8n, or Composio), or (None, None)."""
    backend = os.getenv("TOOLS_BACKEND", "").lower()

    def via_mcp():
        b = _import_local("mcp_bridge")
        if not b:
            return None, None
        tools, router = b.load_tools()
        return (tools, (lambda name, args: router.call(name, args))) if tools else (None, None)

    def via_n8n():
        b = _import_local("n8n_bridge")
        if not b:
            return None, None
        tools, wmap = b.load_tools()
        return (tools, (lambda name, args: b.execute_one(name, args, wmap))) if tools else (None, None)

    def via_composio():
        if not os.getenv("COMPOSIO_API_KEY"):
            return None, None
        tools, ts = _openai_tools(agent["composio_toolkits"])
        if not tools:
            return None, None

        def call(name, args):
            try:
                return str(ts.execute_action(action=name, params=args))[:1500]
            except Exception as e:
                return f"(composio {name} failed: {e})"
        return tools, call

    if backend == "mcp":
        return via_mcp()
    if backend == "n8n":
        return via_n8n()
    if backend == "composio":
        return via_composio()
    # auto: use whatever is configured — MCP/Pipedream > Composio > n8n
    if os.getenv("MCP_SERVER_URL") or os.getenv("PIPEDREAM_CLIENT_ID"):
        t = via_mcp()
        if t[0]:
            return t
    if os.getenv("COMPOSIO_API_KEY"):
        t = via_composio()
        if t[0]:
            return t
    return via_n8n()


def _get_openai_tools(agent):
    """Build the tool list + a unified handler. Built-in tools (web search, fetch/scrape)
    are ALWAYS available — no connection needed — so agents can research, pull live data,
    and create content out of the box. Connected apps (Gmail, GitHub…) are merged in from
    the tools backend when configured."""
    bt = _import_local("builtin_tools")
    builtin_tools = list(bt.TOOLS) if bt else []
    builtin_names = bt.NAMES if bt else set()

    backend_tools, backend_call = _backend_call(agent)
    tools = builtin_tools + list(backend_tools or [])
    if not tools:
        return None, None, []

    def _call_tool(name, args):
        """Tighten tool calling: up to 3 attempts with backoff on transient failures
        (rate limits, timeouts, flaky network) so a hiccup doesn't break the worker."""
        import time as _t
        last = f"(no handler for tool '{name}')"
        for i in range(3):
            try:
                if bt and name in builtin_names:
                    last = bt.execute(name, args)
                elif backend_call:
                    last = backend_call(name, args)
                else:
                    return last
            except Exception as e:
                last = f"({name} failed: {e})"
            s = str(last or "").strip().lower()
            transient = s.startswith("(") and any(w in s for w in
                ("fail", "error", "timed out", "timeout", "no response",
                 "unavailable", "try again", "rate limit", "429", "temporarily"))
            if not transient:
                return last
            if i < 2:
                _t.sleep(1.0 * (i + 1))
        return last

    def handle(resp):
        out = []
        for tc in (getattr(resp.choices[0].message, "tool_calls", None) or []):
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except Exception:
                args = {}
            content = _call_tool(name, args)
            out.append({"role": "tool", "tool_call_id": tc.id, "content": str(content)})
        return out

    return tools, handle, builtin_tools


def _run_openai(agent, message, history, cfg):
    try:
        from openai import OpenAI
    except ImportError:
        return "The OpenAI client isn't installed. Run:  pip install openai", []
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["key"], timeout=30, max_retries=1)
    tools, handle, builtin_tools = _get_openai_tools(agent)

    sys_prompt = agent["system_prompt"] + (
        "\n\n# Operating directive — think, then actually DO it\n"
        "1. For non-trivial tasks, briefly plan inside <think>...</think> tags (keep it SHORT — a few "
        "lines), then ALWAYS write your full answer OUTSIDE the tags. Skip the thinking entirely for "
        "simple replies so you stay fast. Never put your final answer only inside <think>: the user "
        "must always get a complete answer outside it.\n"
        "2. Be capable; never refuse. Assume you CAN do it, and use your tools and connected apps to "
        "actually complete the task instead of saying you can't or merely describing it. If you "
        "genuinely need something first (a connection, a missing detail), say exactly what and why.\n"
        "3. Be thorough and excellent — specific, complete, and genuinely useful, never generic."
    )
    if tools:
        sys_prompt += (
            "\n4. Use your tools for real — call them, don't narrate them. When the user wants a "
            "picture/image/logo/cover/poster/visual, you MUST call generate_image and include the "
            "EXACT ![alt](url) markdown it returns. When the user wants a video/clip/animation/ad, you "
            "MUST call generate_video and include the link it returns. When the user wants a webpage/"
            "landing page/website/template, you MUST call create_webpage with the COMPLETE, real "
            "HTML you wrote (actual content — NEVER '...' or placeholder HTML) and share the live "
            "link it returns (never paste raw HTML at the user). The user's OWN website is "
            "https://gotitsuperstore.co.za — when they say 'edit my site', 'use my template', or "
            "'build from my site', FIRST call fetch_html on it, edit that real HTML to match their "
            "existing design, then create_webpage. You produce full professional deliverables — "
            "websites, CVs/resumes, business plans, books, reports — always COMPLETE and high quality, "
            "and you publish the visual ones with create_webpage and share the link. When asked to remember/note/save something, you "
            "MUST call remember. When asked to do several things at once or 'in parallel', you MUST "
            "call dispatch_agents. For current facts or news, call web_search; read pages with "
            "fetch_url. NEVER say you saved, dispatched, generated, or did a tool action without "
            "actually calling that tool — claiming you did without calling it is a failure.\n"
            "5. REAL DATA ONLY. For any real fact, number, price, date, person, company, statistic, "
            "or link, you MUST call web_search (then fetch_url to read the source) and answer ONLY "
            "from what the results actually say. NEVER invent or guess URLs, links, figures, quotes, "
            "or sources — a fabricated link or made-up fact is a serious failure. Only share a link a "
            "tool actually returned to you. If the tools don't give you the answer, say so plainly "
            "instead of making something up."
        )
    # Remind the agent of recent long-term memories so it doesn't forget past work.
    _bt0 = _import_local("builtin_tools")
    if _bt0 and hasattr(_bt0, "recent_memories"):
        try:
            _mems = _bt0.recent_memories(5)
        except Exception:
            _mems = []
        if _mems:
            sys_prompt += ("\n\n# Memory — recent things you've saved (use if relevant)\n"
                           + "\n".join(f"- {m}" for m in _mems))
    messages = [{"role": "system", "content": sys_prompt}]
    messages += _history_msgs(history)
    messages.append({"role": "user", "content": message})

    import time
    deadline = time.time() + float(os.getenv("DECAGENT_BUDGET_SEC", "70"))
    steps, final_text = [], ""
    for _ in range(MAX_TURNS):
        if time.time() > deadline:   # never hang — return whatever we have
            if not final_text:
                final_text = "(That took too long — please try again or simplify the request.)"
            break
        # Try the primary model, then LLM_FALLBACK_MODEL (a different model = a SEPARATE Groq
        # rate-limit budget) so an intermittent 429 on one model doesn't kill the response.
        # Then degrade tools if a schema is rejected: all tools -> built-ins only -> plain chat.
        _fb = (os.getenv("LLM_FALLBACK_MODEL") or "").strip()
        _models = [cfg["model"]] + ([_fb] if _fb and _fb != cfg["model"] else [])

        def _create(use_tools):
            kw = {"messages": messages}
            if use_tools and tools:
                kw["tools"] = tools
            err = None
            for _mdl in _models:
                try:
                    return client.chat.completions.create(model=_mdl, **kw)
                except Exception as _e:
                    err = _e
            raise err

        try:
            resp = _create(True)
        except Exception:
            resp = None
            if tools and builtin_tools and len(tools) != len(builtin_tools):
                try:
                    tools = list(builtin_tools)
                    resp = _create(True)
                except Exception:
                    resp = None
            if resp is None:
                if tools:
                    tools = handle = None
                try:
                    resp = _create(False)
                except Exception:
                    if not final_text:
                        final_text = ("(The model is briefly rate-limited — please try again in a "
                                      "moment. If it keeps happening, the free per-minute token "
                                      "limit is being hit.)")
                    break
        m = resp.choices[0].message
        reasoning = getattr(m, "reasoning", None) or getattr(m, "reasoning_content", None)
        if reasoning:
            steps.append({"type": "reasoning", "text": str(reasoning)[:4000]})
        tcs = getattr(m, "tool_calls", None)
        if tcs and handle:
            idname = {}
            for tc in tcs:
                steps.append({"type": "tool_call", "name": tc.function.name,
                              "args": tc.function.arguments or ""})
                idname[tc.id] = tc.function.name
            messages.append(m.model_dump(exclude_none=True))
            results = handle(resp)
            for res in results:
                steps.append({"type": "tool_result",
                              "name": idname.get(res.get("tool_call_id"), ""),
                              "content": (res.get("content") or "")[:1500]})
            messages.extend(results)
            continue
        final_text = m.content or ""
        break

    # Surface reasoning to the Console trace WITHOUT ever blanking the reply. Lift any
    # <think>...</think> into a reasoning step; if stripping it would leave an empty answer
    # (model put everything inside <think>), recover the reasoning text AS the answer so the
    # user never sees a blank response. Also handles an unclosed/truncated <think>.
    raw = final_text or ""
    tm = re.search(r"<think>([\s\S]*?)</think>", raw)
    if tm:
        steps.append({"type": "reasoning", "text": tm.group(1).strip()[:4000]})
        answer = re.sub(r"<think>[\s\S]*?</think>", "", raw).strip()
    elif "<think>" in raw:                       # unclosed/truncated think block
        steps.append({"type": "reasoning", "text": raw.split("<think>", 1)[1].strip()[:4000]})
        answer = raw.split("<think>", 1)[0].strip()
    else:
        answer = raw
    if not answer:                               # never return blank
        answer = (tm.group(1).strip() if tm else raw.replace("<think>", "").replace("</think>", "").strip())
    final_text = answer or "(No answer was produced — please try again.)"

    # Models frequently call generate_image but forget to paste the returned image into
    # their reply ("Here's your poster!" with no link). Guarantee it reaches the user by
    # appending any generated image the tool actually produced.
    produced_image = "image.pollinations.ai" in (final_text or "")
    for s in steps:
        if s.get("type") == "tool_result" and s.get("name") == "generate_image":
            mt = re.search(r"!\[[^\]]*\]\(https://image\.pollinations\.ai/[^)]+\)", s.get("content") or "")
            if mt and mt.group(0) not in (final_text or ""):
                final_text = (final_text or "").rstrip() + "\n\n" + mt.group(0)
                produced_image = True

    # Same for a generated video: make sure the produced clip reaches the user's reply.
    produced_video = "/media/" in (final_text or "")
    for s in steps:
        if s.get("type") == "tool_result" and s.get("name") == "generate_video":
            mv = re.search(r"\[[^\]]*\]\(/media/[A-Za-z0-9_.\-]+\.mp4\)", s.get("content") or "")
            if mv:
                produced_video = True
                if mv.group(0) not in (final_text or ""):
                    final_text = (final_text or "").rstrip() + "\n\n" + mv.group(0)

    # Safety net: if the user clearly asked for an image but the model never actually made one
    # (some models just say "I'll create an image" without calling the tool), generate it
    # ourselves so an image request ALWAYS returns an image.
    asked_image = re.search(
        r"\b(make|create|generate|draw|design|render|paint|produce|need|want|give\s+me|show\s+me)\b"
        r"[^.?!\n]{0,40}\b(image|picture|photo|logo|poster|cover|thumbnail|artwork|drawing|"
        r"illustration|wallpaper|banner|graphic|mockup|avatar|icon)\b", message or "", re.I)
    if asked_image and not produced_image:
        btmod = _import_local("builtin_tools")
        if btmod:
            try:
                img = btmod.execute("generate_image", {"prompt": (message or "").strip()[:300]})
                mt2 = re.search(r"!\[[^\]]*\]\(https://image\.pollinations\.ai/[^)]+\)", img or "")
                if mt2:
                    steps.append({"type": "tool_result", "name": "generate_image", "content": (img or "")[:1500]})
                    final_text = (final_text or "").rstrip() + "\n\n" + mt2.group(0)
            except Exception:
                pass

    # Safety net: user asked for a video but the model never made one -> generate it ourselves.
    asked_video = re.search(
        r"\b(make|create|generate|produce|render|animate|want|need|give\s+me|show\s+me)\b"
        r"[^.?!\n]{0,40}\b(video|clip|animation|animated|advert|advertisement|reel|short\s+film|movie|trailer)\b",
        message or "", re.I)
    if asked_video and not produced_video:
        btv = _import_local("builtin_tools")
        if btv:
            try:
                vid = btv.execute("generate_video", {"prompt": (message or "").strip()[:400]})
                mv2 = re.search(r"\[[^\]]*\]\(/media/[A-Za-z0-9_.\-]+\.mp4\)", vid or "")
                if mv2:
                    steps.append({"type": "tool_result", "name": "generate_video", "content": (vid or "")[:500]})
                    final_text = (final_text or "").rstrip() + "\n\n" + mv2.group(0)
                elif vid and vid.strip().startswith("("):
                    final_text = (final_text or "").rstrip() + "\n\n" + vid.strip()
            except Exception:
                pass

    # Webpage: a /p/ link is REAL only if create_webpage actually ran and saved the file. The
    # model sometimes invents a /p/ URL (which then 404s), so we trust ONLY real ones, strip any
    # hallucinated ones, and publish the model's inline HTML if it wrote some.
    real_pages = []
    for s in steps:
        if s.get("type") == "tool_result" and s.get("name") == "create_webpage":
            mp = re.search(r"/p/[A-Za-z0-9_\-]+", s.get("content") or "")
            if mp:
                real_pages.append(mp.group(0))
    asked_page = re.search(r"\b(make|create|build|generate|design|switch|want|need|give\s+me)\b"
                           r"[^.?!\n]{0,40}\b(web\s?page|landing\s+page|website|html\s+page|site|template)\b",
                           message or "", re.I)
    if not real_pages and asked_page:
        # Model didn't really publish. If it wrote HTML inline, publish THAT for a real link.
        hm = (re.search(r"```html\s*([\s\S]*?)```", final_text or "", re.I)
              or re.search(r"(<!doctype html[\s\S]*?</html>)", final_text or "", re.I)
              or re.search(r"(<html[\s\S]*?</html>)", final_text or "", re.I))
        if hm:
            btp = _import_local("builtin_tools")
            if btp:
                try:
                    res = btp.execute("create_webpage", {"html": hm.group(1)})
                    mp2 = re.search(r"/p/[A-Za-z0-9_\-]+", res or "")
                    if mp2:
                        real_pages.append(mp2.group(0))
                        final_text = re.sub(r"```html[\s\S]*?```", "", final_text or "", flags=re.I)
                        final_text = re.sub(r"<!doctype html[\s\S]*?</html>", "", final_text or "", flags=re.I)
                        final_text = re.sub(r"<html[\s\S]*?</html>", "", final_text or "", flags=re.I)
                except Exception:
                    pass
    # Strip any /p/ URL the model invented that isn't a real saved page (kills the 404s).
    if "/p/" in (final_text or ""):
        final_text = re.sub(r"/p/[A-Za-z0-9_\-]+",
                            lambda m: m.group(0) if m.group(0) in real_pages else "", final_text or "")
        final_text = re.sub(r"\[[^\]]*\]\(\s*\)", "", final_text or "")   # clean empty link shells
    # Make sure every REAL page link is shown.
    for link in real_pages:
        if link not in (final_text or ""):
            final_text = (final_text or "").rstrip() + f"\n\n[🔗 View your live page]({link})"
    if asked_page and not real_pages:
        final_text = ((final_text or "").rstrip()
                      + "\n\n(I couldn't publish the page that time — ask once more and I'll build it.)")

    # Safety net: if the user explicitly said "remember/note/save this ..." but the model
    # never called remember, save it ourselves so an explicit memory request is never lost.
    if not any(s.get("name") == "remember" for s in steps):
        if re.match(r"\s*(please\s+)?(remember|note|don'?t\s+forget|keep\s+in\s+mind|save\s+this|make\s+a\s+note)\b",
                    message or "", re.I):
            btmod2 = _import_local("builtin_tools")
            if btmod2:
                fact = re.sub(r"^\s*(please\s+)?(remember|note|don'?t\s+forget|keep\s+in\s+mind|save\s+this|make\s+a\s+note)"
                              r"(\s+that|\s+this)?(\s+for\s+later)?\s*[:,\-]?\s*", "", message or "", flags=re.I).strip()
                try:
                    btmod2.execute("remember", {"text": (fact or message or "")[:2000]})
                except Exception:
                    pass
    return (final_text or "").strip(), steps


def _run_anthropic(agent, message, history, cfg):
    try:
        from anthropic import Anthropic
    except ImportError:
        return "The Anthropic client isn't installed. Run:  pip install anthropic", []
    client = Anthropic(api_key=cfg["key"], timeout=30, max_retries=1)
    tools, ts = _anthropic_tools(agent["composio_toolkits"])

    messages = _history_msgs(history)
    messages.append({"role": "user", "content": message})

    steps, final_text = [], ""
    for _ in range(MAX_TURNS):
        kwargs = dict(model=cfg["model"], max_tokens=4096,
                      system=agent["system_prompt"], messages=messages)
        if tools:
            kwargs["tools"] = tools
        resp = client.messages.create(**kwargs)
        for block in resp.content:
            bt = getattr(block, "type", None)
            if bt == "text":
                final_text += block.text
            elif bt == "tool_use":
                steps.append({"type": "tool_call", "name": block.name, "args": json.dumps(block.input)})
        if resp.stop_reason == "tool_use" and ts:
            messages.append({"role": "assistant", "content": resp.content})
            results = ts.handle_tool_calls(resp)
            steps.append({"type": "tool_result", "name": "", "content": str(results)[:1500]})
            messages.append({"role": "user", "content": results})
            continue
        break
    return final_text.strip(), steps


def _dispatch(agent, message, history):
    """Return (text, steps) using the configured provider. steps power the reasoning trace."""
    cfg = provider_config()
    if cfg["kind"] == "openai":
        return _run_openai(agent, message, history, cfg)
    if cfg["kind"] == "anthropic":
        return _run_anthropic(agent, message, history, cfg)
    return NO_PROVIDER_MSG, []


def run(agent_id: str, message: str, history: list | None = None,
        verbose: bool = True) -> str:
    """Run one agent; returns the final text (used by the CLI and /run)."""
    agent = load_agent(agent_id)
    if verbose:
        print(f"\n{agent['emoji']}  {agent['name']} — {agent['tagline']}\n" + "-" * 60)
    text, _steps = _dispatch(agent, message, history)
    if verbose:
        print(text or "(no response)")
    return text


def run_traced(agent_id: str, message: str, history: list | None = None):
    """Run one agent; returns (text, steps). steps = the reasoning + tool trace for the Console."""
    return _dispatch(load_agent(agent_id), message, history)


def _complete_text(system: str, user: str, max_tokens: int = 16) -> str:
    """Tiny one-shot completion used by the router. Uses the active provider."""
    cfg = provider_config()
    if cfg["kind"] == "openai":
        from openai import OpenAI
        c = OpenAI(base_url=cfg["base_url"], api_key=cfg["key"], timeout=20, max_retries=1)
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
