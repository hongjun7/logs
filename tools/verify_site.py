#!/usr/bin/env python3
"""Check the built Jekyll site's links, math preservation, and accidental tables.

Run after `bundle exec jekyll build`. Browser rendering remains a separate check.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / '_site'
BASEURL = '/logs/'

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.references = []
        self.math_text = []
        self.in_article = False
        self.excluded = 0
        self.tables = 0
        self.table_headers = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        if tag == 'div' and attrs.get('id') == 'article-content':
            self.in_article = True
        if tag == 'footer' and self.in_article:
            self.in_article = False
        if tag == 'a' and 'href' in attrs:
            self.references.append(attrs['href'])
        if tag in ('script', 'link', 'img'):
            self.references.append(attrs.get('src') or attrs.get('href', ''))
        if self.in_article:
            if tag in ('pre', 'code', 'script', 'style'):
                self.excluded += 1
            if tag == 'table':
                self.tables += 1
            if tag == 'thead':
                self.table_headers += 1

    def handle_endtag(self, tag):
        if self.in_article and tag in ('pre', 'code', 'script', 'style'):
            self.excluded -= 1

    def handle_data(self, data):
        if self.in_article and not self.excluded:
            self.math_text.append(data)


def main():
    if not (SITE / 'search.json').exists():
        sys.exit('Build the site first: bundle exec jekyll build')
    pages = {}
    for path in SITE.rglob('*.html'):
        page = Page()
        page.feed(path.read_text())
        pages[path.resolve()] = page
    failures = []
    for path, page in pages.items():
        for reference in page.references:
            parsed = urlparse(reference)
            if parsed.scheme or parsed.netloc or not reference:
                continue
            if not parsed.path:
                target = path
            elif parsed.path.startswith(BASEURL):
                target = SITE / unquote(parsed.path[len(BASEURL):])
            elif parsed.path.startswith('/'):
                failures.append(f'{path.relative_to(ROOT)}: outside baseurl: {reference}')
                continue
            else:
                target = path.parent / unquote(parsed.path)
            if target.is_dir():
                target /= 'index.html'
            target = target.resolve()
            if not target.exists():
                failures.append(f'{path.relative_to(ROOT)}: missing: {reference}')
            elif parsed.fragment and target in pages and unquote(parsed.fragment) not in pages[target].ids:
                failures.append(f'{path.relative_to(ROOT)}: missing anchor: {reference}')

    posts = json.loads((SITE / 'search.json').read_text())
    total_math = 0
    for post in posts:
        path = (SITE / post['url'][len(BASEURL):]).resolve()
        page = pages[path]
        stem = path.stem
        sources = list((ROOT / '_posts').glob(f'*-{stem}.md'))
        if len(sources) != 1:
            failures.append(f'{stem}: expected exactly one Markdown source')
            continue
        source = sources[0].read_text().split('---', 2)[2]
        source = re.sub(r'```[\s\S]*?```', '', source)
        expected = len(re.findall(r'\$\$[\s\S]*?\$\$', source))
        outside_math = re.sub(r'\$\$[\s\S]*?\$\$', '', source)
        if re.search(r'(?<!\\)\$', outside_math):
            failures.append(f'{stem}: raw single-dollar delimiter; use protected Kramdown math')
        rendered_text = ''.join(page.math_text)
        preserved = len(re.findall(r'\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]', rendered_text))
        total_math += preserved
        if expected != preserved:
            failures.append(f'{stem}: math count changed: {expected} source / {preserved} HTML')
        if page.tables != page.table_headers:
            failures.append(f'{stem}: table without a header; check for unescaped TeX pipes')
    print(f'{len(posts)} posts, {total_math} preserved math expressions, {len(pages)} HTML pages')
    print(f'Local links/assets, anchors, math counts, and table structure: {len(failures)} failures')
    for failure in failures:
        print(failure)
    return bool(failures)

if __name__ == '__main__':
    sys.exit(main())
