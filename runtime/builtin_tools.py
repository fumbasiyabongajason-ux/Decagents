#!/usr/bin/env python3
"""
Built-in tools — ALWAYS available to every agent, no connection or OAuth needed.
These cover the "auto" capabilities so agents can research, pull live data in real time,
and create content/templates out of the box:
  • web_search  — search the web (keyless, via DuckDuckGo HTML)
  • fetch_url   — fetch/scrape a page's readable text (keyless)

Apps that need YOUR login (Gmail, GitHub, Slack…) come from the connected tools backend
(Pipedream/MCP) instead — those are the only ones shown on the /connect page.
"""
import os, re


def _web_search(query, max_results=6):
    import requests
    # Preferred: Tavily — reliable from cloud servers, free tier (set TAVILY_API_KEY)
    tav = os.getenv("TAVILY_API_KEY")
    if tav:
        try:
            r = requests.post("https://api.tavily.com/search",
                              json={"api_key": tav, "query": query, "max_results": max_results},
                              timeout=15)
            res = r.json().get("results", [])
            items = [f"- {x.get('title','')}\n  {x.get('url','')}\n  {(x.get('content') or '')[:160]}"
                     for x in res]
            if items:
                return "\n".join(items)
        except Exception:
            pass
    # Fallback: keyless DuckDuckGo (can be rate-limited from datacenter IPs) — fast-fail
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Decagent/1.0)"}
    for ep in ("https://html.duckduckgo.com/html/", "https://lite.duckduckgo.com/lite/"):
        try:
            r = requests.post(ep, data={"q": query}, headers=headers, timeout=8)
        except Exception:
            continue
        items = []
        for m in re.finditer(r'(?:result__a|result-link)[^>]*href="([^"]+)"[^>]*>([^<]{0,300})</a>', r.text):
            url = m.group(1)
            title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            if title:
                items.append(f"- {title}\n  {url}")
            if len(items) >= max_results:
                break
        if items:
            return "\n".join(items)
    return "(no results — for reliable cloud search, set a free TAVILY_API_KEY)"


def _ssrf_ok(url):
    """Block obviously-internal targets (localhost, private/reserved IP literals, cloud-metadata,
    *.local / *.internal) WITHOUT resolving DNS — so it works in proxied environments and never
    false-blocks a normal public website."""
    import ipaddress
    from urllib.parse import urlparse
    host = (urlparse(url).hostname or "").strip("[]").lower()
    if not host:
        return False
    if host == "localhost" or host.endswith(".local") or host.endswith(".internal") or "metadata" in host:
        return False
    try:
        ip = ipaddress.ip_address(host)   # host is a raw IP literal
        return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
                    or ip.is_multicast or ip.is_unspecified)
    except ValueError:
        return True   # ordinary hostname -> allow (requests/proxy resolves it)


def _fetch_url(url, max_chars=6000):
    import requests
    if not re.match(r"^https?://", url or ""):
        url = "https://" + (url or "")
    if not _ssrf_ok(url):
        return "(blocked: that URL points to a private/internal address)"
    # Stream with a hard byte cap so a huge/endless page can't exhaust memory.
    try:
        with requests.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; Decagent/1.0)"},
                          timeout=15, stream=True) as r:
            chunks, total = [], 0
            for chunk in r.iter_content(chunk_size=65536):
                if not chunk:
                    continue
                chunks.append(chunk)
                total += len(chunk)
                if total >= 2_000_000:   # ~2MB
                    break
            raw = b"".join(chunks).decode(r.encoding or "utf-8", "replace")
    except Exception as e:
        return f"(could not fetch page: {e})"
    html = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", raw, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars] or "(no readable text on page)"


def _fetch_html(url, max_chars=30000):
    """Fetch the RAW HTML of a page so an agent can use it as a TEMPLATE to edit/rebuild.
    SSRF-guarded + size-capped. After editing, the agent publishes via create_webpage."""
    import requests
    u = (url or "").strip()
    if not re.match(r"^https?://", u):
        u = "https://" + u
    if not _ssrf_ok(u):
        return "(blocked: that URL points to a private/internal address)"
    try:
        with requests.get(u, headers={"User-Agent": "Mozilla/5.0 (compatible; Decagent/1.0)"},
                          timeout=20, stream=True) as r:
            chunks, total = [], 0
            for chunk in r.iter_content(chunk_size=65536):
                if not chunk:
                    continue
                chunks.append(chunk)
                total += len(chunk)
                if total >= 800000:
                    break
            raw = b"".join(chunks).decode(r.encoding or "utf-8", "replace")
    except Exception as e:
        return f"(could not fetch page: {e})"
    if len(raw) > max_chars:
        raw = raw[:max_chars] + "\n<!-- ...truncated: you have enough of the template's structure & styling to rebuild/edit -->"
    return raw


