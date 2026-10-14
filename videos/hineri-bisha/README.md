# ひねり飛車 解説動画

- `hineri_bisha.mp4` … 完成動画（1280x720、約3分40秒、日本語ナレーション付き）
- `make_video.py` … 動画生成スクリプト（盤面描画・音声合成・エンコード）

## 再生成

```bash
pip install python-shogi pyopenjtalk-plus pillow numpy   # ffmpeg も必要
python3 videos/hineri-bisha/make_video.py
```

指し手はすべて python-shogi で合法手チェックしています。
