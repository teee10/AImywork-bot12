// ============================================================
//  株式会社サード クロージング代行サービス紹介動画  (1920x1080 / 30fps / 120s)
//  120BPM。シーンの頭は小節頭（2秒単位）に合わせている
// ============================================================
const DUR = 120;
const HUD_TITLE = 'THIRD INC.  /  CLOSING OUTSOURCING';
const RED = '#FF3D5A';

// ---------- shared helpers ----------
function slashWipe(w) {
  if (w >= 1) return;
  const px = lerp(-700, W + 200, eInOut(w)), sk = 260;
  ctx.save();
  ctx.fillStyle = BG;
  ctx.beginPath(); ctx.moveTo(px + 420, 0); ctx.lineTo(W + 400, 0); ctx.lineTo(W + 400, H); ctx.lineTo(px + 420 - sk, H); ctx.fill();
  ctx.fillStyle = grad(px, 0, px + 420, 0, BL, CY);
  ctx.beginPath(); ctx.moveTo(px + 120, 0); ctx.lineTo(px + 420, 0); ctx.lineTo(px + 420 - sk, H); ctx.lineTo(px + 120 - sk, H); ctx.fill();
  ctx.fillStyle = '#fff';
  ctx.beginPath(); ctx.moveTo(px + 60, 0); ctx.lineTo(px + 80, 0); ctx.lineTo(px + 80 - sk, H); ctx.lineTo(px + 60 - sk, H); ctx.fill();
  ctx.restore();
}

function barsOut(e) {
  if (e <= 0) return;
  ctx.fillStyle = BG;
  for (let i = 0; i < 12; i++) { const p = eInOut(clamp(e * 1.7 - i * .06)); ctx.fillRect(i % 2 ? W - W * p : 0, i * 90, W * p, 90); }
}

function shade(a, col = '4,5,10') {
  if (a <= 0) return;
  ctx.fillStyle = `rgba(${col},${a})`; ctx.fillRect(0, 0, W, H);
}

function label(x, y, s, lt, t0, o = {}) {
  const { color = CY, align = 'left' } = o;
  const lp = eOutExpo(seg(lt, t0, t0 + .6));
  if (align === 'center') {
    const w = measure(s, 24, 500, EN, 10);
    ctx.fillStyle = color;
    ctx.fillRect(W / 2 - w / 2 - 76, y - 10, 50 * lp, 3);
    ctx.fillRect(W / 2 + w / 2 + 26 + 50 * (1 - lp), y - 10, 50 * lp, 3);
    txt(s, W / 2, y, { size: 24, weight: 500, family: EN, color, ls: 10, align: 'center', alpha: seg(lt, t0 + .05, t0 + .45) });
  } else {
    ctx.fillStyle = color; ctx.fillRect(x, y - 10, 56 * lp, 3);
    txt(s, x + 76, y, { size: 24, weight: 500, family: EN, color, ls: 10, alpha: seg(lt, t0 + .05, t0 + .45) });
  }
}

function rays(t, a) {
  if (a <= 0) return;
  ctx.save();
  ctx.translate(W / 2, H / 2);
  ctx.rotate(t * .05);
  for (let i = 0; i < 18; i++) {
    ctx.rotate(Math.PI * 2 / 18);
    ctx.fillStyle = `rgba(0,224,255,${.03 * a * (i % 2 ? 1 : .5)})`;
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(1400, -90); ctx.lineTo(1400, 90); ctx.fill();
  }
  ctx.restore();
}

function bigNumber(no, lt, ex) {
  ctx.save();
  const nx = W - 70 + 260 * (1 - eOutExpo(seg(lt, .2, 1.4))) - lt * 10 - ex * 300;
  ctx.font = font(700, 620, EN); ctx.letterSpacing = '-10px'; ctx.textAlign = 'right';
  ctx.strokeStyle = `rgba(0,224,255,${.12 * (1 - ex)})`; ctx.lineWidth = 2;
  ctx.strokeText(no, nx, H - 40);
  ctx.restore();
}

function logo(l, Y) {
  const wmSize = 190, wmLs = 34;
  const wmW = measure('THIRD', wmSize, 700, EN, wmLs);
  const markW = 3 * 38 + 2 * 18, gapM = 56;
  const totalW = markW + gapM + wmW;
  const X = W / 2 - totalW / 2;
  const OY = 300;
  lctx.setTransform(1, 0, 0, 1, 0, 0);
  lctx.clearRect(0, 0, W, 400);
  [80, 120, 160].forEach((hh, i) => {
    const p = eOutExpo(seg(l, i * .12, .6 + i * .12));
    const bx = X + i * 56, h2 = hh * p, sk = 30 * p * hh / 160;
    const g = lctx.createLinearGradient(0, OY - 160, 0, OY);
    g.addColorStop(0, CY); g.addColorStop(1, BL);
    lctx.fillStyle = g;
    lctx.beginPath(); lctx.moveTo(bx, OY); lctx.lineTo(bx + 38, OY); lctx.lineTo(bx + 38 + sk, OY - h2); lctx.lineTo(bx + sk, OY - h2); lctx.closePath(); lctx.fill();
  });
  const mp = eInOut(seg(l, .3, 1.1));
  lctx.save();
  lctx.beginPath(); lctx.rect(X + markW + gapM - 10, 0, (wmW + 60) * mp, 400); lctx.clip();
  lctx.font = font(700, wmSize, EN); lctx.letterSpacing = wmLs + 'px'; lctx.fillStyle = '#fff'; lctx.textBaseline = 'alphabetic';
  lctx.fillText('THIRD', X + markW + gapM, OY);
  lctx.restore();
  const sw = seg(l, 2.6, 3.5);
  if (sw > 0 && sw < 1) {
    lctx.save(); lctx.globalCompositeOperation = 'source-atop';
    const sx = lerp(X - 300, X + totalW + 300, eInOut(sw));
    const g = lctx.createLinearGradient(sx - 120, 0, sx + 120, 0);
    g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(.5, 'rgba(255,255,255,.95)'); g.addColorStop(1, 'rgba(255,255,255,0)');
    lctx.fillStyle = g; lctx.transform(1, 0, -.35, 1, 0, 0); lctx.fillRect(sx - 20, 0, 240, 400);
    lctx.restore();
  }
  ctx.save();
  ctx.shadowColor = 'rgba(0,224,255,.35)'; ctx.shadowBlur = 40;
  const lsc = 1 + .02 * l;
  ctx.translate(W / 2, Y); ctx.scale(lsc, lsc); ctx.translate(-W / 2, -Y);
  ctx.drawImage(logoCv, 0, Y - OY);
  ctx.restore();
  if (mp > 0 && mp < 1) { ctx.fillStyle = CY; ctx.fillRect(X + markW + gapM - 10 + (wmW + 60) * mp, Y - 170, 3, 200); }
}