def _generate_image(prompt, width=1024, height=1024):
    """Text-to-image, keyless & free via Pollinations. Returns a markdown image
    that the agent should include verbatim so the Console renders it inline."""
    import urllib.parse
    p = (prompt or "").strip()
    if not p:
        return "(no prompt given for image)"
    try:
        width = max(256, min(int(width), 1536))
        height = max(256, min(int(height), 1536))
    except Exception:
        width, height = 1024, 1024
    q = urllib.parse.quote(p, safe="")
    url = (f"https://image.pollinations.ai/prompt/{q}"
           f"?width={width}&height={height}&nologo=true")
    return f"![{p}]({url})\n\n[Open image in new tab]({url})"


def _gemini_key():
    """Tolerant lookup: find a Gemini/Google key even if the env var NAME got duplicated or
    typo'd (e.g. GEMINI_API_KEYGEMINI_API_KEY) — so a paste mistake doesn't block video."""
    for k, v in os.environ.items():
        ku = k.upper()
        if v and v.strip() and ("GEMINI" in ku or ku in ("GOOGLE_API_KEY", "GOOGLE_GENAI_API_KEY")):
            return v.strip()
    return ""


def _create_webpage(html, title=""):
    """Publish HTML to a live URL on THIS site (/p/{id}) and return a markdown link.
    No GitHub, no 404 — the page is saved and served by the app."""
    import uuid
    h = (html or "").strip()
    m = re.search(r"```(?:html)?\s*([\s\S]*?)```", h)   # unwrap a ```html fenced block if present
    if m and "<" in m.group(1):
        h = m.group(1).strip()
    if "<" not in h:
        return "(no HTML provided for the page)"
    # Reject placeholder/empty HTML so we never publish a blank page.
    visible = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h)).strip()
    if (len(visible) < 40 or "represent the actual" in h.lower()
            or "your html here" in h.lower() or "...</html>" in h.lower()):
        return ("(that looked like placeholder HTML, not a finished page — write the COMPLETE "
                "HTML with real content, then call create_webpage again)")
    if "<html" not in h.lower():
        h = ("<!doctype html><html><head><meta charset='utf-8'>"
             "<meta name='viewport' content='width=device-width,initial-scale=1'>"
             f"<title>{(title or 'Page')[:80]}</title></head><body>{h}</body></html>")
    pages_dir = os.getenv("DECAGENT_PAGES_DIR", "/tmp/dgpages")
    try:
        os.makedirs(pages_dir, exist_ok=True)
        pid = uuid.uuid4().hex[:12]
        with open(os.path.join(pages_dir, pid + ".html"), "w", encoding="utf-8") as f:
            f.write(h)
    except Exception as e:
        return f"(could not publish the page: {e})"
    return f"[🔗 View your live page](/p/{pid})"


