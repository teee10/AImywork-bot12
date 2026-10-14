"""ひねり飛車 解説動画ジェネレーター（初心者 → 将棋ウォーズ1級を目指す人向け）

必要: python-shogi, pyopenjtalk-plus, Pillow, numpy, ffmpeg
使い方: python3 make_video.py  -> hineri_bisha.mp4
"""
import os, re, subprocess, shutil, wave
import numpy as np
import shogi
import pyopenjtalk
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "_build")
OUT = os.path.join(HERE, "hineri_bisha.mp4")
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

def render(board, chapter, title, caption, hl=(), arrows=(), marks=(), last=None, sub=None, ply=None):
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
         ("３手詰", "さんてづめ"), ("５手詰", "ごてづめ"), ("▲", ""), ("△", ""), ("〜", "から")]

def yomi(text):
    for a, b in WORDS:
        text = text.replace(a, b)
    text = re.sub(r"同(歩|香|桂|銀|金|角|飛|玉)", lambda m: "どう" + PIECE[m.group(1)], text)
    text = re.sub(r"([１-９])([一-九])(歩|香|桂|銀|金|角|飛|玉)?",
                  lambda m: DIG[m.group(1)] + DAN[m.group(2)] + (PIECE[m.group(3)] if m.group(3) else ""), text)
    return text

def tts(text, path):
    x, sr = pyopenjtalk.tts(yomi(text), speed=1.08)
    x = np.asarray(x, dtype=np.float64)
    x = x / max(1.0, np.abs(x).max() / 30000)
    x = np.concatenate([np.zeros(int(sr * 0.3)), x, np.zeros(int(sr * 0.7))]).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(x.tobytes())

# ======================================================================
# 台本
# ======================================================================
RANK6 = [(f, B_HL) for f in ("3f", "4f", "5f", "6f")]

