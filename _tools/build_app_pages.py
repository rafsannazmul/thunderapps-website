#!/usr/bin/env python3
"""
Builds the app pages for thunderapps.xyz from _tools/apps.json.

    python3 _tools/build_app_pages.py

Writes, at the site root:
  apps.html          the "Our Apps" menu page
  <slug>.html        one product page per app

To add an app: add an entry to apps.json and run the script again.
Folders starting with "_" are ignored by GitHub Pages, so this tool never ships.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://thunderapps.xyz"

e = html.escape  # every piece of text from apps.json goes through this


def head(title, description, canonical, extra=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{e(title)}</title>
    <meta content="width=device-width, initial-scale=1.0" name="viewport">
    <meta name="description" content="{e(description)}">
    <link rel="canonical" href="{canonical}">
    <meta property="og:site_name" content="Thunder Apps Studio">
    <meta property="og:title" content="{e(title)}">
    <meta property="og:description" content="{e(description)}">
    <meta property="og:url" content="{canonical}">
    <meta property="og:type" content="website">
{extra}
    <!-- Google Web Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Saira:wght@500;600;700&display=swap" rel="stylesheet">

    <!-- Icon Font Stylesheet -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.10.0/css/all.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.4.1/font/bootstrap-icons.css" rel="stylesheet">

    <!-- Libraries Stylesheet -->
    <link href="lib/animate/animate.min.css" rel="stylesheet">
    <link href="lib/owlcarousel/assets/owl.carousel.min.css" rel="stylesheet">

    <!-- Customized Bootstrap Stylesheet -->
    <link href="css/bootstrap.min.css" rel="stylesheet">

    <!-- Template Stylesheet -->
    <link href="css/style.css" rel="stylesheet">
    <link href="css/apps.css" rel="stylesheet">
</head>
"""


NAV = """
<body>
    <!-- Spinner Start -->
    <div id="spinner" class="show position-fixed translate-middle w-100 vh-100 top-50 start-50 d-flex align-items-center justify-content-center">
        <div class="spinner-grow text-primary" role="status"></div>
    </div>
    <!-- Spinner End -->

    <!-- Topbar Start -->
    <div class="container-fluid bg-dark py-2 d-none d-md-flex">
        <div class="container">
            <div class="d-flex justify-content-between topbar">
                <div class="top-info">
                    <small class="me-3 text-white-50"><i class="fas fa-map-marker-alt me-2 text-secondary"></i>Dhaka, Bangladesh</small>
                    <small class="me-3 text-white-50"><i class="fas fa-envelope me-2 text-secondary"></i>info@thunderapps.xyz</small>
                </div>
                <div id="note" class="text-secondary d-none d-xl-flex"><small><a href="apps.html" class="text-secondary">Check Now : New Apps Launched</a></small></div>
                <div class="top-link">
                    <a href="" class="bg-light nav-fill btn btn-sm-square rounded-circle"><i class="fab fa-facebook-f text-primary"></i></a>
                    <a href="" class="bg-light nav-fill btn btn-sm-square rounded-circle"><i class="fab fa-twitter text-primary"></i></a>
                    <a href="" class="bg-light nav-fill btn btn-sm-square rounded-circle"><i class="fab fa-instagram text-primary"></i></a>
                    <a href="" class="bg-light nav-fill btn btn-sm-square rounded-circle me-0"><i class="fab fa-linkedin-in text-primary"></i></a>
                </div>
            </div>
        </div>
    </div>
    <!-- Topbar End -->

    <!-- Navbar Start -->
    <div class="container-fluid bg-primary">
        <div class="container">
            <nav class="navbar navbar-dark navbar-expand-lg py-0">
                <a href="index.html" class="navbar-brand">
                    <h1 class="text-white fw-bold d-block">Thunder<span class="text-secondary">Apps Studio</span> </h1>
                </a>
                <button type="button" class="navbar-toggler me-0" data-bs-toggle="collapse" data-bs-target="#navbarCollapse">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="collapse navbar-collapse bg-transparent" id="navbarCollapse">
                    <div class="navbar-nav ms-auto mx-xl-auto p-0">
                        <a href="index.html" class="nav-item nav-link">Home</a>
                        <a href="about.html" class="nav-item nav-link">About</a>
                        <a href="service.html" class="nav-item nav-link">Services</a>
                        <a href="apps.html" class="nav-item nav-link active text-secondary">Apps</a>
                        <div class="nav-item dropdown">
                            <a href="#" class="nav-link dropdown-toggle" data-bs-toggle="dropdown">Pages</a>
                            <div class="dropdown-menu rounded">
                                <a href="team.html" class="dropdown-item">Our Team</a>
                                <a href="testimonial.html" class="dropdown-item">Testimonial</a>
                                <a href="404.html" class="dropdown-item">404 Page</a>
                            </div>
                        </div>
                        <a href="contact.html" class="nav-item nav-link">Contact</a>
                    </div>
                </div>
                <div class="d-none d-xl-flex flex-shirink-0">
                    <div id="phone-tada" class="d-flex align-items-center justify-content-center me-4">
                        <a href="tel:+8801701013856" class="position-relative animated tada infinite">
                            <i class="fa fa-phone-alt text-white fa-2x"></i>
                            <div class="position-absolute" style="top: -7px; left: 20px;">
                                <span><i class="fa fa-comment-dots text-secondary"></i></span>
                            </div>
                        </a>
                    </div>
                    <div class="d-flex flex-column pe-4">
                        <span class="text-white-50">Have any questions?</span>
                        <span class="text-secondary">Call: +88-017-0101-3856</span>
                    </div>
                </div>
            </nav>
        </div>
    </div>
    <!-- Navbar End -->
"""


