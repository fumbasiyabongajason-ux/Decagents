# Deploy the Console to a permanent URL (no terminal)

This gets you a real `https://…` link you can open from any browser — laptop or phone —
without running anything locally. We'll use **Render** (free tier works fine).

## Before you start — get 2 things (n8n is optional; add it later)
1. **Free LLM key (Cerebras)** — go to cloud.cerebras.ai → **API Keys** → create. Free, fastest
   inference, no card. (Required.) *(Groq / Gemini / OpenRouter also work — see `runtime/.env.example`.)*
2. **A password you'll make up** — anything memorable. This locks your URL so only you can use it.
3. *(Optional, later)* **n8n tools** — for real actions (email, GitHub…). You can deploy now and
   add `N8N_WEBHOOK_URL` anytime. Until then the agents simply work as chat.

## Deploy in ~5 minutes
1. Make sure this repo is on your GitHub (it is: `fumbasiyabongajason-ux/Decagents`).
2. Click this link (or paste it in your browser):
   **https://render.com/deploy?repo=https://github.com/fumbasiyabongajason-ux/Decagents**
3. Sign in to Render with GitHub and approve access to the repo.
4. Render reads `render.yaml` automatically and shows the service. Fill in the secret values:
   - `LLM_API_KEY` → paste your free **Cerebras** key  *(required)*
   - `DECAGENT_PASSWORD` → type the password you chose  *(required)*
   - `N8N_WEBHOOK_URL` → **leave blank for now**; add it later when your n8n tools are ready  *(optional)*
5. Click **Apply** / **Create**. Render builds it (a few minutes the first time).
6. When it's live, Render gives you a URL like `https://decagent-console.onrender.com`.
   Open it → enter your password → start chatting with all 10 agents. Bookmark it on your phone.

## Good to know
- **Free tier sleeps.** After ~15 min idle, the first visit takes ~50 seconds to wake up.
  Upgrade to a paid instance (~$7/mo) if you want it always-on and instant.
- **Your password protects your money.** Anyone with the URL *and* the password can use the
  agents — which use your LLM quota and can touch your connected Gmail/GitHub.
  Keep the password private; change it anytime in Render → Environment.
- **Updating it later:** push changes to the repo's `main` branch and Render auto-redeploys.
- **Costs:** Render free + Cerebras free tier + (n8n free, self-hosted) = **$0** for normal
  personal use. If you outgrow the free LLM quota, switch `LLM_MODEL`/provider in Render → Environment.

## Other hosts
The same app runs anywhere that hosts a Python web service — Railway, Fly.io, or your own
server. Use the same start command: `uvicorn runtime.server:app --host 0.0.0.0 --port $PORT`,
and set the same environment variables.