def script():
    S = []
    def C(img, narr):                       # カード
        S.append(dict(card=img, narr=narr))
    def B(ch, title, cap, narr, moves=(), **kw):   # 盤面
        S.append(dict(chapter=ch, title=title, caption=cap, narr=narr, moves=list(moves), **kw))

    C(card(["ひねり飛車 完全入門", "初心者から将棋ウォーズ１級を目指す", "基本定跡・囲い・手筋・後手の対策まで"], "※盤面はすべて先手（▲）側から見た図です"),
      "ひねり飛車、完全入門。この動画では、初心者の方が将棋ウォーズ１級を目指せるように、ひねり飛車の基本定跡、囲い方、攻めの手筋、そして後手の対策まで、順番にわかりやすく解説します。")
    C(card(["もくじ", "① ひねり飛車ってどんな戦法？", "② 基本定跡（縦歩取りからひねる）", "③ 玉の囲い方（坊主美濃と片美濃）",
            "④ 攻めの手筋（７筋の歩交換）", "⑤ 後手の対策 △８四飛", "⑥ よくある失敗と上達の練習法"], big=64),
      "内容はこの６つです。まず戦法の考え方、次に基本定跡、玉の囲い方、攻めの手筋、後手の対策、最後によくある失敗と練習法を紹介します。")

    ch = "第１章 ひねり飛車ってどんな戦法？"
    B(ch, "符号の読み方", "・タテの列＝「筋」右から１〜９\n・ヨコの行＝「段」上から一〜九\n・▲＝先手（手前） △＝後手（奥）\n\n例：青丸のマスは「７六」\n　　７筋の六段目",
      "はじめに、符号の読み方を確認しましょう。タテの列を筋といい、右から１、２、３と数えます。ヨコの行を段といい、上から一、二、三と数えます。たとえば青い丸のマスは、７筋の六段目なので、７六と読みます。三角の黒が先手、白が後手です。",
      marks=["7f"], hl=[("7a", B_HL), ("7b", B_HL), ("7c", B_HL), ("7d", B_HL), ("7e", B_HL), ("7g", B_HL), ("7h", B_HL), ("7i", B_HL)])
    B(ch, "居飛車と振り飛車", "・居飛車：飛車を２筋に置いたまま戦う\n・振り飛車：飛車を左に動かして戦う\n　玉は飛車と反対の右側に囲う\n\nひねり飛車は\n居飛車で始めて途中で振り飛車になる",
      "将棋の戦法は大きく２つ。飛車を最初の位置に置いたまま戦う居飛車と、飛車を左に動かして戦う振り飛車です。ひねり飛車は、居飛車で始めて、途中で飛車を横に動かして振り飛車に変身する、ちょっと変わった戦法です。",
      hl=[("2h", B_HL)], arrows=[("2h", "7h")])
    B(ch, "ひねり飛車を使える場面", "・お互い飛車先を突く「相掛かり」\n　▲２六歩 △８四歩 の出だし\n・後手が振り飛車なら使えない\n\n強み\n・飛車先の歩を交換して１歩持てる\n・美濃囲いで玉が堅い\n・攻めの形がわかりやすい",
      "ひねり飛車が使えるのは、お互いが飛車先の歩を突き合う、相掛かりという戦型になったときです。強みは３つ。飛車先の歩を交換して１歩を持てること。美濃囲いで玉を堅くできること。そして攻めの形がわかりやすいことです。初心者にもおすすめの戦法です。",
      sub="初手は ▲２六歩 から！")

    ch = "第２章 基本定跡"
    B(ch, "① 飛車先を伸ばし合う", "▲２六歩 △８四歩\n▲２五歩 △８五歩\n\nお互いに飛車先の歩を伸ばす\n「相掛かり」の出だし",
      "それでは基本定跡です。▲２六歩、△８四歩、▲２五歩、△８五歩。お互いに飛車先の歩を伸ばし合う、相掛かりの出だしです。",
      moves=["2g2f", "8c8d", "2f2e", "8d8e"], arrows=[("2g", "2e")])
    B(ch, "② まず角頭を守る", "▲７八金 △３二金\n\n８筋の歩がぶつかる前に\n金で角の頭（８七）を守る\n\nこれを忘れると\n△８六歩から角頭を攻められる",
      "次に▲７八金、△３二金。どちらも、角の頭を金で守る大切な一手です。先手がこれを忘れると、後手から８六歩と突かれて、角の頭を攻められてしまいます。",
      moves=["6i7h", "4a3b"], hl=[("8g", G_HL), ("7h", B_HL)], sub="７八金は必須の一手")
    B(ch, "③ 飛車先の歩交換", "▲２四歩 △同歩\n▲同飛 △２三歩\n\n歩を１枚手に入れた！\n後手は２三に歩を打って受ける",
      "先手は▲２四歩と突き捨てて、△同歩、▲同飛と、飛車先の歩を交換します。これで歩を１枚手に入れました。後手は△２三歩と打って、飛車の成り込みを防ぎます。",
      moves=["2e2d", "2c2d", "2h2d", "P*2c"], hl=[("2d", B_HL)])
    B(ch, "④ ▲２六飛 浮き飛車", "▲２六飛\n\n飛車を六段目に引く「浮き飛車」\n六段目（黄色）は横に空いている\n→ 飛車がいつでも横に動ける\n\nこれがひねり飛車の伏線！",
      "ここで▲２六飛と引きます。これを浮き飛車といいます。黄色のマスを見てください。六段目は横にずっと空いているので、飛車はいつでも横に動けます。これが、あとで飛車をひねるための伏線です。",
      moves=["2d2f"], hl=RANK6)
    B(ch, "⑤ 後手も飛車先交換", "△８六歩 ▲同歩 △同飛\n▲８七歩 △８二飛\n\n後手も歩を交換して\n飛車を８二まで引く「引き飛車」\n（△８四飛の対策は第５章で）",
      "後手も△８六歩、▲同歩、△同飛と、飛車先の歩を交換します。先手は▲８七歩と打って受け、後手は△８二飛と、元の位置まで飛車を引きました。これを引き飛車といいます。後手が８四に浮く対策は、第５章で解説します。",
      moves=["8e8f", "8g8f", "8b8f", "P*8g", "8f8b"])
    B(ch, "⑥ 端歩と△３四歩", "▲１六歩 △３四歩\n\n後手が角道を開けた\n→ ３四の歩が浮いている！\n　（どの駒にも守られていない）",
      "▲１六歩と端歩を突いて様子を見ます。後手は△３四歩と角道を開けました。ここで注目してほしいのが３四の歩です。この歩は、どの駒にも守られていません。",
      moves=["1g1f", "3c3d"], hl=[("3d", R_HL)])
    B(ch, "⑦ ▲３六飛 縦歩取りの狙い", "▲３六飛\n\n浮き飛車を３筋に動かして\n３四の歩を取りにいく\n＝「縦歩取り」\n\n次に▲３四飛と歩を取られると\n後手は大損",
      "そこで▲３六飛！浮き飛車を横に１つ動かして、３四の歩をタテから狙います。これを縦歩取りといいます。次に▲３四飛と歩を取られると、後手は大損です。",
      moves=["2f3f"], arrows=[("3f", "3d")], hl=[("3d", R_HL)])
    B(ch, "⑧ △３三金 金が悪形に", "△３三金\n\n歩を守るには△３三金が自然\nでも金が三段目に上がって\n形が崩れる（悪形）\n→ 後手は囲いが組みにくい\n\nこれが縦歩取りの一番の成果",
      "後手は、△３三金と金を上げて守るのが自然です。でも、金が三段目に浮いてしまい、形が崩れました。こういう形を悪形といいます。後手は玉をきれいに囲いにくくなりました。これが縦歩取りの一番の成果です。",
      moves=["3b3c"], hl=[("3c", R_HL)], marks=["3d"])
    B(ch, "⑨ 端歩を突き合う", "▲９六歩 △１四歩\n\n９筋の端歩を突いておくと\nあとで端攻めの選択肢が増える\n玉のにげ道にもなる",
      "▲９六歩、△１四歩と、お互いに端歩を突き合います。端歩を突いておくと、あとで端攻めを狙えるようになります。",
      moves=["9g9f", "1c1d"], hl=[("9f", B_HL)])
    B(ch, "⑩ 角道を開ける", "▲７六歩 △４二玉\n\n角の利きが３三の金まで通る\n後手は△３三金がいるので\n角交換しにくい",
      "▲７六歩と角道を開けます。先手の角は３三の金まで利いています。後手は玉を４二に上がりました。",
      moves=["7g7f", "5a4b"], hl=[("7g", B_HL), ("6f", B_HL), ("5e", B_HL), ("4d", B_HL)], marks=["3c"])
    B(ch, "⑪ ▲７五歩 飛車の行き先", "▲７五歩 △６二銀\n\n７筋の歩をもう一つ進めて\n７六のマスを空ける\n→ 飛車の行き先ができた",
      "さらに▲７五歩と、７筋の歩をもう一つ伸ばします。これで７六のマスが空いて、飛車の行き先ができました。",
      moves=["7f7e", "7a6b"], hl=[("7f", B_HL)])
    B(ch, "⑫ ▲７六飛 飛車をひねる！", "▲７六飛\n\n３筋にいた飛車を７筋へ！\n居飛車 → 振り飛車に変身\n\n先手は１歩持っていて\n後手は金が悪形\n先手が少し指しやすい",
      "そしていよいよ、▲７六飛！３筋にいた飛車を、一気に７筋へ移動させました。これが飛車をひねる手です。居飛車だった先手が、ここで振り飛車に変身しました。先手は１歩持っていて、後手の金は悪形。先手が指しやすい展開です。",
      moves=["3f7f"], arrows=[("3f", "7f")], sub="ここがひねり飛車の完成形！")
    B(ch, "⑬ ▲７七桂 石田流の攻撃形", "△７二金 ▲７七桂\n\n飛車・桂・歩が並んだ\n「石田流」とよく似た形\n７筋と８筋からの攻めが狙い",
      "後手は△７二金と７筋を守ります。先手は▲７七桂と桂馬を跳ねました。飛車、桂馬、歩が並んだこの形は、石田流とよく似た攻撃的な形です。",
      moves=["6a7b", "8i7g"], hl=[("7f", B_HL), ("7g", B_HL), ("7e", B_HL)])

    ch = "第３章 玉の囲い方"
    B(ch, "玉は右側へ", "△６四歩 ▲４八玉\n△９四歩 ▲３八玉\n△５四歩 ▲２八玉\n\n飛車が左に移ったので\n玉は反対の右側に囲う\n（振り飛車と同じ考え方）",
      "次は玉の囲い方です。飛車が左に移ったので、玉は反対の右側に囲います。▲４八玉、▲３八玉、▲２八玉と、３手かけて右に移動します。",
      moves=["6c6d", "5i4h", "9c9d", "4h3h", "5c5d", "3h2h"], arrows=[("5i", "2h")])
    B(ch, "▲３八銀 坊主美濃", "△３二玉 ▲３八銀\n\n美濃囲いの形になった\nでも２七に歩がない！\n＝「坊主美濃」\n玉の頭（玉頭）が弱いので注意",
      "▲３八銀と上がると、美濃囲いの形になります。ただし、２筋の歩はさっき交換したので、玉の頭、２七に歩がありません。この形を坊主美濃といいます。玉の頭が弱いので注意が必要です。",
      moves=["4b3b", "3i3h"], hl=[("2g", R_HL), ("2h", G_HL), ("3h", G_HL), ("4i", G_HL)])
    B(ch, "▲２七歩 片美濃囲いの完成", "△４二銀 ▲２七歩\n\n持ち歩を２七に打てば\n普通の「片美濃囲い」\n横からの攻めにとても強い\n\n（歩を温存して玉を３九に\n　置く指し方もある）",
      "そこで持ち歩を２七に打てば、普通の片美濃囲いになり、ぐっと堅くなります。美濃囲いは、横からの攻めにとても強い囲いです。歩を温存したいときは、玉を３九に置いたまま戦う指し方もあります。",
      moves=["3a4b", "P*2g"], hl=[("2g", B_HL), ("2h", G_HL), ("3h", G_HL), ("4i", G_HL)], sub="囲いが完成してから攻める！")

    ch = "第４章 攻めの手筋"
    B(ch, "▲７四歩 突き捨て", "△４四歩 ▲７四歩\n\n７筋の歩を突き捨てる\n△同歩なら▲同飛で\n飛車先が通る\n\n７四の地点に後手の駒は\n利いていないのがポイント",
      "ここからは攻めの手筋です。後手が△４四歩としたところで、▲７四歩と７筋の歩を突き捨てます。７四のマスには、後手の駒が１枚も利いていないのがポイントです。",
      moves=["4c4d", "7e7d"], hl=[("7d", B_HL)], arrows=[("7e", "7d")])
    B(ch, "▲同飛 飛車が前に出る", "△同歩 ▲同飛\n\n歩を１枚手に入れた\n飛車が四段目に出て\n後手陣に圧力をかける\n\n石田流・ひねり飛車の\n一番大事な手筋",
      "△同歩、▲同飛。歩を１枚手に入れて、飛車が四段目に出て、後手の陣地に圧力をかけています。この７筋の歩交換は、ひねり飛車や石田流で一番大事な手筋です。",
      moves=["7c7d", "7f7d"], hl=[("7d", B_HL)])
    B(ch, "▲７六飛 歩得して元の位置へ", "△７三歩 ▲７六飛\n\n後手は歩を打って受ける\n先手は飛車を７六に戻す\n\n結果：先手は歩を得して\n次の攻めの準備ができた",
      "後手は△７三歩と打って受けます。先手は▲７六飛と元の位置に戻ります。結果として、先手は歩を手に入れて、次の攻めの準備ができました。持ち歩は、継ぎ歩や垂れ歩などの手筋で大活躍します。",
      moves=["P*7c", "7d7f"], hl=[("7f", B_HL)])
    B(ch, "覚えたい攻めのアイデア", "・飛車交換は歓迎\n　美濃は横（飛車打ち）に強い\n・端攻め：▲９五歩で位を取る\n・継ぎ歩：歩を連続で打って\n　相手の歩を吊り上げる\n・垂れ歩：成れる一歩手前に打つ\n・桂跳ね：▲６五桂で中央を攻める",
      "他にも覚えておきたいアイデアを紹介します。まず、飛車交換は先手が歓迎です。美濃囲いは横からの飛車打ちに強いので、飛車を打ち合う展開になると先手が有利になりやすいです。ほかにも、▲９五歩と端の位を取る端攻め、歩を続けて打つ継ぎ歩、成れる一歩手前に歩を打つ垂れ歩、そして桂馬を跳ねて中央を攻める手などがあります。",
      hl=[("9e", B_HL), ("6e", B_HL), ("2h", G_HL), ("3h", G_HL), ("4i", G_HL), ("2g", G_HL)], arrows=[("9f", "9e"), ("7g", "6e")])

    ch = "第５章 後手の対策 △８四飛"
    B(ch, "△８四飛 浮き飛車で受ける", "（定跡⑤の局面から）\n▲８七歩 △８四飛\n\n後手も飛車を浮く\n四段目に飛車がいると\n３四の歩を横から守れる\n→ 縦歩取りが成立しない",
      "ここで後手の対策を見てみましょう。さきほどの定跡で、後手が△８二飛と引かずに、△８四飛と浮いた場合です。後手の飛車が四段目にいると、３四の歩を横から守ることができます。最近の将棋では、この△８四飛がよく指されます。",
      reset=15, moves=["8f8d", "1g1f", "3c3d"], hl=[(f, G_HL) for f in ("7d", "6d", "5d", "4d")] + [("3d", G_HL)], sub="▲３六飛としても歩は取れない")
    B(ch, "それでも飛車はひねれる", "▲７六歩 △６二銀\n▲７五歩 △４二玉 ▲７六飛\n\n縦歩取りは狙わず\nそのまま７筋に飛車を振る\n\n角交換の変化があるので\n角の打ち込みに注意",
      "その場合は、無理に３四の歩を狙わず、▲７六歩、▲７五歩、▲７六飛と、そのまま７筋に飛車を振ってしまえばOKです。ただし、角道が開いているので、角交換になる変化があります。角を打ち込まれるすきを作らないように注意しましょう。",
      moves=["7g7f", "7a6b", "7f7e", "5a4b", "2f7f"], arrows=[("2f", "7f")], hl=[("7g", R_HL), ("3c", R_HL)])

    ch = "第６章 よくある失敗と練習法"
    C(card(["よくある失敗", "① ▲７八金を忘れて角頭を攻められる", "② 坊主美濃のまま玉頭を攻められる", "③ 浮き飛車を角や桂で狙われる（王手飛車）",
            "④ 囲いが完成する前に攻めてしまう"], big=72),
      "よくある失敗を４つ紹介します。１つ目、▲７八金を忘れて角の頭を攻められる。２つ目、坊主美濃のまま戦って、玉の頭を攻められる。３つ目、浮き飛車を角や桂馬で狙われる。特に王手飛車には要注意です。４つ目、囲いが完成する前に攻めてしまう。この４つに気をつけるだけで、勝率はぐっと上がります。")
    C(card(["１級への練習法", "① この定跡を盤に５回並べて覚える", "② ウォーズの１０分切れ負けで実戦", "③ 負けた将棋は棋譜解析で振り返る",
            "④ ３手詰〜５手詰の詰将棋を毎日"], big=72),
      "最後に、１級を目指すための練習法です。１つ目、今日の定跡を盤に５回並べて手順を覚える。２つ目、将棋ウォーズの１０分切れ負けで、どんどん実戦で使う。３つ目、負けた将棋は棋譜解析で、どこで悪くなったかを振り返る。４つ目、３手詰から５手詰の詰将棋を毎日解いて、終盤力をきたえる。定跡と終盤の両方をきたえるのが、上達の近道です。")
    C(card(["まとめ", "① ▲７八金で角頭を守ってから飛車先交換", "② ▲２六飛の浮き飛車 → ▲３六飛で金を悪形に", "③ ▲７五歩〜▲７六飛で飛車をひねる",
            "④ 玉は右側へ、▲２七歩で片美濃", "⑤ ▲７四歩の歩交換で攻める"], "ご視聴ありがとうございました", big=72),
      "まとめです。▲７八金で角の頭を守ってから飛車先を交換。▲２六飛の浮き飛車から▲３六飛で、後手の金を悪形にする。▲７五歩から▲７六飛で、飛車をひねる。玉は右側に囲い、▲２七歩で片美濃。そして▲７四歩の歩交換で攻める。これがひねり飛車の基本です。ぜひ将棋ウォーズで試してみてください。ご視聴ありがとうございました。")
    return S

def main():
    if os.path.exists(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    board = shogi.Board()
    history = []
    segs = []
    for i, sc in enumerate(script()):
        if "card" in sc:
            img = sc["card"]
        else:
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
                         ply=len(history) or None)
        ip, ap, vp = (os.path.join(WORK, f"s{i:02d}.{e}") for e in ("png", "wav", "mp4"))
        img.save(ip); tts(sc["narr"], ap)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30", "-i", ip, "-i", ap,
                        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "30",
                        "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-shortest", vp], check=True)
        segs.append(vp)
    lst = os.path.join(WORK, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{s}'\n" for s in segs)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", OUT], check=True)
    print("wrote", OUT, len(segs), "scenes")

if __name__ == "__main__":
    main()
