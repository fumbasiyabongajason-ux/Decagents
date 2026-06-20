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
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Decagent/1.0)"}
    for ep in ("https://html.duckduckgo.com/html/", "https://lite.duckduckgo.com/lite/"):
        try:
            r = requests.post(ep, data={"q": query}, headers=headers, timeout=12)
        except Exception:
            continue   # try the next endpoint, never hang
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
    return "(no results found)"


def _fetch_url(url, max_chars=6000):
    import requests
    if not re.match(r"^https?://", url or ""):
        url = "https://" + (url or "")
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (compatible; Decagent/1.0)"}, timeout=15)
    html = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", r.text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars] or "(no readable text on page)"


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
]
NAMES = {"web_search", "fetch_url"}


def execute(name, args):
    try:
        if name == "web_search":
            return _web_search(args.get("query", ""))
        if name == "fetch_url":
            return _fetch_url(args.get("url", ""))
    except Exception as e:
        return f"({name} failed: {e})"
    return f"(unknown built-in tool '{name}')"