FOOTER = """
    <!-- Footer Start -->
    <div class="container-fluid footer bg-dark wow fadeIn" data-wow-delay=".3s">
        <div class="container pt-5 pb-4">
            <div class="row g-4 g-lg-5">
                <div class="col-lg-3 col-md-6">
                    <a href="index.html">
                        <h1 class="text-white fw-bold d-block">Thunder<span class="text-secondary">Apps Studio</span> </h1>
                    </a>
                    <p class="mt-4 text-light">Thunder Apps Studio delivers innovative, user-friendly mobile apps for iOS. Specializing in custom solutions, we create high-quality apps tailored to meet your business needs, ensuring seamless design and exceptional user experiences.</p>
                </div>
                <div class="col-lg-3 col-md-6">
                    <span class="h3 text-secondary">Our Apps</span>
                    <div class="mt-4 d-flex flex-column short-link">
{app_links}
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <span class="h3 text-secondary">Help Link</span>
                    <div class="mt-4 d-flex flex-column help-link">
                        <a href="about.html" class="mb-2 text-white"><i class="fas fa-angle-right text-secondary me-2"></i>About us</a>
                        <a href="terms.html" class="mb-2 text-white"><i class="fas fa-angle-right text-secondary me-2"></i>Terms and Conditions</a>
                        <a href="privacy.html" class="mb-2 text-white"><i class="fas fa-angle-right text-secondary me-2"></i>Privacy Policy</a>
                        <a href="contact.html" class="mb-2 text-white"><i class="fas fa-angle-right text-secondary me-2"></i>Contact</a>
                    </div>
                </div>
                <div class="col-lg-3 col-md-6">
                    <span class="h3 text-secondary">Contact Us</span>
                    <div class="text-white mt-4 d-flex flex-column contact-link">
                        <span class="pb-3 text-light border-bottom border-primary"><i class="fas fa-map-marker-alt text-secondary me-2"></i> Dhaka, Bangladesh</span>
                        <a href="tel:+8801701013856" class="py-3 text-light border-bottom border-primary"><i class="fas fa-phone-alt text-secondary me-2"></i> +88-017-0101-3856</a>
                        <a href="mailto:info@thunderapps.xyz" class="py-3 text-light border-bottom border-primary"><i class="fas fa-envelope text-secondary me-2"></i> info@thunderapps.xyz</a>
                    </div>
                </div>
            </div>
            <hr class="text-light mt-5 mb-4">
            <div class="row">
                <div class="col-md-6 text-center text-md-start">
                    <span class="text-light"><a href="index.html" class="text-secondary"><i class="fas fa-copyright text-secondary me-2"></i>Thunder Apps Studio</a>, All right reserved.</span>
                </div>
            </div>
        </div>
    </div>
    <!-- Footer End -->

    <!-- Back to Top -->
    <a href="#" class="btn btn-secondary btn-square rounded-circle back-to-top"><i class="fa fa-arrow-up text-white"></i></a>

    <!-- JavaScript Libraries -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="lib/wow/wow.min.js"></script>
    <script src="lib/easing/easing.min.js"></script>
    <script src="lib/waypoints/waypoints.min.js"></script>
    <script src="lib/owlcarousel/owl.carousel.min.js"></script>

    <!-- Template Javascript -->
    <script src="js/main.js"></script>
</body>

</html>
"""


