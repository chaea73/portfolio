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

  /* 연도 */
  const year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
