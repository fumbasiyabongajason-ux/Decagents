# ✍️ Scribe — Content on demand — blogs, social, SEO.

Scribe researches, writes, and polishes content in your voice: blog posts, social captions, newsletters, and SEO copy. It backs claims with real sources and can publish straight to your blog.

**Tier:** Starter ($29/mo) · **Version:** 0.1.0

## What it does
- Write blog posts, articles, newsletters, and landing-page copy
- Produce platform-native social captions and threads
- Research topics and cite real, current sources
- Optimize for SEO — keywords, structure, meta
- Publish to WordPress or save to Google Docs

## Try asking it
- "Write a 1,000-word blog post on why small brands should use email marketing."
- "Turn this blog post into a Twitter thread and a LinkedIn post."
- "Write five SEO-optimized product descriptions for my store."

## Tools (Composio toolkits)
`exa`, `googledocs`, `wordpress`

## Run it
```bash
# from the repo root, with your keys in .env (see runtime/.env.example)
python runtime/decagent.py --agent scribe
```

> Plain-language agent. No prompt-engineering required — just tell it what you want.
