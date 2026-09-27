// ============================================================
//  株式会社サード PV（ジェットコースター版） — 3D ワールド
//  夜の新宿を走るコースターの一人称視点。worldFrame(t) で t 秒の画を描く
// ============================================================
const DUR = 72;
const glCanvas = document.getElementById('gl');
glCanvas.width = W; glCanvas.height = H;
const renderer = new THREE.WebGLRenderer({ canvas: glCanvas, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
const scene = new THREE.Scene();
const FOG = 0x0a1030;
scene.fog = new THREE.FogExp2(FOG, 0.00115);
const camera = new THREE.PerspectiveCamera(72, W / H, 0.3, 7000);
scene.add(camera);
const composer = new THREEX.EffectComposer(renderer);
composer.addPass(new THREEX.RenderPass(scene, camera));
const bloom = new THREEX.UnrealBloomPass(new THREE.Vector2(W, H), 0.6, 0.35, 0.68);
composer.addPass(bloom);
composer.addPass(new THREEX.OutputPass());

const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const UP = V3(0, 1, 0);

// ------------------------------------------------------------
// コース（時刻つきウェイポイント）
// ------------------------------------------------------------
const WP = [];
const wp = (t, x, y, z, roll = 0) => WP.push({ t, p: V3(x, y, z), roll });
// 0-8s  ビル屋上からのリフトアップ
wp(0, 0, 190, 770); wp(2, 0, 197, 759); wp(4.5, 0, 208, 742); wp(7.0, 0, 221, 722); wp(7.9, 0, 227, 712);
// 8-16s  ドロップ → 超高層ビルの谷間へ
wp(8.5, 0, 224, 698); wp(9.5, 0, 172, 642); wp(10.6, 0, 96, 592); wp(11.8, 2, 44, 522);
wp(13.2, -20, 34, 420); wp(14.6, 8, 36, 322); wp(16, 30, 44, 230);
// 16-26s  都庁の周りをらせん上昇
const TOCHO = V3(177, 0, 259);
{
  const R = 140, a0 = 191 * Math.PI / 180;
  for (let k = 1; k <= 10; k++) {
    const a = a0 + (k / 10) * 300 * Math.PI / 180;
    wp(16 + k, TOCHO.x + R * Math.cos(a), 44 + (150 - 44) * k / 10, TOCHO.z + R * Math.sin(a));
  }
}
// 26-36s  SERVICE 01  ビルの間をスラローム
wp(28, -40, 112, 250); wp(30, -95, 72, 130); wp(32, -55, 58, 10); wp(34, -110, 70, -100); wp(36, -60, 86, -205);
// 36-46s  SERVICE 02  コクーンタワーを回りながらバレルロール
const COCOON = V3(-165, 0, -345);
wp(38, -40, 104, -305); wp(39.5, -60, 118, -410, 0); wp(41, -150, 126, -478, Math.PI); wp(42.5, -250, 124, -455, Math.PI * 2);
wp(44, -305, 108, -375, Math.PI * 2); wp(46, -322, 78, -240, Math.PI * 2);
// 46-56s  SERVICE 03  ネオン街を低空で駆け抜ける
wp(47.5, -331, 38, -120, Math.PI * 2); wp(49, -335, 15, 0, Math.PI * 2); wp(51, -335, 14, 150, Math.PI * 2);
wp(53, -331, 16, 300, Math.PI * 2); wp(54.5, -300, 32, 400, Math.PI * 2); wp(56, -240, 62, 480, Math.PI * 2);
// 56-62s  上空へらせん上昇
{
  const C = V3(-336, 0, 552), R = 120, a0 = -36.87 * Math.PI / 180;
  const ts = [56.9, 57.8, 58.7, 59.6, 60.5, 61.3, 62.0];
  ts.forEach((tt, k) => {
    const a = a0 + ((k + 1) / ts.length) * 200 * Math.PI / 180;
    wp(tt, C.x + R * Math.cos(a), 62 + (300 - 62) * Math.pow((k + 1) / ts.length, 0.8), C.z + R * Math.sin(a), Math.PI * 2);
  });
}
// 62-72s  レールの先から空へ（ここから先は線路なし）
wp(64, -250, 360, 560, Math.PI * 2); wp(67, -150, 400, 560, Math.PI * 2); wp(72, -40, 420, 540, Math.PI * 2);
const TRACK_END_T = 62.2;

const curve = new THREE.CatmullRomCurve3(WP.map(w => w.p), false, 'centripetal');
curve.arcLengthDivisions = 40000;
const nW = WP.length;
const lengths = curve.getLengths((nW - 1) * 200);
const LTOT = lengths[lengths.length - 1];
WP.forEach((w, i) => { w.s = lengths[i * 200]; });

// 時刻 → 走行距離（単調三次補間）
function pchip(xs, ys) {
  const n = xs.length, h = [], d = [], m = new Array(n);
  for (let i = 0; i < n - 1; i++) { h[i] = xs[i + 1] - xs[i]; d[i] = (ys[i + 1] - ys[i]) / h[i]; }
  m[0] = d[0]; m[n - 1] = d[n - 2];
  for (let i = 1; i < n - 1; i++) {
    if (d[i - 1] * d[i] <= 0) m[i] = 0;
    else { const w1 = 2 * h[i] + h[i - 1], w2 = h[i] + 2 * h[i - 1]; m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i]); }
  }
  return x => {
    if (x <= xs[0]) return ys[0];
    if (x >= xs[n - 1]) return ys[n - 1];
    let i = 0; while (x > xs[i + 1]) i++;
    const t = (x - xs[i]) / h[i], t2 = t * t, t3 = t2 * t;
    return ys[i] * (2 * t3 - 3 * t2 + 1) + h[i] * m[i] * (t3 - 2 * t2 + t) + ys[i + 1] * (-2 * t3 + 3 * t2) + h[i] * m[i + 1] * (t3 - t2);
  };
}
const S = pchip(WP.map(w => w.t), WP.map(w => w.s));
const speedAt = t => (S(t + 0.05) - S(t - 0.05)) / 0.1;

