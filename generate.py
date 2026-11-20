#!/usr/bin/env python3
"""AtlasPos SEO page generator.

Usage:
    python3 generate.py            # рендерит все страницы из pages.json
    python3 generate.py --clean    # очищает public/generated перед сборкой

Dev: Bokov777
"""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent
PUBLIC = ROOT / "public"
OUT = PUBLIC / "generated"


def load_config() -> dict:
    with (ROOT / "pages.json").open(encoding="utf-8") as fh:
        return json.load(fh)


def render_feature(item: dict) -> str:
    return (
        '<article class="card">'
        f'<h3>{escape(item["title"])}</h3>'
        f'<p>{escape(item["text"])}</p>'
        "</article>"
    )


def render_page(template: str, site: dict, page: dict) -> str:
    hero = page["hero"]
    values = {
        "lang": site.get("lang", "ru"),
        "site_name": site["name"],
        "domain": site["domain"],
        "year": str(date.today().year),
        "slug": page["slug"],
        "title": page["title"],
        "description": page["description"],
        "keywords": ", ".join(page.get("keywords", [])),
        "h1": hero["h1"],
        "lead": hero["lead"],
        "image": hero["image"],
        "features": "\n      ".join(render_feature(f) for f in page.get("features", [])),
    }
    html = template
    for key, val in values.items():
        html = html.replace("{{" + key + "}}", str(val))
    return html


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean", action="store_true", help="очистить public/generated")
    args = parser.parse_args()

    config = load_config()
    site = config["site"]
    template = (ROOT / "template.html").read_text(encoding="utf-8")

    if args.clean and OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True, exist_ok=True)

    for page in config["pages"]:
        page_dir = OUT / page["slug"]
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(
            render_page(template, site, page), encoding="utf-8"
        )
        print(f"✓ {page_dir.relative_to(ROOT)}/index.html")

    print(f"\nГотово: {len(config['pages'])} стр. → {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
