/* ═══════════════════════════════════════════════════════════════
   박채아 — Portfolio (Instagram concept)
   1) 테마 전환   2) 게시물 모달   3) 푸터 연도
   ═══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  const root = document.documentElement;

  /* 1. 테마 ─────────────────────────────────────────────── */
  const KEY = 'portfolio-theme';
  const themeBtn = document.getElementById('themeBtn');
  const meta = document.querySelector('meta[name="theme-color"]');

  function setTheme(theme) {
    root.setAttribute('data-theme', theme);
    if (themeBtn) themeBtn.setAttribute('aria-label', theme === 'dark' ? '밝은 테마로 전환' : '어두운 테마로 전환');
    if (meta) meta.setAttribute('content', theme === 'dark' ? '#000000' : '#ffffff');
  }
  setTheme(localStorage.getItem(KEY) ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));

  themeBtn?.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    setTheme(next);
    localStorage.setItem(KEY, next);
  });

  /* 2. 게시물 모달 ──────────────────────────────────────── */
  const modal     = document.getElementById('modal');
  const dialog    = modal?.querySelector('.modal__dialog');
  const modalMedia = document.getElementById('modalMedia');
  const modalBody = document.getElementById('modalBody');
  const modalCat  = document.getElementById('modalCat');
  let lastFocused = null;

  function openPost(id) {
    const data = document.getElementById('data-' + id);
    if (!data || !modal) return;

    const media = data.getAttribute('data-media');
    const cat   = data.getAttribute('data-cat') || '';

    // 미디어(이미지) 유무에 따라 레이아웃 전환
    if (media) {
      dialog.classList.remove('is-text');
      modalMedia.style.backgroundImage = "url('" + media + "')";
    } else {
      dialog.classList.add('is-text');
      modalMedia.style.backgroundImage = '';
    }

    modalCat.textContent = cat;
    modalBody.innerHTML = data.innerHTML;

    lastFocused = document.activeElement;
    modal.hidden = false;
    document.body.classList.add('no-scroll');
    modal.querySelector('.modal__close')?.focus();
  }

  function closePost() {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    document.body.classList.remove('no-scroll');
    modalBody.innerHTML = '';
    if (lastFocused && lastFocused.focus) lastFocused.focus();
  }

  // 타일 · 하이라이트 클릭
  document.querySelectorAll('[data-post]').forEach((el) => {
    el.addEventListener('click', () => openPost(el.getAttribute('data-post')));
  });

  // 닫기: 배경/닫기버튼/ESC
  modal?.querySelectorAll('[data-close]').forEach((el) => el.addEventListener('click', closePost));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closePost(); });

  /* 3. 푸터 연도 ────────────────────────────────────────── */
  const year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
