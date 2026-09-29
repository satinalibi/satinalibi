#!/usr/bin/env python3
"""Build the Satin Alibi site into dist/.

    python build.py            # build pages
    python build.py --pins     # build pages and render every pin to a 1000x1500 JPG
    python build.py --all      # also include drafts and future-dated posts (for previews)

Posts live in content/posts/*.md with YAML front matter (see CLAUDE.md).
A post is published when `status: published` and its `date` is today or earlier
(Toronto time), so posts can be scheduled ahead and the daily build releases them.
"""
import datetime as dt
import json
import re
import shutil
import sys
import threading
from email.utils import format_datetime
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
TZ = ZoneInfo("America/Toronto")
TODAY = dt.datetime.now(TZ).date()
INCLUDE_ALL = "--all" in sys.argv
RENDER_PINS = "--pins" in sys.argv

SITE = yaml.safe_load((ROOT / "site.yml").read_text())
SECTIONS = {s["slug"]: s for s in SITE["sections"]}

env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=select_autoescape(["html", "xml"]))


def md(text):
    return Markup(markdown.markdown(text or "", extensions=["smarty", "attr_list"]))


def md_inline(text):
    html = markdown.markdown(text or "", extensions=["smarty"])
    return Markup(re.sub(r"^<p>(.*)</p>$", r"\1", html.strip(), flags=re.S))


def photo(url, w, h=None, q=80):
    """Sized image URL. Works for Unsplash and Pexels; other URLs pass through."""
    if not url:
        return ""
    base, _, qs = url.partition("?")
    if "images.unsplash.com" in base:
        # a URL can carry its own crop, e.g. "...?crop=top" for a full-length shot
        m = re.search(r"crop=([a-z,]+)", qs)
        crop = m.group(1) if m else "faces,entropy"
        out = f"{base}?auto=format&fit=crop&crop={crop}&w={w}&q={q}"
        return out + (f"&h={h}" if h else "")
    if "images.pexels.com" in base:
        out = f"{base}?auto=compress&cs=tinysrgb&fit=crop&w={w}"
        return out + (f"&h={h}" if h else "")
    return url


env.filters.update(md=md, md_inline=md_inline, photo=photo)
import hashlib
# Stylesheet version = hash of the CSS, so browsers fetch new styles as soon as they change
CSS_VERSION = hashlib.sha1((ROOT / "static" / "style.css").read_bytes()).hexdigest()[:10] if (ROOT / "static" / "style.css").exists() else TODAY.strftime("%Y%m%d")
env.globals.update(site=SITE, sections=SITE["sections"], year=TODAY.year, version=CSS_VERSION)


def read_front_matter(path):
    text = path.read_text()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"{path}: missing front matter")
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def load_posts():
    posts = []
    for path in sorted((ROOT / "content/posts").glob("*.md")):
        meta, body = read_front_matter(path)
        meta.setdefault("slug", path.stem)
        date = meta.get("date")
        meta["date"] = date if isinstance(date, dt.date) else dt.date.fromisoformat(str(date))
        live = meta.get("status") == "published" and meta["date"] <= TODAY
        if not (live or INCLUDE_ALL):
            continue
        if meta.get("section") not in SECTIONS:
            raise SystemExit(f"{path}: unknown section {meta.get('section')!r}")
        intro, _, outro = body.partition("<!-- products -->")
        meta["intro_html"] = md(intro)
        meta["outro_html"] = md(outro)
        meta["url"] = f"/{meta['section']}/{meta['slug']}/"
        meta["abs_url"] = SITE["url"].rstrip("/") + meta["url"]
        meta["section_info"] = SECTIONS[meta["section"]]
        meta.setdefault("products", [])
        meta["affiliate"] = bool(meta["products"]) and meta.get("affiliate", True)
        pins = []
        for i, pin in enumerate(meta.get("pins") or [], start=1):
            pin = dict(pin)
            pin["id"] = f"{meta['slug']}-{i}"
            pin["image"] = f"/pins/{pin['id']}.jpg"
            pin["abs_image"] = SITE["url"].rstrip("/") + pin["image"]
            pin.setdefault("board", meta["section_info"]["board"])
            target = pin.get("link") or meta["abs_url"]
            sep = "&" if "?" in target else "?"
            if target.startswith(SITE["url"]):
                target += f"{sep}utm_source=pinterest&utm_medium=social&utm_campaign={quote(pin['id'])}"
            pin["target"] = target
            pin.setdefault("post_title", meta["title"])
            pins.append(pin)
        meta["pins"] = pins
        pin_photos = [x for pin in pins for x in ([pin.get("photo")] + list(pin.get("photos") or [])) if x]
        meta["collage"] = meta.get("collage") or [u for u in [meta.get("hero")] + pin_photos if u][:3]
        still = next((pin for pin in pins if pin.get("style") == "still" and pin.get("sub")), None)
        meta["interlude"] = meta.get("interlude") or (dict(photo=still["photo"], sub=still["sub"]) if still else None)
        posts.append(meta)
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return posts


