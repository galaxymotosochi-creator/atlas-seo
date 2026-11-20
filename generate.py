#!/usr/bin/env python3
"""AtlasPos SEO blog generator (atlaspos.ru).

Строит статический сайт в dist/:

    dist/
    ├── index.html          # хаб со списком статей
    ├── style.css
    ├── sitemap.xml
    ├── robots.txt
    ├── images/*.jpg
    └── blog/<slug>/index.html

Usage:
    python3 generate.py          # сборка в dist/
    python3 generate.py --open   # собрать и показать размеры

Dev: Bokov777
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date, datetime
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
PUBLIC = ROOT / "public"
DIST = ROOT / "dist"


def load_posts() -> list[dict]:
    with (ROOT / "pages.json").open(encoding="utf-8") as fh:
        return json.load(fh)


def render_sections(sections: list[dict]) -> str:
    parts = []
    for sec in sections:
        parts.append(
            f'<h2>{escape(sec["heading"])}</h2>\n      <p>{escape(sec["text"])}</p>'
        )
    return "\n      ".join(parts)


def render_faq(faq: list[dict]) -> str:
    parts = []
    for i, item in enumerate(faq, 1):
        parts.append(
            "<details>\n        "
            f'<summary>{i}. {escape(item["question"])}</summary>\n        '
            f'<p>{escape(item["answer"])}</p>\n      </details>'
        )
    return "\n      ".join(parts)


def render_related(slugs: list[str], posts: list[dict]) -> str:
    by_slug = {p["slug"]: p for p in posts}
    items = []
    for slug in slugs:
        post = by_slug.get(slug)
        if post:
            items.append(
                f'<li><a href="/blog/{post["slug"]}/">{escape(post["h1"])}</a> '
                f'<span>{escape(post["category"])}</span></li>'
            )
    return "\n        ".join(items)


def render_jsonld(site: dict, post: dict) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post["h1"],
        "description": post["description"],
        "image": f'https://{site["domain"]}{post["image"]}',
        "datePublished": post["published"],
        "dateModified": post["updated"],
        "inLanguage": site.get("lang", "ru"),
        "articleSection": post["category"],
        "publisher": {
            "@type": "Organization",
            "name": site["name"],
            "url": f'https://{site["domain"]}',
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f'https://{site["domain"]}/blog/{post["slug"]}/',
        },
    }
    if post.get("faq"):
        data["mainEntity"] = [
            {
                "@type": "Question",
                "name": q["question"],
                "acceptedAnswer": {"@type": "Answer", "text": q["answer"]},
            }
            for q in post["faq"]
        ]
    # JSON-LD внутри <script>: экранируем только опасные символы
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def fill(template: str, values: dict) -> str:
    html = template
    for key, val in values.items():
        html = html.replace("{{" + key + "}}", str(val))
    return html


def build_post(template: str, site: dict, post: dict, posts: list[dict]) -> str:
    return fill(
        template,
        {
            "lang": site.get("lang", "ru"),
            "site_name": site["name"],
            "domain": site["domain"],
            "year": str(date.today().year),
            "slug": post["slug"],
            "title": post["title"],
            "description": post["description"],
            "category": post["category"],
            "h1": post["h1"],
            "intro": post["intro"],
            "image": post["image"],
            "image_alt": post["image_alt"],
            "published": post["published"],
            "updated": post["updated"],
            "sections": render_sections(post["sections"]),
            "faq": render_faq(post.get("faq", [])),
            "related": render_related(post.get("related", []), posts),
            "jsonld": render_jsonld(site, post),
        },
    )


def build_index(template: str, site: dict, posts: list[dict]) -> str:
    cards = []
    for post in posts:
        cards.append(
            '<article class="card post-card">'
            f'<p class="tag">{escape(post["category"])}</p>'
            f'<h3><a href="/blog/{post["slug"]}/">{escape(post["h1"])}</a></h3>'
            f'<p>{escape(post["intro"][:150])}…</p>'
            f'<p class="meta">{post["published"]}</p>'
            "</article>"
        )
    return fill(
        template,
        {
            "lang": site.get("lang", "ru"),
            "site_name": site["name"],
            "domain": site["domain"],
            "year": str(date.today().year),
            "title": f'{site["name"]} — {site["tagline"]}',
            "description": site["tagline"]
            + ". Касса, склад, зарплаты и аналитика для розницы, услуг и общепита.",
            "tagline": site["tagline"],
            "posts": "\n      ".join(cards),
        },
    )


def build_sitemap(site: dict, posts: list[dict]) -> str:
    base = f'https://{site["domain"]}'
    now = datetime.now().strftime("%Y-%m-%d")
    urls = [(f"{base}/", now, "1.0"), ]
    for post in posts:
        urls.append((f'{base}/blog/{post["slug"]}/', post.get("updated", now), "0.8"))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod, prio in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <priority>{prio}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build_robots(site: dict) -> str:
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /404.html\n\n"
        f'Sitemap: https://{site["domain"]}/sitemap.xml\n'
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--open", action="store_true", help="показать результат сборки")
    args = parser.parse_args()

    posts = load_posts()
    site = {  # настройки сайта
        "name": "ATLAS POS",
        "domain": "atlaspos.ru",
        "tagline": "Касса, склад и учёт для розницы, услуг и общепита",
        "lang": "ru",
    }

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    (DIST / "blog").mkdir()

    # ассеты
    shutil.copytree(PUBLIC / "images", DIST / "images", dirs_exist_ok=True)
    shutil.copy2(PUBLIC / "style.css", DIST / "style.css")

    post_tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    index_tpl = (ROOT / "index.html").read_text(encoding="utf-8")

    for post in posts:
        out = DIST / "blog" / post["slug"]
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(
            build_post(post_tpl, site, post, posts), encoding="utf-8"
        )
        print(f"✓ dist/blog/{post['slug']}/index.html")

    (DIST / "index.html").write_text(
        build_index(index_tpl, site, posts), encoding="utf-8"
    )
    (DIST / "sitemap.xml").write_text(build_sitemap(site, posts), encoding="utf-8")
    (DIST / "robots.txt").write_text(build_robots(site), encoding="utf-8")
    print("✓ dist/index.html\n✓ dist/sitemap.xml\n✓ dist/robots.txt")

    total = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file())
    print(f"\nГотово: {len(posts)} статей, {total/1024:.0f} КБ → dist/")
    if args.open:
        for f in sorted(DIST.rglob("*")):
            if f.is_file():
                print("  ", f.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
