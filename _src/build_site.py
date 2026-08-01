#!/usr/bin/env python3
"""Generate the Elixa site in all locales from content.{en,pt,es}.json.
English at root (/), Portuguese at /pt/, Spanish at /es/. Adds hreflang alternates
+ a language switcher + correct lang attribute per page. Static, no build step at serve time."""
import json, os

# Repo-relative: this script lives in <repo>/_src/, the site root is its parent, and the
# content JSONs sit beside it. (Overridable via ELIXA_SITE_ROOT / ELIXA_SRC for CI.)
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("ELIXA_SITE_ROOT", os.path.dirname(_SRC_DIR))
_CONTENT_DIR = os.environ.get("ELIXA_SRC", _SRC_DIR)
SITE = "https://elixagame.com"
LOCALES = [("en", ""), ("pt", "/pt"), ("es", "/es")]  # (code, url-prefix)
PAGE_PATHS = {  # page-type -> path suffix (locale-prefixed at build)
    "home": "/", "legal": "/legal/", "privacy": "/privacy/",
    "support": "/support/", "terms": "/terms/",
}
CONTENT = {code: json.load(open(os.path.join(_CONTENT_DIR, f"content.{code}.json"))) for code, _ in LOCALES}

FONTS = ('  <link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">')

def base(code):
    return dict(LOCALES)[code]

def url(code, page):
    return base(code) + PAGE_PATHS[page]

def hreflang(page):
    out = []
    for code, _ in LOCALES:
        hl = CONTENT[code]["_htmllang"]
        out.append(f'  <link rel="alternate" hreflang="{hl}" href="{SITE}{url(code,page)}">')
    out.append(f'  <link rel="alternate" hreflang="x-default" href="{SITE}{url("en",page)}">')
    return "\n".join(out)

def lang_switch(code, page):
    labels = {"en": "EN", "pt": "PT", "es": "ES"}
    out = ['      <div class="lang-switch">']
    for c, _ in LOCALES:
        cur = ' aria-current="page"' if c == code else ''
        out.append(f'        <a href="{url(c,page)}" hreflang="{CONTENT[c]["_htmllang"]}"{cur}>{labels[c]}</a>')
    out.append('      </div>')
    return "\n".join(out)

def header(code, page, nav_links):
    C = CONTENT[code]; b = base(code)
    links = "\n".join(f'        <a href="{href}">{label}</a>' for label, href in nav_links)
    return f'''  <a class="skip" href="#main">{C["common"]["skip"]}</a>
  <header class="site-header">
    <div class="inner">
      <a class="wordmark" href="{b}/"><img src="/assets/img/flask.png" alt="" width="34" height="34">ELIXA</a>
      <nav class="site-nav">
{links}
{lang_switch(code, page)}
      </nav>
    </div>
  </header>'''

def footer(code):
    C = CONTENT[code]; b = base(code); N = C["nav"]
    return f'''  <footer class="site-footer">
    <div class="inner">
      <a class="wordmark" href="{b}/" style="font-size:17px"><img src="/assets/img/flask.png" alt="" width="28" height="28">ELIXA</a>
      <nav class="fnav">
        <a href="{b}/privacy/">{N["privacy"]}</a>
        <a href="{b}/support/">{N["support"]}</a>
        <a href="{b}/terms/">{N["terms"]}</a>
        <a href="mailto:mateusl.amaral@gmail.com">{N["contact"]}</a>
      </nav>
      <p class="copy">{C["common"]["copy"]}</p>
    </div>
  </footer>'''

APPLE = '<svg class="ico" viewBox="0 0 24 24" width="22" height="22" fill="currentColor" aria-hidden="true"><path d="M17.05 12.54c-.02-2.3 1.88-3.4 1.96-3.45-1.07-1.56-2.73-1.78-3.32-1.8-1.41-.14-2.76.83-3.47.83-.72 0-1.82-.81-2.99-.79-1.54.02-2.96.9-3.75 2.28-1.6 2.78-.41 6.89 1.15 9.15.76 1.1 1.67 2.34 2.86 2.3 1.15-.05 1.58-.74 2.97-.74 1.38 0 1.77.74 2.98.72 1.23-.02 2.01-1.12 2.76-2.23.87-1.28 1.23-2.52 1.25-2.58-.03-.01-2.4-.92-2.43-3.65zM14.8 5.5c.64-.77 1.07-1.85.95-2.92-.92.04-2.03.61-2.69 1.38-.59.68-1.11 1.78-.97 2.83 1.03.08 2.07-.52 2.71-1.29z"/></svg>'
PLAY = '<svg class="ico" viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true"><path d="M4 3.5v17l13-8.5z"/></svg>'

