# Pipedream Connect — thousands of app tools (managed auth)

Pipedream Connect exposes 2,700+ apps to your agents through one **MCP** endpoint, and
**handles login (OAuth) for you**. Decagent auto-mints + refreshes the access token, so
once it's set up it just keeps working.

> **Cost (important):** Pipedream **development mode is free** and is fine for your own
> personal use. **Production** mode (serving real external users) requires a paid plan.
> 1 credit = 30s of compute; listing/configuring tools is free. So for *you*, it's free.

## Setup (one time)

### 1. Project + OAuth client
1. Sign up at **pipedream.com**, create a **Project** → copy its id (looks like `proj_abc123`).
2. **Settings → API → New OAuth Client** → copy the **client_id** and **client_secret**.
   (Decagent uses these to mint tokens automatically — you never paste a token by hand.)

### 2. Connect the app accounts you want to use
For each app (Gmail, GitHub, Slack…), connect your account to Pipedream for your user id.
- Use Pipedream's **Connect** flow / dashboard to authorize each app under an
  `external_user_id` you choose — for personal use just use **`me`**.
- ⚠️ Tools won't work until the matching account is connected. "Send email via Gmail" needs
  your Gmail connected for user `me` first.

### 3. Set the env vars
Local (`.env`) or Render dashboard:
```
TOOLS_BACKEND=mcp
PIPEDREAM_CLIENT_ID=<your client id>
PIPEDREAM_CLIENT_SECRET=<your client secret>
PIPEDREAM_PROJECT_ID=proj_abc123
PIPEDREAM_ENVIRONMENT=development        # free; use 'production' only on a paid plan
PIPEDREAM_EXTERNAL_USER_ID=me
MCP_APP_SLUGS=gmail,github,slack         # the apps to expose (add as many as you like)
```
That's it — restart/redeploy and your agents gain those apps' tools.

## How it works
- The bridge connects to `https://remote.mcp.pipedream.net/v3` once per app slug (Pipedream
  is app-scoped via the `x-pd-app-slug` header), lists each app's tools, and merges them.
- It mints the bearer token from your client id/secret and **auto-refreshes** it (~1h expiry).
- Tool names are prefixed by app (e.g. `gmail_send_email`) so the agent knows what's what.

## Honest notes (please read before you rely on it)
- **First run is the real test.** This was wired up without live Pipedream credentials, so
  verify on your first deploy. If an agent says a tool failed, check, in order:
  1. Is the app **account connected** in Pipedream for `external_user_id=me`?
  2. Is the **slug** right (e.g. `gmail`, not `google-gmail`)? See Pipedream's app pages.
  3. Is `PIPEDREAM_ENVIRONMENT=development` (free) and the **project id** correct?
  4. Check the server logs for `MCP connect/list failed` — that points at auth.
- **MCP protocol version** isn't officially documented by Pipedream; the bridge sends a
  recent one. If `tools/list` comes back empty, that's the first knob to try.
- **Latency:** the Console discovers your tools on each message — fine for personal use,
  a touch slower than a static list. (We can add caching later if you want.)
- **Falls back to chat:** if anything's misconfigured, the agents simply chat (no crash).

## Prefer Zapier instead?
Zapier MCP gives one URL exposing 9,000+ apps' actions, but its **free plan allows only
~50 tool calls/month** (each call = 2 Zapier "tasks", 100/mo free). To use it:
```
TOOLS_BACKEND=mcp
MCP_SERVER_URL=https://actions.zapier.com/mcp/<your-id>/sse
# (skip the PIPEDREAM_* vars; Zapier returns all your enabled actions in one list)
```
For daily use, Pipedream dev mode (free, unlimited for you) is the better fit.
