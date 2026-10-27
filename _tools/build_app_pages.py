#!/usr/bin/env python3
"""
Builds thunderapps.xyz from _tools/apps.json and keeps the shared parts of every page in sync.

    python3 _tools/build_app_pages.py

1. Writes, at the site root:
     apps.html          the "Our Apps" page
     <slug>.html        one App Store-style product page per app

2. Refreshes the shared blocks inside every other page at the root. Each block sits between
   a pair of comment markers, and everything between the markers is replaced:

     <!-- site:head -->      ... <!-- /site:head -->      fonts, icons, stylesheet
     <!-- site:nav -->       ... <!-- /site:nav -->       top navigation (active link per page)
     <!-- site:footer -->    ... <!-- /site:footer -->    footer, back-to-top, script
     <!-- apps:feature -->   ... <!-- /apps:feature -->   home "App of the Day" card (first app)
     <!-- apps:list -->      ... <!-- /apps:list -->      home app list with Get buttons
     <!-- apps:icons -->     ... <!-- /apps:icons -->     home icon mosaic
     <!-- apps:inside -->    ... <!-- /apps:inside -->    "Inside our apps" cards (from each app's "inside" list)

   So a change to the nav, the footer or the app list is made once, here, and lands everywhere.
   Write page content (anything outside the markers) by hand as usual.

To add an app: add an entry to apps.json and run the script again.
Folders starting with "_" are ignored by GitHub Pages, so this tool never ships.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://thunderapps.xyz"
EMAIL = "info@thunderapps.xyz"
LOCATION = "Dhaka, Bangladesh"

e = html.escape  # every piece of text from apps.json goes through this

# Pages that must never be touched by the sync step.
SKIP = {"documentscannerstudio.html"}

# Which nav item is highlighted on which page. Product pages count as "apps".
# Pages not listed here (services, team, testimonial, legal, 404) aren't in the top menu;
# they're reached from the footer and from links on the home page.
ACTIVE = {
    "index.html": "home",
    "about.html": "about",
    "apps.html": "apps",
    "contact.html": "contact",
}

CATEGORY_ICONS = {
    "Productivity": "fa-briefcase",
    "Food & Drink": "fa-utensils",
    "Lifestyle": "fa-spa",
    "Finance": "fa-chart-pie",
}


# ---------------------------------------------------------------------------
# Shared chrome
# ---------------------------------------------------------------------------

def brand_mark(base=""):
    """The Thunder Apps logo as a 3D app-icon tile. Rebuild it with _tools/make_logo_tile.py."""
    return (f'<img class="brand-mark" src="{base}img/brand/thunder-apps-icon-3d-144.png" '
            f'alt="" width="36" height="36" decoding="async">')


def head_assets(base="", studio_meta=True):
    """studio_meta=False on app product pages: they carry the app's own share image and touch icon."""
    meta = f"""
    <link rel="apple-touch-icon" href="{base}img/brand/apple-touch-icon.png">
    <meta property="og:image" content="{SITE}/img/brand/thunder-apps-logo.png">""" if studio_meta else ""
    return f"""
    <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
    <meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">
    <link rel="icon" type="image/png" sizes="32x32" href="{base}img/brand/favicon-32.png">
    <link rel="icon" type="image/png" sizes="192x192" href="{base}img/brand/favicon-192.png">{meta}

    <!-- Inter is only a fallback: Apple devices use the system font (SF Pro) -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <!-- Icons -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.10.0/css/all.min.css" rel="stylesheet">

    <link href="{base}css/site.css" rel="stylesheet">
    """


def nav(active, base=""):
    def link(href, label, key):
        on = active == key
        cls = "nav-link is-active" if on else "nav-link"
        cur = ' aria-current="page"' if on else ""
        return f'<li><a href="{base}{href}" class="{cls}"{cur}>{label}</a></li>'

    return f"""
    <a class="skip-link" href="#main">Skip to content</a>
    <header class="nav">
        <div class="wrap nav-inner">
            <a href="{base}index.html" class="brand" aria-label="Thunder Apps Studio home">{brand_mark(base)}<span>Thunder Apps Studio</span></a>
            <button type="button" class="nav-toggle" aria-expanded="false" aria-controls="nav-links" aria-label="Menu">
                <span></span><span></span><span></span>
            </button>
            <ul class="nav-links" id="nav-links">
                {link("index.html", "Home", "home")}
                {link("about.html", "About", "about")}
                {link("apps.html", "Apps", "apps")}
                {link("contact.html", "Contact", "contact")}
            </ul>
            <a href="mailto:{EMAIL}" class="btn btn-tinted btn-sm nav-call" title="{EMAIL}"><i class="fas fa-envelope" aria-hidden="true"></i>Email us</a>
        </div>
    </header>
    """


