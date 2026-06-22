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
        for m in re.finditer(r'(?:result__a|result-link)[^>]*href="([^"]+)"[^>]*>(.*?)</a>', r.text, re.S):
            url = m.group(1)
            title = re.sub(r"<[^>]+>", "", m.group(2)).strip()
            if title:
                items.append(f"- {title}\n  {url}")
            if len(items) >= max_results:
                break
        if items:
            return "\n".join(items)
    return "(no results — for reliable cloud search, set a free TAVILY_API_KEY)"


def _fetch_url(url, max_chars=6000):
    import requests
    if not re.match(r"^https?://", url or ""):
        url = "https://" + (url or "")
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; Decagent/1.0)"}, timeout=15)
    html = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", r.text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars] or "(no readable text on page)"


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
]
NAMES = {"web_search", "fetch_url", "generate_image"}


def execute(name, args):
    try:
        if name == "web_search":
            return _web_search(args.get("query", ""))
        if name == "fetch_url":
            return _fetch_url(args.get("url", ""))
        if name == "generate_image":
            return _generate_image(args.get("prompt", ""),
                                   args.get("width", 1024), args.get("height", 1024))
    except Exception as e:
        return f"({name} failed: {e})"
    return f"(unknown built-in tool '{name}')"
