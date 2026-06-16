# Decagent Runtime

One small engine runs all ten agents. It loads an agent's plain-language prompt
and the Composio tools it needs, then runs it against an LLM.

## Setup (5 minutes)
```bash
cd Decagents
pip install -r runtime/requirements.txt
cp runtime/.env.example runtime/.env     # then paste in your keys
```

You need two keys:
- **A free LLM key** — the brain. Easiest: **Google Gemini** at aistudio.google.com (free, no card). Groq and OpenRouter also work — see `.env.example`.
- **Composio** (`COMPOSIO_API_KEY`) — the hands (GitHub, Gmail, scraping, leads…). Get it at app.composio.dev, then connect the apps each agent uses.

> No Composio key? The agents still run as plain chat assistants — they just can't take actions in the outside world yet.

## Run an agent from the terminal
```bash
python runtime/decagent.py --list                       # see all ten
python runtime/decagent.py --agent scout -m "Research the EV charging market in Europe"
python runtime/decagent.py --agent builder -m "Build a URL shortener with a web UI"
```

## Run the API (what your website calls)
```bash
uvicorn runtime.server:app --reload --port 8000
# then:  GET http://localhost:8000/agents
#        POST http://localhost:8000/run   { "agent": "scout", "message": "..." }
```

## Connecting tools (Composio)
Each agent's `agent.json` lists the `composio_toolkits` it uses (e.g. `github`,
`gmail`, `firecrawl`). In the Composio dashboard, connect those apps once and
authorize them. After that, the agents can act on your accounts.

## Files
| File | What it is |
|------|------------|
| `decagent.py` | The runtime + CLI. Loads an agent, wires tools, runs the loop. |
| `server.py` | FastAPI server exposing the agents over HTTP for the website. |
| `requirements.txt` | Python dependencies. |
| `.env.example` | Copy to `.env` and add your keys. |