function redGlow(x, y, r, a) {
  if (a <= 0) return;
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, `rgba(255,61,90,${.14 * a})`); g.addColorStop(1, 'rgba(255,61,90,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
function cyanGlow(x, y, r, a) {
  if (a <= 0) return;
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, `rgba(0,224,255,${.12 * a})`); g.addColorStop(1, 'rgba(0,224,255,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}

// ============================================================
// 0-10s  OPENING  「商談、決めきれていますか？」→ 課題の連打
// ============================================================
const PAINS = [
  { s: '商談はあるのに、決まらない。', x: 560, y: 250 },
  { s: '最後のひと押しが、できない。', x: 1360, y: 330 },
  { s: '見込み客が、他社に流れる。', x: 580, y: 830 },
  { s: '成約率が、人によってバラバラ。', x: 1320, y: 760 },
  { s: '追客が、後回しになる。', x: 960, y: 545 },
];
function sOpen(lt, t) {
  bg(t, { grid: .4 * seg(lt, 0, 3), glow: .4 + .4 * seg(lt, 4, 9), pa: seg(lt, 0, 2) });
  redGlow(W / 2, H / 2, 1000, seg(lt, 4, 6) * (1 + .3 * Math.sin(lt * 8)));

  let shake = 0;
  if (lt > 9) shake = seg(lt, 9, 9.8) * 14;
  ctx.save();
  if (shake) ctx.translate((hash(Math.floor(t * 30), 1) - .5) * shake * 2, (hash(Math.floor(t * 30), 2) - .5) * shake * 2);

  const q = '商談、決めきれていますか？';
  const qa = 1 - seg(lt, 3.4, 3.9);
  if (qa > 0) {
    const chars = [...q];
    const n = Math.floor(seg(lt, .6, .6 + chars.length * .13) * chars.length);
    ctx.save(); ctx.globalAlpha = qa;
    txt('QUESTION', W / 2, 430, { size: 22, weight: 500, family: EN, color: CY, align: 'center', ls: 12, alpha: seg(lt, .2, .6) });
    const full = measure(q, 100, 900, JP, 4);
    const s = chars.slice(0, n).join('');
    if (n) txt(s, W / 2 - full / 2, 590, { size: 100, weight: 900, ls: 4 });
    const cw = n ? measure(s, 100, 900, JP, 4) + 4 : 0;
    if (Math.floor(lt * 3) % 2 === 0 || (n > 0 && n < chars.length)) { ctx.fillStyle = CY; ctx.fillRect(W / 2 - full / 2 + cw + 10, 494, 6, 110); }
    ctx.restore();
  }

  let g = 0;
  PAINS.forEach((p, i) => {
    const t0 = 4 + i;
    if (lt < t0) return;
    const k = eInOut(seg(lt, t0 + .78, t0 + 1.1));
    const ent = eOutExpo(seg(lt, t0, t0 + .3));
    const size = lerp(112, 46, k) * lerp(1.15, 1, ent);
    const x = lerp(W / 2, p.x, k), y = lerp(585, p.y, k);
    const col = k > .5 ? '#FF8FA0' : '#ffffff';
    txt(p.s, x, y, { size, weight: 900, color: col, align: 'center', alpha: lerp(1, .55, k) * clamp(ent * 2) });
    if (k < .5) {
      const w = measure(p.s, size, 900, JP);
      ctx.fillStyle = RED; ctx.fillRect(x - w / 2, y + 30, w * eOutExpo(seg(lt, t0 + .1, t0 + .6)), 5);
      txt('ISSUE', x - w / 2, y - size - 12, { size: 22, weight: 500, family: EN, color: RED, ls: 10, alpha: ent });
    }
    if (lt - t0 < .1) g = .55;
  });
  ctx.restore();
  if (lt > 9) g = seg(lt, 9, 9.8);
  shade(eInCubic(seg(lt, 9.6, 10)));
  return { glitch: g };
}

// ============================================================
// 10-18s  TITLE  「私たちが決めきります。」→ CLOSING OUTSOURCING
// ============================================================
function sTitle(lt, t) {
  bg(t, { grid: .5, glow: 1.2 });
  if (lt < 3) {
    rays(t, seg(lt, 0, 1));
    reveal('その商談、', W / 2, 470, .15, lt, { size: 78, weight: 700, align: 'center', stagger: .06 });
    reveal('私たちが決めきります。', W / 2, 650, .7, lt, { size: 124, weight: 900, align: 'center', stagger: .05, color: grad(W / 2 - 680, 0, W / 2 + 680, 0, '#ffffff', CY) });
    barsOut(seg(lt, 2.5, 3.0));
    return { flash: lt < .25 ? (1 - lt / .25) * .9 : 0, glitch: lt < .15 ? .6 : 0 };
  }
  const l = lt - 3;
  rays(t, 1);
  const z = 1 + eInCubic(seg(l, 4.3, 5.0)) * 3;
  ctx.save();
  ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2);
  ctx.globalAlpha = 1 - eInCubic(seg(l, 4.5, 5.0));
  // mini mark
  [30, 45, 60].forEach((hh, i) => {
    const p = eOutExpo(seg(l, .05 + i * .08, .5 + i * .08));
    const bx = W / 2 - 40 + i * 28, by = 330;
    ctx.fillStyle = grad(0, by - 60, 0, by, CY, BL);
    ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(bx + 18, by); ctx.lineTo(bx + 18 + 12 * p * hh / 60, by - hh * p); ctx.lineTo(bx + 12 * p * hh / 60, by - hh * p); ctx.fill();
  });
  const tw = measure('CLOSING OUTSOURCING', 136, 700, EN, 16);
  const mp = eInOut(seg(l, .2, 1.1));
  ctx.save();
  ctx.beginPath(); ctx.rect(W / 2 - tw / 2 - 20, 350, (tw + 40) * mp, 220); ctx.clip();
  txt('CLOSING OUTSOURCING', W / 2, 540, { size: 136, weight: 700, family: EN, align: 'center', ls: 16 });
  ctx.restore();
  if (mp > 0 && mp < 1) { ctx.fillStyle = CY; ctx.fillRect(W / 2 - tw / 2 - 20 + (tw + 40) * mp, 380, 4, 180); }
  reveal('クロージング代行サービス', W / 2, 670, 1.0, l, { size: 72, weight: 900, align: 'center', ls: 12, stagger: .05, color: grad(W / 2 - 520, 0, W / 2 + 520, 0, '#ffffff', '#9eefff') });
  const dl = eOutExpo(seg(l, 1.5, 2.3));
  ctx.fillStyle = grad(W / 2 - 280, 0, W / 2 + 280, 0, BL, CY); ctx.fillRect(W / 2 - 280 * dl, 720, 560 * dl, 2);
  txt('by THIRD Inc.', W / 2, 785, { size: 28, weight: 300, family: EN, color: GR, align: 'center', ls: 10, alpha: seg(l, 1.8, 2.4) });
  ctx.restore();
  return { flash: seg(l, 4.6, 5.0) * .9 };
}

// ============================================================
// 18-30s  CONCEPT  クロージング代行とは / 商談から成約まで
// ============================================================
const LAYERS = [
  { en: 'HEARING', jp: 'ヒアリング', sub: '課題・予算・決裁者を把握' },
  { en: 'PROPOSAL', jp: '提案', sub: '刺さる提案で意思決定を後押し' },
  { en: 'CLOSING', jp: '成約', sub: '契約締結まで責任を持つ' },
];
function sConcept(lt, t) {
  bg(t, { grid: .6, glow: 1 });
  if (lt < 5.8) {
    const out = seg(lt, 5.2, 5.8);
    ctx.save(); ctx.globalAlpha = 1 - out;
    label(0, 170, 'WHAT WE DO', lt, .1, { align: 'center' });
    reveal('クロージング代行とは、', W / 2, 270, .3, lt, { size: 64, weight: 900, align: 'center', stagger: .05 });
    const m = eInOut(seg(lt, 2.0, 3.2));
    const c1x = lerp(640, 850, m) - out * 120, c2x = lerp(1280, 1070, m) + out * 120, cy = 590;
    const r1 = 190 * clamp(eOutBack(seg(lt, .5, 1.1))), r2 = 190 * clamp(eOutBack(seg(lt, .8, 1.4)));
    if (m > 0) {
      ctx.save();
      ctx.beginPath(); ctx.arc(c1x, cy, r1, 0, 7); ctx.clip();
      ctx.fillStyle = `rgba(0,224,255,${.28 * m * (.8 + .2 * Math.sin(lt * 5))})`;
      ctx.beginPath(); ctx.arc(c2x, cy, r2, 0, 7); ctx.fill();
      ctx.restore();
    }
    if (r1 > 0) {
      ctx.save(); ctx.fillStyle = 'rgba(255,255,255,.04)'; ctx.strokeStyle = 'rgba(255,255,255,.7)'; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.arc(c1x, cy, r1, 0, 7); ctx.fill(); ctx.stroke(); ctx.restore();
    }
    if (r2 > 0) {
      ctx.save(); ctx.fillStyle = 'rgba(0,224,255,.06)'; ctx.strokeStyle = CY; ctx.lineWidth = 3; ctx.shadowColor = CY; ctx.shadowBlur = 20;
      ctx.beginPath(); ctx.arc(c2x, cy, r2, 0, 7); ctx.fill(); ctx.stroke(); ctx.restore();
    }
    const l1 = c1x - 60 * m, l2 = c2x + 60 * m;
    txt('御社', l1, cy + 14, { size: 60, weight: 900, align: 'center', alpha: seg(lt, .9, 1.3) });
    txt('YOUR COMPANY', l1, cy + 58, { size: 18, weight: 500, family: EN, color: GR, align: 'center', ls: 6, alpha: seg(lt, 1.0, 1.4) });
    txt('THIRD', l2, cy + 18, { size: 60, weight: 700, family: EN, align: 'center', ls: 6, alpha: seg(lt, 1.2, 1.6) });
    txt('CLOSING TEAM', l2, cy + 58, { size: 18, weight: 500, family: EN, color: CY, align: 'center', ls: 6, alpha: seg(lt, 1.3, 1.7) });
    txt('ONE TEAM', W / 2, cy - 230, { size: 26, weight: 700, family: EN, color: CY, align: 'center', ls: 10, alpha: seg(lt, 3.1, 3.6) });
    if (lt > 3.1) {
      ctx.save(); ctx.strokeStyle = `rgba(0,224,255,${.6 * seg(lt, 3.1, 3.6)})`; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(W / 2, cy - 215); ctx.lineTo(W / 2, cy - 130); ctx.stroke(); ctx.restore();
    }
    reveal('御社が集めた商談を、THIRDが成約に変える。', W / 2, 910, 3.5, lt, { size: 50, weight: 700, align: 'center', stagger: .03, dur: .5 });
    ctx.restore();
    return { glitch: lt < .08 ? .4 : 0 };
  }
  const l = lt - 5.8;
  const out = eInCubic(seg(l, 5.6, 6.2));
  ctx.save(); ctx.globalAlpha = 1 - out; ctx.translate(0, -out * 80);
  label(0, 160, 'FROM MEETING TO CONTRACT', l, .1, { align: 'center' });
  reveal('商談から、成約まで。', W / 2, 255, .3, l, { size: 66, weight: 900, align: 'center', stagger: .045 });
  const ys = [800, 630, 460];
  const flow = seg(l, 2.4, 3.6);
  LAYERS.forEach((L, i) => {
    const p = eOutExpo(seg(l, .7 + i * .5, 1.4 + i * .5));
    if (p <= 0) return;
    const cx = W / 2, y = ys[i] + (1 - p) * 80, w = 1120, h = 130, sk = 40;
    const lit = i === 2 ? seg(l, 3.4, 3.9) : 0;
    ctx.save(); ctx.globalAlpha *= p;
    const g = ctx.createLinearGradient(cx - w / 2, 0, cx + w / 2, 0);
    g.addColorStop(0, `rgba(42,92,255,${.12 + i * .06 + lit * .2})`); g.addColorStop(1, `rgba(0,224,255,${.06 + i * .05 + lit * .15})`);
    ctx.fillStyle = g;
    ctx.strokeStyle = i === 2 ? CY : 'rgba(0,224,255,.45)'; ctx.lineWidth = i === 2 ? 3 : 1.5;
    if (i === 2) { ctx.shadowColor = CY; ctx.shadowBlur = 10 + 30 * lit; }
    ctx.beginPath();
    ctx.moveTo(cx - w / 2 + sk, y - h / 2); ctx.lineTo(cx + w / 2 + sk, y - h / 2); ctx.lineTo(cx + w / 2 - sk, y + h / 2); ctx.lineTo(cx - w / 2 - sk, y + h / 2); ctx.closePath();
    ctx.fill(); ctx.stroke();
    ctx.restore();
    txt('0' + (i + 1), cx - 510, y + 14, { size: 40, weight: 700, family: EN, color: 'rgba(255,255,255,.35)', alpha: p });
    txt(L.en, cx - 445, y + 14, { size: 38, weight: 700, family: EN, color: CY, ls: 8, alpha: p });
    txt(L.jp, cx - 160, y + 16, { size: 44, weight: 900, alpha: p });
    txt(L.sub, cx + 110, y + 12, { size: 24, weight: 500, color: '#b9c1d0', alpha: p });
  });
  if (flow > 0 && flow < 1) {
    const y = lerp(ys[0] + 65, ys[2] - 65, eInOut(flow));
    ctx.save(); ctx.strokeStyle = CY; ctx.lineWidth = 3; ctx.shadowColor = CY; ctx.shadowBlur = 20;
    ctx.beginPath(); ctx.moveTo(W / 2 + 520, ys[0] + 65); ctx.lineTo(W / 2 + 520, y); ctx.stroke(); ctx.restore();
    glowDot(W / 2 + 520, y, 8);
  } else if (flow >= 1) {
    ctx.save(); ctx.strokeStyle = CY; ctx.lineWidth = 3; ctx.globalAlpha *= 1 - out;
    ctx.beginPath(); ctx.moveTo(W / 2 + 520, ys[0] + 65); ctx.lineTo(W / 2 + 520, ys[2] - 65); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(W / 2 + 506, ys[2] - 45); ctx.lineTo(W / 2 + 520, ys[2] - 65); ctx.lineTo(W / 2 + 534, ys[2] - 45); ctx.stroke();
    ctx.restore();
  }
  ctx.restore();
  return {};
}

// ============================================================
// 30-48s  ISSUE → SOLUTION ×3
// ============================================================
const CASES = [
  { p: ['商談はあるのに', '決まらない。'], ps: '成約率が上がらず、商談がムダになる。', s: ['クロージングの', 'プロが代行。'], ss: '決めきる力で、商談を成約に変える。' },
  { p: ['成約が', '属人化している。'], ps: '決められる人に頼り切り、再現できない。', s: ['勝ちパターンを', '仕組みに。'], ss: '成約トークと進め方を型にして共有。' },
  { p: ['見込み客が', '他社に流れる。'], ps: '追客が後回しになり、検討中のまま失注。', s: ['追客まで', '徹底して伴走。'], ss: '検討中の顧客も、最後まで追いかける。' },
];
function sProblems(lt, t) {
  bg(t, { grid: .5, glow: .7 });
  if (lt < 1.6) {
    const o = seg(lt, 1.25, 1.6);
    ctx.save(); ctx.globalAlpha = 1 - o;
    const a = eOutExpo(seg(lt, .05, .6));
    txt('ISSUE', W / 2 - 60 - 60 * (1 - a), 540, { size: 120, weight: 700, family: EN, color: RED, align: 'right', ls: 10, alpha: a });
    txt('→', W / 2, 530, { size: 90, weight: 300, family: EN, color: '#fff', align: 'center', alpha: seg(lt, .3, .6) });
    txt('SOLUTION', W / 2 + 60 + 60 * (1 - a), 540, { size: 120, weight: 700, family: EN, color: CY, align: 'left', ls: 10, alpha: a });
    reveal('よくあるクロージングの課題を、こう解決する。', W / 2, 660, .45, lt, { size: 44, weight: 700, align: 'center', stagger: .025, dur: .45 });
    ctx.restore();
    return { glitch: lt < .08 ? .5 : 0 };
  }
  const CL = 16.4 / 3;
  const i = Math.min(2, Math.floor((lt - 1.6) / CL)), ct = lt - 1.6 - i * CL, c = CASES[i];
  const ex = eInCubic(seg(ct, CL - .45, CL));
  redGlow(480, 540, 800, seg(ct, .3, 1) * (1 - seg(ct, 2.2, 3)) + .3);
  cyanGlow(1440, 540, 800, seg(ct, 2, 2.8) * 1.2);
  ctx.save(); ctx.globalAlpha = 1 - ex;
  txt(`CASE ${String(i + 1).padStart(2, '0')} / 03`, W - 160, 250, { size: 22, weight: 500, family: EN, color: '#fff', align: 'right', ls: 8, alpha: seg(ct, .3, .7) * .6 });
  // divider
  const dv = eOutExpo(seg(ct, .4, 1.2));
  ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,.18)'; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(W / 2 + 90, 180); ctx.lineTo(lerp(W / 2 + 90, W / 2 - 90, dv), lerp(180, 900, dv)); ctx.stroke(); ctx.restore();
  // issue
  const dim = 1 - .45 * seg(ct, 2.2, 2.8);
  ctx.save(); ctx.globalAlpha *= dim;
  label(160, 380, 'ISSUE ' + String(i + 1).padStart(2, '0'), ct, .3, { color: RED });
  reveal(c.p[0], 156, 490, .4, ct, { size: 84, weight: 900, color: '#e3e7ee', stagger: .045 });
  reveal(c.p[1], 156, 590, .55, ct, { size: 84, weight: 900, color: '#e3e7ee', stagger: .045 });
  ctx.fillStyle = RED; ctx.fillRect(160, 628, 120 * eOutExpo(seg(ct, 1.0, 1.5)), 5);
  txt(c.ps, 160, 690, { size: 27, weight: 500, color: '#b9c1d0', alpha: seg(ct, 1.1, 1.6) });
  ctx.restore();
  // arrow
  const ar = seg(ct, 1.7, 2.2);
  for (let k = 0; k < 3; k++) {
    const a = clamp(ar * 3 - k) * (.4 + .6 * (.5 + .5 * Math.sin(lt * 8 - k)));
    ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = CY; ctx.lineWidth = 5; ctx.lineCap = 'round';
    const x = W / 2 - 40 + k * 32;
    ctx.beginPath(); ctx.moveTo(x, 510); ctx.lineTo(x + 24, 540); ctx.lineTo(x, 570); ctx.stroke(); ctx.restore();
  }
  // solution
  const sx = 1060;
  label(sx, 380, 'SOLUTION', ct, 2.0);
  const sg = grad(sx, 0, sx + 700, 0, '#ffffff', CY);
  reveal(c.s[0], sx - 4, 490, 2.1, ct, { size: 84, weight: 900, color: sg, stagger: .045 });
  reveal(c.s[1], sx - 4, 590, 2.3, ct, { size: 84, weight: 900, color: sg, stagger: .045 });
  ctx.fillStyle = grad(sx, 0, sx + 120, 0); ctx.fillRect(sx, 628, 120 * eOutExpo(seg(ct, 2.7, 3.2)), 5);
  txt(c.ss, sx, 690, { size: 27, weight: 500, color: '#dfe6f2', alpha: seg(ct, 2.8, 3.3) });
  ctx.restore();
  slashWipe(seg(ct, 0, .5));
  return { glitch: (ct > 2.05 && ct < 2.12) ? .3 : 0 };
}