// 1m ごとのフレーム（位置・接線・上方向・横方向）
const NS = Math.ceil(LTOT);
const FP = [], FT = [], FU = [], FB = [];
{
  const rollAt = s => {
    if (s <= WP[0].s) return WP[0].roll;
    for (let i = 0; i < nW - 1; i++) if (s <= WP[i + 1].s) { const f = (s - WP[i].s) / (WP[i + 1].s - WP[i].s); return lerp(WP[i].roll, WP[i + 1].roll, f * f * (3 - 2 * f)); }
    return WP[nW - 1].roll;
  };
  // 時刻テーブル（距離→速度）
  const sTab = [], vTab = [];
  for (let t = 0; t <= DUR; t += 0.02) { sTab.push(S(t)); vTab.push(speedAt(t)); }
  const vAtS = s => { let lo = 0, hi = sTab.length - 1; while (hi - lo > 1) { const m = (lo + hi) >> 1; if (sTab[m] < s) lo = m; else hi = m; } return vTab[lo]; };
  const heads = [];
  for (let k = 0; k <= NS; k++) {
    const u = Math.min(1, k / NS);
    FP.push(curve.getPointAt(u)); FT.push(curve.getTangentAt(u).normalize());
    heads.push(Math.atan2(FT[k].x, -FT[k].z));
  }
  const bank = [];
  for (let k = 0; k <= NS; k++) {
    const a = Math.max(0, k - 12), b = Math.min(NS, k + 12);
    let dh = heads[b] - heads[a]; while (dh > Math.PI) dh -= 2 * Math.PI; while (dh < -Math.PI) dh += 2 * Math.PI;
    const kap = dh / Math.max(1, b - a);
    const v = vAtS(k);
    bank.push(clamp(Math.atan(v * v * kap / 9.8) * 0.42, -0.55, 0.55));
  }
  const sm = bank.map((_, k) => { let s = 0, c = 0; for (let j = -30; j <= 30; j++) { const q = k + j; if (q >= 0 && q <= NS) { s += bank[q]; c++; } } return s / c; });
  let prevUp = UP.clone();
  for (let k = 0; k <= NS; k++) {
    const T = FT[k];
    let up = UP.clone().sub(T.clone().multiplyScalar(T.dot(UP)));
    if (up.lengthSq() < 1e-4) up = prevUp.clone(); up.normalize(); prevUp = up.clone();
    up.applyAxisAngle(T, sm[k] + rollAt(k));
    FU.push(up);
    FB.push(new THREE.Vector3().crossVectors(T, up).normalize());
  }
}
function frameAt(s) {
  s = clamp(s, 0, NS - 1e-3);
  const k = Math.floor(s), f = s - k, k2 = Math.min(NS, k + 1);
  return {
    p: FP[k].clone().lerp(FP[k2], f),
    t: FT[k].clone().lerp(FT[k2], f).normalize(),
    u: FU[k].clone().lerp(FU[k2], f).normalize(),
    b: FB[k].clone().lerp(FB[k2], f).normalize(),
  };
}
const TRACK_END_S = S(TRACK_END_T);

