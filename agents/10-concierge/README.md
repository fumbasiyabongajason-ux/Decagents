# 🛎️ Concierge — Never miss a customer message again.

Concierge triages your inbox, drafts replies to common questions, books meetings, and makes sure nothing falls through the cracks. It works from drafts so you stay in control.

**Tier:** Starter ($29/mo) · **Version:** 0.1.0

## What it does
- Triage and label incoming email by urgency and topic
- Draft replies to common questions in your voice
- Book meetings and send calendar invites on approval
- Summarize what needs your attention each day
- Escalate anything sensitive to you instead of guessing

## Try asking it
- "Go through my inbox and draft replies to anything I can answer quickly."
- "Summarize the emails I got overnight and tell me what's urgent."
- "Book a 30-minute call with this client next week and send the invite."

## Tools (Composio toolkits)
`gmail`, `slack`, `googlecalendar`

## Run it
```bash
# from the repo root, with your keys in .env (see runtime/.env.example)
python runtime/decagent.py --agent concierge
```

> Plain-language agent. No prompt-engineering required — just tell it what you want.