// ============================================================
// 48-66s  SERVICE MENU（6項目）
// ============================================================
const MENU = [
  { jp: '商談前の事前設計', sub: '顧客の課題・決裁構造を整理', ic: 0 },
  { jp: '商談同席・代行', sub: 'オンライン／訪問の商談を担当', ic: 3 },
  { jp: '反論処理・条件交渉', sub: '懸念を解消し、合意形成へ導く', ic: 2 },
  { jp: '契約締結フォロー', sub: '契約まで、責任を持って伴走', ic: 4 },
  { jp: '追客・失注防止', sub: '検討中の顧客を継続フォロー', ic: 1 },
  { jp: '成約データ分析', sub: '勝因・敗因を分析し、成約率を改善', ic: 5 },
];
function icon(i, cx, cy, s, col, k) {
  ctx.save();
  ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = 3; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  if (i === 0) {
    [1, .62, .25].forEach(r => { ctx.beginPath(); ctx.arc(cx, cy, s * r, 0, 7); ctx.stroke(); });
    const d = s * 1.3 * (1 - k * .6);
    ctx.beginPath(); ctx.moveTo(cx + d, cy - d); ctx.lineTo(cx + 4, cy - 4); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx + d, cy - d); ctx.lineTo(cx + d + 10, cy - d - 2); ctx.moveTo(cx + d, cy - d); ctx.lineTo(cx + d + 2, cy - d - 10); ctx.stroke();
  } else if (i === 1) {
    for (let r = 0; r < 3; r++) {
      const y = cy - s * .7 + r * s * .7;
      ctx.strokeRect(cx - s, y - 9, 18, 18);
      ctx.beginPath(); ctx.moveTo(cx - s + 32, y); ctx.lineTo(cx + s, y); ctx.stroke();
      if (k * 3 > r) { ctx.beginPath(); ctx.moveTo(cx - s + 3, y); ctx.lineTo(cx - s + 8, y + 5); ctx.lineTo(cx - s + 16, y - 6); ctx.stroke(); }
    }
  } else if (i === 2) {
    ctx.beginPath(); ctx.roundRect(cx - s, cy - s * .75, s * 2, s * 1.3, 12); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx - s * .4, cy + s * .55); ctx.lineTo(cx - s * .6, cy + s); ctx.lineTo(cx - s * .05, cy + s * .55); ctx.stroke();
    for (let d = 0; d < 3; d++) { ctx.globalAlpha = .4 + .6 * (Math.floor(k * 6) % 3 === d ? 1 : 0); ctx.beginPath(); ctx.arc(cx - s * .45 + d * s * .45, cy - s * .1, 5, 0, 7); ctx.fill(); }
  } else if (i === 3) {
    ctx.strokeRect(cx - s, cy - s * .8, s * 2, s * 1.3);
    ctx.beginPath(); ctx.moveTo(cx, cy + s * .5); ctx.lineTo(cx, cy + s); ctx.moveTo(cx - s * .4, cy + s); ctx.lineTo(cx + s * .4, cy + s); ctx.stroke();
    [.3, .55, .85].forEach((hh, b) => { const h2 = s * .9 * hh * (.4 + .6 * k); ctx.fillRect(cx - s * .6 + b * s * .45, cy + s * .35 - h2, s * .25, h2); });
  } else if (i === 4) {
    ctx.beginPath(); ctx.arc(cx, cy, s, 0, 7); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx - s * .45, cy); ctx.lineTo(cx - s * .1, cy + s * .35); ctx.lineTo(cx + s * .5, cy - s * .35); ctx.lineWidth = 5; ctx.stroke();
  } else {
    ctx.beginPath(); ctx.moveTo(cx - s, cy - s); ctx.lineTo(cx - s, cy + s); ctx.lineTo(cx + s, cy + s); ctx.stroke();
    const pts = [[-.75, .6], [-.35, .2], [0, .4], [.35, -.2], [.75, -.7]];
    ctx.beginPath(); pts.forEach(([x, y], j) => { const X = cx + x * s, Y = cy + lerp(.7, y, .3 + .7 * k) * s; j ? ctx.lineTo(X, Y) : ctx.moveTo(X, Y); }); ctx.stroke();
  }
  ctx.restore();
}
function sMenu(lt, t) {
  bg(t, { grid: .6, glow: 1 });
  const ex = eInCubic(seg(lt, 17.4, 18));
  ctx.save(); ctx.globalAlpha = 1 - ex;
  label(0, 140, 'SERVICE MENU', lt, .1, { align: 'center' });
  reveal('THIRDのクロージング代行で、できること。', W / 2, 225, .3, lt, { size: 60, weight: 900, align: 'center', stagger: .035 });
  const TW = 490, TH = 250, GP = 35, X0 = (W - (3 * TW + 2 * GP)) / 2, Y0 = 290;
  const seqStart = 3.2, seqStep = 1.85;
  const inSeq = lt >= seqStart && lt < seqStart + 6 * seqStep;
  const cur = inSeq ? Math.floor((lt - seqStart) / seqStep) : -1;
  const all = seg(lt, seqStart + 6 * seqStep, seqStart + 6 * seqStep + .4);
  MENU.forEach((m, i) => {
    const a = eOutExpo(seg(lt, .9 + i * .22, 1.6 + i * .22));
    if (a <= 0) return;
    const x = X0 + (i % 3) * (TW + GP), y = Y0 + Math.floor(i / 3) * (TH + GP) + (1 - a) * 50;
    const act = i === cur ? eOutExpo(seg(lt, seqStart + i * seqStep, seqStart + i * seqStep + .3)) : all;
    const dim = inSeq && i !== cur ? 1 : 0;
    const done = inSeq && i < cur;
    ctx.save();
    ctx.globalAlpha *= a * (1 - .55 * dim + (done ? .15 : 0));
    const sc = 1 + .04 * (i === cur ? act : 0);
    ctx.translate(x + TW / 2, y + TH / 2); ctx.scale(sc, sc); ctx.translate(-(x + TW / 2), -(y + TH / 2));
    ctx.fillStyle = `rgba(${act > 0 ? '0,224,255' : '255,255,255'},${.03 + .06 * act})`;
    ctx.fillRect(x, y, TW, TH);
    ctx.strokeStyle = act > 0 ? `rgba(0,224,255,${.3 + .7 * act})` : 'rgba(255,255,255,.16)'; ctx.lineWidth = 1.5 + act;
    if (act > 0) { ctx.shadowColor = CY; ctx.shadowBlur = 24 * act; }
    ctx.strokeRect(x + .5, y + .5, TW, TH);
    ctx.shadowBlur = 0;
    ctx.fillStyle = CY; ctx.fillRect(x, y, 28, 3); ctx.fillRect(x, y, 3, 28);
    txt(String(i + 1).padStart(2, '0'), x + 34, y + 62, { size: 30, weight: 700, family: EN, color: CY, ls: 4 });
    const k = i === cur ? seg(lt, seqStart + i * seqStep + .1, seqStart + i * seqStep + 1.3) : (all > 0 || done ? 1 : .5);
    icon(m.ic, x + TW - 84, y + 78, 36, act > 0 ? CY : 'rgba(255,255,255,.75)', k);
    txt(m.jp, x + 34, y + 168, { size: 40, weight: 900 });
    txt(m.sub, x + 34, y + 214, { size: 22, weight: 500, color: '#aeb6c6' });
    ctx.restore();
  });
  reveal('すべてを、ワンストップで。', W / 2, 950, seqStart + 6 * seqStep + .2, lt, { size: 60, weight: 900, align: 'center', stagger: .05, color: grad(W / 2 - 400, 0, W / 2 + 400, 0, '#ffffff', CY) });
  ctx.restore();
  slashWipe(seg(lt, 0, .55));
  return {};
}