// ------------------------------------------------------------
// テクスチャ
// ------------------------------------------------------------
function canvasTex(w, h, draw) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  return t;
}
function windowTex(seed, warm) {
  const r = rng(seed);
  const t = canvasTex(256, 256, (g, w, h) => {
    g.fillStyle = '#05070d'; g.fillRect(0, 0, w, h);
    for (let y = 0; y < 16; y++) for (let x = 0; x < 8; x++) {
      if (x === 0 && y === 0) continue;
      const v = r();
      if (v < .45) continue;
      const hot = v > .93;
      g.fillStyle = hot ? (warm ? '#ffd9a0' : '#bfe9ff') : (warm ? `rgba(255,190,120,${.25 + r() * .45})` : `rgba(150,190,255,${.2 + r() * .45})`);
      g.fillRect(x * 32 + 5, y * 16 + 3, 22, 10);
    }
  });
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
}
const roadTex = canvasTex(512, 512, (g, w, h) => {
  // タイル境界＝道路の中心（道幅 20m ≒ 146px）
  g.fillStyle = '#05070d'; g.fillRect(0, 0, w, h);
  const rw = 73;
  g.fillStyle = '#10152a';
  g.fillRect(0, 0, rw, h); g.fillRect(w - rw, 0, rw, h); g.fillRect(0, 0, w, rw); g.fillRect(0, h - rw, w, rw);
  g.fillStyle = 'rgba(255,170,90,.6)';
  for (let k = 8; k < h; k += 34) { g.fillRect(rw - 8, k, 5, 5); g.fillRect(w - rw + 3, k, 5, 5); g.fillRect(k, rw - 8, 5, 5); g.fillRect(k, h - rw + 3, 5, 5); }
  g.fillStyle = 'rgba(255,255,255,.22)';
  for (let k = 0; k < h; k += 40) { g.fillRect(0, k, 2, 20); g.fillRect(w - 2, k, 2, 20); g.fillRect(k, 0, 20, 2); g.fillRect(k, h - 2, 20, 2); }
});
roadTex.wrapS = roadTex.wrapT = THREE.RepeatWrapping;

// ------------------------------------------------------------
// 空・地面
// ------------------------------------------------------------
{
  const sky = new THREE.Mesh(new THREE.SphereGeometry(5000, 32, 16), new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: {},
    vertexShader: 'varying vec3 vP; void main(){ vP = normalize(position); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }',
    fragmentShader: `varying vec3 vP; void main(){
      float h = clamp(vP.y, -0.2, 1.0);
      vec3 top = vec3(0.01,0.015,0.05), mid = vec3(0.05,0.07,0.2), hor = vec3(0.35,0.18,0.42);
      vec3 c = mix(hor, mid, smoothstep(0.0, 0.12, h));
      c = mix(c, top, smoothstep(0.12, 0.7, h));
      gl_FragColor = vec4(c, 1.0); }`,
  }));
  scene.add(sky);
  const r = rng(42), pos = [];
  for (let i = 0; i < 2500; i++) {
    const a = r() * Math.PI * 2, e = .08 + r() * 1.4;
    pos.push(Math.cos(a) * Math.cos(e) * 4500, Math.sin(e) * 4500, Math.sin(a) * Math.cos(e) * 4500);
  }
  const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  scene.add(new THREE.Points(sg, new THREE.PointsMaterial({ color: 0xaabbff, size: 2.2, sizeAttenuation: false, fog: false })));
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(6000, 6000), new THREE.MeshLambertMaterial({ color: 0x080a12, emissive: 0xffffff, emissiveMap: roadTex, emissiveIntensity: .9 }));
  roadTex.repeat.set(6000 / 70, 6000 / 70);
  ground.rotation.x = -Math.PI / 2;
  ground.position.set(60, 0, 10); // UV 原点が 70m の倍数に来るように
  scene.add(ground);
  scene.add(new THREE.HemisphereLight(0x4060c0, 0x100818, 0.9));
  const dl = new THREE.DirectionalLight(0x8090ff, 0.6); dl.position.set(-300, 500, 200); scene.add(dl);
}

