"""ひねり飛車 解説動画ジェネレーター

必要: python-shogi, pyopenjtalk-plus, Pillow, numpy, ffmpeg
使い方: python3 make_video.py  -> hineri_bisha.mp4
"""
import os, subprocess, shutil, wave
import numpy as np
import shogi
import pyopenjtalk
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "_build")
OUT = os.path.join(HERE, "hineri_bisha.mp4")
FONT = "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"
W, H = 1280, 720
SR = 48000

KANJI = shogi.PIECE_JAPANESE_SYMBOLS
COLS = "９８７６５４３２１"
ROWS = "一二三四五六七八九"
NUM = "０１２３４５６７８９"

def font(sz):
    return ImageFont.truetype(FONT, sz)

# ---------- 盤面描画 ----------
BX, BY, CELL = 60, 60, 64          # 盤の左上と1マスの大きさ
BOARD_PX = CELL * 9

def sq_xy(sq):
    """python-shogi の square index -> 左上座標"""
    file_idx = sq % 9   # 0 = 9筋
    rank_idx = sq // 9  # 0 = 一段目
    return BX + file_idx * CELL, BY + rank_idx * CELL

def name_to_sq(name):  # '7f' -> index
    return shogi.SQUARE_NAMES.index(name)

def draw_piece(img, x, y, kanji, gote, promoted=False):
    s = CELL
    p = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(p)
    m = 5
    poly = [(s / 2, m), (s - m - 6, m + 10), (s - m, s - m), (m, s - m), (m + 6, m + 10)]
    d.polygon(poly, fill=(240, 205, 140), outline=(90, 60, 20))
    f = font(36)
    col = (180, 0, 0) if promoted else (20, 10, 0)
    tb = d.textbbox((0, 0), kanji, font=f)
    d.text(((s - (tb[2] - tb[0])) / 2 - tb[0], (s - (tb[3] - tb[1])) / 2 - tb[1] + 4), kanji, font=f, fill=col)
    if gote:
        p = p.rotate(180)
    img.alpha_composite(p, (x, y))

def hand_text(board, color):
    c = board.pieces_in_hand[color]
    if not c:
        return "なし"
    out = ""
    for pt in [7, 6, 5, 4, 3, 2, 1]:
        if c[pt]:
            out += KANJI[pt] + (NUM[c[pt]] if c[pt] > 1 else "")
    return out

def render(board, title, caption, hl=(), arrows=(), marks=(), last=None, sub=None):
    img = Image.new("RGBA", (W, H), (34, 40, 52, 255))
    d = ImageDraw.Draw(img)
    # 盤
    d.rectangle([BX - 14, BY - 14, BX + BOARD_PX + 14, BY + BOARD_PX + 14], fill=(205, 160, 90))
    d.rectangle([BX, BY, BX + BOARD_PX, BY + BOARD_PX], fill=(226, 184, 110))
    for name, color in hl:
        x, y = sq_xy(name_to_sq(name))
        d.rectangle([x, y, x + CELL, y + CELL], fill=color)
    if last:
        x, y = sq_xy(name_to_sq(last))
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
            x, y = sq_xy(sq)
            draw_piece(img, x, y, KANJI[pc.piece_type], pc.color == shogi.WHITE, pc.piece_type > 8)
    d = ImageDraw.Draw(img)
    for name, label in marks:
        x, y = sq_xy(name_to_sq(name))
        d.ellipse([x + 8, y + 8, x + CELL - 8, y + CELL - 8], outline=(0, 120, 255), width=5)
    for a, b in arrows:
        x1, y1 = sq_xy(name_to_sq(a)); x2, y2 = sq_xy(name_to_sq(b))
        x1 += CELL / 2; y1 += CELL / 2; x2 += CELL / 2; y2 += CELL / 2
        d.line([x1, y1, x2, y2], fill=(255, 60, 60), width=8)
        v = np.array([x2 - x1, y2 - y1]); v = v / np.linalg.norm(v)
        n = np.array([-v[1], v[0]])
        tip = np.array([x2, y2]); base = tip - v * 26
        d.polygon([tuple(tip), tuple(base + n * 15), tuple(base - n * 15)], fill=(255, 60, 60))
    # 持ち駒
    fh = font(22)
    d.text((BX, BY + BOARD_PX + 22), "▲先手 持駒: " + hand_text(board, shogi.BLACK), font=fh, fill=(255, 255, 255))
    d.text((BX + BOARD_PX + 70, 18), "△後手 持駒: " + hand_text(board, shogi.WHITE), font=fh, fill=(200, 200, 200))
    # 右側パネル
    px = BX + BOARD_PX + 70
    d.rounded_rectangle([px, 60, W - 30, H - 60], radius=18, fill=(250, 248, 240))
    d.text((px + 28, 86), title, font=font(38), fill=(150, 20, 20))
    d.line([px + 28, 142, W - 58, 142], fill=(150, 20, 20), width=3)
    y = 165
    for line in caption.split("\n"):
        d.text((px + 28, y), line, font=font(28), fill=(30, 30, 30))
        y += 46
    if sub:
        d.rounded_rectangle([px + 20, H - 160, W - 50, H - 80], radius=10, fill=(255, 230, 200))
        d.text((px + 40, H - 138), sub, font=font(30), fill=(150, 40, 0))
    return img.convert("RGB")

