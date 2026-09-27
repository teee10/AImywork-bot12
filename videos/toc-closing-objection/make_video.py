"""ToC営業 クロージングの反論処理 解説動画 (約3分) を生成するスクリプト。

必要なもの:
  apt: open-jtalk open-jtalk-mecab-naist-jdic hts-voice-nitech-jp-atr503-m001 fonts-noto-cjk
  pip: pillow imageio-ffmpeg

使い方:
  python3 make_video.py            # -> toc_closing_objection.mp4
"""
import os
import subprocess
import wave
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
OUT = HERE / "toc_closing_objection.mp4"

W, H = 1920, 1080
FPS = 30
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

DIC = "/var/lib/mecab/dic/open-jtalk/naist-jdic"
VOICE = "/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice"
SPEED = float(os.environ.get("SPEED", "1.08"))

FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

# ---- colors ----
BG = (251, 248, 243)
NAVY = (31, 42, 68)
GRAY = (120, 128, 145)
LIGHT = (232, 228, 220)
ORANGE = (242, 140, 60)
TEAL = (38, 150, 190)
RED = (220, 70, 70)
GREEN = (60, 170, 110)
WHITE = (255, 255, 255)

_fonts = {}


def font(size, bold=True):
    key = (size, bold)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT_B if bold else FONT_R, size, index=0)
    return _fonts[key]


# ---------------------------------------------------------------------------
# 台本: (シーン種別, [ナレーション行...])
# 行ごとにスライドの表示要素が段階的に増える
# ---------------------------------------------------------------------------
SCENES = [
    ("title", [
        "営業を始めたばかりのあなたへ。",
        "今日は、クロージングで出てくる、お客様の反論への対応方法を、3分でわかりやすく解説します。",
    ]),
    ("concept", [
        "「高いですね」「ちょっと考えます」。お客様にこう言われると、断られたと感じてしまいますよね。",
        "でも実は、反論は、断りではありません。",
        "買いたい気持ちはあるけれど、まだ不安が残っている。そんなサインなんです。",
        "だから反論が出たら、むしろチャンスだと考えましょう。",
    ]),
    ("steps", [
        "反論処理には、基本の型があります。",
        "ステップ1、受け止める。まずは「そうですよね」と、お客様の気持ちに共感します。",
        "ステップ2、聞く。「具体的には、どのあたりが気になりますか？」と、不安の中身を質問します。",
        "ステップ3、答える。わかった不安に対して、解決策やメリットを伝えます。",
        "ステップ4、確認する。「これで不安は解消されましたか？」と確かめてから、次に進みます。",
    ]),
    ("obj1", [
        "では、よくある反論を3つ見ていきましょう。1つ目は、「高い」です。",
        "まずは、「たしかに、安い買い物ではないですよね」と受け止めます。",
        "そのうえで、「何と比べて、高いと感じましたか？」と聞いてみましょう。",
        "そして、1日あたりの金額に直したり、得られる効果を伝えたりして、価格以上の価値があることを示します。",
    ]),
    ("obj2", [
        "2つ目は、「ちょっと考えます」です。これは、不安がまだ言葉になっていない状態です。",
        "「もちろんです。ちなみに、どのあたりを一番お考えになりたいですか？」と、やさしく聞いてみましょう。",
        "本当の不安が見えれば、その場で解決できることも多いんです。",
    ]),
    ("obj3", [
        "3つ目は、「家族に相談します」です。",
        "「大切なことなので、ご相談は大事ですよね」と、まずは受け止めます。",
        "そのうえで、「ご家族は、どんな点を気にされそうですか？」と聞き、説明のポイントを一緒に整理しましょう。",
        "次にお話しする日程まで決めておくと、安心です。",
    ]),
    ("ng", [
        "反対に、やってはいけないことも覚えておきましょう。",
        "1つ目は、お客様の意見を否定すること。",
        "2つ目は、すぐに値引きをすること。",
        "3つ目は、しつこく押し売りすること。",
        "どれも、お客様の信頼を失ってしまいます。",
    ]),
    ("summary", [
        "最後に、まとめです。反論は、断りではなく、不安のサイン。",
        "受け止める、聞く、答える、確認する。この4ステップで、お客様の不安に寄り添いましょう。",
        "反論処理は、慣れれば必ず上達します。今日から、ぜひ実践してみてください。",
    ]),
]

