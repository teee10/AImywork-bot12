# ひねり飛車 解説動画（初心者 → 将棋ウォーズ1級）

| ファイル | 内容 |
|---|---|
| `hineri_bisha.mp4` | **完全入門**（約8分）基本定跡・囲い（坊主美濃→銀冠）・攻めの考え方・後手の対策・練習法 |
| `hineri_bisha_jissen.mp4` | **実戦編**（約8分）目標の形・序盤の落とし穴2つ・角交換の注意・実戦1局（99手で詰みまで） |
| `hineri_bisha_kougeki.mp4` | **よく出る攻めパターン**（約4分半）ひねったあとの局面からソフト同士で24局を指させ、先手の攻めの手を集計。出現数の多い順に解説（銀の繰り出し・角の転換・▲8六飛・▲7四歩の突き捨てなど） |
| `hineri_bisha_sonota.mp4` | **よく出る攻めパターン2**（約4分）前回「そのほか」にまとめた5つ（▲5六歩〜▲5五歩・8筋の歩・と金・桂跳ね・端攻め）の解説 |
| `make_video.py` / `make_jissen.py` / `make_kougeki.py` / `make_sonota.py` | 各動画の台本と生成スクリプト |
| `shogi_video.py` | 共通部品（盤面描画・読み上げ・動画の組み立て） |

## 手順の検証について

- 指し手はすべて python-shogi で反則がないことを確認している。
- 定跡手順・落とし穴・評価値は、将棋ソフト（やねうら王 + 水匠5）で1手ずつ検証した。
- 実戦編・攻めのパターン集の対局は「先手：強めの設定 / 後手：わざと弱くした設定」のソフト同士の対局。

## 再生成

```bash
pip install python-shogi pyopenjtalk-plus pillow numpy   # ffmpeg も必要
python3 videos/hineri-bisha/make_video.py
python3 videos/hineri-bisha/make_jissen.py
python3 videos/hineri-bisha/make_kougeki.py
python3 videos/hineri-bisha/make_sonota.py
```