// ------------------------------------------------------------
// 線路（レール・枕木・支柱）
// ------------------------------------------------------------
function strip(offB, offU, hw, hh, step, sMax) {
  const pos = [], idx = [];
  let n = 0;
  for (let s = 0; s <= sMax; s += step) {
    const f = frameAt(s);
    const c = f.p.clone().addScaledVector(f.b, offB).addScaledVector(f.u, offU);
    for (const [a, b] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) {
      const v = c.clone().addScaledVector(f.b, a * hw).addScaledVector(f.u, b * hh);
      pos.push(v.x, v.y, v.z);
    }
    if (n > 0) {
      const o = (n - 1) * 4, q = n * 4;
      for (let e = 0; e < 4; e++) { const e2 = (e + 1) % 4; idx.push(o + e, q + e, q + e2, o + e, q + e2, o + e2); }
    }
    n++;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx); g.computeVertexNormals();
  return g;
}
{
  const railMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(0x00e0ff).multiplyScalar(1.6), toneMapped: false });
  scene.add(new THREE.Mesh(strip(0.78, 0, 0.07, 0.07, 1, TRACK_END_S), railMat));
  scene.add(new THREE.Mesh(strip(-0.78, 0, 0.07, 0.07, 1, TRACK_END_S), railMat));
  scene.add(new THREE.Mesh(strip(0, -0.55, 0.28, 0.28, 2, TRACK_END_S), new THREE.MeshLambertMaterial({ color: 0x1a2238, emissive: 0x0a1633 })));
  const nt = Math.floor(TRACK_END_S / 1.6);
  const ties = new THREE.InstancedMesh(new THREE.BoxGeometry(1.9, 0.12, 0.28), new THREE.MeshLambertMaterial({ color: 0x2a3550, emissive: 0x2a6cff, emissiveIntensity: .35 }), nt);
  const m = new THREE.Matrix4();
  for (let i = 0; i < nt; i++) {
    const f = frameAt(i * 1.6);
    m.makeBasis(f.b, f.u, f.t.clone().negate()); m.setPosition(f.p.clone().addScaledVector(f.u, -0.12));
    ties.setMatrixAt(i, m);
  }
  scene.add(ties);
  const pil = [];
  for (let s = 20; s < TRACK_END_S; s += 26) { const f = frameAt(s); if (f.p.y > 6 && s > 60) pil.push(f.p); }
  const pm = new THREE.InstancedMesh(new THREE.CylinderGeometry(0.45, 0.6, 1, 8), new THREE.MeshLambertMaterial({ color: 0x151b2c, emissive: 0x05080f }), pil.length);
  pil.forEach((p, i) => { const h = p.y - 0.8; m.compose(V3(p.x, h / 2, p.z), new THREE.Quaternion(), V3(1, h, 1)); pm.setMatrixAt(i, m); });
  scene.add(pm);
}

