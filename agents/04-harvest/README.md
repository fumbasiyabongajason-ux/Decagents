# 🌾 Harvest — Turn any website into clean, structured data.

Harvest scrapes the pages you point it at and returns clean, structured data — a spreadsheet, JSON, or a table — instead of a mess of HTML. Great for research, monitoring, and building datasets.

**Tier:** Pro ($79/mo) · **Version:** 0.1.0

## What it does
- Scrape single pages or crawl whole sites for the data you need
- Extract structured fields (names, prices, dates, links) reliably
- De-duplicate and clean the results into a usable dataset
- Export to Google Sheets, CSV, or JSON
- Monitor pages and report what changed over time

## Try asking it
- "Scrape this directory and give me every company name, website, and email."
- "Pull all the product names and prices from this store into a spreadsheet."
- "Watch this page and tell me when the price drops."

## Tools (Composio toolkits)
`firecrawl`, `exa`, `googlesheets`

## Run it
```bash
# from the repo root, with your keys in .env (see runtime/.env.example)
python runtime/decagent.py --agent harvest
```

> Plain-language agent. No prompt-engineering required — just tell it what you want.