def footer(apps, base=""):
    app_links = "\n".join(
        f'                        <li><a href="{base}{a["slug"]}.html">{e(a["name"])}</a></li>' for a in apps)
    return f"""
    <footer class="footer">
        <div class="wrap">
            <div class="footer-top">
                <div class="footer-brand">
                    <a href="{base}index.html" class="brand">{brand_mark(base)}<span>Thunder Apps Studio</span></a>
                    <p class="footer-about">Thunder Apps Studio delivers innovative, user-friendly mobile apps for iOS. Specializing in custom solutions, we create high-quality apps tailored to meet your business needs, ensuring seamless design and exceptional user experiences.</p>
                </div>
                <nav aria-label="Our apps">
                    <h2>Our Apps</h2>
                    <ul>
{app_links}
                        <li><a href="{base}apps.html">All apps</a></li>
                    </ul>
                </nav>
                <nav aria-label="Company">
                    <h2>Company</h2>
                    <ul>
                        <li><a href="{base}about.html">About us</a></li>
                        <li><a href="{base}service.html">Services</a></li>
                        <li><a href="{base}team.html">Our Team</a></li>
                        <li><a href="{base}testimonial.html">Inside our apps</a></li>
                    </ul>
                </nav>
                <nav aria-label="Help">
                    <h2>Help</h2>
                    <ul>
                        <li><a href="{base}contact.html">Contact</a></li>
                        <li><a href="{base}terms.html">Terms and Conditions</a></li>
                        <li><a href="{base}privacy.html">Privacy Policy</a></li>
                    </ul>
                </nav>
                <div>
                    <h2>Contact Us</h2>
                    <ul>
                        <li>{LOCATION}</li>
                        <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <span>Copyright &copy; Thunder Apps Studio. All rights reserved.</span>
                <span><a href="{base}terms.html">Terms</a> &nbsp;|&nbsp; <a href="{base}privacy.html">Privacy</a></span>
            </div>
        </div>
    </footer>

    <button type="button" class="to-top" aria-label="Back to top">
        <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M8 13V3M3.5 7.5 8 3l4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </button>

    <script src="{base}js/site.js" defer></script>
    """


# ---------------------------------------------------------------------------
# App components
# ---------------------------------------------------------------------------

def get_button(app, cls="get"):
    return (f'<a href="{e(app["storeUrl"])}" class="{cls}" target="_blank" rel="noopener" '
            f'aria-label="Get {e(app["name"])} on the App Store">Get</a>')


def store_badge(app):
    return (f'<a href="{e(app["storeUrl"])}" class="store-badge" target="_blank" rel="noopener" '
            f'aria-label="Download {e(app["name"])} on the App Store">'
            f'<i class="fab fa-apple" aria-hidden="true"></i>'
            f'<span><small>Download on the</small>App Store</span></a>')


def app_row(app, base=""):
    return f"""<div class="app-row">
                            <img class="app-icon" src="{e(app['icon'])}" alt="" width="64" height="64" loading="lazy" decoding="async">
                            <div class="app-row-body">
                                <div class="app-row-text">
                                    <div class="app-row-name"><a href="{base}{app['slug']}.html">{e(app['name'])}</a></div>
                                    <div class="app-row-sub">{e(app['subtitle'])}</div>
                                    <div class="app-row-cat">{e(app['category'])}</div>
                                </div>
                                {get_button(app)}
                            </div>
                        </div>"""


def app_list(apps, exclude=None):
    rows = "\n".join(f"                    <li>{app_row(a)}</li>" for a in apps if a["slug"] != exclude)
    return f"""
                <ul class="app-list">
{rows}
                </ul>
                """


def app_icons(apps):
    links = "\n".join(
        f'                    <a href="{a["slug"]}.html" aria-label="{e(a["name"])}">'
        f'<img class="app-icon" src="{e(a["icon"])}" alt="" width="150" height="150" loading="lazy" decoding="async"></a>'
        for a in apps[:4])
    return f"""
                <div class="icon-mosaic">
{links}
                </div>
                """