// ============================================================
// 66-86s  FLOW（導入の流れ 5ステップ + 改善サイクル）
// ============================================================
const STEPS = [
  { jp: 'ヒアリング', d: '商材・顧客・これまでの商談状況を把握する。' },
  { jp: '提案設計', d: '勝ち筋となる提案シナリオとトークを設計する。' },
  { jp: 'クロージング', d: 'THIRDのクローザーが商談を担当し、決めきる。' },
  { jp: '契約フォロー', d: '契約締結まで、条件調整と手続きを伴走する。' },
  { jp: '分析・改善', d: '勝因・敗因を振り返り、成約率を上げ続ける。' },
];
function sFlow(lt, t) {
  bg(t, { grid: .6, glow: 1 });
  const ex = eInCubic(seg(lt, 19.4, 20));
  ctx.save(); ctx.globalAlpha = 1 - ex;
  label(0, 140, 'FLOW', lt, .1, { align: 'center' });
  reveal('導入の流れ', W / 2, 228, .3, lt, { size: 64, weight: 900, align: 'center', stagger: .06 });
  const xs = STEPS.map((_, i) => 260 + i * 350), TY = 545;
  const A = STEPS.map((_, i) => 1.6 + i * 2.6);
  const LOOP = 14.6;
  // track
  const tr = eOutExpo(seg(lt, .5, 1.5));
  ctx.save(); ctx.strokeStyle = 'rgba(255,255,255,.15)'; ctx.lineWidth = 2; ctx.setLineDash([6, 10]);
  ctx.beginPath(); ctx.moveTo(xs[0], TY); ctx.lineTo(lerp(xs[0], xs[4], tr), TY); ctx.stroke(); ctx.restore();
  let head = xs[0], cur = -1;
  for (let i = 0; i < 5; i++) if (lt >= A[i]) { head = xs[i]; cur = i; }
  for (let i = 0; i < 4; i++) if (lt >= A[i + 1] - .6 && lt < A[i + 1]) head = lerp(xs[i], xs[i + 1], eInOut(seg(lt, A[i + 1] - .6, A[i + 1])));
  if (lt > A[0] - .6) {
    ctx.save(); ctx.strokeStyle = CY; ctx.lineWidth = 4; ctx.shadowColor = CY; ctx.shadowBlur = 16;
    ctx.beginPath(); ctx.moveTo(xs[0], TY); ctx.lineTo(head, TY); ctx.stroke(); ctx.restore();
  }
  // loop arc (5 -> 2)
  const lp = seg(lt, LOOP, LOOP + 1.4);
  const arc = u => {
    const p0 = [xs[4], TY - 100], p1 = [xs[4], 300], p2 = [xs[1], 300], p3 = [xs[1], TY - 100];
    const v = 1 - u;
    return [v * v * v * p0[0] + 3 * v * v * u * p1[0] + 3 * v * u * u * p2[0] + u * u * u * p3[0], v * v * v * p0[1] + 3 * v * v * u * p1[1] + 3 * v * u * u * p2[1] + u * u * u * p3[1]];
  };
  if (lp > 0) {
    ctx.save(); ctx.strokeStyle = CY; ctx.lineWidth = 3; ctx.shadowColor = CY; ctx.shadowBlur = 14; ctx.setLineDash([14, 10]); ctx.lineDashOffset = -lt * 40;
    ctx.beginPath();
    const n = Math.max(2, Math.floor(60 * lp));
    for (let k = 0; k <= n; k++) { const [x, y] = arc(k / 60); k ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
    ctx.stroke(); ctx.restore();
    if (lp >= 1) {
      const [x, y] = arc(1);
      ctx.save(); ctx.strokeStyle = CY; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(x - 14, y - 18); ctx.lineTo(x, y); ctx.lineTo(x + 14, y - 18); ctx.stroke(); ctx.restore();
      const u = ((lt - LOOP - 1.4) * .5) % 1; const [px, py] = arc(u); glowDot(px, py, 7);
    }
    txt('PDCA', (xs[1] + xs[4]) / 2, 318, { size: 30, weight: 700, family: EN, color: '#fff', align: 'center', ls: 14, alpha: seg(lt, LOOP + .8, LOOP + 1.3) });
  }
  // nodes
  const cyc = lt > LOOP + 1.4 ? 1 + Math.floor((lt - LOOP - 1.4) * 2.5) % 4 : -1;
  STEPS.forEach((s, i) => {
    const ap = clamp(eOutBack(seg(lt, .6 + i * .12, 1.1 + i * .12)));
    const on = lt >= A[i];
    const hot = cyc === i || (cur === i && lt < LOOP);
    ctx.save(); ctx.globalAlpha *= ap;
    if (on) {
      ctx.fillStyle = grad(xs[i] - 46, TY - 46, xs[i] + 46, TY + 46, CY, BL);
      ctx.shadowColor = CY; ctx.shadowBlur = hot ? 36 : 12;
    } else ctx.fillStyle = BG;
    ctx.strokeStyle = on ? CY : 'rgba(255,255,255,.35)'; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(xs[i], TY, 46 * ap, 0, 7); ctx.fill(); ctx.stroke();
    ctx.restore();
    if (hot && lt < LOOP) {
      const q = ((lt - A[i]) * .9) % 1;
      ctx.save(); ctx.strokeStyle = `rgba(0,224,255,${1 - q})`; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(xs[i], TY, 46 + q * 50, 0, 7); ctx.stroke(); ctx.restore();
    }
    txt(String(i + 1).padStart(2, '0'), xs[i], TY + 13, { size: 36, weight: 700, family: EN, color: on ? '#fff' : 'rgba(255,255,255,.5)', align: 'center', alpha: ap });
    txt('STEP', xs[i], TY - 72, { size: 18, weight: 500, family: EN, color: CY, align: 'center', ls: 8, alpha: ap * (on ? 1 : .5) });
    txt(s.jp, xs[i], TY + 100, { size: 34, weight: 900, color: on ? '#fff' : 'rgba(255,255,255,.4)', align: 'center', alpha: ap });
  });
  // detail panel
  const pa = seg(lt, A[0] - .2, A[0] + .3);
  if (pa > 0) {
    const px = 260, py = 735, pw = 1400, ph = 170;
    ctx.save(); ctx.globalAlpha *= pa;
    ctx.fillStyle = 'rgba(255,255,255,.035)'; ctx.fillRect(px, py, pw, ph);
    ctx.fillStyle = CY; ctx.fillRect(px, py, 4, ph);
    ctx.restore();
    const isLoop = lt >= LOOP;
    const si = Math.max(0, cur);
    const kt = isLoop ? LOOP : A[si];
    const e = eOutExpo(seg(lt, kt, kt + .45));
    const big = isLoop ? '∞' : String(si + 1).padStart(2, '0');
    const title = isLoop ? '成約率が上がるまで、回し続ける。' : STEPS[si].jp;
    const desc = isLoop ? '定期的な振り返りで、トークと提案を磨き続けます。' : STEPS[si].d;
    ctx.save(); ctx.globalAlpha *= pa * e; ctx.translate((1 - e) * 40, 0);
    txt(big, px + 60, py + 128, { size: 110, weight: 700, family: EN, color: grad(px, 0, px + 160, 0, '#ffffff', CY) });
    txt(title, px + 260, py + 78, { size: 46, weight: 900 });
    txt(desc, px + 260, py + 130, { size: 30, weight: 500, color: '#cfd6e4' });
    ctx.restore();
  }
  ctx.restore();
  slashWipe(seg(lt, 0, .55));
  return {};
}

// ============================================================
// 86-104s  WHY THIRD（選ばれる3つの理由）
// ============================================================
const REASONS = [
  { t: ['育成のプロが、', 'クロージングする。'], c: ['営業マン育成コンサルティングで培った', '「決める技術」を、そのまま現場に。'] },
  { t: ['マーケティング', '視点で、決める。'], c: ['顧客の検討プロセスを分析し、', '刺さる提案で意思決定を後押し。'] },
  { t: ['成約率を、', '見える化する。'], c: ['商談数から成約・失注理由までを', 'レポートで共有し、次の打ち手へ。'] },
];
function vRadar(rt) {
  const cx = 1400, cy = 560, R = 240;
  const axes = ['ヒアリング', '提案力', 'クロージング', '反論処理', 'マインド'];
  const n = 5, ang = i => -Math.PI / 2 + i * 2 * Math.PI / n;
  const gp = eOutExpo(seg(rt, .6, 1.4));
  ctx.save();
  ctx.strokeStyle = 'rgba(0,224,255,.25)'; ctx.lineWidth = 1.5; ctx.setLineDash([2, 12]);
  ctx.beginPath(); ctx.arc(cx, cy, (R + 70) * gp, rt * .3, rt * .3 + Math.PI * 2 * gp); ctx.stroke();
  ctx.setLineDash([]); ctx.strokeStyle = 'rgba(255,255,255,.14)';
  for (let k = 1; k <= 4; k++) {
    const r = R * k / 4 * gp; ctx.beginPath();
    for (let i = 0; i <= n; i++) { const a = ang(i % n); i ? ctx.lineTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r) : ctx.moveTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r); }
    ctx.stroke();
  }
  for (let i = 0; i < n; i++) { const a = ang(i); ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + Math.cos(a) * R * gp, cy + Math.sin(a) * R * gp); ctx.stroke(); }
  ctx.restore();
  axes.forEach((s, i) => {
    const a = ang(i);
    txt(s, cx + Math.cos(a) * (R + 48), cy + Math.sin(a) * (R + 48) + 10, { size: 26, weight: 700, color: '#dfe6f2', align: Math.abs(Math.cos(a)) < .2 ? 'center' : Math.cos(a) > 0 ? 'left' : 'right', alpha: seg(rt, 1.0 + i * .08, 1.5 + i * .08) });
  });
  const lo = [.3, .26, .22, .36, .3], hi = [.92, .86, .84, .95, .9];
  const m = eInOut(seg(rt, 1.6, 3.0));
  const cur = lo.map((b, i) => lerp(b, hi[i], m));
  ctx.save(); ctx.shadowColor = CY; ctx.shadowBlur = 25; ctx.globalAlpha *= seg(rt, 1.2, 1.6);
  ctx.beginPath();
  cur.forEach((v, i) => { const q = ang(i); const x = cx + Math.cos(q) * R * v, y = cy + Math.sin(q) * R * v; i ? ctx.lineTo(x, y) : ctx.moveTo(x, y); });
  ctx.closePath(); ctx.fillStyle = 'rgba(0,224,255,.16)'; ctx.fill(); ctx.strokeStyle = CY; ctx.lineWidth = 3; ctx.stroke();
  ctx.restore();
  cur.forEach((v, i) => { const q = ang(i); glowDot(cx + Math.cos(q) * R * v, cy + Math.sin(q) * R * v, 5, seg(rt, 1.2, 1.6)); });
}
const tdots = [...Array(70)].map((_, i) => { const r = rng(900 + i); return { a: r() * Math.PI * 2, r: .55 + r() * .5, d: r() * .8, s: r() }; });
function vTarget(rt, lt) {
  const cx = 1400, cy = 560;
  const ap = eOutExpo(seg(rt, .5, 1.3));
  ctx.save();
  [280, 210, 140, 70].forEach((r, i) => {
    ctx.strokeStyle = i === 3 ? CY : `rgba(0,224,255,${.2 + i * .1})`; ctx.lineWidth = i === 3 ? 3 : 1.5;
    if (i % 2 === 0) { ctx.setLineDash([8, 10]); ctx.lineDashOffset = lt * (i ? -30 : 30); } else ctx.setLineDash([]);
    ctx.beginPath(); ctx.arc(cx, cy, r * ap, 0, 7); ctx.stroke();
  });
  ctx.setLineDash([]); ctx.strokeStyle = 'rgba(255,255,255,.25)'; ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(cx - 330 * ap, cy); ctx.lineTo(cx + 330 * ap, cy); ctx.moveTo(cx, cy - 330 * ap); ctx.lineTo(cx, cy + 330 * ap); ctx.stroke();
  ctx.restore();
  const conv = seg(rt, 1.4, 3.2);
  tdots.forEach(d => {
    const k = eInOut(clamp(conv * 1.4 - d.d * .5));
    const hitR = d.s < .6 ? lerp(d.r * 330, d.s * 60, k) : d.r * 330;
    const x = cx + Math.cos(d.a + lt * .1) * hitR, y = cy + Math.sin(d.a + lt * .1) * hitR;
    const hit = d.s < .6 && k > .9;
    ctx.save(); ctx.globalAlpha *= ap * (hit ? 1 : .45);
    ctx.fillStyle = hit ? CY : '#9fb4ff'; ctx.beginPath(); ctx.arc(x, y, hit ? 4 : 3, 0, 7); ctx.fill(); ctx.restore();
  });
  glowDot(cx, cy, 10 + 4 * Math.sin(lt * 6), ap);
  txt('TARGET', cx + 24, cy - 24, { size: 20, weight: 700, family: EN, color: CY, ls: 6, alpha: seg(rt, 2.6, 3.0) });
}
function vDashboard(rt, lt) {
  const x = 1030, y = 300, w = 760, h = 480;
  const ap = eOutExpo(seg(rt, .5, 1.2));
  ctx.save(); ctx.globalAlpha *= ap; ctx.translate(0, (1 - ap) * 40);
  ctx.fillStyle = 'rgba(10,18,40,.85)'; ctx.fillRect(x, y, w, h);
  ctx.strokeStyle = 'rgba(0,224,255,.5)'; ctx.lineWidth = 1.5; ctx.strokeRect(x + .5, y + .5, w, h);
  ctx.fillStyle = 'rgba(0,224,255,.12)'; ctx.fillRect(x, y, w, 52);
  txt('SALES REPORT', x + 24, y + 35, { size: 22, weight: 700, family: EN, color: '#fff', ls: 6 });
  txt('※イメージ', x + w - 24, y + 34, { size: 18, weight: 500, color: GR, align: 'right' });
  // bar chart
  const bx = x + 40, by = y + 330, bw = 380;
  ctx.strokeStyle = 'rgba(255,255,255,.2)'; ctx.beginPath(); ctx.moveTo(bx, y + 90); ctx.lineTo(bx, by); ctx.lineTo(bx + bw, by); ctx.stroke();
  const vals = [.25, .35, .42, .55, .7, .88];
  vals.forEach((v, i) => {
    const g = eOutExpo(seg(rt, 1.0 + i * .12, 1.8 + i * .12));
    const hh = 220 * v * g;
    ctx.fillStyle = i === 5 ? CY : `rgba(42,92,255,${.5 + i * .08})`;
    ctx.fillRect(bx + 20 + i * 60, by - hh, 36, hh);
  });
  txt('成約数の推移', bx, by + 36, { size: 20, weight: 500, color: '#b9c1d0' });
  // line chart
  const lx = x + 460, ly = y + 90, lw = 260, lh = 160;
  ctx.strokeStyle = 'rgba(255,255,255,.2)'; ctx.strokeRect(lx, ly, lw, lh);
  const pts = [.2, .3, .28, .45, .5, .66, .72, .9];
  const lp = seg(rt, 1.4, 2.6);
  ctx.save(); ctx.beginPath(); ctx.rect(lx, ly - 10, lw * lp, lh + 20); ctx.clip();
  ctx.strokeStyle = CY; ctx.lineWidth = 3; ctx.shadowColor = CY; ctx.shadowBlur = 12;
  ctx.beginPath(); pts.forEach((v, i) => { const X = lx + 14 + i * (lw - 28) / 7, Y = ly + lh - 14 - v * (lh - 28); i ? ctx.lineTo(X, Y) : ctx.moveTo(X, Y); }); ctx.stroke();
  ctx.restore();
  txt('成約率の推移', lx, ly + lh + 36, { size: 20, weight: 500, color: '#b9c1d0' });
  // kpi tiles
  ['商談', '成約', '成約率'].forEach((s, i) => {
    const a = seg(rt, 2.0 + i * .2, 2.5 + i * .2);
    const tx = x + 40 + i * 235, ty = y + 385;
    ctx.save(); ctx.globalAlpha *= a;
    ctx.fillStyle = 'rgba(255,255,255,.04)'; ctx.fillRect(tx, ty, 210, 70);
    ctx.strokeStyle = 'rgba(0,224,255,.35)'; ctx.strokeRect(tx + .5, ty + .5, 210, 70);
    ctx.restore();
    txt(s, tx + 20, ty + 45, { size: 26, weight: 700, alpha: a });
    ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = CY; ctx.lineWidth = 4; ctx.lineCap = 'round';
    const ax = tx + 170, ay = ty + 35 - 4 * Math.sin(lt * 5 + i);
    ctx.beginPath(); ctx.moveTo(ax, ay + 14); ctx.lineTo(ax, ay - 14); ctx.moveTo(ax - 10, ay - 4); ctx.lineTo(ax, ay - 14); ctx.lineTo(ax + 10, ay - 4); ctx.stroke(); ctx.restore();
  });
  ctx.restore();
}
function sWhy(lt, t) {
  bg(t, { grid: .6, glow: 1.1 });
  if (lt < 2.6) {
    rays(t, 1 - seg(lt, 2, 2.6));
    const z = 1 + eInCubic(seg(lt, 2.0, 2.6)) * 4;
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-W / 2, -H / 2);
    ctx.globalAlpha = 1 - eInCubic(seg(lt, 2.2, 2.6));
    ctx.font = font(700, 230, EN); ctx.textBaseline = 'alphabetic';
    const letters = [...'WHY THIRD?'], sp = 14;
    const ws = letters.map(c => ctx.measureText(c).width);
    const tw = ws.reduce((a, b) => a + b, 0) + sp * (letters.length - 1);
    let cx = W / 2 - tw / 2;
    letters.forEach((c, i) => {
      const p = eOutExpo(seg(lt, i * .05, .5 + i * .05));
      ctx.save(); ctx.globalAlpha *= p;
      ctx.fillStyle = i >= 4 ? grad(W / 2, 0, W / 2 + tw / 2, 0, '#ffffff', CY) : '#fff';
      ctx.fillText(c, cx, 600 + (1 - p) * 120);
      ctx.restore();
      cx += ws[i] + sp;
    });
    ctx.restore();
    reveal('THIRDが選ばれる、3つの理由。', W / 2, 730, .6, lt, { size: 48, weight: 700, align: 'center', stagger: .035, alpha: 1 - seg(lt, 2.0, 2.3) });
    return { flash: lt < .25 ? (1 - lt / .25) * .8 : 0, glitch: lt < .15 ? .6 : 0 };
  }
  const RL = 15.4 / 3;
  const i = Math.min(2, Math.floor((lt - 2.6) / RL)), rt = lt - 2.6 - i * RL, r = REASONS[i];
  const ex = eInCubic(seg(rt, RL - .45, RL));
  bigNumber('0' + (i + 1), rt, ex);
  ctx.save(); ctx.globalAlpha = 1 - ex; ctx.translate(-ex * 120, 0);
  [vRadar, vTarget, vDashboard][i](rt, lt);
  ctx.restore();
  ctx.save(); ctx.globalAlpha = 1 - ex; ctx.translate(-ex * 200, 0);
  label(160, 300, 'REASON 0' + (i + 1), rt, .3);
  reveal(r.t[0], 156, 440, .45, rt, { size: 92, weight: 900, stagger: .045 });
  reveal(r.t[1], 156, 550, .62, rt, { size: 92, weight: 900, stagger: .045, color: grad(160, 0, 760, 0, '#ffffff', CY) });
  r.c.forEach((s, k) => txt(s, 160, 650 + k * 48, { size: 29, weight: 500, color: '#cfd6e4', alpha: seg(rt, 1.4 + k * .15, 1.9 + k * .15) }));
  ctx.restore();
  slashWipe(seg(rt, 0, .5));
  return { glitch: rt < .06 ? .4 : 0 };
}

