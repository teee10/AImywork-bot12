// ============================================================
//  株式会社サード PV（ジェットコースター版） — 2D オーバーレイ
//  コピー・HUD（速度/高度）・スピード線・フラッシュを WebGL の上に重ねる
// ============================================================
const RED = '#FF3D5A';

function label(x, y, s, lt, t0, o = {}) {
  const { color = CY, align = 'left', size = 24 } = o;
  const lp = eOutExpo(seg(lt, t0, t0 + .6));
  if (align === 'center') {
    const w = measure(s, size, 500, EN, 10);
    ctx.fillStyle = color;
    ctx.fillRect(x - w / 2 - 76, y - 10, 50 * lp, 3);
    ctx.fillRect(x + w / 2 + 26 + 50 * (1 - lp), y - 10, 50 * lp, 3);
    txt(s, x, y, { size, weight: 500, family: EN, color, ls: 10, align: 'center', alpha: seg(lt, t0 + .05, t0 + .45) });
  } else {
    ctx.fillStyle = color; ctx.fillRect(x, y - 10, 56 * lp, 3);
    txt(s, x + 76, y, { size, weight: 500, family: EN, color, ls: 10, alpha: seg(lt, t0 + .05, t0 + .45) });
  }
}

function shadowText(fn) {
  ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.75)'; ctx.shadowBlur = 30; fn(); ctx.restore();
}

function scrim(x0, x1, a) {
  if (a <= 0) return;
  const g = ctx.createLinearGradient(x0, 0, x1, 0);
  g.addColorStop(0, `rgba(2,4,12,${.65 * a})`); g.addColorStop(1, 'rgba(2,4,12,0)');
  ctx.fillStyle = g; ctx.fillRect(Math.min(x0, x1), 0, Math.abs(x1 - x0), H);
}

function speedLines(t, v) {
  const a = clamp((v - 45) / 45);
  if (a <= 0) return;
  const r = rng(Math.floor(t * FPS) * 7 + 3);
  ctx.save();
  ctx.translate(W / 2, H / 2);
  for (let i = 0; i < 70; i++) {
    const ang = r() * Math.PI * 2, r0 = 380 + r() * 500, len = (120 + r() * 380) * a;
    ctx.strokeStyle = `rgba(${r() < .25 ? '0,224,255' : '220,235,255'},${(.08 + r() * .25) * a})`;
    ctx.lineWidth = 1 + r() * 2.5;
    ctx.beginPath(); ctx.moveTo(Math.cos(ang) * r0, Math.sin(ang) * r0 * .7); ctx.lineTo(Math.cos(ang) * (r0 + len), Math.sin(ang) * (r0 + len) * .7); ctx.stroke();
  }
  ctx.restore();
}