def inside_cards(apps, base=""):
    """What you can do in each app. Cards alternate between apps so the shelf mixes them."""
    rounds = max(len(a.get("inside", [])) for a in apps)
    cards = []
    for i in range(rounds):
        for a in apps:
            items = a.get("inside", [])
            if i >= len(items):
                continue
            it = items[i]
            cards.append(f"""                    <li class="inside-card" style="--app-accent: {e(a['accent'])};">
                        <a class="inside-app" href="{base}{a['slug']}.html"><img class="app-icon" src="{e(a['icon'])}" alt="" width="28" height="28" loading="lazy" decoding="async"><span>{e(a['name'])}</span></a>
                        <h3>{e(it['title'])}</h3>
                        <p>{e(it['text'])}</p>
                        <span class="inside-stat">{e(it['stat'])}</span>
                    </li>""")
    return f"""
                <ul class="shelf" id="inside" data-shelf>
{chr(10).join(cards)}
                </ul>
                """


def feature_story(app):
    """The big App Store "App of the Day" card on the home page."""
    shots = "".join(f'<img src="{e(s)}" alt="" width="600" height="1300" decoding="async">'
                    for s in app["screenshots"][:3])
    return f"""
                <article class="story story-feature rise rise-3" style="--app-accent: {e(app['accent'])};">
                    <a class="story-link" href="{app['slug']}.html" aria-label="{e(app['name'])}: see the app"></a>
                    <div class="story-text">
                        <span class="story-label">App of the Day</span>
                        <h2 class="story-title">{e(app['summary'].split('.')[0])}.</h2>
                    </div>
                    <div class="story-shots" aria-hidden="true">{shots}</div>
                    <div class="story-bar">
                        <img class="app-icon" src="{e(app['icon'])}" alt="" width="44" height="44">
                        <div class="story-bar-text"><strong>{e(app['name'])}</strong><span>{e(app['subtitle'])}</span></div>
                        {get_button(app)}
                    </div>
                </article>
                """


# ---------------------------------------------------------------------------
# Generated pages
# ---------------------------------------------------------------------------

def head(title, description, canonical, extra="", studio_meta=True):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{e(title)}</title>
    <meta content="width=device-width, initial-scale=1.0, viewport-fit=cover" name="viewport">
    <meta name="description" content="{e(description)}">
    <link rel="canonical" href="{canonical}">
    <meta property="og:site_name" content="Thunder Apps Studio">
    <meta property="og:title" content="{e(title)}">
    <meta property="og:description" content="{e(description)}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:type" content="website">
{extra}
    <!-- site:head -->{head_assets(studio_meta=studio_meta)}<!-- /site:head -->
</head>
"""


def body_open(active):
    return f"""
<body>
    <!-- site:nav -->{nav(active)}<!-- /site:nav -->
"""


def body_close(apps):
    return f"""
    <!-- site:footer -->{footer(apps)}<!-- /site:footer -->
</body>

