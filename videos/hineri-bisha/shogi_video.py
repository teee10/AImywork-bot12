"""将棋解説動画の共通部品（盤面描画・読み上げ・動画の組み立て）"""
import os, re, subprocess, shutil, wave
import numpy as np
import shogi
import pyopenjtalk
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
W, H = 1280, 720

KANJI = shogi.PIECE_JAPANESE_SYMBOLS
COLS = "９８７６５４３２１"
ROWS = "一二三四五六七八九"
NUM = "０１２３４５６７８９"

def font(sz):
    return ImageFont.truetype(FONT, sz)

# ======================================================================
# 盤面描画
# ======================================================================
BX, BY, CELL = 60, 64, 64
BOARD_PX = CELL * 9
PX = BX + BOARD_PX + 70          # 右パネルの左端

B_HL = (255, 238, 110)            # 黄: 注目
R_HL = (255, 160, 160)            # 赤: 弱点・狙われる所
G_HL = (165, 215, 255)            # 青: 守り・利き

def sq_xy(name):
    sq = shogi.SQUARE_NAMES.index(name)
    return BX + (sq % 9) * CELL, BY + (sq // 9) * CELL

def draw_piece(img, x, y, kanji, gote, promoted=False):
    s = CELL
    p = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(p)
    m = 5
    poly = [(s / 2, m), (s - m - 6, m + 10), (s - m, s - m), (m, s - m), (m + 6, m + 10)]
    d.polygon(poly, fill=(240, 205, 140), outline=(90, 60, 20))
    f = font(36)
    tb = d.textbbox((0, 0), kanji, font=f)
    d.text(((s - (tb[2] - tb[0])) / 2 - tb[0], (s - (tb[3] - tb[1])) / 2 - tb[1] + 4), kanji, font=f,
           fill=(180, 0, 0) if promoted else (20, 10, 0))
    if gote:
        p = p.rotate(180)
    img.alpha_composite(p, (x, y))

def hand_text(board, color):
    c = board.pieces_in_hand[color]
    out = "".join(KANJI[pt] + (NUM[c[pt]] if c[pt] > 1 else "") for pt in [7, 6, 5, 4, 3, 2, 1] if c[pt])
    return out or "なし"

def arrow(d, a, b, col=(235, 40, 40)):
    x1, y1 = sq_xy(a); x2, y2 = sq_xy(b)
    x1 += CELL / 2; y1 += CELL / 2; x2 += CELL / 2; y2 += CELL / 2
    v = np.array([x2 - x1, y2 - y1], dtype=float); v /= np.linalg.norm(v)
    n = np.array([-v[1], v[0]])
    tip = np.array([x2, y2]) - v * 6; base = tip - v * 26
    d.line([x1, y1, *(base + v * 2)], fill=col, width=8)
    d.polygon([tuple(tip), tuple(base + n * 15), tuple(base - n * 15)], fill=col)

def render(board, chapter, title, caption, hl=(), arrows=(), marks=(), last=None, sub=None, ply=None, ev=None):
    img = Image.new("RGBA", (W, H), (34, 40, 52, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([BX - 14, BY - 14, BX + BOARD_PX + 14, BY + BOARD_PX + 14], fill=(205, 160, 90))
    d.rectangle([BX, BY, BX + BOARD_PX, BY + BOARD_PX], fill=(226, 184, 110))
    for name, color in hl:
        x, y = sq_xy(name)
        d.rectangle([x, y, x + CELL, y + CELL], fill=color)
    if last:
        x, y = sq_xy(last)
        d.rectangle([x + 2, y + 2, x + CELL - 2, y + CELL - 2], outline=(220, 30, 30), width=4)
    for i in range(10):
        d.line([BX + i * CELL, BY, BX + i * CELL, BY + BOARD_PX], fill=(60, 40, 10), width=2)
        d.line([BX, BY + i * CELL, BX + BOARD_PX, BY + i * CELL], fill=(60, 40, 10), width=2)
    for fx, fy in [(3, 3), (6, 3), (3, 6), (6, 6)]:
        d.ellipse([BX + fx * CELL - 4, BY + fy * CELL - 4, BX + fx * CELL + 4, BY + fy * CELL + 4], fill=(60, 40, 10))
    fs = font(20)
    for i in range(9):
        d.text((BX + i * CELL + CELL / 2 - 10, BY - 40), COLS[i], font=fs, fill=(230, 230, 230))
        d.text((BX + BOARD_PX + 18, BY + i * CELL + CELL / 2 - 11), ROWS[i], font=fs, fill=(230, 230, 230))
    for sq in range(81):
        pc = board.piece_at(sq)
        if pc:
            x, y = sq_xy(shogi.SQUARE_NAMES[sq])
            draw_piece(img, x, y, KANJI[pc.piece_type], pc.color == shogi.WHITE, pc.piece_type > 8)
    d = ImageDraw.Draw(img)
    for name in marks:
        x, y = sq_xy(name)
        d.ellipse([x + 6, y + 6, x + CELL - 6, y + CELL - 6], outline=(0, 110, 255), width=5)
    for a, b in arrows:
        arrow(d, a, b)
    # 持ち駒
    fh = font(22)
    d.text((BX, BY + BOARD_PX + 20), "▲先手 持駒: " + hand_text(board, shogi.BLACK), font=fh, fill=(255, 255, 255))
    d.text((PX, H - 44), "△後手 持駒: " + hand_text(board, shogi.WHITE), font=fh, fill=(200, 200, 200))
    if ply:
        d.text((BX + BOARD_PX - 110, BY + BOARD_PX + 20), f"{ply}手目", font=fh, fill=(255, 220, 120))
    if ev is not None:
        lab = "互角" if abs(ev) < 200 else ("先手有利" if ev > 0 else "後手有利")
        if abs(ev) >= 1000:
            lab = "先手勝勢" if ev > 0 else "後手勝勢"
        d.text((BX, BY + BOARD_PX + 46), f"評価値 {ev:+d}（{lab}）", font=fh,
               fill=(140, 220, 255) if ev >= 0 else (255, 150, 150))
    # 右パネル
    d.text((PX, 20), chapter, font=font(24), fill=(255, 210, 110))
    d.rounded_rectangle([PX, 60, W - 30, H - 60], radius=18, fill=(250, 248, 240))
    d.text((PX + 26, 80), title, font=font(36), fill=(150, 20, 20))
    d.line([PX + 26, 132, W - 56, 132], fill=(150, 20, 20), width=3)
    y = 150
    for line in caption.split("\n"):
        d.text((PX + 26, y), line, font=font(26), fill=(30, 30, 30))
        y += 40
    if sub:
        d.rounded_rectangle([PX + 18, H - 150, W - 48, H - 76], radius=10, fill=(255, 228, 196))
        d.text((PX + 34, H - 128), sub, font=font(26), fill=(150, 40, 0))
    return img.convert("RGB")

def card(lines, sub="", big=96):
    img = Image.new("RGB", (W, H), (34, 40, 52))
    d = ImageDraw.Draw(img)
    y = 150 if len(lines) > 4 else 210
    for i, l in enumerate(lines):
        f = font(big if i == 0 else 38)
        tb = d.textbbox((0, 0), l, font=f)
        x = (W - (tb[2] - tb[0])) / 2 if i == 0 or not l.startswith(("①", "②", "③", "④", "⑤", "⑥", "⑦", "・")) else 250
        d.text((x, y), l, font=f, fill=(255, 220, 120) if i == 0 else (240, 240, 240))
        y += big + 50 if i == 0 else 62
    if sub:
        f = font(28); tb = d.textbbox((0, 0), sub, font=f)
        d.text(((W - (tb[2] - tb[0])) / 2, H - 90), sub, font=f, fill=(170, 170, 170))
    return img

# ======================================================================
# 音声（符号や将棋用語を読みやすいカナに直してから合成）
# ======================================================================
DIG = {c: r for c, r in zip("１２３４５６７８９", ["いち", "に", "さん", "よん", "ご", "ろく", "なな", "はち", "きゅう"])}
DAN = {c: r for c, r in zip("一二三四五六七八九", ["いち", "に", "さん", "よん", "ご", "ろく", "なな", "はち", "きゅう"])}
PIECE = {"歩": "ふ", "香": "きょう", "桂": "けい", "銀": "ぎん", "金": "きん", "角": "かく", "飛": "ひしゃ", "玉": "ぎょく"}
WORDS = [("ひねり飛車", "ひねりびしゃ"), ("浮き飛車", "うきびしゃ"), ("引き飛車", "ひきびしゃ"), ("居飛車", "いびしゃ"),
         ("振り飛車", "ふりびしゃ"), ("王手飛車", "おうてびしゃ"), ("相掛かり", "あいがかり"), ("悪形", "あくけい"),
         ("角頭", "かくとう"), ("位を取", "くらいを取"), ("垂れ歩", "たれふ"), ("継ぎ歩", "つぎふ"),
         ("３手詰", "さんてづめ"), ("銀冠", "ぎんかんむり"), ("勝勢", "しょうせい"), ("駒得", "こまどく"), ("５手詰", "ごてづめ"), ("▲", ""), ("△", ""), ("〜", "から")]

def yomi(text):
    for a, b in WORDS:
        text = text.replace(a, b)
    suf = lambda x: {"成": "なり", "打": "うち", "": ""}[x or ""]
    text = re.sub(r"同(歩|香|桂|銀|金|角|飛|玉)(成|打)?", lambda m: "どう" + PIECE[m.group(1)] + suf(m.group(2)), text)
    text = re.sub(r"([１-９])([一二三四五六七八九])(歩|香|桂|銀|金|角|飛|玉)?(成|打)?",
                  lambda m: DIG[m.group(1)] + DAN[m.group(2)] + (PIECE[m.group(3)] if m.group(3) else "") + suf(m.group(4)), text)
    return text

def tts(text, path):
    x, sr = pyopenjtalk.tts(yomi(text), speed=1.08)
    x = np.asarray(x, dtype=np.float64)
    x = x / max(1.0, np.abs(x).max() / 30000)
    x = np.concatenate([np.zeros(int(sr * 0.3)), x, np.zeros(int(sr * 0.7))]).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(x.tobytes())

# ======================================================================
# 動画の組み立て
# ======================================================================
def build(scenes, out, work):
    if os.path.exists(work):
        shutil.rmtree(work)
    os.makedirs(work)
    board = shogi.Board()
    history = []
    segs = []
    for i, sc in enumerate(scenes):
        if "card" in sc:
            img = sc["card"]
        else:
            if "start" in sc:   # 初期局面から指定手順を並べた局面にする
                board = shogi.Board(); history = []
                for usi in sc["start"]:
                    m = shogi.Move.from_usi(usi)
                    assert m in board.legal_moves, f"scene {i}: illegal start move {usi}"
                    board.push(m); history.append(m)
            if "reset" in sc:
                board = shogi.Board()
                for mv in history[:sc["reset"]]:
                    board.push(mv)
                history = history[:sc["reset"]]
            last = None
            for usi in sc["moves"]:
                m = shogi.Move.from_usi(usi)
                assert m in board.legal_moves, f"scene {i}: illegal move {usi}"
                board.push(m); history.append(m)
                last = shogi.SQUARE_NAMES[m.to_square]
            img = render(board, sc["chapter"], sc["title"], sc["caption"], hl=sc.get("hl", ()),
                         arrows=sc.get("arrows", ()), marks=sc.get("marks", ()), last=last, sub=sc.get("sub"),
                         ply=len(history) or None, ev=sc.get("ev"))
        ip, ap, vp = (os.path.join(work, f"s{i:02d}.{e}") for e in ("png", "wav", "mp4"))
        img.save(ip); tts(sc["narr"], ap)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30", "-i", ip, "-i", ap,
                        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "30",
                        "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-shortest", vp], check=True)
        segs.append(vp)
    lst = os.path.join(work, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{s}'\n" for s in segs)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out], check=True)
    print("wrote", out, len(segs), "scenes")

class Script:
    """台本を組み立てるヘルパー"""
    def __init__(self):
        self.scenes = []
    def card(self, img, narr):
        self.scenes.append(dict(card=img, narr=narr))
    def board(self, ch, title, cap, narr, moves=(), **kw):
        self.scenes.append(dict(chapter=ch, title=title, caption=cap, narr=narr, moves=list(moves), **kw))

