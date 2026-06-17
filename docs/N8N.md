# n8n — free, self-hosted tools (instead of Composio)

n8n is an open-source automation tool. Self-hosting it is **free**, and it has 400+
integrations (Gmail, GitHub, Slack, HTTP, etc.). Decagent uses it as the agents' "hands":
each tool is an n8n **Webhook workflow**, and your credentials live inside n8n — not in this app.

## How it fits together
```
Agent decides: send_email(to, subject, body)
   │
   ▼  (Decagent's n8n bridge POSTs the args)
n8n Webhook  →  Gmail node (uses your saved Gmail credential)  →  Respond to Webhook
   │
   ▼  (returns a result)
Agent reads the result and continues.
```

## 1. Run n8n (free)
Self-host with Docker:
```bash
docker run -it --rm -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```
Open `http://localhost:5678`, create your account. For a public URL, run it on a small
VPS / Railway / Fly and put it behind HTTPS. (n8n **Cloud** is the paid, hosted option.)

## ⭐ Fastest: connect ALL tools at once (one router workflow)
Instead of one workflow per tool, use a single "router" workflow that receives every tool
call. The Console sends `{ "tool": "<name>", "args": {...} }` to one webhook; n8n routes by tool.

1. **Import the starter:** in n8n → **Workflows → Import from File** → pick
   `n8n/decagent-router.starter.json`. You get a **Webhook** (path `decagent`) → an echo node.
2. **Point Decagent at it** — in `.env`:
   ```
   TOOLS_BACKEND=n8n
   N8N_WEBHOOK_URL=https://your-n8n.example.com/webhook/decagent
   ```
   That single URL now handles **all** tools listed in `runtime/n8n_tools.json`.
3. **Turn the echo into real actions:** replace the "Echo" node with a **Switch** node on
   `{{ $json.body.tool }}`, with one output per tool, each going to its action node:
   | tool | node | map fields from |
   |------|------|-----------------|
   | `send_email` | Gmail → Send | `{{ $json.body.args.to/subject/body }}` |
   | `create_github_issue` | GitHub → Create Issue | `{{ $json.body.args.repo/title/body }}` |
   | `scrape_url` | HTTP Request (GET) | `{{ $json.body.args.url }}` |
   | `web_search` | HTTP Request to your search API | `{{ $json.body.args.query }}` |
   Connect your Gmail/GitHub credentials on those nodes, then **Activate** the workflow.

> Tip: depending on your n8n version the body is at `$json.body` or `$json` — check the
> webhook node's output and adjust the expressions. Add tools anytime by adding a Switch
> branch + an entry in `runtime/n8n_tools.json`. No Console change needed.

## (Alternative) Build one workflow per tool
For each tool (e.g. `send_email`):
1. Add a **Webhook** node → method `POST`, path e.g. `send-email` → this gives you a URL like
   `https://your-n8n/webhook/send-email`.
2. Add the action node (e.g. **Gmail → Send**), mapping fields from the webhook body
   (`{{$json.to}}`, `{{$json.subject}}`, `{{$json.body}}`). Connect your Gmail credential in n8n.
3. Add a **Respond to Webhook** node returning a short result (e.g. "sent" or the data).
4. **Activate** the workflow.

Repeat for the other tools you want (GitHub issue, scrape, search…).

## 3. Tell Decagent about the tools
1. Copy the template: `cp runtime/n8n_tools.example.json runtime/n8n_tools.json`
2. Edit each entry's `name`, `description`, `webhook` path, and `parameters` to match your
   workflows. (Relative paths like `/webhook/send-email` are prefixed with `N8N_BASE_URL`.)
3. In `.env`:
   ```
   TOOLS_BACKEND=n8n
   N8N_BASE_URL=https://your-n8n.example.com
   # N8N_AUTH_HEADER=Bearer your-secret   # optional, if you secure your webhooks
   ```
Restart the Console. Agents can now call your workflows. (No `n8n_tools.json` yet? Agents
still run as normal chat — they just can't take actions until tools exist.)

## Security
- **Protect your webhooks** — anyone with the URL can trigger them. Use n8n's webhook auth
  (header/basic) and set `N8N_AUTH_HEADER` to match, or keep n8n on a private network.
- Your real credentials stay in n8n; Decagent never sees them. Good separation.

## Composio vs n8n (quick take)
- **n8n**: free (self-host), you build each tool, total control, great for *your own* use.
- **Composio**: faster to wire up many tools + per-user OAuth, but it's a paid/hosted service.
You can keep using Composio instead by setting `COMPOSIO_API_KEY` and removing `TOOLS_BACKEND=n8n`.

> License note: self-hosting n8n to power **your own** product is fine. n8n's license does
> **not** let you resell n8n itself (white-label the builder) to your customers. See `SELLING.md`.
