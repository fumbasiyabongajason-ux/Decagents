# 🧭 Scout — Deep research, summarized for decisions.

Scout does the digging for you: market research, competitor analysis, due diligence, and topic deep-dives. It reads widely, cites everything, and hands you a clear, decision-ready summary.

**Tier:** Starter ($29/mo) · **Version:** 0.1.0

## What it does
- Run deep research on markets, companies, people, and topics
- Compare competitors across the dimensions that matter
- Synthesize many sources into a clear, structured brief
- Cite every claim so you can trust and verify it
- Flag what's uncertain, contested, or missing

## Try asking it
- "Give me a competitive analysis of the top 5 project management tools."
- "Research the market for eco-friendly packaging in 2026."
- "What do I need to know before pitching this company?"

## Tools (Composio toolkits)
`exa`, `tavily`, `firecrawl`

## Run it
```bash
# from the repo root, with your keys in .env (see runtime/.env.example)
python runtime/decagent.py --agent scout
```

> Plain-language agent. No prompt-engineering required — just tell it what you want.