// ------------------------------------------------------------
// 街（ビル群）
// ------------------------------------------------------------
const trackGrid = new Map();
const GK = 40;
for (let s = 0; s <= NS; s += 2) {
  const p = FP[s]; const key = Math.floor(p.x / GK) + ',' + Math.floor(p.z / GK);
  if (!trackGrid.has(key)) trackGrid.set(key, []);
  trackGrid.get(key).push(p);
}
function trackClear(x0, z0, x1, z1, h, near = 20, far = 34, margin = 22) {
  const gx0 = Math.floor((x0 - far) / GK), gx1 = Math.floor((x1 + far) / GK), gz0 = Math.floor((z0 - far) / GK), gz1 = Math.floor((z1 + far) / GK);
  for (let gx = gx0; gx <= gx1; gx++) for (let gz = gz0; gz <= gz1; gz++) {
    const list = trackGrid.get(gx + ',' + gz); if (!list) continue;
    for (const p of list) {
      const dx = Math.max(x0 - p.x, 0, p.x - x1), dz = Math.max(z0 - p.z, 0, p.z - z1);
      const d = Math.hypot(dx, dz);
      if (d < near) return false;
      if (d < far && h > p.y - margin) return false;
    }
  }
  return true;
}
function boxGeo(x, z, w, d, h, y0 = 0) {
  const g = new THREE.BoxGeometry(w, h, d);
  const uv = g.attributes.uv;
  // 面の順: +x -x +y -y +z -z（各4頂点）
  const sc = [[d, h], [d, h], [0, 0], [0, 0], [w, h], [w, h]];
  const r = rng(Math.floor(x * 13 + z * 7));
  for (let f = 0; f < 6; f++) for (let v = 0; v < 4; v++) {
    const i = f * 4 + v;
    if (sc[f][0] === 0) { uv.setXY(i, 0.005, 0.995); continue; }
    uv.setXY(i, uv.getX(i) * sc[f][0] / 30 + (r() * 8 | 0) / 8, uv.getY(i) * sc[f][1] / 60);
  }
  g.translate(x, y0 + h / 2, z);
  return g;
}
const blds = [[], []];
const roofLights = [];
function addBuilding(x, z, w, d, h, warm, check = true) {
  if (check && !trackClear(x - w / 2, z - d / 2, x + w / 2, z + d / 2, h)) return false;
  blds[warm ? 1 : 0].push(boxGeo(x, z, w, d, h));
  if (h > 110) roofLights.push(V3(x + w * .3, h + 1.5, z + d * .3), V3(x - w * .3, h + 1.5, z - d * .3));
  return true;
}
function nearLandmark(x, z, r) {
  for (const L of [[TOCHO, 95], [COCOON, 60], [V3(260, 0, -150), 75], [V3(0, 0, 800), 50]]) if (Math.hypot(x - L[0].x, z - L[0].z) < L[1] + r) return true;
  return false;
}
{
  const r = rng(2024);
  for (let bx = -1050; bx < 850; bx += 70) for (let bz = -1050; bz < 1250; bz += 70) {
    const cx = bx + 35, cz = bz + 35; // ブロック中心（周囲 20m が道路）
    const dist = Math.hypot(cx - 0, cz - 50);
    const tall = dist < 520;
    const n = 1 + Math.floor(r() * 3);
    for (let k = 0; k < n; k++) {
      const w = 16 + r() * 26, d = 16 + r() * 26;
      const x = cx + (r() - .5) * (48 - w), z = cz + (r() - .5) * (48 - d);
      let h = tall ? 60 + Math.pow(r(), 1.6) * 180 : 14 + Math.pow(r(), 2) * 80;
      if (nearLandmark(x, z, Math.max(w, d) / 2)) continue;
      addBuilding(x, z, w, d, h, r() < .35);
    }
  }
  // スタート地点のビル
  addBuilding(0, 800, 44, 70, 187, false, false);
  // ネオン街（低層ビル）
  for (let s = S(47.8); s < S(54.6); s += 11 + (hash(s | 0, 3) * 6)) {
    const f = frameAt(s);
    for (const side of [-1, 1]) {
      const lat = 15 + hash(s | 0, side + 5) * 8;
      const w = 9 + hash(s | 0, side + 9) * 5, dpt = 14 + hash(s | 0, side + 11) * 12, h = 10 + hash(s | 0, side + 13) * 24;
      const c = f.p.clone().addScaledVector(f.b, side * (lat + dpt / 2));
      addBuilding(c.x, c.z, w, dpt, h, hash(s | 0, side) < .6, false);
    }
  }
  // 都庁（第一本庁舎）
  const T0 = TOCHO;
  blds[0].push(boxGeo(T0.x, T0.z, 100, 50, 160));
  blds[0].push(boxGeo(T0.x - 32, T0.z, 36, 50, 83, 160));
  blds[0].push(boxGeo(T0.x + 32, T0.z, 36, 50, 83, 160));
  roofLights.push(V3(T0.x - 32, 245, T0.z), V3(T0.x + 32, 245, T0.z));
  // 新宿パークタワー風（3棟＋三角屋根）
  const PK = V3(260, 0, -150);
  [[0, 235], [34, 215], [68, 195]].forEach(([o, h]) => blds[1].push(boxGeo(PK.x + o - 34, PK.z + o * .3 - 10, 30, 30, h)));
  const mergeBuilt = (list, tex) => {
    const g = THREEX.mergeGeometries(list, false);
    return new THREE.Mesh(g, new THREE.MeshLambertMaterial({ color: 0x0c1122, emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: 0.95, map: tex }));
  };
  scene.add(mergeBuilt(blds[0], windowTex(7, false)));
  scene.add(mergeBuilt(blds[1], windowTex(8, true)));
  const pyr = new THREE.ConeGeometry(21, 22, 4); pyr.rotateY(Math.PI / 4);
  const pmat = new THREE.MeshLambertMaterial({ color: 0x1a2030, emissive: 0x223355 });
  [[0, 235], [34, 215], [68, 195]].forEach(([o, h]) => { const m = new THREE.Mesh(pyr, pmat); m.position.set(PK.x + o - 34, h + 11, PK.z + o * .3 - 10); scene.add(m); });
  // コクーンタワー
  const prof = [];
  for (let i = 0; i <= 30; i++) { const y = i / 30 * 204; const u = y / 204; prof.push(new THREE.Vector2(Math.max(0.5, 30 * Math.sin(Math.PI * (0.12 + u * 0.88)) * (1 - u * 0.35)), y)); }
  const lat = canvasTex(256, 512, (g, w, h) => {
    g.fillStyle = '#060a14'; g.fillRect(0, 0, w, h);
    g.strokeStyle = 'rgba(140,220,255,.85)'; g.lineWidth = 3;
    for (let k = -8; k < 16; k++) { g.beginPath(); g.moveTo(k * 32, h); g.lineTo(k * 32 + 256, 0); g.stroke(); g.beginPath(); g.moveTo(k * 32 + 256, h); g.lineTo(k * 32, 0); g.stroke(); }
    for (let y = 0; y < h; y += 12) for (let x = 0; x < w; x += 12) if (hash(x, y, 9) > .6) { g.fillStyle = 'rgba(200,230,255,.5)'; g.fillRect(x + 3, y + 3, 5, 4); }
  });
  lat.wrapS = lat.wrapT = THREE.RepeatWrapping; lat.repeat.set(3, 3);
  const coc = new THREE.Mesh(new THREE.LatheGeometry(prof, 40), new THREE.MeshLambertMaterial({ color: 0x0a1020, emissive: 0xffffff, emissiveMap: lat, emissiveIntensity: 1.1 }));
  coc.position.copy(COCOON); scene.add(coc);
  // 屋上の航空障害灯
  const rl = new THREE.InstancedMesh(new THREE.SphereGeometry(1.3, 8, 6), new THREE.MeshBasicMaterial({ color: new THREE.Color(0xff2040).multiplyScalar(3), toneMapped: false }), roofLights.length);
  const m = new THREE.Matrix4();
  roofLights.forEach((p, i) => { m.makeTranslation(p.x, p.y, p.z); rl.setMatrixAt(i, m); });
  scene.add(rl);
  window.__roofLights = rl;
}

