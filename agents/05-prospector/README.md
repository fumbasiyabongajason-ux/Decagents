# 🔍 Prospector — Find your next 100 customers.

Prospector builds targeted lead lists from a plain description of your ideal customer. It finds companies and people, enriches them with verified contact details, and hands you a ready-to-use list.

**Tier:** Agency ($199/mo) · **Version:** 0.1.0

## What it does
- Build a target list from a plain-language ideal-customer description
- Find decision-makers at matching companies
- Enrich leads with verified emails, titles, and company info
- Score and prioritize leads by fit
- Export a clean, deduplicated list to Google Sheets or CSV

## Try asking it
- "Find me 50 marketing directors at mid-size SaaS companies in the US."
- "Build a list of independent coffee roasters in Europe with their emails."
- "Who are the heads of partnerships at fintech startups in London?"

## Tools (Composio toolkits)
`apollo`, `hunter`, `exa`, `googlesheets`

## Run it
```bash
# from the repo root, with your keys in .env (see runtime/.env.example)
python runtime/decagent.py --agent prospector
```

> Plain-language agent. No prompt-engineering required — just tell it what you want.
