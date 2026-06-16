# 🎨 Webwright — Edit, redesign, and build websites — just say what you want.

Webwright reads an existing site, understands its structure, and makes the edits or full redesign you describe. It can also build polished landing pages from scratch and ship them to GitHub or a host.

**Tier:** Pro ($79/mo) · **Version:** 0.1.0

## What it does
- Read and understand an existing website's pages and structure
- Make precise copy, layout, and style edits from a plain description
- Redesign pages or build new landing pages from scratch
- Produce clean, self-contained HTML/CSS/JS ready to deploy
- Commit changes to GitHub or hand back ready-to-publish files

## Try asking it
- "Redesign my homepage to feel more premium and add a pricing section."
- "Change all the buttons on my site to dark green and fix the mobile layout."
- "Build me a landing page for my new product with an email signup form."

## Tools (Composio toolkits)
`firecrawl`, `github`, `filetool`

## Run it
```bash
# from the repo root, with your keys in .env (see runtime/.env.example)
python runtime/decagent.py --agent webwright
```

> Plain-language agent. No prompt-engineering required — just tell it what you want.