def write(rel, html):
    out = DIST / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)


def build_pages(posts):
    render = lambda tpl, **kw: env.get_template(tpl).render(**kw)
    shopping = [p for p in posts if p["section"] != "take-up-space"]
    space = [p for p in posts if p["section"] == "take-up-space"]
    write("index.html", render("home.html", posts=shopping[:9], space_posts=space[:3], canonical=SITE["url"] + "/"))

    for slug, sec in SECTIONS.items():
        sec_posts = [p for p in posts if p["section"] == slug]
        write(f"{slug}/index.html", render("section.html", section=sec, posts=sec_posts,
                                           current_section=slug, canonical=f"{SITE['url']}/{slug}/"))

    for p in posts:
        more = [q for q in posts if q["section"] == p["section"] and q["slug"] != p["slug"]][:3]
        write(p["url"].strip("/") + "/index.html",
              render("post.html", post=p, more=more, current_section=p["section"], canonical=p["abs_url"]))
        for pin in p["pins"]:
            write(f"pins/{pin['id']}.html", render("pin.html", pin=pin, post=p))

    for path in sorted((ROOT / "content/pages").glob("*.md")):
        meta, body = read_front_matter(path)
        write(f"{path.stem}/index.html", render("page.html", page=meta, body_html=md(body),
                                                canonical=f"{SITE['url']}/{path.stem}/"))

    write("404.html", render("page.html", page={"title": "Not here.", "dek": "That page took itself somewhere louder."},
                             body_html='<p><a href="/">Back to the front page</a></p>', canonical=SITE["url"] + "/404"))

    # Feeds and crawl files
    urls = [SITE["url"] + "/"] + [f"{SITE['url']}/{s}/" for s in SECTIONS] + [p["abs_url"] for p in posts]
    urls += [f"{SITE['url']}/{f.stem}/" for f in (ROOT / "content/pages").glob("*.md")]
    write("sitemap.xml", render("sitemap.xml", urls=urls, today=TODAY.isoformat()))
    write("robots.txt", f"User-agent: *\nDisallow: /pins/*.html\nDisallow: /_products\nSitemap: {SITE['url']}/sitemap.xml\n")
    for_feed = [dict(p, rfc_date=format_datetime(dt.datetime.combine(p["date"], dt.time(9), TZ))) for p in posts[:30]]
    write("feed.xml", render("feed.xml", posts=for_feed, build_date=format_datetime(dt.datetime.now(TZ))))

    schedule = load_schedule()
    manifest = []
    for p in posts:
        for pin in p["pins"]:
            s = schedule.get(pin["id"], {})
            # rev > 1 re-releases a pin as a brand-new Pinterest item (new guid, fresh image URL),
            # e.g. after a redesign when Pinterest already posted the old image
            rev = int(s.get("rev", 1))
            manifest.append(dict(id=pin["id"], rev=rev,
                                 guid=f"satinalibi-pin-{pin['id']}" + (f"-r{rev}" if rev > 1 else ""),
                                 image=pin["abs_image"] + (f"?r={rev}" if rev > 1 else ""), title=pin.get("pin_title", p["title"]),
                                 description=pin.get("pin_description", p.get("dek", "")), link=pin["target"],
                                 board=pin["board"], post=p["abs_url"], date=p["date"].isoformat(),
                                 style=pin.get("style"), status=s.get("status", "pending"),
                                 publish=str(s["publish"]) if s.get("publish") else None))
    write("pins/manifest.json", json.dumps(manifest, indent=2))
    build_board_feeds(manifest)
    return manifest


def load_schedule():
    path = ROOT / "content/pin-schedule.yml"
    return (yaml.safe_load(path.read_text()) or {}) if path.exists() else {}


def build_board_feeds(manifest):
    """One RSS feed per Pinterest board. Pinterest's 'auto-publish from RSS' reads these.
    Only approved pins whose publish date has arrived (Toronto time) appear, so the daily
    build releases them on schedule."""
    tpl = env.get_template("board_feed.xml")
    for sec in SITE["sections"]:
        items = [m for m in manifest if m["board"] == sec["board"] and m["status"] == "approved"
                 and m["publish"] and dt.date.fromisoformat(m["publish"]) <= TODAY
                 and m["link"].startswith(SITE["url"])]
        items.sort(key=lambda m: (m["publish"], m["id"]), reverse=True)
        feed_items = [dict(m, rfc_date=format_datetime(dt.datetime.combine(dt.date.fromisoformat(m["publish"]), dt.time(7), TZ)))
                      for m in items[:100]]
        write(f"feeds/{sec['slug']}.xml", tpl.render(section=sec, items=feed_items,
                                                     build_date=format_datetime(dt.datetime.now(TZ))))