// ------------------------------------------------------------
// 車の光（道路を流れるテールランプ／ヘッドライト）
// ------------------------------------------------------------
const CARS = [];
{
  const r = rng(77);
  for (let i = 0; i < 700; i++) {
    const alongX = r() < .5;
    const lane = (Math.floor(r() * 27) - 15) * 70 + (r() < .5 ? -4 : 4);
    CARS.push({ alongX, lane, off: r() * 2200, v: (8 + r() * 10) * (r() < .5 ? -1 : 1) });
  }
}
const carMesh = new THREE.InstancedMesh(new THREE.BoxGeometry(1.8, 1, 4.2), new THREE.MeshBasicMaterial({ toneMapped: false }), CARS.length);
CARS.forEach((c, i) => carMesh.setColorAt(i, c.v > 0 ? new THREE.Color(3, .25, .2) : new THREE.Color(2.4, 2.2, 1.8)));
scene.add(carMesh);
function updateCars(t) {
  const m = new THREE.Matrix4();
  CARS.forEach((c, i) => {
    const p = ((c.off + c.v * t) % 2200 + 2200) % 2200 - 1100;
    if (c.alongX) m.makeRotationY(Math.PI / 2).setPosition(p, 0.6, c.lane);
    else m.makeTranslation(c.lane, 0.6, p);
    carMesh.setMatrixAt(i, m);
  });
  carMesh.instanceMatrix.needsUpdate = true;
}

