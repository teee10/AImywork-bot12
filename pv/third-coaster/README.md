# 株式会社サード PV（ジェットコースター版）

`third_coaster_pv.mp4` — 1920×1080 / 30fps / 72秒 / BGM付き（H.264 + AAC）

夜の新宿を3DCGで作り、ジェットコースターの先頭車両からの一人称視点で駆け抜ける PV です。
実写素材は使っていません（素材サイトへの接続が制限されていたため、すべて CG）。

## 構成

| 時間 | 内容 |
|---|---|
| 0:00–0:08 | ビル屋上からのリフトアップ（チェーン音）「営業は、才能じゃない。」 |
| 0:08–0:16 | 頂上から落下 →「仕組みだ。」→ 超高層ビルの谷間へ ／ SHINJUKU, TOKYO |
| 0:16–0:26 | 都庁の周りをらせん上昇（外壁スクリーンに THIRD）／ 株式会社サード |
| 0:26–0:36 | ゲート看板をくぐって SERVICE 01 クロージング代行 |
| 0:36–0:46 | コクーンタワーの横でバレルロール → SERVICE 02 営業マン育成コンサルティング |
| 0:46–0:56 | ネオン街を低空で疾走 → SERVICE 03 マーケティングコンサルティング |
| 0:56–1:02 | 上空へらせん上昇「営業を、次のステージへ。」→ 成約。育成。戦略。THIRD. |
| 1:02–1:12 | レールの先から空へ。新宿の夜景を見下ろしてロゴ |

画面下の SPEED / ALT は実際のカメラ速度・高度から計算しています。

## ファイル

- `world.js` — 3D ワールド（コースのウェイポイント、線路、街、都庁・コクーンタワー・パークタワー風のビル、ネオン看板、ゲート看板、カメラ）
- `overlay.js` — 2D オーバーレイ（コピー、HUD、スピード線、フラッシュ、ロゴ）
- `engine.js` — 共通の 2D 描画ヘルパー
- `vendor/three-bundle.js` — three.js r169 + EffectComposer / UnrealBloomPass などを1ファイルにまとめたもの（`vendor/entry.js` から esbuild で生成、MIT License）
- `music.py` — BGM と効果音（速度連動の風切り音・走行音、リフトのチェーン音）を合成
- `render.cjs` — Playwright（WebGL は SwiftShader）でフレームを書き出し、ffmpeg で合成

コースは `world.js` の `wp(時刻, x, y, z, ロール)` で定義しています。時刻つきなので、ゲート看板や効果音は時刻から位置が決まります。

## 再生成

```bash
pip install numpy imageio-ffmpeg fonttools brotli
export FFMPEG=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())") NODE_PATH=$(npm root -g)
node render.cjs --speed          # speed.json（BGM の風切り音用）
python3 music.py                 # music.wav
python3 subset_fonts.py          # テキストを変更したとき（元TTFは ../third/fonts/src/）
for r in "0 18" "18 36" "36 54" "54 72"; do node render.cjs --seg $r & done; wait   # 1フレーム約1秒
node render.cjs --join           # -> third_coaster_pv.mp4
# 動きが激しく CRF 19 だと約140MB になるため、GitHub の100MB制限に収まるよう 8Mbps に再エンコード
mv third_coaster_pv.mp4 master.mp4 && $FFMPEG -i master.mp4 -c:v libx264 -preset slow -b:v 8M -maxrate 10M -bufsize 16M -pix_fmt yuv420p -c:a copy -movflags +faststart third_coaster_pv.mp4
node render.cjs --still 40.5     # 静止画確認 -> stills/
```

`index.html` をブラウザで直接開くとプレビュー再生します（クリックで音声も再生、`index.html?t=26` で26秒目から）。
