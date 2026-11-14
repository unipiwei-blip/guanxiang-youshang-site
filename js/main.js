/* 莞香攸商 · 站点脚本
   仅使用原生 API：无框架、无构建。 */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- 出现动画 ---------- */
  var rvs = document.querySelectorAll('.rv');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add('is-in');
          io.unobserve(e.target);
        }
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.12 });
    rvs.forEach(function (el) { io.observe(el); });
  } else {
    rvs.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* ---------- 顶栏进度 ---------- */
  var line = document.querySelector('.scroll-line');
  if (line) {
    var tick = function () {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      line.style.width = (h > 0 ? (window.scrollY / h) * 100 : 0) + '%';
    };
    window.addEventListener('scroll', tick, { passive: true });
    tick();
  }

  /* ---------- 抽屉菜单 ---------- */
  var drawer = document.querySelector('.drawer');
  var burger = document.querySelector('.burger');
  var closeBtns = document.querySelectorAll('[data-close-drawer]');
  if (drawer && burger) {
    var setOpen = function (open) {
      drawer.dataset.open = open ? 'true' : 'false';
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      document.documentElement.style.overflow = open ? 'hidden' : '';
    };
    burger.addEventListener('click', function () { setOpen(drawer.dataset.open !== 'true'); });
    closeBtns.forEach(function (b) { b.addEventListener('click', function () { setOpen(false); }); });
    drawer.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { setOpen(false); });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer.dataset.open === 'true') setOpen(false);
    });
  }

  /* ---------- 复制 ---------- */
  var toast = document.querySelector('.toast');
  var showToast = function (msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.dataset.show = 'true';
    clearTimeout(showToast.t);
    showToast.t = setTimeout(function () { toast.dataset.show = 'false'; }, 1800);
  };

  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var text = btn.dataset.copy;
      var done = function () {
        btn.dataset.done = 'true';
        btn.textContent = '已复制';
        showToast('已复制到剪贴板');
        setTimeout(function () { btn.dataset.done = 'false'; btn.textContent = '复制'; }, 2000);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () { showToast('复制失败，请手动选择文字复制'); });
      } else {
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand('copy'); done(); } catch (err) { showToast('复制失败，请手动选择文字复制'); }
        document.body.removeChild(ta);
      }
    });
  });

  /* ---------- 动态筛选 ---------- */
  var filters = document.querySelectorAll('.filter');
  var cards = document.querySelectorAll('[data-cat]');
  var empty = document.querySelector('.empty-state');
  if (filters.length && cards.length) {
    filters.forEach(function (f) {
      f.addEventListener('click', function () {
        filters.forEach(function (x) { x.setAttribute('aria-pressed', 'false'); });
        f.setAttribute('aria-pressed', 'true');
        var cat = f.dataset.filter;
        var shown = 0;
        cards.forEach(function (c) {
          var show = cat === 'all' || c.dataset.cat === cat;
          c.hidden = !show;
          if (show) shown++;
        });
        if (empty) empty.hidden = shown > 0;
      });
    });
  }

  /* ---------- FAQ ---------- */
  document.querySelectorAll('.faq__q').forEach(function (q) {
    q.addEventListener('click', function () {
      var item = q.closest('.faq__item');
      var open = item.dataset.open === 'true';
      item.dataset.open = open ? 'false' : 'true';
      q.setAttribute('aria-expanded', open ? 'false' : 'true');
    });
  });

  /* ---------- 年份 ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* ---------- 首屏网络场 ---------- */
  var canvas = document.getElementById('heroCanvas');
  if (canvas && canvas.getContext) {
    var ctx = canvas.getContext('2d');
    var w = 0, h = 0, dpr = Math.min(window.devicePixelRatio || 1, 2);
    var nodes = [];
    var hubs = [];
    var raf = null;
    var visible = true;

    var resize = function () {
      var rect = canvas.getBoundingClientRect();
      w = rect.width; h = rect.height;
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      var count = w < 700 ? 22 : 42;
      nodes = [];
      for (var i = 0; i < count; i++) {
        nodes.push({
          x: Math.random() * w,
          y: Math.random() * h,
          vx: (Math.random() - 0.5) * 0.16,
          vy: (Math.random() - 0.5) * 0.16,
          r: Math.random() * 1.5 + 0.7
        });
      }
      hubs = [
        { x: w * 0.14, y: h * 0.74, label: '攸县', phase: 0 },
        { x: w * 0.86, y: h * 0.36, label: '东莞', phase: 1.4 }
      ];
    };

    var drawArc = function (t) {
      var a = hubs[0], b = hubs[1];
      var cx = (a.x + b.x) / 2 - w * 0.05;
      var cy = Math.min(a.y, b.y) - h * 0.26;
      ctx.beginPath();
      ctx.moveTo(a.x, a.y);
      ctx.quadraticCurveTo(cx, cy, b.x, b.y);
      ctx.strokeStyle = 'rgba(226,35,26,.42)';
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 7]);
      ctx.lineDashOffset = -t * 26;
      ctx.stroke();
      ctx.setLineDash([]);

      // 沿线运动的信号点
      var p = (t * 0.08) % 1;
      var inv = 1 - p;
      var px = inv * inv * a.x + 2 * inv * p * cx + p * p * b.x;
      var py = inv * inv * a.y + 2 * inv * p * cy + p * p * b.y;
      ctx.beginPath();
      ctx.arc(px, py, 3, 0, Math.PI * 2);
      ctx.fillStyle = '#e2231a';
      ctx.fill();
      ctx.beginPath();
      ctx.arc(px, py, 8, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(226,35,26,.16)';
      ctx.fill();
    };

    var drawHub = function (hub, t) {
      var pulse = (Math.sin(t * 1.2 + hub.phase) + 1) / 2;
      ctx.beginPath();
      ctx.arc(hub.x, hub.y, 4 + pulse * 2, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(226,35,26,.9)';
      ctx.fill();
      ctx.beginPath();
      ctx.arc(hub.x, hub.y, 14 + pulse * 16, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(244,238,227,' + (0.22 - pulse * 0.12) + ')';
      ctx.lineWidth = 1;
      ctx.stroke();
      if (w > 760) {
        ctx.font = '600 11px "PingFang SC","Microsoft YaHei",sans-serif';
        ctx.fillStyle = 'rgba(244,238,227,.5)';
        ctx.textAlign = 'center';
        ctx.fillText(hub.label, hub.x, hub.y + 26);
      }
    };

    var frame = function (t) {
      ctx.clearRect(0, 0, w, h);
      for (var i = 0; i < nodes.length; i++) {
        var n = nodes[i];
        n.x += n.vx; n.y += n.vy;
        if (n.x < 0 || n.x > w) n.vx *= -1;
        if (n.y < 0 || n.y > h) n.vy *= -1;
      }
      // 近邻连线
      for (var a = 0; a < nodes.length; a++) {
        for (var b = a + 1; b < nodes.length; b++) {
          var dx = nodes[a].x - nodes[b].x;
          var dy = nodes[a].y - nodes[b].y;
          var d2 = dx * dx + dy * dy;
          if (d2 < 13200) {
            var alpha = (1 - d2 / 13200) * 0.3;
            ctx.strokeStyle = 'rgba(244,238,227,' + alpha.toFixed(3) + ')';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(nodes[a].x, nodes[a].y);
            ctx.lineTo(nodes[b].x, nodes[b].y);
            ctx.stroke();
          }
        }
      }
      for (var k = 0; k < nodes.length; k++) {
        ctx.beginPath();
        ctx.arc(nodes[k].x, nodes[k].y, nodes[k].r, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(244,238,227,.5)';
        ctx.fill();
      }
      drawArc(t);
      hubs.forEach(function (hub) { drawHub(hub, t); });
      raf = requestAnimationFrame(frame);
    };

    var start = function () {
      if (raf || reduce) return;
      raf = requestAnimationFrame(frame);
    };
    var stop = function () {
      if (raf) { cancelAnimationFrame(raf); raf = null; }
    };

    resize();
    if (reduce) {
      ctx.clearRect(0, 0, w, h);
      nodes.forEach(function (n) {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(244,238,227,.45)';
        ctx.fill();
      });
      drawArc(0);
      hubs.forEach(function (hub) { drawHub(hub, 0); });
    } else {
      start();
    }

    var rt = null;
    window.addEventListener('resize', function () {
      clearTimeout(rt);
      rt = setTimeout(function () {
        stop();
        resize();
        if (!reduce) start();
      }, 220);
    });

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
        if (visible) start(); else stop();
      }, { threshold: 0.05 }).observe(canvas);
    }

    document.addEventListener('visibilitychange', function () {
      if (document.hidden) stop(); else if (visible) start();
    });
  }
})();
