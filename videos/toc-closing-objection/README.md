# ToC営業 クロージングの反論処理（解説動画）

営業を始めたばかりの初心者向けに、クロージングで出てくるお客様の反論への対応方法を約3分で解説するナレーション付き動画です。

- 動画: [`toc_closing_objection.mp4`](./toc_closing_objection.mp4)（1920×1080 / 約3分8秒 / 字幕付き）
- 生成スクリプト: [`make_video.py`](./make_video.py)（台本もこのファイル内の `SCENES` にあります）

## 構成

| # | パート | 内容 |
|---|--------|------|
| 1 | オープニング | 対象者と今日のテーマ |
| 2 | 考え方 | 反論は「断り」ではなく「不安のサイン」 |
| 3 | 基本の型 | 受け止める → 聞く → 答える → 確認する の4ステップ |
| 4 | よくある反論1 | 「高いですね」 |
| 5 | よくある反論2 | 「ちょっと考えます」 |
| 6 | よくある反論3 | 「家族に相談します」 |
| 7 | NG行動 | 否定する / すぐ値引きする / 押し売りする |
| 8 | まとめ | 4ステップのおさらい |

## 作り直すには

```bash
sudo apt-get install -y open-jtalk open-jtalk-mecab-naist-jdic hts-voice-nitech-jp-atr503-m001 fonts-noto-cjk
pip install pillow imageio-ffmpeg
python3 make_video.py          # 話す速さを変える場合: SPEED=1.0 python3 make_video.py
```

ナレーション音声は Open JTalk（オフライン音声合成）で生成しています。台本を変えたいときは `SCENES` の文章を書き換えて再実行してください。
