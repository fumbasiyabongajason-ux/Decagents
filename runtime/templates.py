"""Ready-made, high-quality website templates for NEW sites (anything that is NOT the user's own
gotitsuperstore.co.za). Each is a complete, responsive, self-contained styled HTML page that uses
{{TOKEN}} placeholders for the editable text. The agent picks one and calls build_site with a
`fields` object of real text — the SERVER renders the full styled template (so the agent never has
to re-emit the big HTML, which is what used to strip the styling). Any field the agent omits falls
back to a tasteful default, so a page is always complete and good-looking. Switch designs by
rendering a different template name."""
import re

_BASE_HEAD = (
    "<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
)

TEMPLATES = {
    "landing": {
        "desc": "Modern SaaS / product landing — dark hero, gradient accent, feature grid, CTA. Great for apps, tools, startups.",
        "defaults": {
            "BRAND": "Brandname", "HERO_TITLE": "The one-line promise of your product",
            "HERO_SUB": "A short, punchy subheading that explains the value in plain language and who it's for.",
            "CTA_LABEL": "Start free →",
            "F1_TITLE": "⚡ Fast", "F1_TEXT": "Describe the first key benefit in one clear sentence.",
            "F2_TITLE": "🔒 Secure", "F2_TEXT": "Describe the second benefit your customers care about.",
            "F3_TITLE": "🤝 Simple", "F3_TEXT": "Describe the third benefit and why it beats alternatives.",
            "CTA_TITLE": "Ready to get started?", "CTA_TEXT": "One last persuasive line.",
            "FOOTER": "© 2026 Brandname",
        },
        "html": """<!doctype html><html lang="en"><head>__HEAD__<title>{{BRAND}}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
<style>:root{--bg:#0b0d17;--card:#151826;--line:#26293b;--ink:#eef0f6;--mut:#9aa0b4;--accent:#6e8bff;--accent2:#a06bff}
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6}
.wrap{max-width:1080px;margin:0 auto;padding:0 6vw}
header{display:flex;justify-content:space-between;align-items:center;padding:22px 6vw}
.logo{font-weight:800;font-size:20px}.nav a{color:var(--mut);text-decoration:none;margin-left:24px;font-weight:600}
.btn{background:linear-gradient(90deg,var(--accent),var(--accent2));color:#fff;padding:12px 22px;border-radius:10px;text-decoration:none;font-weight:700;display:inline-block}
.hero{text-align:center;padding:90px 6vw 70px}.hero h1{font-size:clamp(34px,6vw,60px);font-weight:800;margin:0 0 18px;letter-spacing:-.02em}
.hero p{color:var(--mut);font-size:20px;max-width:620px;margin:0 auto 34px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px;padding:30px 0 70px}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:28px}
.card h3{margin:0 0 8px;font-size:18px}.card p{color:var(--mut);margin:0}
.cta{text-align:center;background:var(--card);border:1px solid var(--line);border-radius:20px;padding:54px 6vw;margin:0 0 70px}
footer{color:var(--mut);text-align:center;padding:30px;border-top:1px solid var(--line)}</style></head>
<body><header><div class="logo">{{BRAND}}</div><nav class="nav"><a href="#features">Features</a><a href="#cta">Pricing</a><a class="btn" href="#cta">Get started</a></nav></header>
<section class="hero"><h1>{{HERO_TITLE}}</h1><p>{{HERO_SUB}}</p><a class="btn" href="#cta">{{CTA_LABEL}}</a></section>
<section id="features" class="wrap"><div class="grid">
<div class="card"><h3>{{F1_TITLE}}</h3><p>{{F1_TEXT}}</p></div>
<div class="card"><h3>{{F2_TITLE}}</h3><p>{{F2_TEXT}}</p></div>
<div class="card"><h3>{{F3_TITLE}}</h3><p>{{F3_TEXT}}</p></div>
</div></section>
<section id="cta" class="wrap"><div class="cta"><h2>{{CTA_TITLE}}</h2><p style="color:var(--mut)">{{CTA_TEXT}}</p><a class="btn" href="#">{{CTA_LABEL}}</a></div></section>
<footer>{{FOOTER}} · <a href="#" style="color:var(--accent)">Contact</a></footer></body></html>""",
    },
    "business": {
        "desc": "Clean professional / agency / consultancy — light, navy accent, services + about + contact. Great for firms and service businesses.",
        "defaults": {
            "BRAND": "Company", "HERO_TITLE": "A confident statement of what you do",
            "HERO_SUB": "One or two sentences on the outcome you deliver and the clients you serve.",
            "CTA_LABEL": "Book a consultation",
            "S1_TITLE": "Service one", "S1_TEXT": "A clear description of the service and its benefit.",
            "S2_TITLE": "Service two", "S2_TEXT": "A clear description of the service and its benefit.",
            "S3_TITLE": "Service three", "S3_TEXT": "A clear description of the service and its benefit.",
            "ABOUT_TITLE": "About us",
            "ABOUT_TEXT": "Two or three sentences on who you are, your track record, and why clients trust you.",
            "CONTACT_TITLE": "Let's talk", "CONTACT_LINE": "hello@company.com · +27 00 000 0000",
        },
        "html": """<!doctype html><html lang="en"><head>__HEAD__<title>{{BRAND}}</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=DM+Serif+Display&display=swap" rel="stylesheet">
<style>:root{--navy:#0f2a4a;--accent:#1c64f2;--ink:#1b2330;--mut:#5b6577;--bg:#ffffff;--soft:#f4f7fb;--line:#e4e9f0}
*{box-sizing:border-box}body{margin:0;font-family:'DM Sans',system-ui,sans-serif;color:var(--ink);background:var(--bg);line-height:1.65}
.wrap{max-width:1080px;margin:0 auto;padding:0 6vw}h1,h2{font-family:'DM Serif Display',serif;font-weight:400}
header{display:flex;justify-content:space-between;align-items:center;padding:22px 6vw;border-bottom:1px solid var(--line)}
.logo{font-family:'DM Serif Display',serif;font-size:24px;color:var(--navy)}.nav a{color:var(--mut);text-decoration:none;margin-left:26px;font-weight:500}
.btn{background:var(--accent);color:#fff;padding:12px 22px;border-radius:8px;text-decoration:none;font-weight:700}
.hero{padding:80px 6vw;background:var(--soft)}.hero h1{font-size:clamp(32px,5vw,52px);color:var(--navy);margin:0 0 16px;max-width:14ch}
.hero p{color:var(--mut);font-size:19px;max-width:60ch;margin:0 0 28px}
.sec{padding:64px 0}.sec h2{font-size:32px;color:var(--navy);margin:0 0 28px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:24px}
.svc{border:1px solid var(--line);border-radius:14px;padding:26px}.svc h3{margin:0 0 8px;color:var(--navy)}.svc p{color:var(--mut);margin:0}
footer{background:var(--navy);color:#cbd6e6;padding:40px 6vw}footer a{color:#fff}</style></head>
<body><header><div class="logo">{{BRAND}}</div><nav class="nav"><a href="#services">Services</a><a href="#about">About</a><a class="btn" href="#contact">Contact us</a></nav></header>
<section class="hero"><div class="wrap"><h1>{{HERO_TITLE}}</h1><p>{{HERO_SUB}}</p><a class="btn" href="#contact">{{CTA_LABEL}}</a></div></section>
<section id="services" class="wrap sec"><h2>What we do</h2><div class="grid">
<div class="svc"><h3>{{S1_TITLE}}</h3><p>{{S1_TEXT}}</p></div>
<div class="svc"><h3>{{S2_TITLE}}</h3><p>{{S2_TEXT}}</p></div>
<div class="svc"><h3>{{S3_TITLE}}</h3><p>{{S3_TEXT}}</p></div></div></section>
<section id="about" class="wrap sec"><h2>{{ABOUT_TITLE}}</h2><p style="color:var(--mut);max-width:70ch">{{ABOUT_TEXT}}</p></section>
<footer id="contact"><div class="wrap"><h2 style="color:#fff;margin:0 0 10px">{{CONTACT_TITLE}}</h2><p>{{CONTACT_LINE}} · <a href="#">LinkedIn</a></p></div></footer></body></html>""",
    },
    "portfolio": {
        "desc": "Bold minimal creative / personal portfolio — big type, dark, project grid. Great for designers, photographers, artists, freelancers.",
        "defaults": {
            "NAME": "Your Name", "HERO_TITLE": "Creative", "HERO_ACCENT": "that works.",
            "INTRO": "One line on what you make and the kind of work you're looking for.",
            "P1_TITLE": "Project One", "P1_META": "Category · 2026",
            "P2_TITLE": "Project Two", "P2_META": "Category · 2026",
            "P3_TITLE": "Project Three", "P3_META": "Category · 2026",
            "P4_TITLE": "Project Four", "P4_META": "Category · 2026",
            "EMAIL": "you@email.com", "FOOTER_TEXT": "Let's work together —",
        },
        "html": """<!doctype html><html lang="en"><head>__HEAD__<title>{{NAME}} — Portfolio</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet">
<style>:root{--bg:#0a0a0a;--ink:#f2f2f2;--mut:#8a8a8a;--accent:#d6ff3f;--line:#1e1e1e}
*{box-sizing:border-box}body{margin:0;font-family:'Space Grotesk',system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.5}
.wrap{max-width:1100px;margin:0 auto;padding:0 6vw}
header{display:flex;justify-content:space-between;align-items:center;padding:26px 6vw}.logo{font-weight:700}
.nav a{color:var(--mut);text-decoration:none;margin-left:24px}
.hero{padding:90px 6vw 50px}.hero h1{font-size:clamp(40px,9vw,96px);line-height:.98;margin:0;letter-spacing:-.03em}
.hero h1 span{color:var(--accent)}.hero p{color:var(--mut);font-size:20px;max-width:50ch;margin:24px 0 0}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;padding:50px 0 70px}
.proj{background:#121212;border:1px solid var(--line);border-radius:14px;aspect-ratio:4/3;display:flex;align-items:flex-end;padding:22px;text-decoration:none;color:var(--ink);transition:.2s}
.proj:hover{border-color:var(--accent);transform:translateY(-4px)}.proj b{font-size:20px}.proj small{color:var(--mut);display:block}
footer{border-top:1px solid var(--line);padding:36px 6vw;color:var(--mut)}footer a{color:var(--accent)}</style></head>
<body><header><div class="logo">{{NAME}}</div><nav class="nav"><a href="#work">Work</a><a href="#contact">Contact</a></nav></header>
<section class="hero"><h1>{{HERO_TITLE}}<br><span>{{HERO_ACCENT}}</span></h1><p>{{INTRO}}</p></section>
<section id="work" class="wrap"><div class="grid">
<a class="proj" href="#"><div><b>{{P1_TITLE}}</b><small>{{P1_META}}</small></div></a>
<a class="proj" href="#"><div><b>{{P2_TITLE}}</b><small>{{P2_META}}</small></div></a>
<a class="proj" href="#"><div><b>{{P3_TITLE}}</b><small>{{P3_META}}</small></div></a>
<a class="proj" href="#"><div><b>{{P4_TITLE}}</b><small>{{P4_META}}</small></div></a></div></section>
<footer id="contact">{{FOOTER_TEXT}} <a href="mailto:{{EMAIL}}">{{EMAIL}}</a></footer></body></html>""",
    },
    "restaurant": {
        "desc": "Warm hospitality / local business — inviting hero, menu, hours, location. Great for restaurants, cafés, salons, shops.",
        "defaults": {
            "BRAND": "Place", "HERO_TITLE": "Honest food, warm welcome",
            "HERO_SUB": "A short, mouth-watering line about your place and what makes it special.",
            "CTA_LABEL": "See the menu",
            "I1_NAME": "Dish one", "I1_PRICE": "R000", "I1_DESC": "Short tempting description.",
            "I2_NAME": "Dish two", "I2_PRICE": "R000", "I2_DESC": "Short tempting description.",
            "I3_NAME": "Dish three", "I3_PRICE": "R000", "I3_DESC": "Short tempting description.",
            "VISIT_TITLE": "Visit us", "HOURS": "Mon–Fri 9–22 · Sat–Sun 10–23",
            "ADDRESS": "123 Street, City · +27 00 000 0000", "FOOTER": "© 2026 Place · Made with love",
        },
        "html": """<!doctype html><html lang="en"><head>__HEAD__<title>{{BRAND}}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;800&family=Nunito+Sans:wght@400;600&display=swap" rel="stylesheet">
<style>:root{--bg:#fbf6ef;--ink:#2a211a;--mut:#7a6c5d;--accent:#c0492b;--card:#fff;--line:#ece3d6}
*{box-sizing:border-box}body{margin:0;font-family:'Nunito Sans',system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.65}
h1,h2,h3{font-family:'Playfair Display',serif}.wrap{max-width:1000px;margin:0 auto;padding:0 6vw}
header{display:flex;justify-content:space-between;align-items:center;padding:22px 6vw}.logo{font-family:'Playfair Display',serif;font-weight:800;font-size:24px;color:var(--accent)}
.nav a{color:var(--ink);text-decoration:none;margin-left:24px;font-weight:600}
.hero{text-align:center;padding:80px 6vw 60px}.hero h1{font-size:clamp(40px,7vw,68px);margin:0 0 14px}.hero p{color:var(--mut);font-size:20px;max-width:50ch;margin:0 auto 26px}
.btn{background:var(--accent);color:#fff;padding:13px 26px;border-radius:30px;text-decoration:none;font-weight:700}
.sec{padding:56px 0}.sec h2{text-align:center;font-size:34px;margin:0 0 30px}
.menu{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px}
.item{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px}.item .row{display:flex;justify-content:space-between;font-weight:600}.item small{color:var(--mut)}
.hours{text-align:center;background:var(--card);border:1px solid var(--line);border-radius:16px;padding:34px;max-width:520px;margin:0 auto}
footer{text-align:center;color:var(--mut);padding:34px}</style></head>
<body><header><div class="logo">{{BRAND}}</div><nav class="nav"><a href="#menu">Menu</a><a href="#visit">Visit</a><a class="btn" href="#visit">Book a table</a></nav></header>
<section class="hero"><h1>{{HERO_TITLE}}</h1><p>{{HERO_SUB}}</p><a class="btn" href="#menu">{{CTA_LABEL}}</a></section>
<section id="menu" class="wrap sec"><h2>Menu</h2><div class="menu">
<div class="item"><div class="row"><span>{{I1_NAME}}</span><span>{{I1_PRICE}}</span></div><small>{{I1_DESC}}</small></div>
<div class="item"><div class="row"><span>{{I2_NAME}}</span><span>{{I2_PRICE}}</span></div><small>{{I2_DESC}}</small></div>
<div class="item"><div class="row"><span>{{I3_NAME}}</span><span>{{I3_PRICE}}</span></div><small>{{I3_DESC}}</small></div></div></section>
<section id="visit" class="wrap sec"><h2>{{VISIT_TITLE}}</h2><div class="hours"><p><b>Open</b><br>{{HOURS}}</p><p>{{ADDRESS}}</p></div></section>
<footer>{{FOOTER}}</footer></body></html>""",
    },
    "event": {
        "desc": "Event / launch one-pager — bold hero, date, schedule, RSVP. Great for launches, conferences, parties, releases.",
        "defaults": {
            "PILL": "EVENT · CITY", "TITLE": "Event Name",
            "SUBLINE": "One line on what it is · Saturday, 00 Month 2026", "CTA_LABEL": "RSVP free →",
            "S1_LABEL": "Doors open & welcome", "S1_TIME": "18:00",
            "S2_LABEL": "Main session / headline act", "S2_TIME": "19:00",
            "S3_LABEL": "Networking & close", "S3_TIME": "21:00",
            "RSVP": "RSVP: hello@event.com · @eventhandle",
        },
        "html": """<!doctype html><html lang="en"><head>__HEAD__<title>{{TITLE}}</title>
<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;800&display=swap" rel="stylesheet">
<style>:root{--bg:#10071f;--ink:#f3eefb;--mut:#b6a9cc;--accent:#ff4d8d;--accent2:#7a5cff;--card:#1c1233;--line:#2e2148}
*{box-sizing:border-box}body{margin:0;font-family:Sora,system-ui,sans-serif;background:radial-gradient(900px 500px at 80% -10%,#2a1650,var(--bg));color:var(--ink);line-height:1.6}
.wrap{max-width:980px;margin:0 auto;padding:0 6vw}
.hero{text-align:center;padding:90px 6vw 50px}.pill{display:inline-block;background:var(--card);border:1px solid var(--line);color:var(--accent);padding:7px 16px;border-radius:30px;font-weight:600;font-size:14px;letter-spacing:.08em}
.hero h1{font-size:clamp(40px,8vw,82px);font-weight:800;margin:18px 0;letter-spacing:-.02em;background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{color:var(--mut);font-size:20px}.btn{background:linear-gradient(90deg,var(--accent),var(--accent2));color:#fff;padding:14px 30px;border-radius:12px;text-decoration:none;font-weight:700;display:inline-block;margin-top:20px}
.sched{display:grid;gap:14px;padding:50px 0 70px;max-width:640px;margin:0 auto}
.slot{display:flex;justify-content:space-between;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 22px}.slot b{color:var(--accent)}
footer{text-align:center;color:var(--mut);padding:30px;border-top:1px solid var(--line)}</style></head>
<body><section class="hero"><span class="pill">{{PILL}}</span><h1>{{TITLE}}</h1><p>{{SUBLINE}}</p><a class="btn" href="#rsvp">{{CTA_LABEL}}</a></section>
<section class="wrap"><div class="sched">
<div class="slot"><span>{{S1_LABEL}}</span><b>{{S1_TIME}}</b></div>
<div class="slot"><span>{{S2_LABEL}}</span><b>{{S2_TIME}}</b></div>
<div class="slot"><span>{{S3_LABEL}}</span><b>{{S3_TIME}}</b></div></div></section>
<footer id="rsvp">{{RSVP}}</footer></body></html>""",
    },
    "blog": {
        "desc": "Blog / magazine — editorial serif, featured story + article grid. Great for writers, publications, news, personal blogs.",
        "defaults": {
            "BRAND": "The Journal", "TAGLINE": "Words worth your time",
            "FEAT_TITLE": "The headline of your featured story",
            "FEAT_EXCERPT": "A compelling two-line standfirst that pulls the reader into the lead article and makes them want to read on.",
            "FEAT_META": "Featured · 6 min read",
            "P1_TITLE": "First article title", "P1_EXCERPT": "A short summary of what this post is about.", "P1_META": "Essays · 4 min",
            "P2_TITLE": "Second article title", "P2_EXCERPT": "A short summary of what this post is about.", "P2_META": "Notes · 3 min",
            "P3_TITLE": "Third article title", "P3_EXCERPT": "A short summary of what this post is about.", "P3_META": "Ideas · 5 min",
            "FOOTER": "© 2026 The Journal · Subscribe for new posts",
        },
        "html": """<!doctype html><html lang="en"><head>__HEAD__<title>{{BRAND}}</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>:root{--bg:#fffdf8;--ink:#1d1b16;--mut:#6b6657;--accent:#9a3412;--line:#eae5d9;--card:#fff}
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.7}
h1,h2,h3{font-family:Fraunces,Georgia,serif;font-weight:600;letter-spacing:-.01em}
.wrap{max-width:1020px;margin:0 auto;padding:0 6vw}
header{text-align:center;padding:40px 6vw 16px;border-bottom:1px solid var(--line)}
.logo{font-family:Fraunces,serif;font-size:34px}.tag{color:var(--mut);font-style:italic;margin-top:4px}
.nav{display:flex;justify-content:center;gap:24px;padding:16px 0 0}.nav a{color:var(--mut);text-decoration:none;font-weight:500;font-size:14px;text-transform:uppercase;letter-spacing:.06em}
.feat{padding:60px 0 30px;border-bottom:1px solid var(--line)}.feat .k{color:var(--accent);font-weight:600;font-size:13px;text-transform:uppercase;letter-spacing:.08em}
.feat h2{font-size:clamp(30px,5vw,48px);margin:10px 0 14px;max-width:18ch}.feat p{color:var(--mut);font-size:20px;max-width:60ch}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:34px;padding:44px 0 70px}
.post .k{color:var(--accent);font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.06em}
.post h3{font-size:22px;margin:8px 0 8px}.post p{color:var(--mut);margin:0}
footer{border-top:1px solid var(--line);text-align:center;color:var(--mut);padding:34px}</style></head>
<body><header><div class="logo">{{BRAND}}</div><div class="tag">{{TAGLINE}}</div>
<nav class="nav"><a href="#">Latest</a><a href="#">Essays</a><a href="#">About</a></nav></header>
<div class="wrap"><section class="feat"><div class="k">{{FEAT_META}}</div><h2>{{FEAT_TITLE}}</h2><p>{{FEAT_EXCERPT}}</p></section>
<section class="grid">
<article class="post"><div class="k">{{P1_META}}</div><h3>{{P1_TITLE}}</h3><p>{{P1_EXCERPT}}</p></article>
<article class="post"><div class="k">{{P2_META}}</div><h3>{{P2_TITLE}}</h3><p>{{P2_EXCERPT}}</p></article>
<article class="post"><div class="k">{{P3_META}}</div><h3>{{P3_TITLE}}</h3><p>{{P3_EXCERPT}}</p></article>
</section></div><footer>{{FOOTER}}</footer></body></html>""",
    },
    "store": {
        "desc": "Online store / e-commerce — product grid with prices and buy buttons. Great for shops, brands, makers selling products.",
        "defaults": {
            "BRAND": "Shop", "HERO_TITLE": "Products you'll love", "HERO_SUB": "A short line about your shop and what makes your products special.",
            "CTA_LABEL": "Shop now",
            "P1_NAME": "Product one", "P1_PRICE": "R000", "P1_DESC": "Short product description.",
            "P2_NAME": "Product two", "P2_PRICE": "R000", "P2_DESC": "Short product description.",
            "P3_NAME": "Product three", "P3_PRICE": "R000", "P3_DESC": "Short product description.",
            "P4_NAME": "Product four", "P4_PRICE": "R000", "P4_DESC": "Short product description.",
            "FOOTER": "© 2026 Shop · Free shipping over R500 · Secure checkout",
        },
        "html": """<!doctype html><html lang="en"><head>__HEAD__<title>{{BRAND}}</title>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&display=swap" rel="stylesheet">
<style>:root{--bg:#ffffff;--ink:#15161a;--mut:#6a6f7a;--accent:#111827;--pop:#e11d48;--line:#ececf0;--soft:#f7f7f9}
*{box-sizing:border-box}body{margin:0;font-family:Manrope,system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.6}
.wrap{max-width:1100px;margin:0 auto;padding:0 5vw}
header{display:flex;justify-content:space-between;align-items:center;padding:20px 5vw;border-bottom:1px solid var(--line)}
.logo{font-weight:800;font-size:21px}.nav a{color:var(--mut);text-decoration:none;margin-left:22px;font-weight:600}
.cart{background:var(--accent);color:#fff;padding:9px 16px;border-radius:9px;font-weight:700;text-decoration:none}
.hero{text-align:center;padding:70px 5vw;background:var(--soft)}.hero h1{font-size:clamp(32px,5vw,52px);margin:0 0 12px}.hero p{color:var(--mut);font-size:19px;max-width:54ch;margin:0 auto 24px}
.btn{background:var(--pop);color:#fff;padding:13px 26px;border-radius:10px;text-decoration:none;font-weight:700}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:26px;padding:54px 0 70px}
.prod{border:1px solid var(--line);border-radius:14px;overflow:hidden}
.prod .ph{height:180px;background:linear-gradient(135deg,#f0f0f4,#e2e2ea)}
.prod .b{padding:16px}.prod h3{margin:0 0 4px;font-size:17px}.prod .desc{color:var(--mut);font-size:14px;margin:0 0 12px}
.prod .row{display:flex;justify-content:space-between;align-items:center}.prod .price{font-weight:800}
.add{background:var(--accent);color:#fff;border:0;padding:8px 14px;border-radius:8px;font-weight:700;text-decoration:none;font-size:14px}
footer{border-top:1px solid var(--line);text-align:center;color:var(--mut);padding:30px}</style></head>
<body><header><div class="logo">{{BRAND}}</div><nav class="nav"><a href="#shop">Shop</a><a href="#">About</a><a class="cart" href="#shop">Cart</a></nav></header>
<section class="hero"><h1>{{HERO_TITLE}}</h1><p>{{HERO_SUB}}</p><a class="btn" href="#shop">{{CTA_LABEL}}</a></section>
<section id="shop" class="wrap"><div class="grid">
<div class="prod"><div class="ph"></div><div class="b"><h3>{{P1_NAME}}</h3><div class="desc">{{P1_DESC}}</div><div class="row"><span class="price">{{P1_PRICE}}</span><a class="add" href="#">Add to cart</a></div></div></div>
<div class="prod"><div class="ph"></div><div class="b"><h3>{{P2_NAME}}</h3><div class="desc">{{P2_DESC}}</div><div class="row"><span class="price">{{P2_PRICE}}</span><a class="add" href="#">Add to cart</a></div></div></div>
<div class="prod"><div class="ph"></div><div class="b"><h3>{{P3_NAME}}</h3><div class="desc">{{P3_DESC}}</div><div class="row"><span class="price">{{P3_PRICE}}</span><a class="add" href="#">Add to cart</a></div></div></div>
<div class="prod"><div class="ph"></div><div class="b"><h3>{{P4_NAME}}</h3><div class="desc">{{P4_DESC}}</div><div class="row"><span class="price">{{P4_PRICE}}</span><a class="add" href="#">Add to cart</a></div></div></div>
</div></section><footer>{{FOOTER}}</footer></body></html>""",
    },
    "nonprofit": {
        "desc": "Nonprofit / charity / cause — mission hero, impact stats, donate CTA. Great for NGOs, foundations, community causes.",
        "defaults": {
            "BRAND": "Cause", "HERO_TITLE": "Together we can make a difference",
            "HERO_SUB": "One or two sentences on your mission and the change you're working toward.",
            "DONATE_LABEL": "Donate now",
            "STAT1_NUM": "10,000+", "STAT1_LABEL": "people helped",
            "STAT2_NUM": "120", "STAT2_LABEL": "volunteers",
            "STAT3_NUM": "15", "STAT3_LABEL": "communities served",
            "ABOUT_TITLE": "Our mission",
            "ABOUT_TEXT": "Two or three sentences on who you are, the problem you tackle, and how donations and volunteers create real impact.",
            "CONTACT_LINE": "hello@cause.org · +27 00 000 0000",
        },
        "html": """<!doctype html><html lang="en"><head>__HEAD__<title>{{BRAND}}</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;700;800&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>:root{--bg:#f3faf7;--ink:#102a23;--mut:#4f6b62;--accent:#0e8f6e;--accent2:#0b6b8f;--card:#fff;--line:#d9ece4}
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--ink);line-height:1.65}
h1,h2,h3{font-family:Poppins,system-ui,sans-serif;font-weight:800}
.wrap{max-width:1040px;margin:0 auto;padding:0 6vw}
header{display:flex;justify-content:space-between;align-items:center;padding:20px 6vw}
.logo{font-family:Poppins,sans-serif;font-weight:800;font-size:21px;color:var(--accent)}
.nav a{color:var(--ink);text-decoration:none;margin-left:22px;font-weight:600}
.btn{background:var(--accent);color:#fff;padding:12px 22px;border-radius:30px;text-decoration:none;font-weight:700}
.hero{padding:80px 6vw;background:linear-gradient(135deg,#e7f6ef,#e3f0f6)}
.hero h1{font-size:clamp(32px,5.5vw,54px);margin:0 0 16px;max-width:16ch}.hero p{color:var(--mut);font-size:20px;max-width:58ch;margin:0 0 28px}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;padding:54px 0}
.stat{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:28px;text-align:center}
.stat .n{font-family:Poppins,sans-serif;font-weight:800;font-size:34px;color:var(--accent)}.stat .l{color:var(--mut);margin-top:4px}
.about{padding:20px 0 60px}.about h2{font-size:30px;color:var(--accent2);margin:0 0 14px}.about p{color:var(--mut);max-width:70ch;font-size:18px}
footer{background:var(--accent);color:#eafff7;padding:40px 6vw;text-align:center}footer a{color:#fff}
@media(max-width:640px){.stats{grid-template-columns:1fr}}</style></head>
<body><header><div class="logo">{{BRAND}}</div><nav class="nav"><a href="#mission">Mission</a><a href="#contact">Contact</a><a class="btn" href="#donate">{{DONATE_LABEL}}</a></nav></header>
<section class="hero"><h1>{{HERO_TITLE}}</h1><p>{{HERO_SUB}}</p><a class="btn" href="#donate">{{DONATE_LABEL}}</a></section>
<div class="wrap"><section class="stats">
<div class="stat"><div class="n">{{STAT1_NUM}}</div><div class="l">{{STAT1_LABEL}}</div></div>
<div class="stat"><div class="n">{{STAT2_NUM}}</div><div class="l">{{STAT2_LABEL}}</div></div>
<div class="stat"><div class="n">{{STAT3_NUM}}</div><div class="l">{{STAT3_LABEL}}</div></div>
</section><section id="mission" class="about"><h2>{{ABOUT_TITLE}}</h2><p>{{ABOUT_TEXT}}</p></section></div>
<footer id="contact"><h2 id="donate" style="color:#fff;margin:0 0 10px">{{DONATE_LABEL}}</h2><p>{{CONTACT_LINE}} · <a href="#">Volunteer</a></p></footer></body></html>""",
    },
}