// ============================================================
// 104-112s  CLIMAX  準備。商談。決断。成約。→ メインコピー
// ============================================================
function sClimax(lt, t) {
  if (lt < 2) {
    const k = Math.floor(lt / .5), kt = lt - k * .5;
    const words = ['準備。', '商談。', '決断。', '成約。'];
    const ens = ['PREPARE', 'MEETING', 'DECISION', 'CLOSED'];
    const bgc = [BG, '#fff', CY, BG][k], fg = ['#fff', '#000', '#000', CY][k];
    ctx.fillStyle = bgc; ctx.fillRect(0, 0, W, H);
    const sc = lerp(1.2, 1, eOutExpo(seg(kt, 0, .3)));
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(sc, sc);
    ctx.font = font(900, 340, JP); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = fg;
    if (k === 3) { ctx.shadowColor = CY; ctx.shadowBlur = 50; }
    ctx.fillText(words[k], 0, 0);
    ctx.restore();
    txt(ens[k], W / 2, H / 2 + 260, { size: 32, weight: 500, family: EN, color: fg, align: 'center', ls: 20, alpha: .75 });
    return { glitch: kt < .07 ? .5 : 0 };
  }
  const l = lt - 2;
  bg(t, { grid: .5, glow: 1.4, pa: 1.5 });
  rays(t, seg(l, 0, 1));
  const sc = 1 + .012 * l;
  ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(sc, sc); ctx.translate(-W / 2, -H / 2);
  reveal('その商談を、', W / 2, 480, .1, l, { size: 128, weight: 900, align: 'center', stagger: .06 });
  reveal('成約に変える。', W / 2, 650, .7, l, { size: 128, weight: 900, align: 'center', stagger: .06, color: grad(W / 2 - 520, 0, W / 2 + 520, 0, '#ffffff', CY) });
  txt('WE TURN MEETINGS INTO CONTRACTS.', W / 2, 760, { size: 30, weight: 300, family: EN, color: GR, align: 'center', ls: 14, alpha: seg(l, 1.8, 2.5) });
  ctx.restore();
  return { flash: eInCubic(seg(l, 5.4, 6.0)) };
}

