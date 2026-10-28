(() => {
  'use strict';
  const korean = document.documentElement.lang === 'ko';
  const localized = (english, koreanText) => korean ? koreanText : english;
  // Remember an explicit choice without redirecting deep links or browser history.
  let preferredLanguage;
  try { preferredLanguage = localStorage.getItem('logs-language'); } catch (e) {}
  document.querySelectorAll('[data-language-link]').forEach(link => {
    if (link.dataset.languageLink === preferredLanguage) {
      link.dataset.preferredLanguage = 'true';
      link.title = localized('Your saved language preference', '저장한 언어 설정');
    }
    link.addEventListener('click', () => {
      try { localStorage.setItem('logs-language', link.dataset.languageLink); } catch (e) {}
    });
  });
  const toggle = document.getElementById('theme-toggle');
  const themeLabel = () => {
    const dark = document.documentElement.dataset.theme === 'dark';
    toggle?.setAttribute('aria-label', localized(`Switch to ${dark ? 'light' : 'dark'} theme`, `${dark ? '밝은' : '어두운'} 테마로 전환`));
    toggle?.setAttribute('aria-pressed', String(dark));
  };
  themeLabel();
  toggle?.addEventListener('click', () => {
    const value = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = value;
    try { localStorage.setItem('logs-theme', value); } catch (e) {}
    themeLabel();
  });
  // Kramdown emits TeX script nodes. Convert them before the deferred MathJax
  // component runs; both block equations and raw $inline$ TeX then share v3.
  document.querySelectorAll('script[type^="math/tex"]').forEach(script => {
    const display = script.type.includes('mode=display');
    const node = document.createElement(display ? 'div' : 'span');
    node.className = display ? 'math-display' : 'math-inline';
    node.textContent = display ? `\\[${script.textContent}\\]` : `\\(${script.textContent}\\)`;
    script.replaceWith(node);
  });
  const body = document.getElementById('article-content');
  const toc = document.getElementById('toc-list');
  if (body && toc) {
    const list = document.createElement('ul');
    body.querySelectorAll('h2').forEach((heading, index) => {
      if (!heading.id) heading.id = `section-${index + 1}`;
      const link = document.createElement('a');
      link.href = `#${heading.id}`;
      link.textContent = heading.textContent;
      const item = document.createElement('li'); item.append(link); list.append(item);
      const anchor = document.createElement('a'); anchor.className = 'heading-link';
      anchor.href = `#${heading.id}`; anchor.textContent = '#';
      anchor.setAttribute('aria-label', localized(`Link to ${heading.textContent}`, `${heading.textContent} 항목으로 이동`)); heading.append(anchor);
    });
    toc.append(list);
    if (!list.children.length) toc.closest('details').hidden = true;
    body.querySelectorAll('table').forEach(table => {
      const wrapper = document.createElement('div'); wrapper.className = 'table-wrap';
      wrapper.tabIndex = 0; wrapper.setAttribute('role', 'region');
      wrapper.setAttribute('aria-label', localized('Scrollable data table', '가로로 스크롤할 수 있는 표'));
      table.before(wrapper); wrapper.append(table);
    });
  }
  document.querySelectorAll('[data-probability-explorer]').forEach(explorer => {
    const sliders = [...explorer.querySelectorAll('[data-weight]')];
    const result = explorer.querySelector('[data-result]');
    const update = () => {
      const weights = sliders.map(slider => Number(slider.value));
      const total = weights.reduce((sum, weight) => sum + weight, 0);
      const probabilities = total ? weights.map(weight => weight / total) : [1 / 3, 1 / 3, 1 / 3];
      const peak = Math.max(...probabilities);
      const mode = probabilities.indexOf(peak);
      const choice = (peak - 1 / 3) / (1 - 1 / 3);
      const mean = probabilities.reduce((sum, probability, i) => sum + i * probability, 0);
      const spread = probabilities.reduce((sum, probability, i) => sum + probability * Math.abs(i - mode), 0);
      const score = Math.max(0, 1 - spread / (2 / 3));
      explorer.querySelectorAll('[data-bar]').forEach((bar, i) => {
        bar.style.width = `${probabilities[i] * 100}%`;
      });
      sliders.forEach((slider, i) => slider.setAttribute('aria-valuetext', localized(`Weight ${weights[i]}; probability ${probabilities[i].toFixed(3)}`, `가중치 ${weights[i]}; 확률 ${probabilities[i].toFixed(3)}`)));
      result.textContent = localized(`${total ? '' : 'All weights are zero; using a uniform distribution. '}Probabilities (${probabilities.map(p => p.toFixed(3)).join(', ')}). Choice confidence ${choice.toFixed(3)}. Mean level ${mean.toFixed(3)}. Score confidence ${score.toFixed(3)}. Tied modes use the lowest index.`, `${total ? '' : '모든 가중치가 0이므로 균등분포를 사용합니다. '}확률 (${probabilities.map(p => p.toFixed(3)).join(', ')}). 선택 신뢰도 ${choice.toFixed(3)}. 평균 수준 ${mean.toFixed(3)}. 점수 신뢰도 ${score.toFixed(3)}. 최빈값이 여러 개이면 가장 작은 인덱스를 사용합니다.`);
    };
    sliders.forEach(slider => slider.addEventListener('input', update));
    update();
  });
  const input = document.getElementById('search-input');
  if (!input) return;
  const status = document.getElementById('search-status');
  const results = document.getElementById('search-results');
  let index = null, timer;
  const normalize = value => String(value || '').normalize('NFKC').toLowerCase();
  const render = () => {
    results.replaceChildren();
    const terms = normalize(input.value).trim().split(/\s+/).filter(Boolean);
    if (!terms.length) { status.textContent = localized('Enter a word or phrase to start.', '검색할 단어나 구문을 입력하세요.'); return; }
    if (!index) return;
    const matches = index.filter(post => post.lang === input.dataset.lang).map(post => {
      const title = normalize(post.title), tags = normalize(post.tags.join(' '));
      const text = normalize(`${post.title} ${post.tags.join(' ')} ${post.description} ${post.content}`);
      return { post, score: terms.every(term => text.includes(term)) ? terms.reduce((sum, term) => sum + (title.includes(term) ? 4 : tags.includes(term) ? 2 : 1), 0) : 0 };
    }).filter(row => row.score).sort((a, b) => b.score - a.score);
    status.textContent = localized(`${matches.length} ${matches.length === 1 ? 'article' : 'articles'} found.`, `${matches.length}편의 글을 찾았습니다.`);
    matches.forEach(({post}) => {
      const card = document.createElement('article'); card.className = 'post-card';
      const heading = document.createElement('h2'), link = document.createElement('a');
      link.href = post.url; link.textContent = post.title; heading.append(link);
      const description = document.createElement('p'); description.textContent = post.description;
      const meta = document.createElement('div'); meta.className = 'post-meta'; meta.textContent = post.date;
      card.append(heading, description, meta); results.append(card);
    });
  };
  const load = async () => {
    try {
      const response = await fetch(input.dataset.index);
      if (!response.ok) throw new Error('Search index unavailable');
      index = await response.json(); render();
    } catch (error) { status.textContent = localized('Search is unavailable. Please use Archive or try again later.', '검색을 불러오지 못했습니다. 전체 글에서 찾거나 잠시 후 다시 시도하세요.'); }
  };
  input.addEventListener('input', () => {
    clearTimeout(timer); timer = setTimeout(render, 100);
  });
  load();
})();