def title_card(lines, sub=""):
    img = Image.new("RGB", (W, H), (34, 40, 52))
    d = ImageDraw.Draw(img)
    y = 220
    for i, l in enumerate(lines):
        f = font(96 if i == 0 else 44)
        tb = d.textbbox((0, 0), l, font=f)
        d.text(((W - (tb[2] - tb[0])) / 2, y), l, font=f, fill=(255, 220, 120) if i == 0 else (240, 240, 240))
        y += 140 if i == 0 else 70
    if sub:
        f = font(28); tb = d.textbbox((0, 0), sub, font=f)
        d.text(((W - (tb[2] - tb[0])) / 2, H - 100), sub, font=f, fill=(170, 170, 170))
    return img

# ---------- 音声 ----------
def tts(text, path):
    x, sr = pyopenjtalk.tts(text, speed=1.05)
    x = np.asarray(x, dtype=np.float64)
    x = x / max(1.0, np.abs(x).max() / 30000)
    pad = np.zeros(int(sr * 0.5))
    x = np.concatenate([pad * 0, x, pad]).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(x.tobytes())

# ---------- 台本 ----------
# 各要素: (USI 指し手リスト, 描画オプション, ナレーション)
B_HL = (255, 240, 120)
G_HL = (170, 220, 255)
R_HL = (255, 170, 170)

