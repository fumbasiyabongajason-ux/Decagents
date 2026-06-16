# 🛠️ Builder — Describe an app in plain English. Get working code.

Builder turns a plain-language description into a real, runnable application. It picks a sensible stack, writes clean code file-by-file, pushes it to GitHub, and hands you exact steps to run and deploy it.

**Tier:** Pro ($79/mo) · **Version:** 0.1.0

## What it does
- Scaffold full-stack apps, APIs, scripts, and CLIs from a description
- Write clean, commented, runnable code — not pseudo-code
- Create a GitHub repo and commit the project for you
- Run and test code in a sandbox before handing it over
- Explain what it built in plain language and give run/deploy steps

## Try asking it
- "Build me a to-do app with a Postgres backend and a simple web UI."
- "Write a Python script that watches a folder and emails me when a new file lands."
- "Make a REST API for a bookstore with search and checkout, and push it to GitHub."

## Tools (Composio toolkits)
`github`, `codeinterpreter`, `filetool`

## Run it
```bash
# from the repo root, with your keys in .env (see runtime/.env.example)
python runtime/decagent.py --agent builder
```

> Plain-language agent. No prompt-engineering required — just tell it what you want.
