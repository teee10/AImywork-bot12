# ひねり飛車 解説動画（初心者 → 将棋ウォーズ1級）

| ファイル | 内容 |
|---|---|
| `hineri_bisha.mp4` | **完全入門**（約8分）基本定跡・囲い（坊主美濃→銀冠）・攻めの考え方・後手の対策・練習法 |
| `hineri_bisha_jissen.mp4` | **実戦編**（約8分）目標の形・序盤の落とし穴2つ・角交換の注意・実戦1局（99手で詰みまで） |
| `make_video.py` / `make_jissen.py` | 各動画の台本と生成スクリプト |
| `shogi_video.py` | 共通部品（盤面描画・読み上げ・動画の組み立て） |

## 手順の検証について

- 指し手はすべて python-shogi で反則がないことを確認している。
- 定跡手順・落とし穴・評価値は、将棋ソフト（やねうら王 + 水匠5）で1手ずつ検証した。
- 実戦編の1局は「先手：強めの設定 / 後手：わざと弱くした設定」のソフト同士の対局。

## 再生成

```bash
pip install python-shogi pyopenjtalk-plus pillow numpy   # ffmpeg も必要
python3 videos/hineri-bisha/make_video.py
python3 videos/hineri-bisha/make_jissen.py
```
