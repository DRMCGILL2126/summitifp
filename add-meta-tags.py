#!/usr/bin/env python3
"""Backfill social/SEO meta tags on any page that is missing them.

Safe to re-run: every tag is added only if absent, so existing hand-written
tags are never overwritten and nothing is ever duplicated.

Run this after new pages are published (the Insights pages are generated
automatically and arrive without social tags), then regenerate the sitemap:

    python3 add-meta-tags.py && python3 generate-sitemap.py
"""
import glob, re, html

BASE = "https://www.summitifp.com"

def og_image(path):
    if path.startswith("knowledge-center/"):
        return f"{BASE}/images/og-knowledge-center.png"
    if path.startswith("insights/"):
        return f"{BASE}/images/og-insights.png"
    return f"{BASE}/images/og-default.png"

def url_for(path):
    if path == "index.html":
        return BASE + "/"
    if path.endswith("/index.html"):
        return f"{BASE}/{path[:-len('index.html')]}"
    return f"{BASE}/{path}"

def is_article(path):
    return (path.startswith(("knowledge-center/", "insights/"))
            and not path.endswith("index.html"))

def main():
    files = sorted(f for f in glob.glob("**/*.html", recursive=True)
                   if "node_modules" not in f)
    changed = 0
    for f in files:
        src = open(f, encoding="utf-8").read()
        i = src.find("</head>")
        if i == -1:
            continue
        head = src[:i]

        m = re.search(r"<title>(.*?)</title>", head, re.S | re.I)
        title = html.unescape(m.group(1)).strip() if m else "Summit Investments & Financial Planning"
        short = html.escape(title.split(" | ")[0])
        d = re.search(r'<meta name="description" content="(.*?)"', head, re.S | re.I)
        desc = d.group(1).strip() if d else ""
        url = url_for(f)

        def missing(pat):
            return not re.search(pat, head, re.I)

        add = []
        if missing(r'rel="canonical"'):
            add.append(f'  <link rel="canonical" href="{url}">')
        if missing(r'property="og:title"'):
            add.append(f'  <meta property="og:title" content="{short}">')
        if missing(r'property="og:description"') and desc:
            add.append(f'  <meta property="og:description" content="{desc}">')
        if missing(r'property="og:url"'):
            add.append(f'  <meta property="og:url" content="{url}">')
        if missing(r'property="og:type"'):
            add.append(f'  <meta property="og:type" content="{"article" if is_article(f) else "website"}">')
        if missing(r'property="og:image"'):
            add.append(f'  <meta property="og:image" content="{og_image(f)}">')
            add.append('  <meta property="og:image:width" content="1200">')
            add.append('  <meta property="og:image:height" content="630">')
        if missing(r'property="og:site_name"'):
            add.append('  <meta property="og:site_name" content="Summit Investments &amp; Financial Planning">')
        if missing(r'name="twitter:card"'):
            add.append('  <meta name="twitter:card" content="summary_large_image">')
        if missing(r'name="twitter:title"'):
            add.append(f'  <meta name="twitter:title" content="{short}">')
        if missing(r'name="twitter:description"') and desc:
            add.append(f'  <meta name="twitter:description" content="{desc}">')
        if missing(r'name="twitter:image"'):
            add.append(f'  <meta name="twitter:image" content="{og_image(f)}">')

        if add:
            open(f, "w", encoding="utf-8").write(src[:i] + "\n".join(add) + "\n" + src[i:])
            changed += 1
            print(f"  +{len(add):2d} tags → {f}")

    print(f"\n{changed} of {len(files)} pages updated"
          if changed else f"\nall {len(files)} pages already tagged")

if __name__ == "__main__":
    main()