function vignetteFx(a = 1) {
  const g = ctx.createRadialGradient(W / 2, H / 2, H * .45, W / 2, H / 2, H * 1.05);
  g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${.7 * a})`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}

function coasterHud(t, info, a) {
  if (a <= 0) return;
  ctx.save(); ctx.globalAlpha = a;
  const m = 48, L = 34;
  ctx.strokeStyle = 'rgba(255,255,255,.55)'; ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(m, m + L); ctx.lineTo(m, m); ctx.lineTo(m + L, m);
  ctx.moveTo(W - m - L, m); ctx.lineTo(W - m, m); ctx.lineTo(W - m, m + L);
  ctx.moveTo(m, H - m - L); ctx.lineTo(m, H - m); ctx.lineTo(m + L, H - m);
  ctx.moveTo(W - m - L, H - m); ctx.lineTo(W - m, H - m); ctx.lineTo(W - m, H - m - L);
  ctx.stroke();
  txt('THIRD INC.  /  RIDE THE SALES', m + 56, m + 24, { size: 17, weight: 500, family: EN, color: '#fff', ls: 5, alpha: .7 });
  const sec = t < 16 ? 'SHINJUKU' : t < 26 ? 'THIRD INC.' : t < 36 ? 'SERVICE 01' : t < 46 ? 'SERVICE 02' : t < 56 ? 'SERVICE 03' : 'FINAL';
  txt(sec, W - m - 56, m + 24, { size: 17, weight: 500, family: EN, color: CY, ls: 6, align: 'right', alpha: .9 });
  // speed / altitude
  const kmh = Math.round(info.v * 3.6);
  txt('SPEED', m + 56, H - m - 70, { size: 16, weight: 500, family: EN, color: CY, ls: 6 });
  txt(String(kmh).padStart(3, '0'), m + 52, H - m - 8, { size: 64, weight: 700, family: EN, color: '#fff', ls: 2 });
  txt('km/h', m + 180, H - m - 12, { size: 20, weight: 300, family: EN, color: '#cfd6e4', ls: 3 });
  const bw = 200, fillw = bw * clamp(info.v / 90);
  ctx.fillStyle = 'rgba(255,255,255,.2)'; ctx.fillRect(m + 260, H - m - 26, bw, 4);
  ctx.fillStyle = info.v > 65 ? RED : CY; ctx.fillRect(m + 260, H - m - 26, fillw, 4);
  txt('ALT', m + 500, H - m - 70, { size: 16, weight: 500, family: EN, color: CY, ls: 6 });
  txt(String(Math.max(0, Math.round(info.alt))).padStart(3, '0'), m + 496, H - m - 8, { size: 64, weight: 700, family: EN, color: '#fff', ls: 2 });
  txt('m', m + 622, H - m - 12, { size: 20, weight: 300, family: EN, color: '#cfd6e4', ls: 3 });
  const s = Math.floor(t), fr = Math.floor((t - s) * FPS);
  txt(`00:00:${String(s).padStart(2, '0')}:${String(fr).padStart(2, '0')}`, W - m - 56, H - m - 10, { size: 17, weight: 300, family: EN, color: '#fff', ls: 4, align: 'right', alpha: .7 });
  ctx.restore();
}

function logo(l, Y) {
  const wmSize = 190, wmLs = 34;
  const wmW = measure('THIRD', wmSize, 700, EN, wmLs);
  const markW = 3 * 38 + 2 * 18, gapM = 56;
  const totalW = markW + gapM + wmW;
  const X = W / 2 - totalW / 2, OY = 300;
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
  ctx.shadowColor = 'rgba(0,224,255,.45)'; ctx.shadowBlur = 40;
  ctx.drawImage(logoCv, 0, Y - OY);
  ctx.restore();
  if (mp > 0 && mp < 1) { ctx.fillStyle = CY; ctx.fillRect(X + markW + gapM - 10 + (wmW + 60) * mp, Y - 170, 3, 200); }
}

const SERVICES = [
  { t: 26, no: '01', en: 'CLOSING OUTSOURCING', jp: ['クロージング代行'], copy: 'その商談を、成約に変える。' },
  { t: 36, no: '02', en: 'SALES TRAINING CONSULTING', jp: ['営業マン育成', 'コンサルティング'], copy: '個の力を、組織の武器に。' },
  { t: 46, no: '03', en: 'MARKETING CONSULTING', jp: ['マーケティング', 'コンサルティング'], copy: '選ばれる理由を、設計する。' },
];

function overlayFrame(t, info) {
  reset();
  ctx.clearRect(0, 0, W, H);
  let flash = 0, gl = 0;
  vignetteFx(1);
  speedLines(t, info.v);

  // 0-8 リフトアップ
  if (t < 8) {
    txt('THIRD INC. PRESENTS', W / 2, H / 2 - 150, { size: 26, weight: 500, family: EN, color: '#fff', align: 'center', ls: 16, alpha: seg(t, .8, 1.6) * (1 - seg(t, 2.6, 3.1)) });
    const out = seg(t, 7.3, 7.9);
    ctx.save(); ctx.globalAlpha = 1 - out;
    if (t > 7.0) ctx.translate((hash(Math.floor(t * 30), 4) - .5) * 10, (hash(Math.floor(t * 30), 5) - .5) * 10);
    shadowText(() => reveal('営業は、才能じゃない。', W / 2, H / 2 + 30, 3.0, t, { size: 104, weight: 900, align: 'center', stagger: .08, dur: .7 }));
    ctx.restore();
    txt('SALES IS NOT ABOUT TALENT.', W / 2, H / 2 + 110, { size: 28, weight: 300, family: EN, color: '#cfd6e4', align: 'center', ls: 16, alpha: seg(t, 4.2, 5.0) * (1 - out) });
  }
  // 8-10.6 ドロップ「仕組みだ。」
  if (t >= 8 && t < 10.6) {
    const l = t - 8;
    const sc = lerp(1.3, 1, eOutExpo(seg(l, 0, .5))) * (1 + eInCubic(seg(l, 1.8, 2.6)) * 1.5);
    ctx.save(); ctx.globalAlpha = 1 - eInCubic(seg(l, 1.9, 2.6));
    ctx.translate(W / 2, H / 2); ctx.scale(sc, sc);
    ctx.font = font(900, 300, JP); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.shadowColor = 'rgba(0,224,255,.8)'; ctx.shadowBlur = 50;
    ctx.fillStyle = '#fff'; ctx.fillText('仕組みだ。', 0, 0);
    ctx.restore();
    if (l < .2) { flash = (1 - l / .2) * .9; gl = .7; }
  }
  // 10.8-15.8 SHINJUKU
  if (t >= 10.8 && t < 16) {
    const l = t - 10.8, o = seg(l, 4.5, 5.2);
    ctx.save(); ctx.globalAlpha = 1 - o;
    scrim(0, 1100, seg(l, 0, .6));
    label(140, 640, 'LOCATION', l, .1);
    shadowText(() => reveal('SHINJUKU, TOKYO', 136, 790, .25, l, { size: 150, weight: 700, family: EN, stagger: .035, dur: .6, ls: 4 }));
    shadowText(() => reveal('東京・新宿から、日本の営業を変える。', 140, 870, .9, l, { size: 46, weight: 900, stagger: .025, dur: .5 }));
    txt('35.6938° N  /  139.7034° E', 140, 930, { size: 26, weight: 300, family: EN, color: '#cfd6e4', ls: 6, alpha: seg(l, 1.6, 2.2) });
    ctx.restore();
  }
  // 17-25 株式会社サード
  if (t >= 17 && t < 25.6) {
    const l = t - 17, o = seg(l, 7.8, 8.5);
    ctx.save(); ctx.globalAlpha = 1 - o;
    scrim(1920, 900, seg(l, 0, .6));
    label(1180, 560, 'WHO WE ARE', l, .1);
    shadowText(() => reveal('株式会社サード', 1176, 690, .3, l, { size: 100, weight: 900, stagger: .06 }));
    shadowText(() => reveal('第三の答えを、営業に。', 1180, 780, 1.0, l, { size: 50, weight: 700, stagger: .04, color: '#9eefff' }));
    txt('CLOSING  /  TRAINING  /  MARKETING', 1180, 840, { size: 24, weight: 300, family: EN, color: '#cfd6e4', ls: 8, alpha: seg(l, 1.8, 2.4) });
    ctx.restore();
  }
  // 26-56 サービス
  SERVICES.forEach((sv, i) => {
    const l = t - sv.t;
    if (l < -0.25 || l >= 10) return;
    if (l < 0) { flash = Math.max(flash, eInCubic(seg(l, -0.25, 0)) * .5); return; }
    if (l < .15) { flash = Math.max(flash, (1 - l / .15) * .7); gl = .5; }
    const o = seg(l, 9.2, 9.9);
    ctx.save(); ctx.globalAlpha = 1 - o; ctx.translate(-o * 120, 0);
    scrim(0, 1150, seg(l, .1, .7));
    label(140, 560, 'SERVICE ' + sv.no, l, .3);
    txt(sv.en, 140, 612, { size: 24, weight: 300, family: EN, color: '#cfd6e4', ls: 8, alpha: seg(l, .45, .9) });
    const size = sv.jp.length > 1 ? 92 : 116;
    let y = 612 + size * 1.15;
    sv.jp.forEach((line, k) => { shadowText(() => reveal(line, 136, y, .5 + k * .15, l, { size, weight: 900, stagger: .04 })); y += size * 1.15; });
    shadowText(() => reveal(sv.copy, 140, y + 10, 1.4, l, { size: 50, weight: 900, stagger: .035, color: grad(140, 0, 840, 0, '#ffffff', CY) }));
    ctx.restore();
  });
  // 56-60 上昇
  if (t >= 56.3 && t < 60) {
    const l = t - 56.3;
    ctx.save(); ctx.globalAlpha = 1 - seg(l, 3.2, 3.7);
    shadowText(() => reveal('営業を、', W / 2, H / 2 - 20, .1, l, { size: 110, weight: 900, align: 'center', stagger: .07 }));
    shadowText(() => reveal('次のステージへ。', W / 2, H / 2 + 120, .6, l, { size: 110, weight: 900, align: 'center', stagger: .07, color: grad(W / 2 - 450, 0, W / 2 + 450, 0, '#ffffff', CY) }));
    ctx.restore();
  }
  // 60-62 ビートに合わせた連打
  if (t >= 60 && t < 62) {
    const k = Math.floor((t - 60) / .5), kt = t - 60 - k * .5;
    const words = ['成約。', '育成。', '戦略。', 'THIRD.'];
    const bgc = ['rgba(4,5,10,.92)', 'rgba(255,255,255,.95)', 'rgba(0,224,255,.95)', 'rgba(4,5,10,.9)'][k];
    const fg = ['#fff', '#000', '#000', CY][k];
    ctx.fillStyle = bgc; ctx.fillRect(0, 0, W, H);
    const sc = lerp(1.2, 1, eOutExpo(seg(kt, 0, .3)));
    ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(sc, sc);
    ctx.font = k === 3 ? font(700, 300, EN) : font(900, 320, JP); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = fg;
    if (k === 3) { ctx.letterSpacing = '30px'; ctx.shadowColor = CY; ctx.shadowBlur = 40; }
    ctx.fillText(words[k], 0, 0);
    ctx.restore();
    if (kt < .07) gl = .5;
  }
  // 62-72 ロゴ
  if (t >= 62) {
    const l = t - 62.8;
    if (t < 62.4) flash = 1 - seg(t, 62, 62.4) * .9;
    const dk = seg(t, 63.5, 65);
    ctx.fillStyle = `rgba(2,4,12,${.45 * dk})`; ctx.fillRect(0, 0, W, H);
    if (l > 0) {
      logo(l, 440);
      txt('株式会社サード', W / 2, 560, { size: 46, weight: 700, align: 'center', ls: 22, alpha: seg(l, 1.0, 1.6) });
      const dl = eOutExpo(seg(l, 1.4, 2.2));
      ctx.fillStyle = grad(W / 2 - 300, 0, W / 2 + 300, 0, BL, CY); ctx.fillRect(W / 2 - 300 * dl, 605, 600 * dl, 2);
      shadowText(() => reveal('売れる組織を、共に創る。', W / 2, 700, 1.8, l, { size: 58, weight: 900, align: 'center', stagger: .05, color: grad(W / 2 - 360, 0, W / 2 + 360, 0, '#ffffff', '#9eefff') }));
      txt('クロージング代行　｜　営業マン育成コンサルティング　｜　マーケティングコンサルティング', W / 2, 830, { size: 24, weight: 500, color: '#dfe6f2', align: 'center', ls: 3, alpha: seg(l, 2.8, 3.4) });
      txt('SHINJUKU, TOKYO', W / 2, 880, { size: 20, weight: 300, family: EN, color: '#cfd6e4', align: 'center', ls: 12, alpha: seg(l, 3.0, 3.6) });
    }
  }

  coasterHud(t, info, seg(t, 8.6, 9.4) * (1 - seg(t, 59.6, 60)));
  // 黒フェード
  const fin = seg(t, 0, 1.4), fout = seg(t, 70.6, 71.9);
  const blk = Math.max(1 - fin, fout);
  if (blk > 0) { ctx.fillStyle = `rgba(0,0,0,${blk})`; ctx.fillRect(0, 0, W, H); }
  if (flash > 0) { ctx.fillStyle = `rgba(255,255,255,${flash})`; ctx.fillRect(0, 0, W, H); }
  return { glitch: gl };
}
