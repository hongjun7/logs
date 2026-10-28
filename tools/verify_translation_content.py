#!/usr/bin/env python3
"""Check content invariants; human semantic review is still required for prose."""
from collections import Counter
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
PATTERNS = {
    'math': r'\$\$[\s\S]*?\$\$',
    'fenced_code': r'```[\s\S]*?```',
    'source_urls': r'https?://[^\s)<>"\]]+',
}


def main():
    failures, report = [], []
    for original in sorted((ROOT / '_posts').glob('*.md')):
        translation = ROOT / 'ko' / original.name
        if not translation.exists():
            failures.append(f'{original.name}: missing Korean edition')
            continue
        english = original.read_text().split('---', 2)[2]
        korean = translation.read_text().split('---', 2)[2]
        row = {'article': original.stem}
        for name, pattern in PATTERNS.items():
            source = Counter(re.findall(pattern, english))
            target = Counter(re.findall(pattern, korean))
            row[name] = sum(source.values())
            if source != target:
                failures.append(f'{original.name}: {name} changed in translation')
        row['sections'] = len(re.findall(r'^## ', english, re.M))
        if row['sections'] != len(re.findall(r'^## ', korean, re.M)):
            failures.append(f'{original.name}: section coverage changed')
        report.append(row)
    print(f'{len(report)} article pairs: math, fenced code, source URLs and section counts; {len(failures)} failures')
    for failure in failures:
        print(failure)
    if '--json' in sys.argv:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
