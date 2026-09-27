// 使い方:
//   node render.cjs                 -> third_coaster_pv.mp4 を書き出し（music.wav を合成）
//   node render.cjs --speed         -> speed.json（BGM の風切り音用）を書き出し
//   node render.cjs --still 13.5    -> still_13.5.png を1枚書き出し
//   node render.cjs --seg 0 30      -> 0〜30秒の映像だけを segments/ に書き出し（長尺は分割して書き出す）
//   node render.cjs --join          -> segments/*.mp4 を連結して music.wav と合成
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const W = 1920, H = 1080, FPS = 30;
const FFMPEG = process.env.FFMPEG || 'ffmpeg';
const dir = __dirname;

(async () => {
  const args = process.argv.slice(2);
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('PAGEERROR', e.message));
  await page.goto('file://' + path.join(dir, 'index.html') + '?render=1');
  await page.waitForFunction('window.__ready === true', null, { timeout: 120000 });

  if (args[0] === '--speed') {
    // BGM 用に 1/30 秒ごとの速度（m/s）を書き出す
    const sp = await page.evaluate(() => { const a = []; for (let f = 0; f <= DUR * FPS; f++) a.push(+speedAt(f / FPS).toFixed(3)); return a; });
    require('fs').writeFileSync(path.join(dir, 'speed.json'), JSON.stringify(sp));
    await browser.close();
    console.log('speed.json', sp.length);
    return;
  }
  if (args[0] === '--still') {
    for (const t of args.slice(1)) {
      await page.evaluate(x => renderFrame(x), parseFloat(t));
      await page.screenshot({ path: path.join(dir, 'stills', `still_${t}.png`) });
    }
    await browser.close();
    return;
  }

  if (args[0] === '--seg') {
    const [a, b] = args.slice(1, 3).map(parseFloat);
    const f0 = Math.round(a * FPS), f1 = Math.round(b * FPS);
    const fs = require('fs');
    fs.mkdirSync(path.join(dir, 'segments'), { recursive: true });
    const segOut = path.join(dir, 'segments', `seg_${String(f0).padStart(5, '0')}.mp4`);
    const sf = spawn(FFMPEG, ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', segOut], { stdio: ['pipe', 'ignore', 'ignore'] });
    for (let f = f0; f < f1; f++) {
      await page.evaluate(x => renderFrame(x), f / FPS);
      const img = await page.screenshot({ type: 'jpeg', quality: 95 });
      if (!sf.stdin.write(img)) await new Promise(r => sf.stdin.once('drain', r));
    }
    sf.stdin.end();
    await new Promise(r => sf.on('close', r));
    await browser.close();
    console.log('segment ->', segOut);
    return;
  }
  if (args[0] === '--join') {
    await browser.close();
    const fs = require('fs');
    const segs = fs.readdirSync(path.join(dir, 'segments')).filter(f => f.endsWith('.mp4')).sort();
    const list = path.join(dir, 'segments', 'list.txt');
    fs.writeFileSync(list, segs.map(f => `file '${f}'`).join('\n'));
    const jf = spawn(FFMPEG, ['-y', '-f', 'concat', '-safe', '0', '-i', list, '-i', path.join(dir, 'music.wav'),
      '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart',
      path.join(dir, 'third_coaster_pv.mp4')], { stdio: ['ignore', 'ignore', 'inherit'] });
    await new Promise(r => jf.on('close', r));
    console.log('done');
    return;
  }

  const dur = await page.evaluate('DUR');
  const total = Math.round(dur * FPS);
  const out = path.join(dir, 'third_coaster_pv.mp4');
  const ff = spawn(FFMPEG, [
    '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', path.join(dir, 'music.wav'),
    '-map', '0:v', '-map', '1:a',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p',
    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out,
  ], { stdio: ['pipe', 'ignore', 'inherit'] });

  for (let f = 0; f < total; f++) {
    await page.evaluate(x => renderFrame(x), f / FPS);
    const img = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(img)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(`frame ${f}/${total}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await browser.close();
  console.log('done ->', out);
})();
