# Decagent — 10 AI agents you hire in plain English

> **Working title — rename freely.** "Decagent" = *deca* (ten) + *agent*.

Ten powerful AI agents that do real work — build apps, edit websites, pilot GitHub,
scrape the web, find leads, write emails, create content, research, run social, and
handle your inbox. You talk to them in plain English. No prompt-engineering, no code
required to *use* them.

Built to be **stored on GitHub**, **run anywhere**, and **sold as subscriptions** from
your own website.

---

## The ten agents

| Agent | What it does | Tier | id |
|-------|--------------|------|----|
| 🛠️ **Builder** | Describe an app in plain English. Get working code. | Pro | `builder` |
| 🎨 **Webwright** | Edit, redesign, and build websites — just say what you want. | Pro | `webwright` |
| 🐙 **Octopilot** | Your GitHub co-pilot — repos, branches, PRs, reviews. | Agency | `octopilot` |
| 🌾 **Harvest** | Turn any website into clean, structured data. | Pro | `harvest` |
| 🔍 **Prospector** | Find your next 100 customers. | Agency | `prospector` |
| ✉️ **Outreach** | Write emails that actually get replies. | Starter | `outreach` |
| ✍️ **Scribe** | Content on demand — blogs, social, SEO. | Starter | `scribe` |
| 🧭 **Scout** | Deep research, summarized for decisions. | Starter | `scout` |
| 📡 **Broadcast** | Run all your social channels from one place. | Agency | `broadcast` |
| 🛎️ **Concierge** | Never miss a customer message again. | Starter | `concierge` |

Each agent lives in `agents/<id>/` with three files: its plain-language `system_prompt.md`
(the brain), an `agent.json` manifest (model + tools + tier), and a `README.md`.

---

## Run one in 2 minutes
```bash
git clone https://github.com/fumbasiyabongajason-ux/Decagents.git
cd Decagents
pip install -r runtime/requirements.txt
cp runtime/.env.example runtime/.env      # add your Anthropic + Composio keys

python runtime/decagent.py --list
python runtime/decagent.py --agent scout -m "Research the home-fitness market in 2026"
```
The agents use **[Composio](https://composio.dev)** for their tools (GitHub, Gmail,
scraping, leads, social…). One Composio account powers all the real-world actions.

## 💬 Use all 10 from one chat — the Console
The easiest way to use your team: a private, ChatGPT-style web app where every agent
lives in **one thread**.
```bash
uvicorn runtime.server:app --port 8000
# then open http://localhost:8000
```
Pick any agent from the sidebar, or leave it on **Auto** and your message is routed to
the right specialist automatically. (UI lives in `app/index.html`.)

## Turn it into a business
- **Website** (`website/`) — a ready landing + pricing page for your subscription product.
- **API** (`runtime/server.py`) — serve the agents over HTTP so the website can call them.
- **Billing** (`billing/`) — Stripe subscription model + the four price tiers.
- **Selling** (`SELLING.md`) — how to actually sell (GitHub's real role, Polar/Gumroad, go-to-market).

## What's here
```
decagent/
├── agents/            # the 10 agents (the product IP)
│   ├── 01-builder/  …  10-concierge/
│   └── catalog.json   # machine-readable index of all agents
├── runtime/           # the engine: run agents via CLI or HTTP API
├── billing/           # Stripe subscription model + pricing.json
├── website/           # your marketing + subscription site (index.html)
├── docs/              # QUICKSTART and guides
├── SELLING.md         # how to sell + drive traffic
└── build_agents.py    # regenerate all agent files from one source of truth
```

## Status
**v0.1 — Phase 1 complete.** Agents, runtime, website, and billing model are in place.
**Phase 2** (your keys): connect Stripe, deploy the API, point a domain at the site, go live.
See `billing/README.md`.

## License
See `LICENSE`. Source-available for personal & evaluation use; a commercial license is
required to resell or run as a paid service. (You own this — adjust to taste.)

---
*Built as a starting product, not a toy. Read each agent's prompt — that's the craft.*