def _generate_video(prompt):
    """Text-to-video. PREFERS Pollinations (free starter credits, NO credit card) when
    POLLINATIONS_API_KEY is set; otherwise falls back to Google Veo (needs GEMINI_API_KEY +
    billing). Saves the mp4 and returns a markdown link the Console plays inline."""
    import requests, time, uuid, urllib.parse
    p = (prompt or "").strip()
    if not p:
        return "(no prompt given for the video)"

    # Option 1 — Pollinations video: free to start, no credit card. Simple GET -> MP4.
    pk = (os.getenv("POLLINATIONS_API_KEY") or os.getenv("POLLINATIONS_TOKEN") or "").strip()
    if pk:
        try:
            pmodel = os.getenv("POLLINATIONS_VIDEO_MODEL", "wan-fast")
            purl = (f"https://gen.pollinations.ai/video/{urllib.parse.quote(p, safe='')}"
                    f"?model={pmodel}&audio=true")
            pr = requests.get(purl, headers={"Authorization": f"Bearer {pk}"}, timeout=120)
            if pr.ok and pr.content and "video" in (pr.headers.get("Content-Type") or "").lower():
                os.makedirs("/tmp/dgmedia", exist_ok=True)
                pname = uuid.uuid4().hex[:16] + ".mp4"
                with open(os.path.join("/tmp/dgmedia", pname), "wb") as f:
                    f.write(pr.content)
                return f"[▶ Watch the generated video](/media/{pname})"
            # Pollinations responded but not with a video — report clearly; do NOT silently use Veo.
            if pr.status_code == 401:
                return "(Pollinations key invalid — set POLLINATIONS_API_KEY (the sk_ key from enter.pollinations.ai))"
            if pr.status_code in (402, 403):
                return "(Pollinations video credits exhausted — top up at enter.pollinations.ai)"
            return f"(Pollinations video error {pr.status_code}: {(pr.text or '')[:140]})"
        except Exception as e:
            return f"(could not reach Pollinations video: {e})"

    # Option 2 — Google Veo (needs GEMINI_API_KEY; Veo itself requires billing on the project).
    key = _gemini_key()
    if not key:
        return ("(video needs a key — easiest FREE path: get a Pollinations key at "
                "enter.pollinations.ai (no card) and set POLLINATIONS_API_KEY. Or set GEMINI_API_KEY "
                "with billing enabled for Google Veo.)")
    model = os.getenv("VEO_MODEL", "veo-3.1-fast-generate-preview")
    base = "https://generativelanguage.googleapis.com/v1beta"
    hdr = {"x-goog-api-key": key, "Content-Type": "application/json"}
    try:
        r = requests.post(f"{base}/models/{model}:predictLongRunning", headers=hdr,
                          json={"instances": [{"prompt": p}], "parameters": {"aspectRatio": "16:9"}},
                          timeout=30)
        if not r.ok:
            return f"(video request rejected: {r.status_code} {r.text[:160]})"
        op = (r.json() or {}).get("name")
        if not op:
            return "(video service did not return an operation id)"
    except Exception as e:
        return f"(could not start video: {e})"
    # Poll the long-running op. Kept tight so it fits the chat budget; fast model usually finishes.
    uri, deadline = None, time.time() + 55
    while time.time() < deadline:
        time.sleep(7)
        try:
            s = requests.get(f"{base}/{op}", headers=hdr, timeout=20).json()
        except Exception:
            continue
        if s.get("error"):
            return f"(video generation failed: {str(s.get('error'))[:160]})"
        if s.get("done"):
            try:
                uri = s["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]
            except Exception:
                return "(video finished but no file was returned)"
            break
    if not uri:
        return "(the video is still rendering — Veo can take ~a minute. Ask me to make it again shortly.)"
    try:
        vr = requests.get(uri, headers=hdr, timeout=25, allow_redirects=True)
        if not vr.ok or not vr.content:
            return "(could not download the finished video)"
        os.makedirs("/tmp/dgmedia", exist_ok=True)
        name = uuid.uuid4().hex[:16] + ".mp4"
        with open(os.path.join("/tmp/dgmedia", name), "wb") as f:
            f.write(vr.content)
    except Exception as e:
        return f"(could not save the video: {e})"
    return f"[▶ Watch the generated video](/media/{name})"


# --------------------------------------------------------------------------- #
# Memory — remember/recall across conversations. File-backed so it works now;
# set SUPABASE_URL + SUPABASE_KEY (+ a 'decagent_memories' table with a text
# column) for true cross-restart persistence ("never forget").
# --------------------------------------------------------------------------- #
import json as _json, time as _time
_MEM_FILE = os.getenv("DECAGENT_MEMORY_FILE", "/tmp/decagent_memory.json")


def _sb():
    url = (os.getenv("SUPABASE_URL") or "").rstrip("/")
    key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY") or ""
    table = os.getenv("DECAGENT_MEMORY_TABLE", "decagent_memories")
    return (url, key, table) if (url and key) else (None, None, None)


def _mem_load():
    url, key, table = _sb()
    if url:
        try:
            import requests
            r = requests.get(f"{url}/rest/v1/{table}?select=text&order=created_at.desc&limit=500",
                             headers={"apikey": key, "Authorization": f"Bearer {key}"}, timeout=10)
            if r.ok:
                return [{"text": it.get("text", "")} for it in r.json()][::-1]
        except Exception:
            pass  # fall back to the local file on any error
    try:
        with open(_MEM_FILE) as f:
            return _json.load(f)
    except Exception:
        return []


def _mem_add(text):
    url, key, _table = _sb()
    if url:
        try:
            import requests
            r = requests.post(f"{url}/rest/v1/{_table}",
                              headers={"apikey": key, "Authorization": f"Bearer {key}",
                                       "Content-Type": "application/json"},
                              json={"text": text}, timeout=10)
            if r.ok:
                return
        except Exception:
            pass
    try:
        items = _mem_load()
    except Exception:
        items = []
    items.append({"t": int(_time.time()), "text": text})
    try:
        with open(_MEM_FILE, "w") as f:
            _json.dump(items[-500:], f)
    except Exception:
        pass


def _remember(text):
    text = (text or "").strip()
    if not text:
        return "(nothing to remember)"
    _mem_add(text[:2000])
    return "Saved to memory."


def _recall(query, k=6):
    items = _mem_load()
    if not items:
        return "(no memories saved yet)"
    q = [w for w in re.split(r"\W+", (query or "").lower()) if len(w) > 2]
    hits = []
    if q:
        scored = sorted(items, key=lambda it: sum(1 for w in q if w in (it.get("text") or "").lower()),
                        reverse=True)
        hits = [it for it in scored if any(w in (it.get("text") or "").lower() for w in q)][:k]
    if not hits:
        hits = items[-k:]   # fall back to most recent
    return "\n".join(f"- {(it.get('text') or '').strip()}" for it in hits)


def recent_memories(k=5):
    """Runtime helper: surface the latest memories so agents stay aware of past work."""
    items = _mem_load()
    return [(it.get("text") or "").strip() for it in items[-k:] if (it.get("text") or "").strip()]


# --------------------------------------------------------------------------- #
# Parallel dispatch — a worker can fan subtasks out to several agents at once.
# One level deep only (nested dispatch disabled) and capped, so it can never
# runaway-recurse or blow the LLM rate limit.
# --------------------------------------------------------------------------- #
import threading as _threading
_DISPATCH = _threading.local()


_KNOWN_AGENTS = {"builder", "webwright", "octopilot", "harvest", "prospector",
                 "outreach", "scribe", "scout", "broadcast", "concierge", "patch", "buzz", "auto"}


def _dispatch_agents(tasks, max_parallel=5):
    if getattr(_DISPATCH, "active", False):
        return "(nested dispatch disabled — a dispatched agent can't dispatch again)"
    if not isinstance(tasks, list) or not tasks:
        return "(dispatch_agents needs a non-empty list of subtasks)"
    # Accept simple strings ("agent: task" or "task") OR {agent, task} dicts.
    norm = []
    for t in tasks[:max_parallel]:
        if isinstance(t, dict):
            norm.append(((t.get("agent") or "auto"), (t.get("task") or "")))
        elif isinstance(t, str) and t.strip():
            if ":" in t and t.split(":", 1)[0].strip().lower() in _KNOWN_AGENTS:
                a, task = t.split(":", 1)
                norm.append((a.strip().lower(), task.strip()))
            else:
                norm.append(("auto", t.strip()))
    norm = [(a, tk) for a, tk in norm if tk]
    if not norm:
        return "(no valid subtasks)"
    import importlib, concurrent.futures
    dec = None
    for modname in ("runtime.decagent", "decagent"):
        try:
            dec = importlib.import_module(modname)
            break
        except Exception:
            continue
    if not dec:
        return "(dispatch unavailable)"

    def _one(pair):
        _DISPATCH.active = True
        try:
            aid, task = pair
            aid = (aid or "auto").strip() or "auto"
            task = (task or "").strip()
            try:
                agent_id = dec.route(task) if aid == "auto" else aid
                text, _steps = dec.run_traced(agent_id, task, history=[])
                return f"### {agent_id}\n{(text or '(no output)').strip()}"
            except SystemExit:
                return f"### {aid}\n(unknown agent '{aid}')"
            except Exception as e:
                return f"### {aid}\n(failed: {e})"
        finally:
            _DISPATCH.active = False

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(max_parallel, len(norm))) as ex:
        for r in ex.map(_one, norm):
            results.append(r)
    return "\n\n".join(results)