def render_page(path, out, w, h):
    """Screenshot one built page (a full-page contact sheet for checking, not published anywhere important)."""
    from playwright.sync_api import sync_playwright
    handler = partial(SimpleHTTPRequestHandler, directory=str(DIST))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page(viewport={"width": w, "height": h})
            page.goto(f"http://127.0.0.1:{server.server_address[1]}/{path}", wait_until="networkidle", timeout=90000)
            page.screenshot(path=str(DIST / out), type="jpeg", quality=80, full_page=True)
            browser.close()
    except Exception as e:
        print("contact sheet failed:", e)
    server.shutdown()


def render_pins(manifest):
    from playwright.sync_api import sync_playwright

    handler = partial(SimpleHTTPRequestHandler, directory=str(DIST))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 1500}, device_scale_factor=1)
        for pin in manifest:
            page.goto(f"http://127.0.0.1:{port}/pins/{pin['id']}.html", wait_until="networkidle", timeout=60000)
            page.evaluate("document.fonts.ready")
            page.screenshot(path=str(DIST / "pins" / f"{pin['id']}.jpg"), type="jpeg", quality=90)
            print("pin", pin["id"])
        browser.close()
    server.shutdown()


IMG_CACHE = ROOT / "content" / "product-images.yml"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/128.0 Safari/537.36")


def fetch_og_image(url):
    """The product photo a store shares for its page (og:image), or None. Only runs on GitHub Actions."""
    import html as _html
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9",
                                                   "Accept": "text/html,application/xhtml+xml"})
        with urllib.request.urlopen(req, timeout=12) as r:
            page = r.read(2_000_000).decode("utf-8", "replace")
    except Exception as e:  # blocked, timed out, gone: leave the product without a photo
        print("  no image:", url, type(e).__name__)
        return None
    for pat in (r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image',
                r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)'):
        m = re.search(pat, page, re.I)
        if m:
            img = _html.unescape(m.group(1)).strip()
            if img.startswith("//"):
                img = "https:" + img
            img = re.sub(r"^http://", "https://", img)
            if re.search(r"og_general|logo|default|placeholder", img, re.I):  # a store-wide card, not the product
                return None
            # Shopify shares a cropped social card; ask for the plain photo instead
            img = re.sub(r"_(\d+x\d*|\d*x\d+)(_crop_[a-z]+)?(?=\.(jpe?g|png|webp)\b)", "", img)
            return img
    print("  no og:image:", url)
    return None


def resolve_product_images(posts):
    """Give every product a photo. Uses `image:` from the post if set, else the cache in
    content/product-images.yml, else (on GitHub Actions only) looks it up on the store's page.
    New lookups are written to dist/product-images.yml; copy them into the cache to keep them."""
    import os
    cache = (yaml.safe_load(IMG_CACHE.read_text()) or {}) if IMG_CACHE.exists() else {}
    online = os.environ.get("GITHUB_ACTIONS") == "true"
    for p in posts:
        for pr in p.get("products") or []:
            if pr.get("image") or not pr.get("url"):
                continue
            if pr["url"] not in cache and online:
                cache[pr["url"]] = fetch_og_image(pr["url"]) or ""
            if cache.get(pr["url"]):
                pr["image"] = cache[pr["url"]]
    write("product-images.yml", yaml.safe_dump(cache, sort_keys=True, allow_unicode=True, width=1000))
    # a contact sheet of every product photo, so a person can check them at a glance
    tiles = "".join(f'<figure><div><img src="{pr["image"]}"></div><figcaption>{p["slug"]} / {pr["brand"]} {pr["name"]}</figcaption></figure>'
                    for p in posts for pr in p.get("products") or [] if pr.get("image"))
    write("_products.html", "<!doctype html><meta charset=utf-8><style>body{margin:0;background:#F3EDE4;font:11px sans-serif}"
          "main{display:grid;grid-template-columns:repeat(8,1fr);gap:8px;padding:8px}figure{margin:0}"
          "div{height:150px;background:#fff;display:flex;align-items:center;justify-content:center}"
          "img{max-width:92%;max-height:92%;mix-blend-mode:multiply}</style><main>" + tiles + "</main>")


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "static", DIST)
    posts = load_posts()
    resolve_product_images(posts)
    manifest = build_pages(posts)
    if RENDER_PINS:
        render_pins(manifest)
        render_page("_products.html", "_products.jpg", 1600, 1800)
    print(f"Built {len(posts)} posts, {len(manifest)} pins -> {DIST}")


if __name__ == "__main__":
    main()
