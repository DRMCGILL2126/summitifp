#!/usr/bin/env python3
"""Regenerate sitemap.xml from the HTML files actually present.

Run after adding or removing pages:  python3 generate-sitemap.py

The previous sitemap was maintained by hand and had drifted badly — it listed 17
of 53 pages, so most Knowledge Center articles were invisible to search engines.
"""
import glob, os, subprocess, datetime

BASE = "https://www.summitifp.com"
EXCLUDE = {"404.html"}

def priority(path):
    if path == "index.html":                     return "1.0"
    if path.endswith("index.html"):              return "0.8"   # section landing pages
    if path.startswith("pages/"):                return "0.8"
    if path.startswith("knowledge-center/"):     return "0.7"
    if path.startswith("insights/"):             return "0.6"
    return "0.5"

def changefreq(path):
    if path == "index.html":                 return "weekly"
    if path.startswith("insights/"):         return "weekly"
    return "monthly"

def lastmod(path):
    """Last git commit date for the file, falling back to filesystem mtime."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", path],
                             capture_output=True, text=True, timeout=10)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()

def url_for(path):
    if path == "index.html":
        return BASE + "/"
    if path.endswith("/index.html"):
        return f"{BASE}/{path[:-len('index.html')]}"
    return f"{BASE}/{path}"

files = sorted(f for f in glob.glob("**/*.html", recursive=True)
               if "node_modules" not in f and f not in EXCLUDE)

rows = []
for f in files:
    rows.append(
        "  <url>\n"
        f"    <loc>{url_for(f)}</loc>\n"
        f"    <lastmod>{lastmod(f)}</lastmod>\n"
        f"    <changefreq>{changefreq(f)}</changefreq>\n"
        f"    <priority>{priority(f)}</priority>\n"
        "  </url>"
    )

xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
       + "\n".join(rows) + "\n</urlset>\n")

with open("sitemap.xml", "w", encoding="utf-8") as fh:
    fh.write(xml)

print(f"sitemap.xml regenerated — {len(files)} URLs")
