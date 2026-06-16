# Selling Decagent

You asked to "store, run and sell on GitHub." Here's the honest map of how that
actually works, because GitHub itself is **not a store** — but it's a powerful part
of the machine.

## What GitHub is good for here
- **Storing & versioning** the product (you're doing this now). ✅
- **Credibility & discovery.** A clean public repo with a great README is free
  marketing. Developers find it, star it, and share it.
- **Distribution of the free tier.** People clone it and self-host. That's your funnel.
- **What GitHub is NOT:** a subscription billing system. You can't charge a recurring
  fee "on GitHub" for arbitrary agents. GitHub Sponsors and GitHub Marketplace exist,
  but Marketplace is for Actions/Apps, not a general agent store.

## The two-repo strategy (recommended)
1. **Public repo — `decagent`** (this one): the free Community tier. Full agent
   definitions, runtime, docs. This is your storefront and top-of-funnel.
2. **Private repo — `decagent-pro`** (optional): premium agents, advanced tools,
   priority updates. Sell access to it (see below).

## Where the money actually comes from — ranked
1. **Your subscription website (primary).** You host the agents; customers pay
   monthly to use them without touching code or keys. This is the real business.
   Everything in `billing/` and `website/` supports this.
2. **Paid access to the private repo / one-time license.** Sell with:
   - **Polar** (polar.sh) — built for developers, handles GitHub repo access + subs.
   - **Gumroad** — dead-simple one-time or subscription sales of a downloadable.
   - **Lemon Squeezy** — merchant-of-record, handles global tax for you.
3. **Done-for-you / custom agents.** Charge to build a customer a bespoke agent.
4. **GitHub Sponsors.** Recurring support from fans of the free tier. Nice-to-have, not the engine.

## Pricing recap
Free (self-host) → Starter $29 → Pro $79 → Agency $199. See `billing/pricing.json`.
The free tier is the magnet; the hosted convenience is what people pay for.

## Getting customers (go-to-market)
You were already researching traffic channels — good instinct. Beyond Google/SEO,
these drive *targeted* traffic without ad spend:

- **Reddit** — the highest-intent channel for tools like this. Be genuinely useful in
  subreddits like r/Entrepreneur, r/SaaS, r/smallbusiness, r/artificial, r/SideProject.
  Show results, don't spam. Reddit removes low-effort self-promo fast (Broadcast agent knows this).
- **Medium** — publish "how I built X with an agent" stories; rank in Google and on Medium's network.
- **Flipboard** — syndicate those articles to reach curated-interest audiences.
- **Product Hunt** — launch the website here for a concentrated traffic spike + backlinks.
- **Hacker News (Show HN)** — the public GitHub repo is perfect for this crowd.
- **X / LinkedIn** — build in public; post each agent's wins. (Let Broadcast run this.)
- **YouTube / TikTok demos** — short "watch this agent do X in 30 seconds" clips convert well.

## A simple launch sequence
1. Publish the public repo (done) and polish the README.
2. Stand up the website + waitlist or live checkout.
3. Write 3 Medium posts (one per use case) → syndicate to Flipboard.
4. Post genuinely-helpful answers in 3-4 relevant subreddits, linking only when it fits.
5. Launch on Product Hunt + Show HN the same week for a spike.
6. Let the free tier do the rest: every self-hoster is a potential upgrade.
