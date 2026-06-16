# Quickstart

## 1. Get the code
```bash
git clone https://github.com/fumbasiyabongajason-ux/Decagents.git
cd Decagents
pip install -r runtime/requirements.txt
```

## 2. Add your keys
```bash
cp runtime/.env.example runtime/.env
```
Open `runtime/.env` and paste in:
- `ANTHROPIC_API_KEY` — from console.anthropic.com (the agents' brain)
- `COMPOSIO_API_KEY` — from app.composio.dev (the agents' tools)

In Composio, connect the apps your agents use (GitHub, Gmail, etc.). Each agent's
`agent.json` lists which `composio_toolkits` it needs.

## 3. Talk to an agent
```bash
python runtime/decagent.py --list
python runtime/decagent.py --agent outreach -m "Write a cold email to dentists offering my booking app"
```

## 4. Run the API (for the website)
```bash
uvicorn runtime.server:app --reload --port 8000
curl http://localhost:8000/agents
```

## 5. Go to market
- Open `website/index.html` to see your storefront. Host it (Netlify/Vercel/GitHub Pages).
- Wire up Stripe using `billing/README.md`.
- Drive traffic using the playbook in `SELLING.md`.

## Common questions
**Do my customers need API keys?** No — on the hosted plans, *you* hold the keys and
charge a subscription. Keys are only for self-hosters (Community tier).

**Can I add an 11th agent?** Yes. Add it to the `AGENTS` list in `build_agents.py` and
re-run `python build_agents.py`. Everything regenerates.

**Which model?** Default is `claude-opus-4-8`. Change `DECAGENT_MODEL` in `.env`.
