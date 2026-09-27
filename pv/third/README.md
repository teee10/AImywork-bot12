# 株式会社サード 会社紹介PV

`third_pv.mp4` — 1920×1080 / 30fps / 45秒 / BGM付き（H.264 + AAC）

## 構成（120BPM、シーンの切り替えを音に合わせています）

| 時間 | シーン | 内容 |
|---|---|---|
| 0–4s | Opening | 「営業は、才能じゃない。」 |
| 4–7s | Impact | 「仕組みだ。」 |
| 7–12s | Concept | 自社で抱えるか／外に丸投げするか → 「第三の答え。」 → THIRD |
| 12–18s | SERVICE 01 | 営業代行：戦略設計→アプローチ→商談→成約 |
| 18–24s | SERVICE 02 | 営業マン育成コンサルティング：スキルレーダー BEFORE→AFTER |
| 24–30s | SERVICE 03 | マーケティングコンサルティング：認知→興味→比較→選ばれる |
| 30–36s | Office | SHINJUKU, TOKYO（新宿の夜景・都庁にピン） |
| 36–45s | Ending | 代行。育成。戦略。→ ロゴ／株式会社サード／「売れる組織を、共に創る。」 |

## ファイル

- `index.html` — 映像本体（Canvas）。`renderFrame(t)` が t 秒のフレームを描画。ブラウザで開くとプレビュー再生（クリックで音声も再生）
- `music.py` — BGM を numpy で合成して `music.wav` を出力
- `render.cjs` — Playwright で全フレームを書き出し、ffmpeg で `music.wav` と合成
- `subset_fonts.py` — Noto Sans JP を使用文字だけにサブセット化
- `fonts/` — Noto Sans JP / Oswald（SIL Open Font License 1.1、`fonts/OFL.txt`）

## 再生成

```bash
pip install numpy imageio-ffmpeg
python3 music.py
FFMPEG=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())") \
  NODE_PATH=$(npm root -g) node render.cjs          # -> third_pv.mp4
NODE_PATH=$(npm root -g) node render.cjs --still 21.5   # 静止画確認 -> stills/
```

テキストを変更したら `fonts/src/` に Noto Sans JP の TTF を置いて `python3 subset_fonts.py` を再実行してください。
ロゴ（3本のバー＋THIRD）とコピーは仮のものです。正式なロゴ・コピーがあれば差し替えます。
