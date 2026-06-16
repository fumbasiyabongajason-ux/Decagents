# 📡 Broadcast — Run all your social channels from one place.

Broadcast plans, writes, and posts across your social channels. It adapts each message to the platform, keeps a consistent voice, and can schedule a whole content calendar.

**Tier:** Agency ($199/mo) · **Version:** 0.1.0

## What it does
- Plan and schedule a multi-platform content calendar
- Write platform-native posts — not the same copy everywhere
- Post to X, LinkedIn, Reddit, and more
- Repurpose one idea into many formats
- Suggest the best times and channels for your audience

## Try asking it
- "Plan a week of posts promoting my new product across X and LinkedIn."
- "Turn this announcement into a post for each of my channels."
- "Find the best subreddits for my tool and draft a post that won't get removed."

## Tools (Composio toolkits)
`twitter`, `linkedin`, `reddit`

## Run it
```bash
# from the repo root, with your keys in .env (see runtime/.env.example)
python runtime/decagent.py --agent broadcast
```

> Plain-language agent. No prompt-engineering required — just tell it what you want.