def store_pills(code):
    C = CONTENT[code]; cs = C["common"]["coming_soon"]
    return f'''<div class="store-row">
          <span class="store-btn soon" role="img" aria-label="App Store: {cs}">{APPLE}<span><span class="l1">{cs}</span><br><span class="l2">App&nbsp;Store</span></span></span>
          <span class="store-btn soon" role="img" aria-label="Google Play: {cs}">{PLAY}<span><span class="l1">{cs}</span><br><span class="l2">Google&nbsp;Play</span></span></span>
        </div>'''

def build_home(code):
    C = CONTENT[code]; H = C["home"]; b = base(code); EL = C["elements"]
    nav = [(C["nav"]["features"], f"{b}/#features"), (C["nav"]["elements"], f"{b}/#elements")]
    feats = "\n".join(
        f'''        <div class="card">
          <h3>{f["t"]}</h3>
          <p>{f["b"]}</p>
        </div>''' for f in H["feat"])
    els = "\n".join(
        f'''        <div class="el" style="--c:var(--{k})"><img src="/assets/img/ore/{k}.png" alt="" width="72" height="72" loading="lazy"><div class="name">{EL[k]}</div></div>'''
        for k in ["fire","water","earth","light","darkness","air","spirit"])
    promise = "\n".join(f'        <li>{p}</li>' for p in H["promise_items"])
    html = f'''<!DOCTYPE html>
<html lang="{C["_htmllang"]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{H["meta_title"]}</title>
  <meta name="description" content="{H["meta_desc"]}">
  <link rel="canonical" href="{SITE}{url(code,"home")}">
  <meta property="og:title" content="{H["og_title"]}">
  <meta property="og:description" content="{H["og_desc"]}">
  <meta property="og:url" content="{SITE}{url(code,"home")}">
  <meta property="og:image" content="{SITE}/assets/img/hero.jpg">
  <meta property="og:type" content="website">
  <meta name="theme-color" content="#0b0914">
{hreflang("home")}
{FONTS}
  <link rel="icon" href="/assets/img/flask.png">
  <link rel="stylesheet" href="/assets/css/styles.css">
</head>
<body>
{header(code, "home", nav)}

  <main id="main">
  <section class="hero">
    <div class="hero-bg"><img src="/assets/img/hero.jpg" alt="{H["hero_tagline"][:60]}" fetchpriority="high" width="1600" height="900"></div>
    <div class="hero-content">
      <h1 class="brandmark">ELIXA</h1>
      <p class="kicker">{C["common"]["elemental_sort"]}</p>
      <p class="tagline">{H["hero_tagline"]}</p>
      <div class="cta-row">
        {store_pills(code)}
      </div>
    </div>
  </section>

  <section class="section" id="about">
    <div class="inner center">
      <p class="eyebrow">{H["about_eyebrow"]}</p>
      <h2 class="title">{H["about_h2"]}</h2>
      <p class="lead prose" style="margin:0 auto">{H["about_lead"]}</p>
    </div>
  </section>

  <section class="section" id="features" style="background:var(--bg1)">
    <div class="inner">
      <h2 class="title">{H["feat_h2"]}</h2>
      <div class="grid grid-3" style="margin-top:var(--s7)">
{feats}
      </div>
    </div>
  </section>

  <section class="section" id="elements">
    <div class="inner">
      <h2 class="title center">{H["el_h2"]}</h2>
      <div class="elements" style="margin-top:var(--s7)">
{els}
      </div>
    </div>
  </section>

  <section class="section" id="gallery">
    <div class="inner center">
      <h2 class="title">{H["gal_h2"]}</h2>
      <div class="gallery" style="margin-top:var(--s7)">
        <figure class="phone" style="margin:0"><img src="/assets/img/shots/menu.jpg" alt="{H["gal_cap3"]}" width="646" height="1400" loading="lazy"><figcaption class="cap">{H["gal_cap3"]}</figcaption></figure>
        <figure class="phone" style="margin:0"><img src="/assets/img/shots/level24.jpg" alt="{H["gal_cap1"]}" width="646" height="1400" loading="lazy"><figcaption class="cap">{H["gal_cap1"]}</figcaption></figure>
        <figure class="phone" style="margin:0"><img src="/assets/img/shots/level8.jpg" alt="{H["gal_cap2"]}" width="646" height="1400" loading="lazy"><figcaption class="cap">{H["gal_cap2"]}</figcaption></figure>
      </div>
    </div>
  </section>

  <section class="section band" id="promise">
    <div class="inner center">
      <p class="eyebrow">{H["promise_eyebrow"]}</p>
      <h2 class="title">{H["promise_h2"]}</h2>
      <p class="lead prose" style="margin:0 auto">{H["promise_lead"]}</p>
      <ul class="promise-list prose" style="margin-left:auto;margin-right:auto">
{promise}
      </ul>
    </div>
  </section>

  <section class="section" id="coming-soon">
    <div class="inner center">
      <h2 class="title">{H["coming_h2"]}</h2>
      <p class="lead prose" style="margin:0 auto">{H["coming_lead_pre"]}<a href="mailto:mateusl.amaral@gmail.com?subject=Elixa%20beta">{H["coming_lead_link"]}</a>{H["coming_lead_post"]}</p>
      <div style="margin-top:var(--s7)">
        {store_pills(code)}
      </div>
    </div>
  </section>
  </main>

{footer(code)}
</body>
</html>
'''
    write(code, "home", html)