# 字幕はそのまま、音声合成のときだけ読みを補正する
READINGS = [
    ("1つ目", "ひとつめ"), ("2つ目", "ふたつめ"), ("3つ目", "みっつめ"), ("3つ", "みっつ"),
    ("1日あたり", "いちにちあたり"), ("4ステップ", "よんステップ"), ("3分", "さんぷん"),
    ("ステップ1", "ステップいち"), ("ステップ2", "ステップに"),
    ("ステップ3", "ステップさん"), ("ステップ4", "ステップよん"),
]

SECTION_LABEL = {
    "title": "",
    "concept": "考え方",
    "steps": "基本の型",
    "obj1": "よくある反論 1",
    "obj2": "よくある反論 2",
    "obj3": "よくある反論 3",
    "ng": "NG行動",
    "summary": "まとめ",
}


# ---------------------------------------------------------------------------
# drawing helpers
# ---------------------------------------------------------------------------
def text_w(d, s, f):
    return d.textlength(s, font=f)


def center_text(d, cx, y, s, f, fill):
    d.text((cx - text_w(d, s, f) / 2, y), s, font=f, fill=fill)


def wrap(d, s, f, max_w):
    lines, cur = [], ""
    for ch in s:
        if text_w(d, cur + ch, f) > max_w and cur:
            # 句読点・閉じ括弧は行頭に来ないようにする
            if ch in "、。」）？！":
                cur += ch
                lines.append(cur)
                cur = ""
                continue
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def rbox(d, xy, r, fill, outline=None, width=0):
    d.rounded_rectangle(xy, r, fill=fill, outline=outline, width=width)


def person(d, cx, cy, color, s=1.0):
    """シンプルな人物アイコン"""
    hr = 34 * s
    d.ellipse((cx - hr, cy - 70 * s - hr, cx + hr, cy - 70 * s + hr), fill=color)
    d.rounded_rectangle((cx - 58 * s, cy - 20 * s, cx + 58 * s, cy + 70 * s), 40 * s, fill=color)


def bubble(d, xy, text, f, fill, fg, tail="left"):
    x0, y0, x1, y1 = xy
    rbox(d, xy, 28, fill)
    my = (y0 + y1) / 2
    if tail == "left":
        d.polygon([(x0 + 2, my - 18), (x0 - 30, my + 6), (x0 + 2, my + 22)], fill=fill)
    else:
        d.polygon([(x1 - 2, my - 18), (x1 + 30, my + 6), (x1 - 2, my + 22)], fill=fill)
    lines = wrap(d, text, f, x1 - x0 - 60)
    lh = f.size * 1.35
    ty = my - lh * len(lines) / 2
    for i, ln in enumerate(lines):
        d.text((x0 + 30, ty + i * lh), ln, font=f, fill=fg)


def cross(d, cx, cy, r, color, w=14):
    d.line((cx - r, cy - r, cx + r, cy + r), fill=color, width=w)
    d.line((cx - r, cy + r, cx + r, cy - r), fill=color, width=w)


def check(d, cx, cy, r, color, w=14):
    d.line((cx - r, cy, cx - r * 0.3, cy + r * 0.7, cx + r, cy - r * 0.7), fill=color, width=w, joint="curve")


def header(d, scene):
    label = SECTION_LABEL[scene]
    if not label:
        return
    f = font(34)
    tw = text_w(d, label, f)
    rbox(d, (80, 60, 80 + tw + 56, 120), 30, ORANGE)
    d.text((108, 64), label, font=f, fill=WHITE)
    d.text((W - 80 - text_w(d, "ToC営業 反論処理講座", font(28, False)), 72),
           "ToC営業 反論処理講座", font=font(28, False), fill=GRAY)


