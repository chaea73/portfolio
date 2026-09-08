/* ═══════════════════════════════════════════════════════════════
   박채아 — Portfolio
   1) 테마 전환  2) 모바일 메뉴  3) 스크롤 상태
   4) 스킬 숙련도 점 그리기  5) 등장 애니메이션
   ═══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  const root = document.documentElement;

  /* 1. 테마 ─────────────────────────────────────────────── */
  const KEY = 'portfolio-theme';
  const themeBtn = document.getElementById('themeBtn');
  const meta = document.querySelector('meta[name="theme-color"]');

  setTheme(localStorage.getItem(KEY) ||
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));

  function setTheme(theme) {
    root.setAttribute('data-theme', theme);
    if (themeBtn) themeBtn.setAttribute('aria-label', theme === 'dark' ? '밝은 테마로 전환' : '어두운 테마로 전환');
    if (meta) meta.setAttribute('content', theme === 'dark' ? '#0d1117' : '#f6f8fa');
  }

  themeBtn?.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    setTheme(next);
    localStorage.setItem(KEY, next);
  });

  /* 2. 모바일 메뉴 ──────────────────────────────────────── */
  const menuBtn = document.getElementById('menuBtn');
  const nav = document.getElementById('nav');

  function closeMenu() {
    nav?.classList.remove('open');
    menuBtn?.setAttribute('aria-expanded', 'false');
    menuBtn?.setAttribute('aria-label', '메뉴 열기');
  }

  menuBtn?.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.setAttribute('aria-label', open ? '메뉴 닫기' : '메뉴 열기');
  });

  nav?.addEventListener('click', (e) => { if (e.target.closest('a')) closeMenu(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeMenu(); });

  /* 3. 스크롤: 헤더 선 + 현재 섹션 표시 ─────────────────── */
  const header = document.getElementById('header');
  const navLinks = Array.from(document.querySelectorAll('.nav a'));
  const targets = navLinks
    .map((a) => document.querySelector(a.getAttribute('href')))
    .filter(Boolean);

  let queued = false;

  function onScroll() {
    queued = false;
    header?.classList.toggle('stuck', window.scrollY > 8);

    const line = window.scrollY + 160;
    let current = null;
    for (const el of targets) if (el.offsetTop <= line) current = el;

    // 페이지 맨 아래에 도달하면 마지막 항목을 활성화
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 4) {
      current = targets[targets.length - 1];
    }

    navLinks.forEach((a) => {
      a.classList.toggle('on', !!current && a.getAttribute('href') === '#' + current.id);
    });
  }

  window.addEventListener('scroll', () => {
    if (!queued) { queued = true; requestAnimationFrame(onScroll); }
  }, { passive: true });

  window.addEventListener('resize', onScroll);
  onScroll();

  /* 4. 스킬 숙련도 (data-level 0~3 → 점 세 개) ──────────── */
  document.querySelectorAll('.skills__list li[data-level]').forEach((li) => {
    const level = Math.max(0, Math.min(3, Number(li.dataset.level) || 0));
    if (!level) return;

    const gauge = document.createElement('span');
    gauge.className = 'lv';
    gauge.setAttribute('role', 'img');
    gauge.setAttribute('aria-label', `숙련도 ${['', '하', '중', '상'][level]}`);

    for (let i = 1; i <= 3; i++) {
      const dot = document.createElement('i');
      if (i <= level) dot.className = 'f';
      gauge.appendChild(dot);
    }
    li.appendChild(gauge);
  });

  /* 5. 등장 애니메이션 ──────────────────────────────────── */
  const items = document.querySelectorAll('.fade');

  if (!window.IntersectionObserver || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    items.forEach((el) => el.classList.add('in'));
  } else {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry, i) => {
        if (!entry.isIntersecting) return;
        setTimeout(() => entry.target.classList.add('in'), i * 80);
        io.unobserve(entry.target);
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -6% 0px' });

    items.forEach((el) => io.observe(el));
  }

  /* 6. 푸터 연도 ────────────────────────────────────────── */
  const year = document.getElementById('year');
  if (year) year.textContent = String(new Date().getFullYear());
})();