def build_doc(code, page):
    C = CONTENT[code]; P = C[page]; b = base(code)
    nav = [(C["nav"]["features"], f"{b}/#features"), (C["nav"]["elements"], f"{b}/#elements"),
           (C["nav"]["privacy"], f"{b}/privacy/")]
    if page == "legal":
        bodyhtml = f'''    <p class="lead">{P["lead"]}</p>
    <div class="card">
      <p style="margin:0 0 12px"><a href="{b}/privacy/">{P["card_privacy"]}</a></p>
      <p style="margin:0 0 12px"><a href="{b}/support/">{P["card_support"]}</a></p>
      <p style="margin:0"><a href="{b}/terms/">{P["card_terms"]}</a></p>
    </div>
    <p>{P["note"]}</p>'''
        back = ""
    else:
        body = P["body"].replace("{PRIVACY}", f"{b}/privacy/")
        bodyhtml = "    " + body
        back = f'    <a class="back" href="{b}/legal/">&larr; {C["nav"]["legal"] if False else C["common"]["back_legal"]}</a>\n'
    updated = f'    <p class="updated">{P["updated"]}</p>\n' if P.get("updated") else ''
    html = f'''<!DOCTYPE html>
<html lang="{C["_htmllang"]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{P["meta_title"]}</title>
  <meta name="description" content="{P["meta_desc"]}">
  <link rel="canonical" href="{SITE}{url(code,page)}">
  <meta name="theme-color" content="#0b0914">
{hreflang(page)}
{FONTS}
  <link rel="icon" href="/assets/img/flask.png">
  <link rel="stylesheet" href="/assets/css/styles.css">
</head>
<body>
{header(code, page, nav)}

  <main class="doc" id="main">
    <a class="back" href="{b}/">&larr; {C["common"]["back_home"]}</a>
    <h1>{P["h1"]}</h1>
{updated}{bodyhtml}
  </main>

{footer(code)}
</body>
</html>
'''
    write(code, page, html)

def write(code, page, html):
    rel = url(code, page).lstrip("/")
    if rel == "" or rel.endswith("/"):
        rel = rel + "index.html"
    fp = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w").write(html)
    print("wrote", rel)

def build_sitemap():
    urls = []
    for page in PAGE_PATHS:
        for code, _ in LOCALES:
            urls.append(f"  <url><loc>{SITE}{url(code,page)}</loc></url>")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n"
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(xml)
    print("wrote sitemap.xml", len(urls), "urls")

for code, _ in LOCALES:
    build_home(code)
    for page in ["legal", "privacy", "support", "terms"]:
        build_doc(code, page)
build_sitemap()
print("done")