def page_header(title, crumbs):
    items = "".join(
        f'<li class="breadcrumb-item"><a href="{href}">{e(label)}</a></li>' if href
        else f'<li class="breadcrumb-item" aria-current="page">{e(label)}</li>'
        for label, href in crumbs
    )
    return f"""
    <!-- Page Header Start -->
    <div class="container-fluid page-header py-5">
        <div class="container text-center py-5">
            <h1 class="display-2 text-white mb-4 animated slideInDown">{e(title)}</h1>
            <nav aria-label="breadcrumb animated slideInDown">
                <ol class="breadcrumb justify-content-center mb-0">{items}</ol>
            </nav>
        </div>
    </div>
    <!-- Page Header End -->
"""


def store_badge(app, extra_class=""):
    return (f'<a href="{e(app["storeUrl"])}" class="ta-badge {extra_class}" target="_blank" rel="noopener" '
            f'aria-label="Download {e(app["name"])} on the App Store">'
            f'<i class="fab fa-apple" aria-hidden="true"></i>'
            f'<span><small>Download on the</small>App Store</span></a>')


def footer(apps):
    links = "\n".join(
        f'                        <a href="{a["slug"]}.html" class="mb-2 text-white">'
        f'<i class="fas fa-angle-right text-secondary me-2"></i>{e(a["name"])}</a>'
        for a in apps
    )
    return FOOTER.replace("{app_links}", links)


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
        f'                    <figure class="ta-shot ta-shot-{i + 1}">'
        f'<img src="{e(src)}" alt="{e(app["name"])} screenshot {i + 1}" width="600" height="1300" '
        f'{"" if i == 0 else lazy}decoding="async"></figure>'
        for i, src in enumerate(app["screenshots"][:3])
    )
    intro = "\n".join(f'                    <p>{e(p)}</p>' for p in app["intro"])
    highlights = "\n".join(
        f'                <li><i class="fas fa-check-circle"></i>{e(h)}</li>' for h in app["highlights"]
    )
    features = "\n".join(
        f"""                <div class="col-sm-6 col-lg-3">
                    <div class="ta-feature h-100">
                        <span class="ta-feature-icon"><i class="fas {e(f['icon'])}"></i></span>
                        <h3>{e(f['title'])}</h3>
                        <p>{e(f['text'])}</p>
                    </div>
                </div>""" for f in app["features"]
    )
    note = f'<p class="ta-note">{e(app["note"])}</p>' if app.get("note") else ""
    others = "\n".join(app_card(a, compact=True) for a in apps if a["slug"] != app["slug"])

    return (head(title, app["summary"], canonical, extra) + NAV
            + page_header(app["name"], [("Home", "index.html"), ("Apps", "apps.html"), (app["name"], None)])
            + f"""
    <main class="ta-app" style="--app-accent: {e(app['accent'])};">

        <!-- Hero: icon, name, download -->
        <section class="container-fluid py-5 bg-light">
            <div class="container">
                <div class="row g-4 g-lg-5 align-items-center">
                    <div class="col-lg-5 ta-hero-text wow fadeIn" data-wow-delay=".1s">
                        <img class="ta-icon" src="{e(app['icon'])}" alt="{e(app['name'])} app icon" width="112" height="112">
                        <h2 class="ta-title">{e(app['storeName'])}</h2>
                        <p class="ta-subtitle">{e(app['subtitle'])}</p>
                        <ul class="ta-chips">
                            <li>{e(app['category'])}</li>
                            <li>iPhone</li>
                            <li>Free · In-App Purchases</li>
                        </ul>
                        <p class="ta-summary">{e(app['summary'])}</p>
                        {store_badge(app)}
                    </div>
                    <div class="col-lg-7">
                        <div class="ta-shots" aria-label="{e(app['name'])} screenshots">
{shots}
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- About -->
        <section class="container py-5">
            <div class="row g-4 g-lg-5">
                <div class="col-lg-7 ta-about">
                    <h2>About {e(app['name'])}</h2>
{intro}
                </div>
                <div class="col-lg-5">
                    <ul class="ta-highlights">
{highlights}
                    </ul>
                </div>
            </div>
        </section>

        <!-- Features -->
        <section class="container pb-5">
            <h2 class="ta-section-title">What you can do</h2>
            <div class="row g-4">
{features}
            </div>
        </section>

        <!-- Download CTA -->
        <section class="container pb-5">
            <div class="ta-cta">
                <img src="{e(app['icon'])}" alt="" width="72" height="72">
                <div>
                    <h2>Get {e(app['name'])} for iPhone</h2>
                    <p>Free to download on the App Store.</p>
                </div>
                {store_badge(app, "ms-md-auto")}
            </div>
            {note}
        </section>

        <!-- More apps -->
        <section class="container-fluid py-5 bg-light">
            <div class="container">
                <h2 class="ta-section-title">More apps from Thunder Apps</h2>
                <div class="row g-4">
{others}
                </div>
            </div>
        </section>
    </main>
""" + footer(apps))


