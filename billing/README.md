# Billing — turning Decagent into a subscription business

This folder explains how money flows. The product sells as **monthly subscriptions**
through your own website. Stripe handles the payments; your server checks whether a
logged-in user's plan covers the agent they're trying to use.

## The plans
See `pricing.json` for the machine-readable version. In plain terms:

| Plan | Price | Who it's for | Agents included |
|------|-------|--------------|-----------------|
| **Community** | Free | Developers who self-host | All 10 (run it yourself with your own keys) |
| **Starter** | $29/mo | Freelancers & creators | Outreach, Scribe, Scout, Concierge |
| **Pro** | $79/mo | Small businesses | Starter + Builder, Webwright, Harvest |
| **Agency** | $199/mo | Agencies & teams | All 10 + priority support |

The free Community tier is deliberate: it's your top-of-funnel. People try it from
GitHub, love it, and upgrade to the hosted plans so they don't have to run servers
or manage keys. **The product you sell isn't the prompts — it's the convenience of
not self-hosting.**

## How the money flow works
```
User picks a plan on your site
        │
        ▼
Stripe Checkout collects payment ───► Stripe creates a Subscription
        │                                      │
        ▼                                      ▼
Stripe webhook hits your server  ◄──── subscription.created / .updated / .deleted
        │
        ▼
Your DB stores: user → plan tier, status (active / past_due / canceled)
        │
        ▼
When the user runs an agent, server.py checks their tier covers that agent
(the `require_active_subscription` stub in runtime/server.py is where this goes)
```

## Setup steps (Phase 2 — needs your Stripe account)
1. **Create a Stripe account** and switch to live mode when ready.
2. **Create 3 Products** (Starter, Pro, Agency), each with a recurring monthly Price.
   Copy each Price ID into `pricing.json` (`stripe_price_id`).
3. **Add Stripe Checkout** to the website's pricing buttons (one Checkout Session per plan).
4. **Add a webhook** pointing at `POST /stripe/webhook` on your server. Listen for
   `checkout.session.completed`, `customer.subscription.updated`, and
   `customer.subscription.deleted`. Store the resulting tier against the user.
5. **Fill in `require_active_subscription`** in `runtime/server.py` so each `/run`
   call confirms the user's plan covers the requested agent.
6. **Add a Customer Portal** link so users can manage/cancel their own subscriptions.

## Metering (optional)
If you'd rather charge by usage (per message / per run), record each `/run` call and
report quantities to Stripe with metered prices. Start with flat tiers — they're
simpler to sell and easier for customers to understand.

## What you still need to decide
- A database for users + subscription status (Postgres/SQLite/Supabase all fine).
- Auth (email magic links or Google sign-in are simplest).
- Where to host the API (`server.py`) — Render, Railway, Fly.io, or a VPS.
