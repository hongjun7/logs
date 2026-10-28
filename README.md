# Logs

Hongjun Jang's research and engineering notes: machine learning, knowledge graphs,
algorithms, and systems. The custom Jekyll layouts use a quiet, narrow-column
reading design inspired by [Lil'Log](https://lilianweng.github.io/).

## Build and preview

Use Ruby 3.3 and Bundler. Dependencies are locked in `Gemfile.lock`.

```sh
bundle install
bundle exec jekyll build
python3 tools/verify_site.py
python3 tools/verify_bilingual.py
python3 tools/verify_translation_content.py
python3 tools/verify_examples.py
bundle exec jekyll serve --host 127.0.0.1 --port 4000
```

Open <http://127.0.0.1:4000/logs/>. Production configuration uses
`https://hongjun7.github.io/logs/`; `relative_url` handles assets and local links.
The repository remains a Jekyll/GitHub Pages site. A local build does not publish
changes. The legacy TeXt gem remains for build compatibility; active pages use
`note-base`, `home`, and `article` layouts and `assets/css/notes.css`.

## Writing an article

Put posts in `_posts/YYYY-MM-DD-slug.md`. Preserve existing filenames to preserve
URLs. Use a title, subtitle, tag array, revision date, source-check date, and translation links:

```yaml
---
title: "A precise title"
lang: en
translation_key: YYYY-MM-DD-slug
translation_url: /ko/YYYY/MM/DD/slug.html
tags: ["machine-learning", "engineering"]
subtitle: "A one-sentence explanation of the topic."
last_modified_at: 2026-10-11
sources_checked_at: 2026-10-11
---
```

Start with an accessible summary and reading path. Define notation and assumptions
before derivations. Identify illustrative calculations, author-reported results,
and locally measured results separately. Link primary papers, official docs, or
pinned implementation revisions near the claims they support. Update the
source-check date only after checking the relevant evidence.

### English and Korean

Existing English URLs stay at `/YYYY/MM/DD/slug.html`. Each complete Korean
translation is a regular Jekyll page in `ko/YYYY-MM-DD-slug.md` with this metadata:

```yaml
---
layout: article
lang: ko
date: YYYY-MM-DD
translation_key: YYYY-MM-DD-slug
permalink: /ko/YYYY/MM/DD/slug.html
original_url: /YYYY/MM/DD/slug.html
title: "한국어 제목"
subtitle: "한국어 설명"
tags: ["same-tags-as-the-original"]
last_modified_at: YYYY-MM-DD
sources_checked_at: YYYY-MM-DD
translated_at: YYYY-MM-DD
---
```

Keep the original article's revision and source-check dates; the translation date
does not imply that its sources were checked again. Translate the full body,
including caveats and figure descriptions, and preserve equations, code, cited
URLs, and measured numbers. Each pair shares one `translation_key` and identical
tags. Static pages require an explicit `date`; filenames alone do not set it.

The EN / 한국어 links lead to the same article in the other language, including
with JavaScript disabled. Navigation, article neighbors, archive, topics, and
search stay in the current language. An explicit switch is remembered locally;
there is no automatic redirect, so shared URLs and browser history remain stable.
English posts use the existing paginator; the Korean home lists all translations.
Search indexes both languages and filters results to the selected language.
No custom Jekyll plugin is required.

Run `python3 tools/verify_bilingual.py` after the build to check pair completeness,
reciprocal language links, metadata, localized listings, and search isolation.
Run `python3 tools/verify_translation_content.py` to compare equations, fenced
code, source URLs, and section coverage across each translation pair. These
checks protect content invariants; they do not replace semantic review of prose.

### Mathematics

Kramdown uses `$$...$$` **on one line** for inline mathematics. For a display
formula, put opening and closing `$$` on separate lines, with blank lines around
the whole block. Kramdown protects TeX before Markdown processing; local MathJax
3.2.2 then renders it as SVG in the browser.

```text
Inline: $$p_k\ge0$$ and $$\sum_k p_k=1$$.

$$
\mathbb E[X]=\sum_x x\,p(x).
$$
```

Use `\lvert ... \rvert` or `\vert` for cardinality/absolute-value bars, `\Vert`
for norms, and `\mid` for conditioning. Literal pipes can make Markdown interpret
prose as a table, including inside an inline formula. Do not write raw single
`$` delimiters: Markdown escape/emphasis processing can change their TeX.

Display equations, tables, and code blocks scroll within the article on small
screens. Verify every new formula in a real desktop and mobile browser; a clean
build alone cannot establish correct rendering. The static checker detects math
loss, broken internal links/assets, and suspicious headerless tables. The
[verification record](verification/2026-10-11.md) records the current browser QA.

## Dependencies and attribution

MathJax is served locally, including its license; see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Search runs on the generated
`search.json` index. Theme selection is stored only in the browser's local storage.
No external fonts or math CDN are required.
