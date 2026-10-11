(() => {
  'use strict';
  const toggle = document.getElementById('theme-toggle');
  const themeLabel = () => {
    const dark = document.documentElement.dataset.theme === 'dark';
    toggle?.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} theme`);
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
      anchor.setAttribute('aria-label', `Link to ${heading.textContent}`); heading.append(anchor);
    });
    toc.append(list);
    if (!list.children.length) toc.closest('details').hidden = true;
    body.querySelectorAll('table').forEach(table => {
      const wrapper = document.createElement('div'); wrapper.className = 'table-wrap';
      wrapper.tabIndex = 0; wrapper.setAttribute('role', 'region');
      wrapper.setAttribute('aria-label', 'Scrollable data table');
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
      sliders.forEach((slider, i) => slider.setAttribute('aria-valuetext', `Weight ${weights[i]}; probability ${probabilities[i].toFixed(3)}`));
      result.textContent = `${total ? '' : 'All weights are zero; using a uniform distribution. '}Probabilities (${probabilities.map(p => p.toFixed(3)).join(', ')}). Choice confidence ${choice.toFixed(3)}. Mean level ${mean.toFixed(3)}. Score confidence ${score.toFixed(3)}. Tied modes use the lowest index.`;
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
    if (!terms.length) { status.textContent = 'Enter a word or phrase to start.'; return; }
    if (!index) return;
    const matches = index.map(post => {
      const title = normalize(post.title), tags = normalize(post.tags.join(' '));
      const text = normalize(`${post.title} ${post.tags.join(' ')} ${post.description} ${post.content}`);
      return { post, score: terms.every(term => text.includes(term)) ? terms.reduce((sum, term) => sum + (title.includes(term) ? 4 : tags.includes(term) ? 2 : 1), 0) : 0 };
    }).filter(row => row.score).sort((a, b) => b.score - a.score);
    status.textContent = `${matches.length} ${matches.length === 1 ? 'article' : 'articles'} found.`;
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
    } catch (error) { status.textContent = 'Search is unavailable. Please use Archive or try again later.'; }
  };
  input.addEventListener('input', () => {
    clearTimeout(timer); timer = setTimeout(render, 100);
  });
  load();
})();