def names():
    """Template name + what it's best for + the fields you can fill (for build_site)."""
    return [{"name": k, "desc": v["desc"], "fields": sorted(v["defaults"].keys())}
            for k, v in TEMPLATES.items()]


def fields(name):
    t = TEMPLATES.get((name or "").strip().lower())
    return dict(t["defaults"]) if t else None


def render(name, values=None):
    """Render a template's FULL styled HTML, filling {{TOKEN}}s from `values` (a flat dict of
    token -> text). Any token not supplied uses the template's tasteful default, and any leftover
    token is blanked, so the page is always complete and never shows a raw {{TOKEN}}."""
    t = TEMPLATES.get((name or "").strip().lower())
    if not t:
        return None
    vals = {k.upper(): v for k, v in t["defaults"].items()}
    if isinstance(values, dict):
        for k, v in values.items():
            if v is None:
                continue
            vals[str(k).strip().upper()] = str(v)
    html = t["html"].replace("__HEAD__", _BASE_HEAD)
    html = re.sub(r"\{\{\s*([A-Za-z0-9_]+)\s*\}\}",
                  lambda m: vals.get(m.group(1).strip().upper(), ""), html)
    return html


def get(name):
    """Backward-compat: full styled HTML with default content (a finished preview of the template)."""
    return render(name, None)
