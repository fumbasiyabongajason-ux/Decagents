# ✉️ Outreach — Write emails that actually get replies.

Outreach writes cold emails, follow-up sequences, and replies that sound human and get responses. It personalizes each message, drafts everything in Gmail for your review, and never sends without your say-so.

**Tier:** Starter ($29/mo) · **Version:** 0.1.0

## What it does
- Write personalized cold emails and multi-step follow-up sequences
- Draft replies to inbound emails in your voice
- Personalize at scale from a lead list
- Save everything as Gmail drafts for your review — never auto-send
- Track who was contacted and when

## Try asking it
- "Write a 3-email cold sequence for my web design service to local restaurants."
- "Draft a friendly follow-up to the leads who haven't replied in a week."
- "Reply to this inquiry and propose three times for a call."

## Tools (Composio toolkits)
`gmail`, `googlesheets`

## Run it
```bash
# from the repo root, with your keys in .env (see runtime/.env.example)
python runtime/decagent.py --agent outreach
```

> Plain-language agent. No prompt-engineering required — just tell it what you want.
