// 共通描画エンジン（株式会社サード 動画シリーズ）
// 1920x1080 Canvas。各シーンは scenes.js で定義し renderFrame(t) を実装する
const W = 1920, H = 1080, FPS = 30;
// DUR / HUD_TITLE は各動画の scenes.js で定義する
const cv = document.getElementById('c'); cv.width = W; cv.height = H; // 2D オーバーレイ（WebGL の上に重ねる）
const ctx = cv.getContext('2d');
const buf = document.createElement('canvas'); buf.width = W; buf.height = H;
const bctx = buf.getContext('2d');
const tint = document.createElement('canvas'); tint.width = W; tint.height = H;
const tctx = tint.getContext('2d');
const logoCv = document.createElement('canvas'); logoCv.width = W; logoCv.height = 400;
const lctx = logoCv.getContext('2d');

const JP = '"Noto Sans JP"', EN = '"Oswald"';
const CY = '#00E0FF', BL = '#2A5CFF', GR = '#8A93A6', BG = '#04050A';

// ---------- utils ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const lerp = (a, b, x) => a + (b - a) * x;
const eOutExpo = x => x >= 1 ? 1 : 1 - Math.pow(2, -10 * x);
const eOutCubic = x => 1 - Math.pow(1 - x, 3);
const eInCubic = x => x * x * x;
const eInOut = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const eOutBack = x => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
function rng(seed) {
  return function () {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
const hash = (...n) => rng(n.reduce((a, b) => a * 31 + b * 7919 + 13, 7))();
const font = (w, s, f) => `${w} ${s}px ${f}`;

function reset() {
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  ctx.shadowBlur = 0; ctx.shadowColor = 'transparent';
  ctx.letterSpacing = '0px'; ctx.textAlign = 'left'; ctx.textBaseline = 'alphabetic';
}

function txt(s, x, y, o = {}) {
  const { size = 60, weight = 700, family = JP, color = '#fff', align = 'left', ls = 0, alpha = 1, base = 'alphabetic' } = o;
  if (alpha <= 0) return;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.font = font(weight, size, family);
  ctx.letterSpacing = ls + 'px';
  ctx.textBaseline = base;
  ctx.fillStyle = color;
  let w = ctx.measureText(s).width - ls;
  let sx = align === 'center' ? x - w / 2 : align === 'right' ? x - w : x;
  ctx.fillText(s, sx, y);
  ctx.restore();
  return w;
}

// 1文字ずつ下からせり上がる
function reveal(s, x, y, t0, t, o = {}) {
  const { size = 80, weight = 900, family = JP, color = '#fff', align = 'left', ls = 0, stagger = 0.05, dur = 0.6, alpha = 1 } = o;
  ctx.save();
  ctx.font = font(weight, size, family);
  const chars = [...s];
  const ws = chars.map(c => ctx.measureText(c).width + ls);
  const total = ws.reduce((a, b) => a + b, 0) - ls;
  let cx = align === 'center' ? x - total / 2 : align === 'right' ? x - total : x;
  ctx.beginPath(); ctx.rect(0, y - size * 1.25, W, size * 1.5); ctx.clip();
  ctx.fillStyle = color;
  const ba = ctx.globalAlpha;
  chars.forEach((c, i) => {
    const p = eOutExpo(seg(t, t0 + i * stagger, t0 + i * stagger + dur));
    if (p > 0) {
      ctx.globalAlpha = ba * p * alpha;
      ctx.fillText(c, cx, y + (1 - p) * size * 1.1);
    }
    cx += ws[i];
  });
  ctx.restore();
  return total;
}

function measure(s, size, weight, family, ls = 0) {
  ctx.save(); ctx.font = font(weight, size, family); ctx.letterSpacing = ls + 'px';
  const w = ctx.measureText(s).width - ls; ctx.restore(); return w;
}

function grad(x0, y0, x1, y1, a = CY, b = BL) {
  const g = ctx.createLinearGradient(x0, y0, x1, y1);
  g.addColorStop(0, a); g.addColorStop(1, b); return g;
}

// ---------- background ----------
const parts = [...Array(150)].map((_, i) => {
  const r = rng(i + 1);
  return { x: r() * W, y: r() * H, z: .2 + r() * .8, s: r() * 2 + .6, ph: r() * 6.28 };
});
function bg(t, o = {}) {
  const { grid = 0.6, glow = 1, pa = 1, hue = 0 } = o;
  ctx.fillStyle = BG; ctx.fillRect(0, 0, W, H);
  if (glow > 0) {
    const gx = W * .5 + Math.sin(t * .3) * 420, gy = H * .55 + Math.cos(t * .23) * 160;
    let g = ctx.createRadialGradient(gx, gy, 0, gx, gy, 950);
    g.addColorStop(0, `rgba(42,92,255,${.20 * glow})`); g.addColorStop(1, 'rgba(42,92,255,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
    const hx = W * .8 + Math.cos(t * .21) * 200, hy = H * .2 + Math.sin(t * .31) * 100;
    g = ctx.createRadialGradient(hx, hy, 0, hx, hy, 600);
    g.addColorStop(0, `rgba(0,224,255,${.08 * glow})`); g.addColorStop(1, 'rgba(0,224,255,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }
  if (grid > 0) {
    ctx.save();
    ctx.strokeStyle = `rgba(120,160,255,${.07 * grid})`; ctx.lineWidth = 1;
    const sp = 96, off = (t * 18) % sp;
    ctx.beginPath();
    for (let x = -sp + off; x < W + sp; x += sp) { ctx.moveTo(Math.round(x) + .5, 0); ctx.lineTo(Math.round(x) + .5, H); }
    for (let y = 12; y < H; y += sp) { ctx.moveTo(0, y + .5); ctx.lineTo(W, y + .5); }
    ctx.stroke();
    ctx.restore();
  }
  if (pa > 0) {
    ctx.save();
    for (const p of parts) {
      const y = ((p.y - t * 38 * p.z) % H + H) % H;
      const x = p.x + Math.sin(t * .5 + p.ph) * 22;
      ctx.globalAlpha = pa * (.12 + .5 * p.z) * (.6 + .4 * Math.sin(t * 2 + p.ph));
      ctx.fillStyle = p.z > .85 ? CY : '#9fb4ff';
      const s = p.s * p.z * 1.6;
      ctx.fillRect(x, y, s, s);
    }
    ctx.restore();
  }
}

// ---------- post effects ----------
const grains = [...Array(6)].map((_, k) => {
  const c = document.createElement('canvas'); c.width = 960; c.height = 540;
  const g = c.getContext('2d'); const im = g.createImageData(960, 540); const r = rng(1000 + k);
  for (let i = 0; i < im.data.length; i += 4) { const v = r() * 255; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
  g.putImageData(im, 0, 0); return c;
});
let vignette;
function post(t) {
  if (!vignette) {
    vignette = ctx.createRadialGradient(W / 2, H / 2, H * .55, W / 2, H / 2, H * 1.1);
    vignette.addColorStop(0, 'rgba(0,0,0,0)'); vignette.addColorStop(1, 'rgba(0,0,0,.6)');
  }
  ctx.fillStyle = vignette; ctx.fillRect(0, 0, W, H);
  ctx.save();
  ctx.globalCompositeOperation = 'overlay'; ctx.globalAlpha = .045;
  ctx.drawImage(grains[Math.floor(t * FPS) % grains.length], 0, 0, W, H);
  ctx.restore();
}

function glitch(a, seed) {
  if (a <= 0) return;
  bctx.globalCompositeOperation = 'source-over';
  bctx.drawImage(cv, 0, 0);
  const r = rng(seed * 101 + 7);
  const n = Math.floor(3 + a * 16);
  for (let i = 0; i < n; i++) {
    const y = r() * H, h = 4 + r() * 70 * a, dx = (r() - .5) * 220 * a;
    ctx.drawImage(buf, 0, y, W, h, dx, y, W, h);
  }
  // chromatic split
  const off = 14 * a;
  for (const [col, dx] of [['#ff0040', off], ['#00e0ff', -off]]) {
    tctx.globalCompositeOperation = 'source-over'; tctx.drawImage(buf, 0, 0);
    tctx.globalCompositeOperation = 'multiply'; tctx.fillStyle = col; tctx.fillRect(0, 0, W, H);
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = .7 * a;
    ctx.drawImage(tint, dx, 0); ctx.restore();
  }
}

// ---------- HUD ----------
function hud(t, a) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a * .55;
  ctx.strokeStyle = '#fff'; ctx.lineWidth = 2;
  const m = 48, L = 34;
  ctx.beginPath();
  ctx.moveTo(m, m + L); ctx.lineTo(m, m); ctx.lineTo(m + L, m);
  ctx.moveTo(W - m - L, m); ctx.lineTo(W - m, m); ctx.lineTo(W - m, m + L);
  ctx.moveTo(m, H - m - L); ctx.lineTo(m, H - m); ctx.lineTo(m + L, H - m);
  ctx.moveTo(W - m - L, H - m); ctx.lineTo(W - m, H - m); ctx.lineTo(W - m, H - m - L);
  ctx.stroke();
  ctx.restore();
  txt(HUD_TITLE, m + 56, m + 24, { size: 17, weight: 500, family: EN, color: '#fff', ls: 5, alpha: a * .6 });
  txt('SHINJUKU — TOKYO', W - m - 56, m + 24, { size: 17, weight: 500, family: EN, color: '#fff', ls: 5, align: 'right', alpha: a * .6 });
  const sec = Math.floor(t), fr = Math.floor((t - sec) * FPS);
  const tc = `00:00:${String(sec).padStart(2, '0')}:${String(fr).padStart(2, '0')}`;
  txt(tc, W - m - 56, H - m - 10, { size: 17, weight: 300, family: EN, color: '#fff', ls: 4, align: 'right', alpha: a * .6 });
  // progress
  ctx.save(); ctx.globalAlpha = a * .5;
  ctx.fillStyle = 'rgba(255,255,255,.2)'; ctx.fillRect(m + 56, H - m - 16, 260, 2);
  ctx.fillStyle = CY; ctx.fillRect(m + 56, H - m - 16, 260 * (t / DUR), 2);
  ctx.restore();
  // blinking dot
  if (Math.floor(t * 2) % 2 === 0) { ctx.save(); ctx.globalAlpha = a * .8; ctx.fillStyle = CY; ctx.beginPath(); ctx.arc(m + 330, H - m - 15, 4, 0, 7); ctx.fill(); ctx.restore(); }
}


function glowDot(x, y, r, a = 1, col = CY) {
  ctx.save(); ctx.globalAlpha *= a;
  const g = ctx.createRadialGradient(x, y, 0, x, y, r * 4);
  g.addColorStop(0, col); g.addColorStop(1, col + '00');
  ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r * 4, 0, 7); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(x, y, r * .6, 0, 7); ctx.fill();
  ctx.restore();
}

