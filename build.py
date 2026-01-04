#!/usr/bin/env python3

import re
import shutil
import yaml
import markdown
from pathlib import Path

ROOT = Path.cwd()
out_folder = "docs"
OUT = ROOT / out_folder
TEMPLATE = ROOT / "page-template.html"

STYLE = ROOT / "style.css"
ASSETS = ROOT / "assets"

OUT.mkdir(exist_ok=True)

md = markdown.Markdown(
    extensions=["codehilite", "tables", "fenced_code", "footnotes"],
    extension_configs={"codehilite": {"guess_lang": False}},
)

template_html = TEMPLATE.read_text(encoding="utf-8")

# Xử lý cái FRONT_MATTER, tức là mấy cái metadata của tệp Markdown ấy

def parse_front_matter(text):
    if text.startswith("---"):
        _, fm, body = text.split("---", 2)
        meta = yaml.safe_load(fm) or {}
        return meta, body.strip()
    return {}, text

# Cập nhật lại các link tệp Markdown sang HTMl đã được built
def rewrite_md_links(html):
    return re.sub(r'href="([^"]+)\.md"', r'href="\1.html"', html)

# Copy style.css và `assets` sang.

if STYLE.exists():
    shutil.copy2(STYLE, OUT / STYLE.name)

if ASSETS.exists():
    shutil.copytree(ASSETS, OUT / "assets", dirs_exist_ok=True)

# Bắt đầu build Markdown từ đây

for md_path in ROOT.rglob("*.md"):
    if md_path.parts[0] == out_folder:
        continue

    if md_path.name.lower() == "readme.md":
        continue

    rel = md_path.relative_to(ROOT)
    out_path = (OUT / rel).with_suffix(".html")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    raw = md_path.read_text(encoding="utf-8")
    meta, body = parse_front_matter(raw)

    html_body = md.convert(body)
    html_body = rewrite_md_links(html_body)

    title = meta.get("title", md_path.stem)

    page = (
        template_html
        .replace("{{ title }}", title)
        .replace("{{ content }}", html_body)
    )

    out_path.write_text(page, encoding="utf-8")
    md.reset()

    print(f"✔ {rel} → {out_path.relative_to(ROOT)}")