// ------------------------------------------------------------
// ネオン看板・巨大スクリーン・ゲート看板
// ------------------------------------------------------------
function textPlane(w, h, pw, ph, draw, opts = {}) {
  const tex = canvasTex(w, h, draw);
  const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, side: THREE.DoubleSide, toneMapped: false, depthWrite: opts.depthWrite ?? true });
  if (opts.boost) mat.color.setScalar(opts.boost);
  return new THREE.Mesh(new THREE.PlaneGeometry(pw, ph), mat);
}
{
  const words = ['成約', '商談', 'CLOSING', '営業', '育成', 'THIRD', '戦略', '決断', 'SALES', '新宿', '提案', '集客', '即決', 'WIN', '売上', '突破'];
  const cols = ['#ff3d9a', '#00e0ff', '#ffd23d', '#7dff6a', '#ff6a3d', '#b36bff'];
  let k = 0;
  for (let s = S(47.9); s < S(54.3); s += 9) {
    const f = frameAt(s);
    for (const side of [-1, 1]) {
      const word = words[k % words.length], col = cols[(k * 7 + (side > 0 ? 3 : 0)) % cols.length];
      k++;
      const vertical = !/^[A-Z]/.test(word);
      const sign = vertical
        ? textPlane(160, 512, 4.2, 13.4, (g, w, h) => {
          g.fillStyle = 'rgba(8,4,16,.92)'; g.fillRect(0, 0, w, h);
          g.strokeStyle = col; g.lineWidth = 8; g.strokeRect(8, 8, w - 16, h - 16);
          g.font = `900 118px "Noto Sans JP"`; g.textAlign = 'center'; g.fillStyle = col;
          g.shadowColor = col; g.shadowBlur = 18;
          [...word].forEach((c, i) => g.fillText(c, w / 2, 150 + i * 150));
        }, { boost: 1.8 })
        : textPlane(512, 160, 14, 4.4, (g, w, h) => {
          g.fillStyle = 'rgba(8,4,16,.92)'; g.fillRect(0, 0, w, h);
          g.strokeStyle = col; g.lineWidth = 8; g.strokeRect(8, 8, w - 16, h - 16);
          g.font = `700 104px "Oswald"`; g.textAlign = 'center'; g.fillStyle = col; g.shadowColor = col; g.shadowBlur = 18;
          g.fillText(word, w / 2, 118);
        }, { boost: 1.8 });
      const pos = f.p.clone().addScaledVector(f.b, side * (9.5 + hash(k, 1) * 2));
      pos.y = 8 + hash(k, 2) * 12;
      sign.position.copy(pos);
      sign.lookAt(pos.clone().sub(f.t));
      scene.add(sign);
    }
  }
  // 都庁の外壁スクリーン（4面）
  const screenTex = (i) => (g, w, h) => {
    g.fillStyle = 'rgba(2,8,20,.95)'; g.fillRect(0, 0, w, h);
    const gr = g.createLinearGradient(0, 0, w, h); gr.addColorStop(0, 'rgba(42,92,255,.35)'); gr.addColorStop(1, 'rgba(0,224,255,.2)');
    g.fillStyle = gr; g.fillRect(0, 0, w, h);
    g.strokeStyle = '#00e0ff'; g.lineWidth = 10; g.strokeRect(10, 10, w - 20, h - 20);
    g.textAlign = 'center'; g.fillStyle = '#fff';
    if (i % 2 === 0) {
      g.font = '700 300px "Oswald"'; g.letterSpacing = '40px'; g.fillText('THIRD', w / 2 + 20, 400);
      g.letterSpacing = '12px'; g.font = '700 70px "Noto Sans JP"'; g.fillText('株式会社サード', w / 2 + 6, 520);
    } else {
      g.font = '900 104px "Noto Sans JP"'; g.fillText('第三の答えを、', w / 2, 270); g.fillStyle = '#9eefff'; g.fillText('営業に。', w / 2, 410);
      g.fillStyle = '#fff'; g.font = '500 44px "Oswald"'; g.letterSpacing = '18px'; g.fillText('SHINJUKU, TOKYO', w / 2 + 9, 510);
    }
  };
  [[0, 0, 25.6, 0, 96, 60], [Math.PI, 0, -25.6, 0, 96, 60], [Math.PI / 2, 50.6, 0, 1, 48, 30], [-Math.PI / 2, -50.6, 0, 1, 48, 30]].forEach(([ry, ox, oz, i, pw, ph], k) => {
    const sc = textPlane(1024, 640, pw, ph, screenTex(k), { boost: 1.5 });
    sc.position.set(TOCHO.x + ox, 95, TOCHO.z + oz);
    sc.rotation.y = ry;
    scene.add(sc);
  });
}
// サービスのゲート看板（カメラがくぐる）
const GATES = [
  { t: 26.0, no: '01', en: 'CLOSING OUTSOURCING', jp: 'クロージング代行' },
  { t: 36.0, no: '02', en: 'SALES TRAINING', jp: '営業マン育成コンサル' },
  { t: 46.0, no: '03', en: 'MARKETING', jp: 'マーケティングコンサル' },
];
GATES.forEach(G => {
  const f = frameAt(S(G.t));
  const grp = new THREE.Group();
  const panel = textPlane(1024, 560, 34, 18.6, (g, w, h) => {
    g.fillStyle = 'rgba(2,10,28,.55)'; g.fillRect(0, 0, w, h);
    g.strokeStyle = '#00e0ff'; g.lineWidth = 12; g.strokeRect(6, 6, w - 12, h - 12);
    g.textAlign = 'center';
    g.fillStyle = '#00e0ff'; g.font = '500 54px "Oswald"'; g.letterSpacing = '20px'; g.fillText('SERVICE ' + G.no, w / 2 + 10, 120);
    g.letterSpacing = '0px'; g.fillStyle = '#fff';
    g.font = `900 ${G.jp.length > 9 ? 84 : 110}px "Noto Sans JP"`; g.fillText(G.jp, w / 2, 300);
    g.font = '300 46px "Oswald"'; g.letterSpacing = '14px'; g.fillStyle = '#bfefff'; g.fillText(G.en, w / 2 + 7, 420);
  }, { boost: 1.0, depthWrite: false });
  grp.add(panel);
  const fm = new THREE.MeshBasicMaterial({ color: new THREE.Color(0x00e0ff).multiplyScalar(1.4), toneMapped: false });
  for (const [x, y, w, h] of [[0, 9.8, 36, .5], [0, -9.8, 36, .5], [-17.8, 0, .5, 20], [17.8, 0, .5, 20]]) {
    const b = new THREE.Mesh(new THREE.BoxGeometry(w, h, .5), fm); b.position.set(x, y, 0); grp.add(b);
  }
  grp.position.copy(f.p.clone().addScaledVector(f.u, 2.4));
  const m = new THREE.Matrix4().makeBasis(f.b, f.u, f.t.clone().negate());
  grp.quaternion.setFromRotationMatrix(m);
  scene.add(grp);
});