</html>
"""


def crumbs(items):
    lis = "".join(
        f'<li><a href="{href}">{e(label)}</a></li>' if href else f'<li aria-current="page">{e(label)}</li>'
        for label, href in items)
    return f'<nav aria-label="Breadcrumb"><ol class="crumbs">{lis}</ol></nav>'


def product_page(app, apps):
    canonical = f"{SITE}/{app['slug']}"
    title = f"{app['storeName']} | Thunder Apps Studio"
    json_ld = json.dumps({
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": app["storeName"],
        "operatingSystem": "iOS",
        "applicationCategory": app["category"],
        "description": app["summary"],
        "image": app["icon"],
        "url": canonical,
        "downloadUrl": app["storeUrl"],
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "author": {"@type": "Organization", "name": "Thunder Apps Studio", "url": SITE},
    }, indent=2).replace("</", "<\\/")
    extra = (f'    <meta property="og:image" content="{e(app["icon"])}">\n'
             f'    <!-- Smart App Banner: Safari on iPhone shows an "Open / Get" bar for the app -->\n'
             f'    <meta name="apple-itunes-app" content="app-id={app["appId"]}">\n'
             f'    <link rel="apple-touch-icon" href="{e(app["icon"])}">\n'
             f'    <script type="application/ld+json">\n{json_ld}\n    </script>\n')

    lazy = 'loading="lazy" '
    shots = "\n".join(
        f'                    <li><img src="{e(src)}" alt="{e(app["name"])} screenshot {i + 1}" width="600" height="1300" '
        f'{"" if i == 0 else lazy}decoding="async"></li>'
        for i, src in enumerate(app["screenshots"]))
    intro = "\n".join(f'                        <p>{e(p)}</p>' for p in app["intro"])
    highlights = "\n".join(
        f'                        <li><i class="fas fa-check-circle" aria-hidden="true"></i>{e(h)}</li>'
        for h in app["highlights"])
    features = "\n".join(
        f"""                    <li class="tile">
                        <span class="glyph glyph-accent"><i class="fas {e(f['icon'])}" aria-hidden="true"></i></span>
                        <h3>{e(f['title'])}</h3>
                        <p>{e(f['text'])}</p>
                    </li>""" for f in app["features"])
    note = f'<p class="note">{e(app["note"])}</p>' if app.get("note") else ""
    cat_icon = CATEGORY_ICONS.get(app["category"], "fa-th-large")

    return (head(title, app["summary"], canonical, extra, studio_meta=False) + body_open("apps") + f"""
    <main id="main" style="--app-accent: {e(app['accent'])};">
        <div class="wrap">
            <div class="page-head" style="padding-bottom: 0;">
                {crumbs([("Home", "index.html"), ("Apps", "apps.html"), (app["name"], None)])}
            </div>

            <!-- Header: icon, name, Get -->
            <section class="product-head" aria-labelledby="app-title">
                <img class="app-icon" src="{e(app['icon'])}" alt="{e(app['name'])} app icon" width="168" height="168">
                <div>
                    <h1 class="product-title" id="app-title">{e(app['storeName'])}</h1>
                    <p class="product-sub">{e(app['subtitle'])}</p>
                    <a class="product-dev" href="apps.html">Thunder Apps Studio</a>
                    <div class="product-actions">
                        {get_button(app, "get get-lg")}
                        <span class="product-price">Free<br>In-App Purchases</span>
                    </div>
                </div>
            </section>

            <dl class="info-strip">
                <div><dt>Category</dt><dd><span class="info-value"><i class="fas {cat_icon}" aria-hidden="true"></i></span><span class="info-sub">{e(app['category'])}</span></dd></div>
                <div><dt>Device</dt><dd><span class="info-value"><i class="fas fa-mobile-alt" aria-hidden="true"></i></span><span class="info-sub">iPhone</span></dd></div>
                <div><dt>Price</dt><dd><span class="info-value">Free</span><span class="info-sub">In-App Purchases</span></dd></div>
                <div><dt>Developer</dt><dd><span class="info-value"><i class="fas fa-user-circle" aria-hidden="true"></i></span><span class="info-sub">Thunder Apps Studio</span></dd></div>
            </dl>
        </div>

        <!-- Screenshots -->
        <section class="section" aria-labelledby="shots-title">
            <div class="wrap">
                <div class="section-head">
                    <h2 class="section-title" id="shots-title">iPhone Screenshots</h2>
                    <div class="shelf-nav">
                        <button type="button" class="shelf-btn" data-shelf-prev="shots" aria-label="Previous screenshots"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10 3 5 8l5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
                        <button type="button" class="shelf-btn" data-shelf-next="shots" aria-label="Next screenshots"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="m6 3 5 5-5 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
                    </div>
                </div>
                <ul class="shelf shots" id="shots" data-shelf>
{shots}
                </ul>
            </div>
        </section>

        <!-- About -->
        <section class="section ruled" aria-labelledby="about-title">
            <div class="wrap">
                <div class="desc">
                    <div class="prose">
                        <h2 class="section-title" id="about-title" style="margin-bottom: 16px;">About {e(app['name'])}</h2>
{intro}
                    </div>
                    <ul class="checks">
{highlights}
                    </ul>
                </div>
            </div>
        </section>

        <!-- Features -->
        <section class="section ruled" aria-labelledby="features-title">
            <div class="wrap">
                <div class="section-head"><h2 class="section-title" id="features-title">What you can do</h2></div>
                <ul class="tiles tiles-4">
{features}
                </ul>
            </div>
        </section>

        <!-- Information -->
        <section class="section ruled" aria-labelledby="info-title">
            <div class="wrap">
                <div class="section-head"><h2 class="section-title" id="info-title">Information</h2></div>
                <dl class="info-table">
                    <div><dt>Provider</dt><dd>Thunder Apps Studio</dd></div>
                    <div><dt>Category</dt><dd>{e(app['category'])}</dd></div>
                    <div><dt>Compatibility</dt><dd>iPhone</dd></div>
                    <div><dt>Price</dt><dd>Free</dd></div>
                    <div><dt>In-App Purchases</dt><dd>Yes</dd></div>
                    <div><dt>App Store</dt><dd><a href="{e(app['storeUrl'])}" target="_blank" rel="noopener">View on the App Store</a></dd></div>
                </dl>
                {note}
            </div>
        </section>

        <!-- Download -->
        <section class="section-tight">
            <div class="wrap">
                <div class="cta">
                    <img class="app-icon" src="{e(app['icon'])}" alt="" width="72" height="72" loading="lazy">
                    <div>
                        <h2>Get {e(app['name'])} for iPhone</h2>
                        <p>Free to download on the App Store.</p>
                    </div>
                    {store_badge(app)}
                </div>
            </div>
        </section>

        <!-- More apps -->
        <section class="section" aria-labelledby="more-title">
            <div class="wrap">
                <div class="section-head">
                    <h2 class="section-title" id="more-title">More by Thunder Apps Studio</h2>
                    <a class="link-more" href="apps.html">See All</a>
                </div>{app_list(apps, exclude=app["slug"])}</div>
        </section>
    </main>
