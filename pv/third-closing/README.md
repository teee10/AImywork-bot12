# 株式会社サード クロージング代行サービス紹介動画

`third_closing_pv.mp4` — 1920×1080 / 30fps / 120秒 / BGM付き（H.264 + AAC）

## 構成（120BPM、シーンの頭を小節頭に合わせています）

| 時間 | シーン | 内容 |
|---|---|---|
| 0:00–0:10 | Opening | 「商談、決めきれていますか？」→ 課題の連打（決まらない／最後のひと押し／他社に流れる…） |
| 0:10–0:18 | Title | 「その商談、私たちが決めきります。」→ CLOSING OUTSOURCING／クロージング代行サービス |
| 0:18–0:30 | Concept | 御社 × THIRD = ONE TEAM／商談から、成約まで（ヒアリング→提案→成約） |
| 0:30–0:48 | Issue → Solution | 課題と解決 ×3 |
| 0:48–1:06 | Service Menu | 事前設計／商談同席・代行／反論処理・条件交渉／契約締結フォロー／追客・失注防止／成約データ分析 |
| 1:06–1:26 | Flow | ヒアリング→提案設計→クロージング→契約フォロー→分析・改善（PDCA） |
| 1:26–1:44 | Why THIRD | 育成のプロがクロージング／マーケ視点で決める／成約率の見える化 |
| 1:44–1:52 | Climax | 準備。商談。決断。成約。→「その商談を、成約に変える。」 |
| 1:52–2:00 | Ending | ロゴ／株式会社サード／「まずは、お気軽にご相談ください。」 |

## ファイル

- `engine.js` — 共通の描画エンジン（背景・文字アニメ・グリッチ・HUD など）
- `scenes.js` — この動画のシーン定義（テキストはここを編集）
- `index.html` — ブラウザで開くとプレビュー再生（クリックで音声も再生、`?t=30` で30秒目から）
- `music.py` — BGM を numpy で合成して `music.wav` を出力
- `render.cjs` — Playwright で全フレームを書き出し、ffmpeg で `music.wav` と合成
- `subset_fonts.py` — Noto Sans JP を使用文字だけにサブセット化（Oswald は `../third/fonts` を共用）

## 再生成

```bash
pip install numpy imageio-ffmpeg fonttools brotli
python3 music.py
python3 subset_fonts.py        # テキストを変更したとき（元TTFは ../third/fonts/src/）
FFMPEG=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())") \
  NODE_PATH=$(npm root -g) node render.cjs                 # -> third_closing_pv.mp4
NODE_PATH=$(npm root -g) node render.cjs --still 40.5      # 静止画確認 -> stills/
```

ロゴ・コピー・レポート画面（「※イメージ」表記）は仮のものです。実績の数値や顧客名は入れていません。
