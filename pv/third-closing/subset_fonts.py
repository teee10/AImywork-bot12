# index.html / scenes.js で使っている文字だけに Noto Sans JP をサブセット化する
# 元フォントは ../third/fonts/src/ に置く（Google Fonts から取得、SIL OFL 1.1）
import glob, os, subprocess
here = os.path.dirname(os.path.abspath(__file__))
chars = set()
for f in ('index.html', 'scenes.js'):
    chars |= set(open(os.path.join(here, f), encoding='utf-8').read())
chars |= set(chr(c) for c in range(0x20, 0x7f))
text = ''.join(sorted(chars))
for src in glob.glob(os.path.join(here, '..', 'third', 'fonts', 'src', 'NotoSansJP-*.ttf')):
    out = os.path.join(here, 'fonts', os.path.basename(src).replace('.ttf', '.woff2'))
    subprocess.run(['pyftsubset', src, f'--text={text}', '--flavor=woff2', f'--output-file={out}'], check=True)
    print(out, os.path.getsize(out))
