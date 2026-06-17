# Groq — free + fast brain for your agents

Groq runs open models (Llama, etc.) at very high speed, with a **free tier** and no card.
It's OpenAI-compatible, so Decagent already supports it — you just set three values.

## 1. Get your free key
1. Go to **console.groq.com** and sign in.
2. Open **API Keys** → **Create API Key** → copy it.

## 2. Point Decagent at Groq
**Local** — in `runtime/.env` (Groq is already the default block):
```
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=gsk_your_key_here
LLM_MODEL=llama-3.3-70b-versatile
```
**Cloud (Render)** — paste your key into the `LLM_API_KEY` field (the blueprint already
sets the Groq base URL + model).

Then run `uvicorn runtime.server:app --port 8000` and open the Console. That's it.

## 3. Which model?
Model names change over time — see the current list at **console.groq.com/docs/models**.
Good picks today:
| Model | Best for |
|-------|----------|
| `llama-3.3-70b-versatile` | **Default.** Smart + supports tool-calling (needed for n8n/Composio actions). |
| `llama-3.1-8b-instant` | Fastest/cheapest; great for quick chat, lighter reasoning. |

Put the exact id in `LLM_MODEL`.

## Good to know
- **Free-tier limits.** Groq's free tier caps requests/tokens per minute and per day —
  plenty for personal use. If you hit a limit you'll get a 429; wait, or switch model/provider.
- **Tool-calling.** Use a tool-capable model (like `llama-3.3-70b-versatile`) so agents can
  call your n8n/Composio tools. If a model rejects tools, the runtime auto-falls back to plain chat.
- **Switching providers is one block** in `.env` (Gemini/OpenRouter presets are there too).