""" + body_close(apps))


def app_card(app):
    shots = "".join(
        f'<img src="{e(s)}" alt="" width="600" height="1300" loading="lazy" decoding="async">'
        for s in app["screenshots"][:3])
    return f"""                <article class="app-card" style="--app-accent: {e(app['accent'])};">
                    {app_row(app)}
                    <p class="app-card-summary">{e(app['summary'])}</p>
                    <div class="app-card-shots" aria-hidden="true">{shots}</div>
                </article>"""


def apps_page(apps):
    cards = "\n".join(app_card(a) for a in apps)
    desc = "iPhone apps by Thunder Apps Studio: " + ", ".join(a["storeName"] for a in apps) + "."
    return (head("Our Apps | Thunder Apps Studio", desc, f"{SITE}/apps") + body_open("apps") + f"""
    <main id="main">
        <div class="wrap page-head">
            {crumbs([("Home", "index.html"), ("Apps", None)])}
            <h1 class="page-title">Our Apps</h1>
            <p class="page-lead">Thoughtfully designed iPhone apps for getting things done, managing money, mixing drinks and dating with confidence.</p>
        </div>

        <section class="section" aria-label="Apps on the App Store">
            <div class="wrap">
                <div class="app-cards">
{cards}
                </div>
            </div>
        </section>
    </main>
""" + body_close(apps))


# ---------------------------------------------------------------------------
# Sync shared blocks into hand-written pages
# ---------------------------------------------------------------------------

def replace_block(text, name, content):
    pattern = re.compile(r"(<!-- " + re.escape(name) + r" -->)(.*?)(<!-- /" + re.escape(name) + r" -->)", re.S)
    return pattern.sub(lambda m: m.group(1) + content + m.group(3), text)


def sync_page(path, apps, generated):
    if path.name in SKIP or path.name in generated:
        return False
    text = path.read_text(encoding="utf-8")
    if "<!-- site:nav -->" not in text:
        return False
    # 404.html is served for any missing URL, at any depth, so it links from the site root.
    base = "/" if path.name == "404.html" else ""
    active = ACTIVE.get(path.name, "")
    new = text
    new = replace_block(new, "site:head", head_assets(base))
    new = replace_block(new, "site:nav", nav(active, base))
    new = replace_block(new, "site:footer", footer(apps, base))
    new = replace_block(new, "apps:feature", feature_story(apps[0]))
    new = replace_block(new, "apps:list", app_list(apps))
    new = replace_block(new, "apps:icons", app_icons(apps))
    new = replace_block(new, "apps:inside", inside_cards(apps, base))
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def main():
    apps = json.loads((ROOT / "_tools" / "apps.json").read_text(encoding="utf-8"))

    (ROOT / "apps.html").write_text(apps_page(apps), encoding="utf-8")
    print("wrote apps.html")
    generated = {"apps.html"}
    for app in apps:
        name = f"{app['slug']}.html"
        (ROOT / name).write_text(product_page(app, apps), encoding="utf-8")
        generated.add(name)
        print(f"wrote {name}")

    for path in sorted(ROOT.glob("*.html")):
        if sync_page(path, apps, generated):
            print(f"synced {path.name}")


if __name__ == "__main__":
    main()