def subtitle(d, s):
    f = font(46)
    max_w = W - 360
    lines = wrap(d, s, f, max_w)
    if len(lines) > 1:
        # 行の長さをそろえて、1〜2文字だけの行ができないようにする
        target = text_w(d, s, f) / len(lines) + f.size
        balanced = wrap(d, s, f, min(max_w, target))
        if len(balanced) == len(lines):
            lines = balanced
    lh = 66
    box_h = lh * len(lines) + 40
    y0 = H - 60 - box_h
    rbox(d, (140, y0, W - 140, H - 60), 24, (31, 42, 68, 235))
    for i, ln in enumerate(lines):
        center_text(d, W / 2, y0 + 16 + i * lh, ln, f, WHITE)


def progress(d, frac):
    d.rectangle((0, H - 14, W, H), fill=LIGHT)
    d.rectangle((0, H - 14, int(W * frac), H), fill=ORANGE)


# ---------------------------------------------------------------------------
# scenes: draw(d, step) — step は現在のナレーション行番号
# ---------------------------------------------------------------------------
def draw_title(d, step):
    d.rectangle((0, 0, W, H), fill=NAVY)
    d.rectangle((0, 0, 24, H), fill=ORANGE)
    rbox(d, (160, 190, 560, 256), 33, ORANGE)
    d.text((196, 194), "営業初心者向け", font=font(38), fill=WHITE)
    d.text((160, 290), "ToC営業", font=font(72), fill=(200, 210, 230))
    d.text((160, 380), "クロージングの", font=font(110), fill=WHITE)
    d.text((160, 510), "反論処理", font=font(150), fill=ORANGE)
    d.text((160, 750), "〜 お客様の「不安」に寄り添う4ステップ 〜", font=font(48, False), fill=(220, 225, 235))
    person(d, 1560, 560, (70, 85, 120), 2.2)
    bubble(d, (1180, 200, 1480, 310), "考えます…", font(44), WHITE, NAVY, tail="right")


def draw_concept(d, step):
    header(d, "concept")
    # customer + quotes
    person(d, 300, 530, TEAL, 1.6)
    bubble(d, (480, 290, 1000, 390), "高いですね…", font(48), WHITE, NAVY)
    bubble(d, (480, 430, 1000, 530), "ちょっと考えます", font(48), WHITE, NAVY)
    d.rounded_rectangle((480, 290, 1000, 390), 28, outline=LIGHT, width=3)
    d.rounded_rectangle((480, 430, 1000, 530), 28, outline=LIGHT, width=3)
    if step >= 1:
        rbox(d, (1100, 230, 1800, 360), 24, WHITE, outline=LIGHT, width=3)
        center_text(d, 1450, 258, "反論  ＝  断り", font(60), GRAY)
        cross(d, 1450, 295, 70, RED, 16)
    if step >= 2:
        rbox(d, (1100, 400, 1800, 590), 24, ORANGE)
        center_text(d, 1450, 425, "反論  ＝", font(52), WHITE)
        center_text(d, 1450, 495, "不安のサイン", font(64), WHITE)
    if step >= 3:
        center_text(d, 1450, 625, "→ チャンス！", font(64), ORANGE)


STEP_ITEMS = [
    ("受け止める", "共感する", "「そうですよね」"),
    ("聞く", "不安を質問", "「どのあたりが？」"),
    ("答える", "解決策を伝える", "メリット・事例"),
    ("確認する", "解消を確かめる", "「解消されましたか？」"),
]