TOOLS = [
    {"type": "function", "function": {
        "name": "web_search",
        "description": ("Search the web for current, real-time information. Returns top results "
                        "with titles and URLs. Use whenever you need up-to-date facts, news, "
                        "prices, or to find pages to read."),
        "parameters": {"type": "object",
                       "properties": {"query": {"type": "string", "description": "the search query"}},
                       "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "fetch_url",
        "description": ("Fetch a web page and return its readable text. Use to scrape/read a "
                        "specific URL in real time — e.g. after web_search, or when given a link."),
        "parameters": {"type": "object",
                       "properties": {"url": {"type": "string", "description": "the page URL"}},
                       "required": ["url"]}}},
    {"type": "function", "function": {
        "name": "fetch_html",
        "description": ("Fetch the RAW HTML source of a page to use as a TEMPLATE you can edit/"
                        "rebuild. Use when the user says 'edit my site', 'use my template', or gives "
                        "a site to base a page on. After editing the HTML, call create_webpage to publish."),
        "parameters": {"type": "object",
                       "properties": {"url": {"type": "string", "description": "the page URL to pull as a template"}},
                       "required": ["url"]}}},
    {"type": "function", "function": {
        "name": "generate_image",
        "description": ("Generate an image from a text prompt (free, no key). Use when the user "
                        "asks for a picture, logo, artwork, cover, thumbnail, poster, or any visual. "
                        "Returns a markdown image tag — you MUST include it verbatim in your reply "
                        "so the user actually sees the image."),
        "parameters": {"type": "object",
                       "properties": {
                           "prompt": {"type": "string", "description": "detailed description of the image to create"},
                           "width": {"type": "integer", "description": "optional width in px (256-1536, default 1024)"},
                           "height": {"type": "integer", "description": "optional height in px (256-1536, default 1024)"}},
                       "required": ["prompt"]}}},
    {"type": "function", "function": {
        "name": "generate_video",
        "description": ("Generate a short video (~8s, with audio) from a text prompt via Veo. Use when "
                        "the user asks for a video, clip, animation, or ad. Returns a markdown video "
                        "link you MUST include verbatim. Note: takes about a minute."),
        "parameters": {"type": "object",
                       "properties": {"prompt": {"type": "string", "description": "detailed description of the video to create"}},
                       "required": ["prompt"]}}},
    {"type": "function", "function": {
        "name": "create_webpage",
        "description": ("Publish a webpage and get a LIVE shareable URL on THIS site (not GitHub). Use "
                        "when the user wants a webpage, landing page, website, or to switch templates: "
                        "YOU write the full HTML (any template/style requested), pass it here, and "
                        "include the returned link in your reply."),
        "parameters": {"type": "object",
                       "properties": {
                           "html": {"type": "string", "description": "the complete HTML document for the page"},
                           "title": {"type": "string", "description": "optional page title"}},
                       "required": ["html"]}}},
    {"type": "function", "function": {
        "name": "dispatch_agents",
        "description": ("Run several specialist agents IN PARALLEL and combine their results. Use for "
                        "big multi-part jobs ('war times') — e.g. research + write + plan at once. "
                        "Give a list of subtasks; each runs at the same time."),
        "parameters": {"type": "object",
                       "properties": {"tasks": {"type": "array", "items": {"type": "string"},
                           "description": ("subtasks to run in parallel (max 5). Optionally prefix one "
                                           "with an agent id, e.g. 'scout: find the BPM of reggae'; "
                                           "otherwise it auto-routes.")}},
                       "required": ["tasks"]}}},
    {"type": "function", "function": {
        "name": "remember",
        "description": ("Save an important fact, preference, decision, or detail to long-term memory "
                        "so it is not forgotten in future conversations."),
        "parameters": {"type": "object",
                       "properties": {"text": {"type": "string", "description": "the fact to remember"}},
                       "required": ["text"]}}},
    {"type": "function", "function": {
        "name": "recall",
        "description": ("Search long-term memory for previously saved facts relevant to a query — "
                        "earlier work, preferences, or context."),
        "parameters": {"type": "object",
                       "properties": {"query": {"type": "string", "description": "what to look up"}},
                       "required": ["query"]}}},
]
NAMES = {"web_search", "fetch_url", "fetch_html", "generate_image", "generate_video", "create_webpage", "dispatch_agents", "remember", "recall"}


def execute(name, args):
    try:
        if name == "web_search":
            return _web_search(args.get("query", ""))
        if name == "fetch_url":
            return _fetch_url(args.get("url", ""))
        if name == "fetch_html":
            return _fetch_html(args.get("url", ""))
        if name == "generate_image":
            return _generate_image(args.get("prompt", ""),
                                   args.get("width", 1024), args.get("height", 1024))
        if name == "generate_video":
            return _generate_video(args.get("prompt", ""))
        if name == "create_webpage":
            return _create_webpage(args.get("html", ""), args.get("title", ""))
        if name == "dispatch_agents":
            return _dispatch_agents(args.get("tasks", []))
        if name == "remember":
            return _remember(args.get("text", ""))
        if name == "recall":
            return _recall(args.get("query", ""))
    except Exception as e:
        return f"({name} failed: {e})"
    return f"(unknown built-in tool '{name}')"