// ============================================================
// 112-120s  ENDING  ロゴ → お問い合わせ
// ============================================================
function sEnd(lt, t) {
  bg(t, { grid: .4, glow: 1, pa: 1 });
  logo(lt, 400);
  txt('株式会社サード', W / 2, 520, { size: 44, weight: 700, align: 'center', ls: 22, alpha: seg(lt, 1.0, 1.6) });
  txt('CLOSING OUTSOURCING SERVICE', W / 2, 575, { size: 22, weight: 500, family: EN, color: CY, align: 'center', ls: 12, alpha: seg(lt, 1.2, 1.8) });
  const dl = eOutExpo(seg(lt, 1.4, 2.2));
  ctx.fillStyle = grad(W / 2 - 300, 0, W / 2 + 300, 0, BL, CY); ctx.fillRect(W / 2 - 300 * dl, 615, 600 * dl, 2);
  reveal('まずは、お気軽にご相談ください。', W / 2, 720, 1.8, lt, { size: 56, weight: 900, align: 'center', stagger: .04, dur: .6, color: grad(W / 2 - 460, 0, W / 2 + 460, 0, '#ffffff', '#9eefff') });
  txt('クロージング代行　｜　営業マン育成コンサルティング　｜　マーケティングコンサルティング', W / 2, 850, { size: 24, weight: 500, color: '#b9c1d0', align: 'center', ls: 3, alpha: seg(lt, 2.8, 3.4) });
  txt('SHINJUKU, TOKYO', W / 2, 900, { size: 20, weight: 300, family: EN, color: GR, align: 'center', ls: 12, alpha: seg(lt, 3.0, 3.6) });
  shade(eInOut(seg(lt, 6.8, 7.9)), '0,0,0');
  return { flash: lt < .3 ? (1 - lt / .3) : 0 };
}

// ============================================================
const SCENES = [
  [0, 10, sOpen], [10, 18, sTitle], [18, 30, sConcept], [30, 48, sProblems],
  [48, 66, sMenu], [66, 86, sFlow], [86, 104, sWhy], [104, 112, sClimax], [112, 120, sEnd],
];
function renderFrame(t) {
  reset();
  const sc = SCENES.find(s => t >= s[0] && t < s[1]) || SCENES[SCENES.length - 1];
  const fx = sc[2](t - sc[0], t) || {};
  reset();
  hud(t, seg(t, 10.6, 11.4) * (1 - seg(t, 103.6, 104)));
  if (fx.glitch) glitch(fx.glitch, Math.floor(t * FPS));
  post(t);
  if (fx.flash > 0) { ctx.fillStyle = `rgba(255,255,255,${fx.flash})`; ctx.fillRect(0, 0, W, H); }
}