def draw_steps(d, step):
    header(d, "steps")
    center_text(d, W / 2, 150, "反論処理の基本  4ステップ", font(64), NAVY)
    bw, gap = 380, 50
    x = (W - (bw * 4 + gap * 3)) / 2
    for i, (name, sub, ex) in enumerate(STEP_ITEMS):
        active = step == i + 1
        shown = step >= i + 1 or step == 0
        x0 = x + i * (bw + gap)
        fill = ORANGE if active else (WHITE if shown else (240, 237, 231))
        fg = WHITE if active else (NAVY if shown else (200, 200, 205))
        rbox(d, (x0, 290, x0 + bw, 700), 28, fill, outline=None if active else LIGHT, width=3)
        d.ellipse((x0 + bw / 2 - 45, 320, x0 + bw / 2 + 45, 410), fill=WHITE if active else (NAVY if shown else LIGHT))
        center_text(d, x0 + bw / 2, 330, str(i + 1), font(56), ORANGE if active else WHITE)
        center_text(d, x0 + bw / 2, 440, name, font(56), fg)
        center_text(d, x0 + bw / 2, 530, sub, font(36, False), fg)
        if shown and step > 0:
            center_text(d, x0 + bw / 2, 610, ex, font(32), WHITE if active else GRAY)
        if i < 3:
            ax = x0 + bw + gap / 2
            d.polygon([(ax - 12, 475), (ax + 14, 495), (ax - 12, 515)], fill=ORANGE if shown else LIGHT)


def objection_scene(d, step, label, quote, rows, reveal):
    """rows: [(タグ, テキスト)], reveal: 各行を表示し始める step"""
    header(d, label)
    person(d, 250, 420, TEAL, 1.5)
    bubble(d, (420, 210, 1100, 330), quote, font(60), WHITE, NAVY)
    d.rounded_rectangle((420, 210, 1100, 330), 28, outline=LIGHT, width=3)
    d.text((170, 540), "お客様", font=font(34), fill=GRAY)
    person(d, 1680, 420, ORANGE, 1.5)
    d.text((1620, 540), "あなた", font=font(34), fill=GRAY)
    y = 400
    for (tag, text), st in zip(rows, reveal):
        if step < st:
            continue
        active = step == st
        rbox(d, (420, y, 1500, y + 120), 20, WHITE, outline=ORANGE if active else LIGHT, width=5 if active else 3)
        rbox(d, (440, y + 30, 620, y + 90), 30, ORANGE if active else NAVY)
        center_text(d, 530, y + 36, tag, font(32), WHITE)
        lines = wrap(d, text, font(36), 840)
        lh = 48
        ty = y + 60 - lh * len(lines) / 2
        for i, ln in enumerate(lines):
            d.text((650, ty + i * lh), ln, font=font(36), fill=NAVY)
        y += 140


def draw_obj1(d, step):
    objection_scene(d, step, "obj1", "高いですね…", [
        ("受け止める", "「たしかに、安い買い物ではないですよね」"),
        ("聞く", "「何と比べて、高いと感じましたか？」"),
        ("答える", "1日あたりの金額・得られる効果で価値を伝える"),
    ], [1, 2, 3])


def draw_obj2(d, step):
    objection_scene(d, step, "obj2", "ちょっと考えます", [
        ("ポイント", "不安がまだ言葉になっていない状態"),
        ("聞く", "「ちなみに、どのあたりを一番お考えになりたいですか？」"),
        ("答える", "本当の不安がわかれば、その場で解決できる"),
    ], [0, 1, 2])


def draw_obj3(d, step):
    objection_scene(d, step, "obj3", "家族に相談します", [
        ("受け止める", "「大切なことなので、ご相談は大事ですよね」"),
        ("聞く", "「ご家族は、どんな点を気にされそうですか？」"),
        ("次の約束", "説明のポイントを整理し、次回の日程を決める"),
    ], [1, 2, 3])


