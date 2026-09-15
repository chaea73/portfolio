/* ═══════════════════════════════════════════════════════════════
   박채아 — Portfolio (Instagram clone)
   ═══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';
  const root = document.documentElement;

  /* 테마 */
  const KEY = 'portfolio-theme';
  const themeBtn = document.getElementById('themeBtn');
  const meta = document.querySelector('meta[name="theme-color"]');
  function setTheme(t) {
    root.setAttribute('data-theme', t);
    if (meta) meta.setAttribute('content', t === 'dark' ? '#000000' : '#ffffff');
  }
  setTheme(localStorage.getItem(KEY) ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
  themeBtn?.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    setTheme(next); localStorage.setItem(KEY, next);
  });

  /* 사이드바 데코 버튼 → 맨 위로 */
  document.querySelectorAll('[data-scrolltop]').forEach((el) => {
    el.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  });

  /* 게시물 모달 */
  const modal = document.getElementById('modal');
  const dialog = modal?.querySelector('.modal__dialog');
  const media = document.getElementById('modalMedia');
  const body = document.getElementById('modalBody');
  const cat = document.getElementById('modalCat');
  const likes = document.getElementById('modalLikes');
  let last = null;

  function open(id) {
    const data = document.getElementById('data-' + id);
    if (!data || !modal) return;
    const img = data.getAttribute('data-media');
    if (img) {
      dialog.classList.remove('is-text');
      media.style.backgroundImage = "url('" + img + "')";
      if (likes) likes.textContent = '좋아요 ' + (data.getAttribute('data-likes') || '0') + '개';
    } else {
      dialog.classList.add('is-text');
      media.style.backgroundImage = '';
    }
    cat.textContent = data.getAttribute('data-cat') || '';
    body.innerHTML = data.innerHTML;
    last = document.activeElement;
    modal.hidden = false;
    document.body.classList.add('no-scroll');
    modal.querySelector('.modal__x')?.focus();
  }
  function close() {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    document.body.classList.remove('no-scroll');
    body.innerHTML = '';
    if (last && last.focus) last.focus();
  }

  document.querySelectorAll('[data-post]').forEach((el) => {
    el.addEventListener('click', () => open(el.getAttribute('data-post')));
  });
  // 모달 안 목록(둘러보기·알림)에서 항목 클릭 → 해당 게시물 열기
  body?.addEventListener('click', (e) => {
    const t = e.target.closest('[data-post]');
    if (t) open(t.getAttribute('data-post'));
  });
  modal?.querySelectorAll('[data-close]').forEach((el) => el.addEventListener('click', close));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });

  /* 스토리 뷰어 */
  const sv = document.getElementById('sv');
  const svStage = document.getElementById('svStage');
  const svBars = document.getElementById('svBars');
  const svName = document.getElementById('svName');
  let pages = [], idx = 0, timer = null, lastSv = null;
  const DUR = 4500;

  function openStory(id) {
    const src = document.getElementById('sd-' + id);
    if (!src || !sv) return;
    pages = Array.from(src.querySelectorAll('.spage'));
    if (!pages.length) return;
    if (svName) svName.textContent = src.getAttribute('data-label') || '';
    svBars.innerHTML = pages.map(() => '<span class="sv__bar"><span></span></span>').join('');
    lastSv = document.activeElement;
    sv.hidden = false;
    document.body.classList.add('no-scroll');
    showPage(0);
  }
  function showPage(i) {
    if (i >= pages.length) { closeStory(); return; }
    if (i < 0) i = 0;
    idx = i;
    svStage.innerHTML = pages[i].outerHTML;
    const bars = Array.from(svBars.children);
    bars.forEach((b, k) => {
      const f = b.firstElementChild;
      f.style.transition = 'none';
      f.style.width = k < i ? '100%' : '0%';
    });
    const cur = bars[i] && bars[i].firstElementChild;
    if (cur) {
      void cur.offsetWidth;
      cur.style.transition = 'width ' + DUR + 'ms linear';
      cur.style.width = '100%';
    }
    clearTimeout(timer);
    timer = setTimeout(() => showPage(i + 1), DUR);
  }
  function closeStory() {
    if (!sv || sv.hidden) return;
    clearTimeout(timer);
    sv.hidden = true;
    document.body.classList.remove('no-scroll');
    svStage.innerHTML = '';
    if (lastSv && lastSv.focus) lastSv.focus();
  }

  document.querySelectorAll('[data-story]').forEach((el) => {
    el.addEventListener('click', () => openStory(el.getAttribute('data-story')));
  });
  document.getElementById('svNext')?.addEventListener('click', () => showPage(idx + 1));
  document.getElementById('svPrev')?.addEventListener('click', () => showPage(idx - 1));
  sv?.querySelectorAll('[data-svclose]').forEach((el) => el.addEventListener('click', closeStory));
  document.addEventListener('keydown', (e) => {
    if (!sv || sv.hidden) return;
    if (e.key === 'Escape') closeStory();
    else if (e.key === 'ArrowRight') showPage(idx + 1);
    else if (e.key === 'ArrowLeft') showPage(idx - 1);
  });

  /* 연도 */
  const year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
