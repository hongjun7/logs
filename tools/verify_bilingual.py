#!/usr/bin/env python3
"""Check static bilingual routing and language-specific article collections."""
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json
import sys

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / '_site'
BASE = '/logs'

class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.language = None
        self.alternates = {}
        self.switches = {}
        self.links = []
        self.card_count = 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.language = attrs.get('lang')
        if tag == 'link' and attrs.get('hreflang'):
            self.alternates[attrs['hreflang']] = urlparse(attrs.get('href', '')).path
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
            if attrs.get('data-language-link'):
                self.switches[attrs['data-language-link']] = attrs.get('href')
        if tag == 'article' and 'post-card' in attrs.get('class', '').split():
            self.card_count += 1


def main():
    failures = []
    check = lambda condition, message: failures.append(message) if not condition else None
    index = json.loads((SITE / 'search.json').read_text())
    groups = defaultdict(dict)
    documents = {}
    for row in index:
        key, lang = row.get('translation_key'), row.get('lang')
        check(bool(key), f"Missing translation_key: {row['url']}")
        check(lang in ('en', 'ko'), f"Invalid language: {row['url']}")
        check(lang not in groups[key], f"Duplicate edition: {key} / {lang}")
        groups[key][lang] = row
        path = SITE / row['url'].removeprefix(BASE + '/')
        document = Document(path.read_text())
        documents[row['url']] = document
        check(document.language == lang, f"Wrong html language: {row['url']}")
    check(len(groups) == len(list((ROOT / '_posts').glob('*.md'))), 'Logical article count differs from _posts')
    for key, editions in groups.items():
        check(set(editions) == {'en', 'ko'}, f'Incomplete translation pair: {key}')
        if set(editions) != {'en', 'ko'}:
            continue
        check(editions['en']['tags'] == editions['ko']['tags'], f'Translation tags differ: {key}')
        check(editions['ko']['url'] == BASE + '/ko' + editions['en']['url'].removeprefix(BASE), f'Unexpected translation URL: {key}')
        for lang, row in editions.items():
            document = documents[row['url']]
            for target_lang, target in editions.items():
                check(document.switches.get(target_lang) == target['url'], f'Incorrect switch: {key} / {lang} to {target_lang}')
                check(document.alternates.get(target_lang) == target['url'], f'Incorrect hreflang: {key} / {lang} to {target_lang}')
            # Navigation must not silently send a Korean reader to an English article.
            for link in document.links:
                if link in documents:
                    check(documents[link].language == lang or link in document.switches.values(), f'Cross-language article navigation: {row["url"]} to {link}')
    for relative, lang in [('index.html', 'en'), ('archive.html', 'en'), ('tags.html', 'en'), ('search.html', 'en'), ('ko/index.html', 'ko'), ('ko/archive.html', 'ko'), ('ko/tags.html', 'ko'), ('ko/search.html', 'ko')]:
        path = SITE / relative
        text = path.read_text()
        document = Document(text)
        check(document.language == lang, f'Wrong listing language: {relative}')
        check(set(document.switches) == {'en', 'ko'}, f'Missing listing switches: {relative}')
        for link in document.links:
            if link in documents:
                check(documents[link].language == lang, f'Wrong listing edition: {relative} -> {link}')
        if relative == 'ko/index.html':
            check(document.card_count == len(groups), 'Korean home omits or duplicates articles')
        check('Welcome to Logs. hongjun7' not in text and "Hi, this is Hongjun. I'm interested in computation and optimization." not in text, f'Removed introduction reappeared: {relative}')
    counts = Counter(row.get('lang') for row in index)
    check(counts['en'] == counts['ko'] == len(groups), 'Search editions do not form complete pairs')
    script = (ROOT / 'assets/js/notes.js').read_text()
    check('post.lang === input.dataset.lang' in script, 'Search does not filter by language')
    print(f'{len(groups)} logical articles; search editions: {dict(counts)}')
    print(f'Bilingual routes, pairs, listings, hreflang and search isolation: {len(failures)} failures')
    for failure in failures:
        print(failure)
    return bool(failures)

if __name__ == '__main__':
    sys.exit(main())