def draw_ng(d, step):
    header(d, "ng")
    center_text(d, W / 2, 150, "やってはいけない  3つのNG", font(64), NAVY)
    items = [("否定する", "「いや、それは違います」"),
             ("すぐ値引きする", "価値が下がって見える"),
             ("押し売りする", "しつこく迫ると逆効果")]
    bw, gap = 500, 60
    x = (W - (bw * 3 + gap * 2)) / 2
    for i, (name, sub) in enumerate(items):
        if step < i + 1:
            continue
        x0 = x + i * (bw + gap)
        active = step == i + 1
        rbox(d, (x0, 290, x0 + bw, 680), 28, WHITE, outline=RED if active else LIGHT, width=6 if active else 3)
        d.ellipse((x0 + bw / 2 - 70, 320, x0 + bw / 2 + 70, 460), fill=(253, 232, 232))
        cross(d, x0 + bw / 2, 390, 38, RED, 16)
        center_text(d, x0 + bw / 2, 490, name, font(52), NAVY)
        center_text(d, x0 + bw / 2, 580, sub, font(34, False), GRAY)
    if step >= 4:
        center_text(d, W / 2, 710, "→ どれも「信頼」を失う原因に", font(48), RED)


def draw_summary(d, step):
    header(d, "summary")
    rbox(d, (200, 170, W - 200, 330), 28, ORANGE)
    center_text(d, W / 2, 200, "反論 ＝ 断りではなく「不安のサイン」", font(64), WHITE)
    if step >= 1:
        bw, gap = 350, 30
        x = (W - (bw * 4 + gap * 3)) / 2
        for i, (name, _, _) in enumerate(STEP_ITEMS):
            x0 = x + i * (bw + gap)
            rbox(d, (x0, 380, x0 + bw, 530), 24, WHITE, outline=NAVY, width=4)
            check(d, x0 + 55, 455, 24, GREEN, 10)
            d.text((x0 + 95, 420), name, font=font(44), fill=NAVY)
    if step >= 2:
        center_text(d, W / 2, 590, "今日から実践してみよう！", font(72), NAVY)


DRAWERS = {
    "title": draw_title,
    "concept": draw_concept,
    "steps": draw_steps,
    "obj1": draw_obj1,
    "obj2": draw_obj2,
    "obj3": draw_obj3,
    "ng": draw_ng,
    "summary": draw_summary,
}


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------
def tts(text, path):
    for a, b in READINGS:
        text = text.replace(a, b)
    subprocess.run(
        ["open_jtalk", "-x", DIC, "-m", VOICE, "-r", str(SPEED), "-fm", "1", "-a", "0.55",
         "-jf", "1.2", "-ow", str(path)],
        input=text.encode("utf-8"), check=True)
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


def render(scene, step, line, frac, path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")
    DRAWERS[scene](d, step)
    subtitle(d, line)
    progress(d, frac)
    img.save(path)


def main():
    BUILD.mkdir(exist_ok=True)
    items = []
    n = 0
    for scene, lines in SCENES:
        for step, line in enumerate(lines):
            wav = BUILD / f"{n:03d}.wav"
            dur = tts(line, wav)
            # シーンの最後の行は少し長めに間を取る
            pause = 0.9 if step == len(lines) - 1 else 0.35
            items.append((scene, step, line, wav, dur + pause))
            n += 1
    total = sum(it[4] for it in items)
    print(f"total narration: {total:.1f}s")

    elapsed = 0.0
    segs = []
    for i, (scene, step, line, wav, dur) in enumerate(items):
        png = BUILD / f"{i:03d}.png"
        render(scene, step, line, (elapsed + dur) / total, png)
        seg = BUILD / f"{i:03d}.mp4"
        subprocess.run([
            FFMPEG, "-y", "-loglevel", "error",
            "-loop", "1", "-framerate", str(FPS), "-i", str(png),
            "-i", str(wav),
            "-af", f"apad,atrim=0:{dur:.3f}",
            "-t", f"{dur:.3f}",
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "1",
            str(seg)], check=True)
        segs.append(seg)
        elapsed += dur

    lst = BUILD / "list.txt"
    lst.write_text("".join(f"file '{s.name}'\n" for s in segs))
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(OUT)], check=True)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
