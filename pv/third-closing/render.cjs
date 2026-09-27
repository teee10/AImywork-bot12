// 使い方:
//   node render.cjs                 -> third_closing_pv.mp4 を書き出し（music.wav を合成）
//   node render.cjs --still 13.5    -> still_13.5.png を1枚書き出し
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const W = 1920, H = 1080, FPS = 30;
const FFMPEG = process.env.FFMPEG || 'ffmpeg';
const dir = __dirname;

(async () => {
  const args = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('PAGEERROR', e.message));
  await page.goto('file://' + path.join(dir, 'index.html') + '?render=1');
  await page.waitForFunction('window.__ready === true', null, { timeout: 120000 });

  if (args[0] === '--still') {
    for (const t of args.slice(1)) {
      await page.evaluate(x => renderFrame(x), parseFloat(t));
      await page.screenshot({ path: path.join(dir, 'stills', `still_${t}.png`) });
    }
    await browser.close();
    return;
  }

  const dur = await page.evaluate('DUR');
  const total = Math.round(dur * FPS);
  const out = path.join(dir, 'third_closing_pv.mp4');
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