def script():
    S = []
    S.append(("title", title_card(["ひねり飛車", "居飛車から振り飛車へ ―― 飛車を「ひねる」戦法", "はじめての戦法解説"], "※盤面は先手（▲）側から見た図です"),
              "ひねり飛車の解説です。この動画では、ひねり飛車がどんな戦法なのか、どういう手順で組むのか、そして狙いとコツを、盤面を使ってわかりやすく説明します。"))
    S.append(([], dict(title="ひねり飛車とは？", caption="・相掛かりから生まれる戦法\n・最初は居飛車（飛車は２筋）\n・途中で飛車を７筋へ横移動\n・飛車を「ひねって」振り飛車に\n・居飛車と振り飛車のいいとこ取り",
               hl=[("2h", R_HL), ("7h", B_HL)]),
              "ひねり飛車は、相掛かりという居飛車の戦型から生まれる作戦です。最初は飛車を２筋に置いたまま、飛車先の歩を交換します。そのあと、飛車を横にスライドさせて７筋に回します。居飛車から途中で振り飛車にひねるので、ひねり飛車と呼ばれます。"))
    S.append((["2g2f", "8c8d", "2f2e", "8d8e"], dict(title="① 飛車先を伸ばす", caption="▲２六歩 △８四歩\n▲２五歩 △８五歩\n\nお互いに飛車先の歩を\n伸ばし合う「相掛かり」の出だし", last="8e"),
              "まずはお互いに飛車先の歩を伸ばします。先手は２六歩から２五歩、後手は８四歩から８五歩。これが相掛かりの出だしです。"))
    S.append((["6i7h", "4a3b"], dict(title="② 金で守る", caption="▲７八金 △３二金\n\n飛車先交換の前に、\n角の頭を金で守っておく", last="3b", hl=[("7h", B_HL)]),
              "次に、先手は７八金、後手は３二金と、角の頭を金で守ります。飛車先を交換する前の大切な準備です。"))
    S.append((["2e2d", "2c2d", "2h2d", "P*2c"], dict(title="③ 飛車先の歩交換", caption="▲２四歩 △同歩\n▲同飛 △２三歩\n\n歩を１枚手に入れた！", last="2c", hl=[("2d", B_HL)]),
              "先手は２四歩と突き捨て、同歩、同飛車で飛車先の歩を交換します。歩を１枚手持ちにできました。後手は２三歩と打って受けます。"))
    S.append((["2d2f"], dict(title="④ 浮き飛車 ▲２六飛", caption="▲２六飛\n\n飛車を６段目に引く「浮き飛車」\nここがポイント！\n６段目は横に通っているので\n飛車がいつでも横に動ける", last="2f",
                               hl=[("3f", B_HL), ("4f", B_HL), ("5f", B_HL), ("6f", B_HL)]),
              "ここで先手は２六飛車と引きます。これを浮き飛車といいます。黄色のマスを見てください。６段目は横にずっと空いているので、飛車はいつでも横に動けます。これがひねり飛車の伏線です。"))
    S.append((["8e8f", "8g8f", "8b8f", "P*8g", "8f8b"], dict(title="⑤ 後手も飛車先交換", caption="△８六歩 ▲同歩 △同飛\n▲８七歩 △８二飛\n\n後手も歩を交換して\n飛車を８二に引き揚げる", last="8b"),
              "後手も８六歩、同歩、同飛車と飛車先の歩を交換します。先手は８七歩と打って受け、後手は８二飛車と元の位置に引き揚げました。"))
    S.append((["7g7f", "7a6b", "7f7e", "5a4a"], dict(title="⑥ ７筋の歩を伸ばす", caption="▲７六歩 △６二銀\n▲７五歩 △４一玉\n\n７筋の歩を２つ進めて\n飛車の通り道と行き先を作る", last="7e",
               hl=[("7f", B_HL)]),
              "ここからがひねり飛車らしい手順です。先手は７六歩、さらに７五歩と、７筋の歩を伸ばします。これで７六のマスが空き、飛車の行き先ができました。"))
    S.append((["2f7f"], dict(title="⑦ 飛車をひねる！", caption="▲７六飛\n\n２筋にいた飛車を７筋へ！\n居飛車 → 振り飛車に変身\n歩を持っているのが大きい", last="7f",
                               arrows=[("2f", "7f")]),
              "そしていよいよ、７六飛車！２筋にいた飛車を、一気に７筋へ横移動させました。これが飛車をひねる、という手です。居飛車だった先手が、ここで振り飛車に変身しました。しかも、すでに飛車先の歩を交換して１歩を持っているのが大きな得です。"))
    S.append((["6a7b", "8i7g"], dict(title="⑧ 桂馬を跳ねる", caption="△７二金 ▲７七桂\n\n石田流のような攻撃形\n飛車・桂・歩で７筋〜８筋を攻める", last="7g",
               hl=[("7f", B_HL), ("7g", B_HL), ("7e", B_HL)]),
              "後手は７二金と７筋を守ります。先手は７七桂と桂馬を跳ねました。飛車、桂馬、歩が並んだこの形は、石田流とよく似た攻撃的な形です。"))
    S.append((["6c6d", "5i4h", "6b6c", "4h3h", "9c9d", "3h2h", "1c1d", "3i3h"], dict(title="⑨ 玉を右に囲う", caption="▲４八玉 ▲３八玉 ▲２八玉\n▲３八銀\n\n飛車が左に移ったので\n玉は右側の美濃囲いへ\n（振り飛車と同じ考え方）", last="3h",
               hl=[("2h", R_HL), ("3h", B_HL), ("4i", B_HL)]),
              "飛車が左に移ったので、玉は反対の右側に囲います。４八玉、３八玉、２八玉と移動し、３八銀と上がれば、振り飛車でおなじみの、片美濃囲いの完成です。"))
    S.append(([], dict(title="ひねり飛車の狙い", caption="① ７筋・８筋からの攻め\n  ▲７四歩などで後手の弱点を突く\n② 手持ちの１歩を活かす\n③ 浮き飛車で横にも縦にも\n  柔軟に動ける", hl=[("7c", R_HL), ("7d", R_HL)], marks=[("7d", ""), ("8c", "")]),
              "ひねり飛車の狙いは３つです。１つ目は、７筋や８筋からの攻め。たとえば７四歩と突いて、後手の金銀を攻めます。２つ目は、手持ちの１歩を攻めに活かすこと。３つ目は、浮き飛車なので、縦にも横にも柔軟に動けることです。"))
    S.append(([], dict(title="注意点とコツ", caption="・２筋が薄くなる\n  → △２四歩などの反撃に注意\n・玉の囲いはしっかりと\n・飛車が浮いているので\n  角や桂で狙われないように", hl=[("2g", R_HL), ("2f", R_HL), ("2e", R_HL)]),
              "注意点もあります。飛車がいなくなった２筋は手薄になるので、後手からの２筋の反撃に気をつけましょう。また、浮き飛車は角や桂馬で狙われやすいので、飛車の位置には常に注意が必要です。玉の囲いをしっかり固めてから攻めるのがコツです。"))
    S.append(("title", title_card(["まとめ", "① 相掛かりで飛車先を交換して１歩得", "② ▲２六飛の浮き飛車から ▲７六飛とひねる", "③ 玉は右の美濃囲い、７筋から攻める"], "ご視聴ありがとうございました"),
              "まとめです。相掛かりで飛車先の歩を交換し、２六飛車の浮き飛車から、７六飛車とひねる。玉は右側の美濃囲いに囲って、７筋から攻める。これがひねり飛車の基本です。ぜひ実戦で試してみてください。ご視聴ありがとうございました。"))
    return S

def main():
    if os.path.exists(WORK):
        shutil.rmtree(WORK)
    os.makedirs(WORK)
    board = shogi.Board()
    segs = []
    for i, (moves, opt, narr) in enumerate(script()):
        if moves == "title":
            img = opt
        else:
            for mv in moves:
                m = shogi.Move.from_usi(mv)
                assert m in board.legal_moves, f"illegal move {mv}"
                board.push(m)
            img = render(board, **opt)
        ip = os.path.join(WORK, f"s{i:02d}.png"); ap = os.path.join(WORK, f"s{i:02d}.wav")
        vp = os.path.join(WORK, f"s{i:02d}.mp4")
        img.save(ip); tts(narr, ap)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30", "-i", ip, "-i", ap,
                        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", "30",
                        "-c:a", "aac", "-ar", "48000", "-b:a", "128k", "-shortest", vp], check=True)
        segs.append(vp)
    lst = os.path.join(WORK, "list.txt")
    with open(lst, "w") as f:
        for s in segs:
            f.write(f"file '{s}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", OUT], check=True)
    print("wrote", OUT)

if __name__ == "__main__":
    main()
