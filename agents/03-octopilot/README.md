# 🐙 Octopilot — Your GitHub co-pilot — repos, branches, PRs, reviews.

Octopilot runs your GitHub for you in plain language. Open issues, create branches, review pull requests, merge, tag releases — without memorizing git commands.

**Tier:** Agency ($199/mo) · **Version:** 0.1.0

## What it does
- Create repos, branches, issues, and pull requests on request
- Review pull requests and leave useful, specific comments
- Summarize what changed across commits and PRs in plain language
- Triage and label issues, link related work, close stale items
- Cut releases and tags, and keep the changelog honest

## Try asking it
- "Open a PR from my feature branch into main and summarize the changes."
- "Review the open pull requests and tell me which ones are safe to merge."
- "Create issues for each bug in this list and label them by priority."

## Tools (Composio toolkits)
`github`

## Run it
```bash
# from the repo root, with your keys in .env (see runtime/.env.example)
python runtime/decagent.py --agent octopilot
```

> Plain-language agent. No prompt-engineering required — just tell it what you want.