def app_card(app, compact=False):
    col = "col-md-6 col-lg-4" if compact else "col-md-6"
    shots = "" if compact else (
        '<div class="ta-card-shots">' + "".join(
            f'<img src="{e(s)}" alt="" width="600" height="1300" loading="lazy" decoding="async">'
            for s in app["screenshots"][:3]) + "</div>")
    return f"""                <div class="{col}">
                    <article class="ta-card h-100" style="--app-accent: {e(app['accent'])};">
                        <a class="ta-card-link" href="{app['slug']}.html" aria-label="{e(app['name'])} details"></a>
                        <div class="ta-card-head">
                            <img class="ta-card-icon" src="{e(app['icon'])}" alt="{e(app['name'])} app icon" width="72" height="72" loading="lazy">
                            <div>
                                <h3>{e(app['name'])}</h3>
                                <p class="ta-card-sub">{e(app['subtitle'])}</p>
                                <span class="ta-card-cat">{e(app['category'])}</span>
                            </div>
                        </div>
                        <p class="ta-card-summary">{e(app['summary'])}</p>
                        {shots}
                        <div class="ta-card-actions">
                            <a href="{app['slug']}.html" class="btn btn-primary rounded-pill px-4">Learn more</a>
                            {store_badge(app)}
                        </div>
                    </article>
                </div>"""


def apps_page(apps):
    cards = "\n".join(app_card(a) for a in apps)
    desc = "iPhone apps by Thunder Apps Studio: " + ", ".join(a["storeName"] for a in apps) + "."
    return (head("Our Apps | Thunder Apps Studio", desc, f"{SITE}/apps") + NAV
            + page_header("Our Apps", [("Home", "index.html"), ("Apps", None)])
            + f"""
    <main class="ta-apps container-fluid py-5 bg-light">
        <div class="container">
            <div class="text-center mx-auto mb-5" style="max-width: 640px;">
                <p class="ta-eyebrow">On the App Store now</p>
                <h2 class="ta-section-title">Apps built by Thunder Apps Studio</h2>
                <p class="text-muted">Thoughtfully designed iPhone apps for getting things done, managing money, mixing drinks and dating with confidence.</p>
            </div>
            <div class="row g-4">
{cards}
            </div>
        </div>
    </main>
""" + footer(apps))


def main():
    apps = json.loads((ROOT / "_tools" / "apps.json").read_text(encoding="utf-8"))
    (ROOT / "apps.html").write_text(apps_page(apps), encoding="utf-8")
    print("wrote apps.html")
    for app in apps:
        (ROOT / f"{app['slug']}.html").write_text(product_page(app, apps), encoding="utf-8")
        print(f"wrote {app['slug']}.html")


if __name__ == "__main__":
    main()
