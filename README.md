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
URLs. Use a title, subtitle, tag array, revision date, and source-check date:

```yaml
---
title: "A precise title"
tags: ["machine-learning", "engineering"]
subtitle: "A one-sentence explanation of the topic."
last_modified_at: 2026-10-11
sources_checked_at: 2026-10-11
---
```

Use a short topic title and a direct introductory paragraph. Keep the subtitle
to one brief listing description; the article opens with its own explanation.
Use descriptive section headings, define notation before derivations, and place
each result's assumptions and limits beside it. Avoid reading guides, repeated
summary labels, and generic warnings. Distinguish illustrative calculations,
author-reported results, and local measurements. Link primary sources near the
claims they support. An editorial revision changes `last_modified_at`, not
`sources_checked_at`; advance the latter only after rechecking the evidence.

### Mathematics

Kramdown uses `$$...$$` **on one line** for inline mathematics. For a display
formula, put opening and closing `$$` on separate lines, with blank lines around
the whole block. Kramdown protects TeX before Markdown processing; MathJax
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

MathJax 3.2.2 loads from jsDelivr, pinned by SRI, because GitHub Pages serves the
2 MB bundle slowly. A byte-identical copy and its license live in
`assets/js/vendor/` as the fallback; see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Search runs on the generated
`search.json` index. Theme selection is stored only in the browser's local storage.
No external fonts are required.
