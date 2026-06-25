"""Ready-made, high-quality website templates the agents use for NEW sites (anything that is NOT
the user's own gotitsuperstore.co.za). Each is a complete, responsive, self-contained HTML page;
the agent loads one with get_template, swaps in the real content/brand/colors, and publishes it
with create_webpage. Agents can switch between templates on request."""

_BASE_HEAD = (
    "<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
)

TEMPLATES = {
    "landing": {
        "desc": "Modern SaaS / product landing — dark hero, gradient accent, feature grid, CTA. Great for apps, tools, startups.",
        "html": """<!doctype html><html lang="en"><head>__HEAD__<title>Brandname — Tagline</title>
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
<body><header><div class="logo">Brandname</div><nav class="nav"><a href="#features">Features</a><a href="#cta">Pricing</a><a class="btn" href="#cta">Get started</a></nav></header>
<section class="hero"><h1>The one-line promise of your product</h1><p>A short, punchy subheading that explains the value in plain language and who it's for.</p><a class="btn" href="#cta">Start free →</a></section>
<section id="features" class="wrap"><div class="grid">
<div class="card"><h3>⚡ Fast</h3><p>Describe the first key benefit in one clear sentence.</p></div>
<div class="card"><h3>🔒 Secure</h3><p>Describe the second benefit your customers care about.</p></div>
<div class="card"><h3>🤝 Simple</h3><p>Describe the third benefit and why it beats alternatives.</p></div>
</div></section>
<section id="cta" class="wrap"><div class="cta"><h2>Ready to get started?</h2><p style="color:var(--mut)">One last persuasive line.</p><a class="btn" href="#">Get started free</a></div></section>
<footer>© 2026 Brandname · <a href="#" style="color:var(--accent)">Contact</a></footer></body></html>""",
    },
    "business": {
        "desc": "Clean professional / agency / consultancy — light, navy accent, services + about + contact. Great for firms and service businesses.",
        "html": """<!doctype html><html lang="en"><head>__HEAD__<title>Company — What you do</title>
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
<body><header><div class="logo">Company</div><nav class="nav"><a href="#services">Services</a><a href="#about">About</a><a class="btn" href="#contact">Contact us</a></nav></header>
<section class="hero"><div class="wrap"><h1>A confident statement of what you do</h1><p>One or two sentences on the outcome you deliver and the clients you serve.</p><a class="btn" href="#contact">Book a consultation</a></div></section>
<section id="services" class="wrap sec"><h2>What we do</h2><div class="grid">
<div class="svc"><h3>Service one</h3><p>A clear description of the service and its benefit.</p></div>
<div class="svc"><h3>Service two</h3><p>A clear description of the service and its benefit.</p></div>
<div class="svc"><h3>Service three</h3><p>A clear description of the service and its benefit.</p></div></div></section>
<section id="about" class="wrap sec"><h2>About us</h2><p style="color:var(--mut);max-width:70ch">Two or three sentences on who you are, your track record, and why clients trust you.</p></section>
<footer id="contact"><div class="wrap"><h2 style="color:#fff;margin:0 0 10px">Let's talk</h2><p>hello@company.com · +27 00 000 0000 · <a href="#">LinkedIn</a></p></div></footer></body></html>""",
    },
    "portfolio": {
        "desc": "Bold minimal creative / personal portfolio — big type, dark, project grid. Great for designers, photographers, artists, freelancers.",
        "html": """<!doctype html><html lang="en"><head>__HEAD__<title>Your Name — Portfolio</title>
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
<body><header><div class="logo">Your Name</div><nav class="nav"><a href="#work">Work</a><a href="#contact">Contact</a></nav></header>
<section class="hero"><h1>Creative<br><span>that</span> works.</h1><p>One line on what you make and the kind of work you're looking for.</p></section>
<section id="work" class="wrap"><div class="grid">
<a class="proj" href="#"><div><b>Project One</b><small>Category · 2026</small></div></a>
<a class="proj" href="#"><div><b>Project Two</b><small>Category · 2026</small></div></a>
<a class="proj" href="#"><div><b>Project Three</b><small>Category · 2026</small></div></a>
<a class="proj" href="#"><div><b>Project Four</b><small>Category · 2026</small></div></a></div></section>
<footer id="contact">Let's work together — <a href="mailto:you@email.com">you@email.com</a></footer></body></html>""",
    },
    "restaurant": {
        "desc": "Warm hospitality / local business — inviting hero, menu, hours, location. Great for restaurants, cafés, salons, shops.",
        "html": """<!doctype html><html lang="en"><head>__HEAD__<title>Place — Eat well</title>
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
<body><header><div class="logo">Place</div><nav class="nav"><a href="#menu">Menu</a><a href="#visit">Visit</a><a class="btn" href="#visit">Book a table</a></nav></header>
<section class="hero"><h1>Honest food, warm welcome</h1><p>A short, mouth-watering line about your place and what makes it special.</p><a class="btn" href="#menu">See the menu</a></section>
<section id="menu" class="wrap sec"><h2>Menu</h2><div class="menu">
<div class="item"><div class="row"><span>Dish one</span><span>R000</span></div><small>Short tempting description.</small></div>
<div class="item"><div class="row"><span>Dish two</span><span>R000</span></div><small>Short tempting description.</small></div>
<div class="item"><div class="row"><span>Dish three</span><span>R000</span></div><small>Short tempting description.</small></div></div></section>
<section id="visit" class="wrap sec"><h2>Visit us</h2><div class="hours"><p><b>Open</b><br>Mon–Fri 9–22 · Sat–Sun 10–23</p><p>123 Street, City · +27 00 000 0000</p></div></section>
<footer>© 2026 Place · Made with love</footer></body></html>""",
    },
    "event": {
        "desc": "Event / launch one-pager — bold hero, date, schedule, RSVP. Great for launches, conferences, parties, releases.",
        "html": """<!doctype html><html lang="en"><head>__HEAD__<title>Event — Date</title>
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
<body><section class="hero"><span class="pill">EVENT · CITY</span><h1>Event Name</h1><p>One line on what it is · <b style="color:var(--ink)">Saturday, 00 Month 2026</b></p><a class="btn" href="#rsvp">RSVP free →</a></section>
<section class="wrap"><div class="sched">
<div class="slot"><span>Doors open & welcome</span><b>18:00</b></div>
<div class="slot"><span>Main session / headline act</span><b>19:00</b></div>
<div class="slot"><span>Networking & close</span><b>21:00</b></div></div></section>
<footer id="rsvp">RSVP: hello@event.com · @eventhandle</footer></body></html>""",
    },
}


def names():
    return [{"name": k, "desc": v["desc"]} for k, v in TEMPLATES.items()]


def get(name):
    t = TEMPLATES.get((name or "").strip().lower())
    return t["html"].replace("__HEAD__", _BASE_HEAD) if t else None