// コースターの先頭車両（カメラに固定）
{
  const car = new THREE.Group();
  const hull = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.4, 1.6), new THREE.MeshLambertMaterial({ color: 0x0b1020, emissive: 0x050a18 }));
  hull.position.set(0, -1.6, -2.0); car.add(hull);
  const edge = new THREE.Mesh(new THREE.BoxGeometry(1.54, 0.04, 0.04), new THREE.MeshBasicMaterial({ color: new THREE.Color(0x00e0ff).multiplyScalar(0.9), toneMapped: false }));
  edge.position.set(0, -1.4, -2.8); car.add(edge);
  const nose = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.03, 0.03), new THREE.MeshBasicMaterial({ color: new THREE.Color(0xffffff).multiplyScalar(0.9), toneMapped: false }));
  nose.position.set(0, -1.38, -2.81); car.add(nose);
  camera.add(car);
}

// ------------------------------------------------------------
// カメラ
// ------------------------------------------------------------
const LOGO_TARGET = V3(40, 60, 120);
function worldFrame(t) {
  const s = S(t), v = speedAt(t);
  const f = frameAt(s);
  const ahead = frameAt(s + 14 + v * 0.25);
  const camH = 2.6;
  const pos = f.p.clone().addScaledVector(f.u, camH);
  const look = ahead.p.clone().addScaledVector(ahead.u, camH);
  const upv = f.u.clone();
  // 振動（速度に比例）
  const sh = clamp((v - 25) / 60) * 0.09;
  pos.addScaledVector(f.b, (hash(Math.floor(t * 30), 1) - .5) * sh).addScaledVector(f.u, (hash(Math.floor(t * 30), 2) - .5) * sh);
  // 線路の先から空へ：視線を街へ向ける
  const lg = eInOut(seg(t, 62.3, 66.5));
  if (lg > 0) {
    look.lerp(LOGO_TARGET, lg);
    upv.lerp(UP, lg).normalize();
  }
  camera.position.copy(pos);
  camera.up.copy(upv);
  camera.lookAt(look);
  camera.fov = lerp(66 + 26 * clamp((v - 15) / 70), 58, lg);
  camera.updateProjectionMatrix();
  camera.children[0].visible = t < TRACK_END_T + 0.15;
  updateCars(t);
  window.__roofLights.material.color.setScalar(Math.sin(t * 4) > 0 ? 3 : 0.4).multiply(new THREE.Color(1, .12, .2));
  bloom.strength = 0.5 + 0.3 * clamp((v - 40) / 50);
  composer.render();
  return { v, alt: pos.y, s };
}
