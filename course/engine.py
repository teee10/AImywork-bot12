#!/usr/bin/env python3
"""色分け学習教材PDFを生成する共通エンジン。

book の中身（タイトル・色・章立てテキスト）を持たず、`course/content*/*.txt`
に書かれた独自記法のテキストを読み込んで PDF を組版する処理だけを提供する。
各教材固有の設定（タイトル・配色・表紙文言など）は configure() に辞書で渡す。
実際のエントリポイントは course/build_pdf.py（AIフリーランス版）や
course/build_sns.py（SNS運用代行版）など、教材ごとの薄いスクリプト側にある。
"""

from __future__ import annotations

import glob
import os
import re
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT_DIR = os.path.join(HERE, "fonts")

# configure() が呼ばれるまでのプレースホルダ。実値は configure() で設定される。
CONTENT_DIR = os.path.join(HERE, "content")
OUT_PATH = os.path.join(ROOT, "manuals", "output.pdf")
TITLE = ""
SUBTITLE = ""

# ---------------------------------------------------------------- フォント

FONT = "NotoJP"
FONT_B = "NotoJP-Bold"


def register_fonts() -> None:
    reg = os.path.join(FONT_DIR, "NotoSansJP-Regular.ttf")
    bold = os.path.join(FONT_DIR, "NotoSansJP-Bold.ttf")
    if not (os.path.exists(reg) and os.path.exists(bold)):
        raise SystemExit(
            "フォントがありません。先に `python course/fonts/prepare_fonts.py` を実行してください。"
        )
    pdfmetrics.registerFont(TTFont(FONT, reg))
    pdfmetrics.registerFont(TTFont(FONT_B, bold))
    pdfmetrics.registerFontFamily(FONT, normal=FONT, bold=FONT_B, italic=FONT, boldItalic=FONT_B)


# ---------------------------------------------------------------- カラー

INK = colors.HexColor("#1F2433")
INK_SOFT = colors.HexColor("#4A5468")
INK_MUTE = colors.HexColor("#7A8499")
RULE = colors.HexColor("#E3E7EF")
PAPER = colors.HexColor("#FFFFFF")

# 部ごとのテーマカラー（configure() で教材ごとに差し替えられる）
PART_COLORS: dict[str, colors.Color] = {
    "base": colors.HexColor("#2B5CE6"),
}
DEFAULT_THEME = PART_COLORS["base"]
CFG: dict = {}

WARN_C = colors.HexColor("#DC2626")
TIP_C = colors.HexColor("#0F9D58")
CASE_C = colors.HexColor("#B45309")
PROMPT_C = colors.HexColor("#334155")


def tint(color: colors.Color, ratio: float) -> colors.Color:
    """color を白と混ぜた淡色を返す（ratio=0 で白、1 で原色）。"""
    return colors.Color(
        1 - (1 - color.red) * ratio,
        1 - (1 - color.green) * ratio,
        1 - (1 - color.blue) * ratio,
    )


def shade(color: colors.Color, ratio: float) -> colors.Color:
    """color を黒と混ぜた濃色を返す。"""
    return colors.Color(color.red * ratio, color.green * ratio, color.blue * ratio)


# ---------------------------------------------------------------- ページ寸法

PAGE_W, PAGE_H = A4
M_LEFT = 50
M_RIGHT = 50
M_TOP = 64
M_BOTTOM = 58
FRAME_W = PAGE_W - M_LEFT - M_RIGHT

# 現在位置トラッキング（ヘッダー／フッター描画用）
STATE = {"part": "", "chapter": "", "theme": DEFAULT_THEME, "page_offset": 0}


# ---------------------------------------------------------------- スタイル

def make_styles() -> dict[str, ParagraphStyle]:
    body = ParagraphStyle(
        "body", fontName=FONT, fontSize=10.2, leading=18.4, textColor=INK,
        alignment=TA_JUSTIFY, wordWrap="CJK", spaceAfter=7.5, firstLineIndent=0,
    )
    return {
        "body": body,
        "lead": ParagraphStyle("lead", parent=body, fontSize=10.6, leading=19.5,
                               textColor=INK_SOFT, spaceAfter=10),
        "h2": ParagraphStyle("h2", fontName=FONT_B, fontSize=14.2, leading=20,
                             textColor=INK, wordWrap="CJK", spaceAfter=0),
        "h3": ParagraphStyle("h3", fontName=FONT_B, fontSize=11.6, leading=18,
                             textColor=INK, wordWrap="CJK", spaceAfter=0),
        "li": ParagraphStyle("li", parent=body, spaceAfter=3.5, leading=17.6),
        "boxtitle": ParagraphStyle("boxtitle", fontName=FONT_B, fontSize=10.6, leading=15,
                                   textColor=INK, wordWrap="CJK", spaceAfter=0),
        "boxbody": ParagraphStyle("boxbody", parent=body, fontSize=9.8, leading=17.2,
                                  spaceAfter=5),
        "prompt": ParagraphStyle("prompt", fontName=FONT, fontSize=9.3, leading=15.6,
                                 textColor=colors.HexColor("#1E293B"), wordWrap="CJK",
                                 alignment=TA_LEFT, spaceAfter=1.5),
        "cell": ParagraphStyle("cell", fontName=FONT, fontSize=9.2, leading=14.6,
                               textColor=INK, wordWrap="CJK"),
        "cellhead": ParagraphStyle("cellhead", fontName=FONT_B, fontSize=9.2, leading=14.6,
                                   textColor=colors.white, wordWrap="CJK"),
        "toc_part": ParagraphStyle("toc_part", fontName=FONT_B, fontSize=11, leading=22,
                                   textColor=INK, wordWrap="CJK"),
        "toc_ch": ParagraphStyle("toc_ch", fontName=FONT, fontSize=9.8, leading=17.4,
                                 textColor=INK_SOFT, wordWrap="CJK"),
        "center": ParagraphStyle("center", parent=body, alignment=TA_CENTER),
    }


S = {}


# ---------------------------------------------------------------- インライン記法

def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(text: str, theme: colors.Color | None = None) -> str:
    """**太字** / ==マーカー== / `コード` を変換する。"""
    out = esc(text)
    accent = theme or STATE["theme"]
    out = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)
    out = re.sub(
        r"==(.+?)==",
        lambda m: f'<font backColor="#{tint(accent, 0.18).hexval()[2:]}"><b>{m.group(1)}</b></font>',
        out,
    )
    out = re.sub(
        r"`(.+?)`",
        lambda m: f'<font backColor="#EEF1F6" color="#B02A5B">{m.group(1)}</font>',
        out,
    )
    return out


def P(text: str, style: str = "body", theme: colors.Color | None = None) -> Paragraph:
    return Paragraph(inline(text, theme), S[style])


# ---------------------------------------------------------------- 基本フロアブル

class Rule(Flowable):
    """細い区切り線。"""

    def __init__(self, color=RULE, width=None, thickness=0.6, space_before=2, space_after=8):
        Flowable.__init__(self)
        self.color, self.thickness = color, thickness
        self._w = width
        self.sb, self.sa = space_before, space_after

    def wrap(self, aw, ah):
        self.width = self._w or aw
        self.height = self.thickness + self.sb + self.sa
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        c.setStrokeColor(self.color)
        c.setLineWidth(self.thickness)
        y = self.sa
        c.line(0, y, self.width, y)


class HeadingH2(Flowable):
    """左に太いカラーバーを持つ大見出し。"""

    BAR_W = 5.0
    PAD_L = 12
    SPACE_BEFORE = 13
    SPACE_AFTER = 7

    def __init__(self, text: str, theme: colors.Color):
        Flowable.__init__(self)
        self.text = text
        self.theme = theme
        self._para = Paragraph(inline(text, theme), S["h2"])

    def wrap(self, aw, ah):
        self.width = aw
        _, ph = self._para.wrap(aw - self.PAD_L - self.BAR_W, ah)
        self._ph = ph
        self.height = ph + self.SPACE_BEFORE + self.SPACE_AFTER + 6
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        top = self.height - self.SPACE_BEFORE
        block_h = self._ph + 4
        c.setFillColor(self.theme)
        c.roundRect(0, top - block_h, self.BAR_W, block_h, self.BAR_W / 2, stroke=0, fill=1)
        # 下側に淡いライン
        c.setStrokeColor(tint(self.theme, 0.28))
        c.setLineWidth(1.1)
        c.line(0, top - block_h - 6, self.width, top - block_h - 6)
        self._para.drawOn(c, self.BAR_W + self.PAD_L, top - block_h + 2)


class HeadingH3(Flowable):
    """カラードットつきの中見出し。"""

    SPACE_BEFORE = 9
    SPACE_AFTER = 4
    PAD_L = 14

    def __init__(self, text: str, theme: colors.Color):
        Flowable.__init__(self)
        self.text = text
        self.theme = theme
        self._para = Paragraph(inline(text, theme), S["h3"])

    def wrap(self, aw, ah):
        self.width = aw
        _, ph = self._para.wrap(aw - self.PAD_L, ah)
        self._ph = ph
        self.height = ph + self.SPACE_BEFORE + self.SPACE_AFTER
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        top = self.height - self.SPACE_BEFORE
        c.setFillColor(self.theme)
        c.circle(3.6, top - 8.6, 3.4, stroke=0, fill=1)
        c.setFillColor(tint(self.theme, 0.35))
        c.circle(3.6, top - 8.6, 6.4, stroke=0, fill=0)
        self._para.drawOn(c, self.PAD_L, top - self._ph)


class Bullet(Flowable):
    """・記号つきの箇条書き 1 行（マーカーはベクター描画）。"""

    PAD_L = 15

    def __init__(self, text: str, theme: colors.Color, number: int | None = None):
        Flowable.__init__(self)
        self.theme = theme
        self.number = number
        self._para = Paragraph(inline(text, theme), S["li"])

    def wrap(self, aw, ah):
        self.width = aw
        _, ph = self._para.wrap(aw - self.PAD_L, ah)
        self.height = ph + 3.5
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        top = self.height - 3.5
        cy = top - 8.2
        if self.number is None:
            c.setFillColor(self.theme)
            c.circle(5.0, cy, 2.5, stroke=0, fill=1)
        else:
            c.setFillColor(self.theme)
            c.circle(5.4, cy, 6.0, stroke=0, fill=1)
            c.setFillColor(colors.white)
            c.setFont(FONT_B, 7.4)
            c.drawCentredString(5.4, cy - 2.6, str(self.number))
        self._para.drawOn(c, self.PAD_L, 0)


class CheckItem(Flowable):
    """チェックボックス付き項目。"""

    PAD_L = 19

    def __init__(self, text: str, theme: colors.Color):
        Flowable.__init__(self)
        self.theme = theme
        self._para = Paragraph(inline(text, theme), S["li"])

    def wrap(self, aw, ah):
        self.width = aw
        _, ph = self._para.wrap(aw - self.PAD_L, ah)
        self.height = ph + 4
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        top = self.height - 4
        c.setStrokeColor(self.theme)
        c.setFillColor(colors.white)
        c.setLineWidth(1.1)
        c.roundRect(1.5, top - 13.2, 10.5, 10.5, 2.4, stroke=1, fill=1)
        self._para.drawOn(c, self.PAD_L, 0)


class Panel(Flowable):
    """タイトルチップ付きのカラーボックス。ページ跨ぎ分割に対応。"""

    PAD_X = 13
    PAD_TOP = 11
    PAD_BOTTOM = 11
    BAR_W = 3.6
    SPACE_BEFORE = 6
    SPACE_AFTER = 9

    def __init__(self, title, body_flowables, accent, bg=None, label=None,
                 dashed=False, continued=False, first=True, last=True):
        Flowable.__init__(self)
        self.title = title
        self.items = list(body_flowables)
        self.accent = accent
        self.bg = bg if bg is not None else tint(accent, 0.085)
        self.label = label
        self.dashed = dashed
        self.continued = continued
        self.first = first
        self.last = last
        self._chip_h = 0.0

    # -- 内部レイアウト -------------------------------------------------
    def _inner_width(self, aw):
        return aw - self.PAD_X * 2 - self.BAR_W

    def _chip_height(self):
        return 15.5 if self.title else 0.0

    def wrap(self, aw, ah):
        self.width = aw
        iw = self._inner_width(aw)
        h = self.PAD_TOP + self.PAD_BOTTOM
        if self.title:
            h += self._chip_height() + 7
        if self.continued:
            h += 12
        self._heights = []
        for f in self.items:
            fw, fh = f.wrap(iw, ah)
            sb = getattr(f, "spaceBefore", 0) or 0
            sa = getattr(f, "spaceAfter", 0) or 0
            self._heights.append(fh + sb + sa)
            h += fh + sb + sa
        self.height = h + (self.SPACE_BEFORE if self.first else 0) + (self.SPACE_AFTER if self.last else 0)
        return (self.width, self.height)

    def split(self, aw, ah):
        """内容が入り切らない場合、収まる分だけ前半として返す。"""
        self.wrap(aw, 0xFFFFFF)
        if self.height <= ah:
            return [self]
        iw = self._inner_width(aw)
        overhead = self.PAD_TOP + self.PAD_BOTTOM + (self.SPACE_BEFORE if self.first else 0)
        if self.title:
            overhead += self._chip_height() + 7
        if self.continued:
            overhead += 12
        budget = ah - overhead - 6
        if budget < 40:
            return []
        head, tail, used = [], [], 0.0
        for f, fh in zip(self.items, self._heights):
            if tail:
                tail.append(f)
                continue
            if used + fh <= budget:
                head.append(f)
                used += fh
            else:
                parts = f.split(iw, budget - used) if hasattr(f, "split") else []
                if parts and len(parts) == 2:
                    head.append(parts[0])
                    tail.append(parts[1])
                else:
                    tail.append(f)
        if not head or not tail:
            return [self] if not tail else []
        top = Panel(self.title, head, self.accent, self.bg, self.label, self.dashed,
                    continued=self.continued, first=self.first, last=False)
        bottom = Panel(None, tail, self.accent, self.bg, self.label, self.dashed,
                       continued=True, first=False, last=self.last)
        return [top, bottom]

    # -- 描画 -----------------------------------------------------------
    def draw(self):
        c = self.canv
        sb = self.SPACE_BEFORE if self.first else 0
        sa = self.SPACE_AFTER if self.last else 0
        box_h = self.height - sb - sa
        y0 = sa
        radius = 5.5
        c.saveState()
        c.setFillColor(self.bg)
        if self.first and self.last:
            c.roundRect(0, y0, self.width, box_h, radius, stroke=0, fill=1)
        else:
            c.rect(0, y0, self.width, box_h, stroke=0, fill=1)
        # 左のアクセントバー
        c.setFillColor(self.accent)
        c.rect(0, y0, self.BAR_W, box_h, stroke=0, fill=1)
        if self.dashed:
            c.setDash(2.4, 2.4)
            c.setStrokeColor(tint(self.accent, 0.45))
            c.setLineWidth(0.8)
            c.rect(self.BAR_W, y0, self.width - self.BAR_W, box_h, stroke=1, fill=0)
            c.setDash()
        c.restoreState()

        x = self.BAR_W + self.PAD_X
        top = y0 + box_h - self.PAD_TOP
        if self.title:
            chip_h = self._chip_height()
            tw = pdfmetrics.stringWidth(self.title, FONT_B, 8.6)
            c.setFillColor(self.accent)
            c.roundRect(x, top - chip_h, tw + 17, chip_h, chip_h / 2, stroke=0, fill=1)
            c.setFillColor(colors.white)
            c.setFont(FONT_B, 8.6)
            c.drawString(x + 8.5, top - chip_h + 4.6, self.title)
            top -= chip_h + 7
        if self.continued:
            c.setFillColor(shade(self.accent, 0.8))
            c.setFont(FONT, 7.8)
            c.drawString(x, top - 9, "（前ページからの続き）")
            top -= 12

        iw = self._inner_width(self.width)
        for f, fh in zip(self.items, self._heights):
            sa_f = getattr(f, "spaceAfter", 0) or 0
            sb_f = getattr(f, "spaceBefore", 0) or 0
            f.wrap(iw, fh)
            f.drawOn(c, x, top - fh + sa_f)
            top -= fh


class ChapterHeader(Flowable):
    """章扉（ページ上部のカラーバンド）。"""

    HEIGHT = 116

    def __init__(self, label: str, title: str, lead: str, theme: colors.Color, part_name: str):
        Flowable.__init__(self)
        self.label, self.title, self.lead = label, title, lead
        self.theme = theme
        self.part_name = part_name

    def wrap(self, aw, ah):
        self.width = aw
        self._title_p = Paragraph(
            f'<font name="{FONT_B}" size="19" color="#1F2433">{esc(self.title)}</font>',
            ParagraphStyle("ct", fontName=FONT_B, fontSize=19, leading=27, wordWrap="CJK"),
        )
        _, th = self._title_p.wrap(aw - 34, ah)
        self._lead_p = Paragraph(
            inline(self.lead, self.theme),
            ParagraphStyle("cl", fontName=FONT, fontSize=9.6, leading=16.4,
                           textColor=INK_SOFT, wordWrap="CJK", alignment=TA_JUSTIFY),
        )
        _, lh = self._lead_p.wrap(aw - 34, ah)
        self._th, self._lh = th, lh
        self.height = 40 + th + lh + 24
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        STATE["chapter"] = self.title
        STATE["part"] = self.part_name
        STATE["theme"] = self.theme
        h = self.height
        w = self.width
        # 背景（淡色）と左アクセント
        c.setFillColor(tint(self.theme, 0.075))
        c.roundRect(-6, 0, w + 12, h - 6, 7, stroke=0, fill=1)
        c.setFillColor(self.theme)
        c.roundRect(-6, 0, 6.5, h - 6, 3, stroke=0, fill=1)
        # ラベル
        c.setFillColor(self.theme)
        c.setFont(FONT_B, 9.2)
        c.drawString(17, h - 26, self.label)
        lw = pdfmetrics.stringWidth(self.label, FONT_B, 9.2)
        c.setStrokeColor(tint(self.theme, 0.4))
        c.setLineWidth(0.9)
        c.line(17 + lw + 10, h - 22.5, w - 14, h - 22.5)
        self._title_p.drawOn(c, 17, h - 40 - self._th)
        self._lead_p.drawOn(c, 17, h - 40 - self._th - self._lh - 8)


class PartDivider(Flowable):
    """部の扉ページ（全面カラー）。"""

    def __init__(self, label: str, title: str, lead: str, theme: colors.Color, chapters: list[str]):
        Flowable.__init__(self)
        self.label, self.title, self.lead = label, title, lead
        self.theme = theme
        self.chapters = chapters

    def wrap(self, aw, ah):
        self.width, self.height = aw, 10
        return (aw, 10)

    def draw(self):
        c = self.canv
        STATE["part"] = self.title
        STATE["theme"] = self.theme
        STATE["chapter"] = ""
        c.saveState()
        # ページ全面を塗る（フレーム座標系からページ座標系へ戻す）
        c.translate(-M_LEFT, -(PAGE_H - M_TOP - self.height) + 0)
        c.setFillColor(self.theme)
        c.rect(0, -200, PAGE_W, PAGE_H + 400, stroke=0, fill=1)
        # 装飾の円
        c.setFillColor(shade(self.theme, 0.86))
        c.circle(PAGE_W - 60, PAGE_H * 0.12, 150, stroke=0, fill=1)
        c.setFillColor(tint(self.theme, 0.86))
        c.circle(70, PAGE_H * 0.9, 90, stroke=0, fill=1)

        base_y = PAGE_H * 0.62
        c.setFillColor(colors.white)
        c.setFont(FONT_B, 12)
        c.drawString(M_LEFT + 4, base_y + 92, self.label)
        c.setStrokeColor(colors.Color(1, 1, 1, alpha=0.55))
        c.setLineWidth(2)
        c.line(M_LEFT + 4, base_y + 82, M_LEFT + 74, base_y + 82)

        c.setFont(FONT_B, 30)
        c.drawString(M_LEFT + 2, base_y + 34, self.title)

        lead_style = ParagraphStyle("pl", fontName=FONT, fontSize=10.6, leading=19,
                                    textColor=colors.white, wordWrap="CJK")
        p = Paragraph(esc(self.lead), lead_style)
        pw, ph = p.wrap(PAGE_W - 2 * M_LEFT - 40, 400)
        p.drawOn(c, M_LEFT + 3, base_y - ph + 16)

        # 収録章リスト
        y = base_y - ph - 24
        c.setFillColor(colors.Color(1, 1, 1, alpha=0.16))
        box_h = 26 + 20 * len(self.chapters)
        c.roundRect(M_LEFT, y - box_h + 12, PAGE_W - 2 * M_LEFT, box_h, 8, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont(FONT_B, 9)
        c.drawString(M_LEFT + 18, y - 6, "この部で学ぶこと")
        c.setFont(FONT, 10)
        for i, ch in enumerate(self.chapters):
            c.drawString(M_LEFT + 18, y - 28 - i * 20, ch)
        c.restoreState()


class CoverPage(Flowable):
    """表紙。内容は CFG["cover"] から供給される。"""

    def wrap(self, aw, ah):
        self.width, self.height = aw, 10
        return (aw, 10)

    def draw(self):
        cover = CFG["cover"]
        c = self.canv
        c.saveState()
        c.translate(-M_LEFT, -(PAGE_H - M_TOP - self.height))
        navy = colors.HexColor("#131A2E")
        c.setFillColor(navy)
        c.rect(0, -200, PAGE_W, PAGE_H + 400, stroke=0, fill=1)

        # 上部のカラーストライプ
        stripe_colors = [PART_COLORS[k] for k in cover["stripe_keys"]]
        sw = PAGE_W / len(stripe_colors)
        for i, col in enumerate(stripe_colors):
            c.setFillColor(col)
            c.rect(i * sw, PAGE_H - 13, sw, 13, stroke=0, fill=1)

        # 背景の装飾
        c.setFillColor(colors.HexColor("#1B2440"))
        c.circle(PAGE_W - 40, 150, 190, stroke=0, fill=1)
        c.setFillColor(colors.HexColor("#1A213F"))
        c.circle(30, PAGE_H - 220, 120, stroke=0, fill=1)

        c.setFillColor(colors.HexColor("#8FA3C8"))
        c.setFont(FONT_B, 10.5)
        c.drawString(M_LEFT, PAGE_H - 96, cover["kicker"])
        c.setStrokeColor(stripe_colors[0])
        c.setLineWidth(3)
        c.line(M_LEFT, PAGE_H - 112, M_LEFT + 58, PAGE_H - 112)

        c.setFillColor(colors.white)
        c.setFont(FONT_B, 33)
        title_lines = cover["title_lines"]
        for i, line in enumerate(title_lines):
            c.drawString(M_LEFT, PAGE_H - 190 - i * 46, line)
        title_bottom = PAGE_H - 190 - (len(title_lines) - 1) * 46

        c.setFillColor(colors.HexColor("#C6D2E8"))
        c.setFont(FONT, 12)
        c.drawString(M_LEFT, title_bottom - 38, cover["tagline"])
        c.setFont(FONT, 10.5)
        c.setFillColor(colors.HexColor("#8FA3C8"))
        c.drawString(M_LEFT, title_bottom - 60, cover["tagline2"])

        # ジャンル・プラットフォームのバッジ
        badges = [(en, ja, PART_COLORS[key]) for en, ja, key in cover["badges"]]
        n = len(badges)
        bw = (PAGE_W - 2 * M_LEFT - 12 * (n - 1)) / n
        by = PAGE_H - 420
        for i, (en, ja, col) in enumerate(badges):
            x = M_LEFT + i * (bw + 12)
            c.setFillColor(colors.HexColor("#1C2440"))
            c.roundRect(x, by, bw, 76, 8, stroke=0, fill=1)
            c.setFillColor(col)
            c.roundRect(x, by + 66, bw, 10, 5, stroke=0, fill=1)
            c.rect(x, by + 66, bw, 6, stroke=0, fill=1)
            c.setFillColor(col)
            c.setFont(FONT_B, 7.6)
            c.drawString(x + 12, by + 44, en)
            c.setFillColor(colors.white)
            c.setFont(FONT_B, 11.5)
            c.drawString(x + 12, by + 22, ja)

        # 下部の情報
        c.setStrokeColor(colors.HexColor("#2C3A5C"))
        c.setLineWidth(1)
        c.line(M_LEFT, 150, PAGE_W - M_RIGHT, 150)
        c.setFillColor(colors.HexColor("#8FA3C8"))
        c.setFont(FONT, 9.6)
        c.drawString(M_LEFT, 128, cover["structure_note"])
        c.setFont(FONT_B, 10)
        c.setFillColor(colors.white)
        c.drawString(M_LEFT, 104, CFG.get("org_line", "マイワーク AIスクール"))
        c.restoreState()


class TocEntry(Flowable):
    """目次の1行（リーダー線つき）。"""

    def __init__(self, text: str, page: str, level: int, theme: colors.Color):
        Flowable.__init__(self)
        self.text, self.page, self.level, self.theme = text, page, level, theme

    def wrap(self, aw, ah):
        self.width = aw
        self.height = 25 if self.level == 0 else 17.5
        return (self.width, self.height)

    def draw(self):
        c = self.canv
        indent = 0 if self.level == 0 else 18
        if self.level == 0:
            c.setFillColor(self.theme)
            c.roundRect(0, 4, 4, 13, 2, stroke=0, fill=1)
            c.setFillColor(INK)
            c.setFont(FONT_B, 11.4)
            c.drawString(11, 7, self.text)
            c.setFillColor(self.theme)
            c.setFont(FONT_B, 10)
            c.drawRightString(self.width, 7, self.page)
        else:
            c.setFillColor(INK_SOFT)
            c.setFont(FONT, 9.8)
            c.drawString(indent, 4, self.text)
            tw = pdfmetrics.stringWidth(self.text, FONT, 9.8)
            pw = pdfmetrics.stringWidth(self.page, FONT, 9.4)
            c.setStrokeColor(colors.HexColor("#D8DEE9"))
            c.setLineWidth(0.5)
            c.setDash(0.8, 2.6)
            c.line(indent + tw + 6, 7, self.width - pw - 6, 7)
            c.setDash()
            c.setFillColor(INK_SOFT)
            c.setFont(FONT, 9.4)
            c.drawRightString(self.width, 4, self.page)


class Anchor(Flowable):
    """ページ番号記録用の透明マーカー。"""

    def __init__(self, key: str, registry: dict, level: int = 1, title: str = ""):
        Flowable.__init__(self)
        self.key, self.registry, self.level, self.title = key, registry, level, title

    def wrap(self, aw, ah):
        self.width, self.height = aw, 0
        return (aw, 0)

    def draw(self):
        page_no = self.canv.getPageNumber() - STATE["page_offset"]
        self.registry[self.key] = page_no
        if self.title:
            bm = f"bm{abs(hash(self.key)) % 10**9}"
            self.canv.bookmarkPage(bm)
            self.canv.addOutlineEntry(self.title, bm, level=self.level, closed=(self.level == 0))


# ---------------------------------------------------------------- 表・ステップ

def build_table(rows: list[list[str]], theme: colors.Color, widths=None) -> Table:
    head = [Paragraph(inline(cell, theme), S["cellhead"]) for cell in rows[0]]
    body = [[Paragraph(inline(cell, theme), S["cell"]) for cell in r] for r in rows[1:]]
    data = [head] + body
    ncols = len(rows[0])
    if widths is None:
        first = FRAME_W * 0.26 if ncols > 2 else FRAME_W * 0.3
        rest = (FRAME_W - first) / (ncols - 1) if ncols > 1 else FRAME_W
        widths = [first] + [rest] * (ncols - 1)
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), theme),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#E1E6F0")),
        ("BOX", (0, 0), (-1, -1), 0.6, tint(theme, 0.35)),
        ("LINEAFTER", (0, 0), (-2, -1), 0.4, colors.HexColor("#E8ECF4")),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F7F9FC")))
    t.setStyle(TableStyle(style))
    return t


def build_steps(items: list[str], theme: colors.Color) -> Table:
    rows = []
    for i, item in enumerate(items, 1):
        title, _, desc = item.partition("::")
        chip = StepChip(i, theme)
        text = f"<b>{esc(title)}</b>"
        if desc:
            text += f'<br/><font size="9.2" color="#4A5468">{inline(desc, theme)}</font>'
        rows.append([chip, Paragraph(text, ParagraphStyle(
            "st", fontName=FONT, fontSize=10.1, leading=17.2, textColor=INK, wordWrap="CJK"))])
    t = Table(rows, colWidths=[34, FRAME_W - 34], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


class StepChip(Flowable):
    def __init__(self, num: int, theme: colors.Color):
        Flowable.__init__(self)
        self.num, self.theme = num, theme
        self.width, self.height = 24, 24

    def wrap(self, aw, ah):
        return (24, 24)

    def draw(self):
        c = self.canv
        c.setFillColor(self.theme)
        c.roundRect(0, 0, 23, 23, 6, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont(FONT_B, 11)
        c.drawCentredString(11.5, 6.6, str(self.num))


# ---------------------------------------------------------------- パーサ

class Doc:
    def __init__(self):
        self.story = []
        self.parts = []          # [(label, title, theme_key, [chapter_titles])]
        self.toc = []            # [(level, text, key, theme)]
        self.pages = {}          # key -> page number
        self.theme = DEFAULT_THEME
        self.part_name = ""
        self.body_chars = 0

    def add(self, f):
        self.story.append(f)


MULTILINE = {"ul", "ol", "check", "summary", "goal", "steps", "table",
             "point", "warn", "tip", "case", "prompt", "work"}


def split_args(line: str) -> list[str]:
    return [a.strip() for a in line.split("|")]


def parse_files(paths: list[str], pages: dict) -> Doc:
    doc = Doc()
    pending = []  # panel の中身を集める用

    def flush_panel(kind, title, buf, theme):
        accent = {"point": theme, "warn": WARN_C, "tip": TIP_C,
                  "case": CASE_C, "prompt": PROMPT_C, "check": theme,
                  "summary": theme, "work": CASE_C}[kind]
        bg = {"prompt": colors.HexColor("#F4F6FA")}.get(kind)
        return Panel(title, buf, accent, bg=bg, dashed=(kind == "prompt"))

    for path in paths:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().split("\n")

        i = 0
        while i < len(lines):
            raw = lines[i].rstrip()
            i += 1
            if not raw.strip() or raw.strip().startswith("//"):
                continue
            if not raw.startswith("@"):
                doc.body_chars += len(raw)
                doc.add(P(raw))
                continue

            directive, _, rest = raw[1:].partition("|")
            directive = directive.strip()
            args = split_args(rest) if rest else []
            # リスト系ディレクティブは、空行または次のディレクティブまでの行を
            # 追加の要素として取り込む（1行1項目で書けるようにするため）
            if directive in MULTILINE:
                while i < len(lines):
                    nxt = lines[i].rstrip()
                    if not nxt.strip() or nxt.startswith("@"):
                        break
                    args.append(nxt.strip())
                    doc.body_chars += len(nxt)
                    i += 1
            doc.body_chars += len(rest)
            theme = doc.theme

            if directive == "part":
                label, title, lead, theme_key = args[0], args[1], args[2], args[3]
                doc.theme = theme = PART_COLORS[theme_key]
                doc.part_name = title
                chapters = [a for a in args[4:] if a]
                doc.parts.append((label, title, theme_key, chapters))
                key = f"part:{title}"
                doc.toc.append((0, f"{label}　{title}", key, theme))
                doc.add(NextPageTemplate("part"))
                doc.add(PageBreak())
                doc.add(PartDivider(label, title, lead, theme, chapters))
                doc.add(Anchor(key, pages, level=0, title=f"{label} {title}"))
                doc.add(NextPageTemplate("body"))
                doc.add(PageBreak())

            elif directive == "chapter":
                label, title, lead = args[0], args[1], args[2]
                key = f"ch:{label}"
                doc.toc.append((1, f"{label}　{title}", key, theme))
                doc.add(ChapterHeader(label, title, lead, theme, doc.part_name))
                doc.add(Anchor(key, pages, level=1, title=f"{label} {title}"))
                doc.add(Spacer(1, 10))

            elif directive == "goal":
                items = [Bullet(a, theme) for a in args if a]
                doc.add(Panel("この章のゴール", items, theme))

            elif directive == "h2":
                doc.add(HeadingH2(args[0], theme))
            elif directive == "h3":
                doc.add(HeadingH3(args[0], theme))
            elif directive == "ul":
                for a in args:
                    if a:
                        doc.add(Bullet(a, theme))
                doc.add(Spacer(1, 4))
            elif directive == "ol":
                for n, a in enumerate([x for x in args if x], 1):
                    doc.add(Bullet(a, theme, number=n))
                doc.add(Spacer(1, 4))
            elif directive == "steps":
                doc.add(Spacer(1, 2))
                doc.add(build_steps([a for a in args if a], theme))
                doc.add(Spacer(1, 4))
            elif directive == "table":
                rows = [[c.strip() for c in a.split(";")] for a in args if a]
                doc.add(Spacer(1, 3))
                doc.add(build_table(rows, theme))
                doc.add(Spacer(1, 10))
            elif directive in ("point", "warn", "tip", "case", "work"):
                title = args[0]
                buf = [P(a, "boxbody", theme) for a in args[1:] if a]
                doc.add(flush_panel(directive, title, buf, theme))
            elif directive == "prompt":
                title = args[0] or "プロンプト例"
                buf = [P(a, "prompt", theme) for a in args[1:] if a]
                doc.add(flush_panel("prompt", title, buf, theme))
            elif directive == "check":
                title = args[0]
                buf = [CheckItem(a, theme) for a in args[1:] if a]
                doc.add(flush_panel("check", title, buf, theme))
            elif directive == "summary":
                buf = [Bullet(a, theme, number=n) for n, a in enumerate([x for x in args if x], 1)]
                doc.add(Spacer(1, 4))
                doc.add(flush_panel("summary", "この章のまとめ", buf, theme))
            elif directive == "rule":
                doc.add(Rule(tint(theme, 0.35)))
            elif directive == "pagebreak":
                doc.add(PageBreak())
            elif directive == "space":
                doc.add(Spacer(1, float(args[0]) if args else 10))
            else:
                raise SystemExit(f"未知のディレクティブ: @{directive} ({path})")

    return doc


# ---------------------------------------------------------------- 前付け

def front_matter(doc: Doc, pages: dict) -> list:
    base = PART_COLORS[CFG["default_theme_key"]]
    story = [CoverPage(), NextPageTemplate("plain"), PageBreak()]

    # はじめに
    story.append(Paragraph(
        '<font name="%s" size="20" color="#1F2433">本書の使い方</font>' % FONT_B,
        ParagraphStyle("fh", fontName=FONT_B, fontSize=20, leading=30, wordWrap="CJK")))
    story.append(Rule(base, thickness=2.4, space_after=14))
    for t in CFG["intro_paragraphs"]:
        story.append(P(t))
    story.append(Spacer(1, 6))

    story.append(HeadingH2("本書の構成", base))
    rows = [["部", "内容", "身につくこと"]] + CFG["structure_rows"]
    wr = CFG.get("structure_widths_ratio", [0.22, 0.45, 0.33])
    story.append(build_table(rows, base, widths=[FRAME_W * r for r in wr]))
    story.append(Spacer(1, 8))

    story.append(HeadingH2("紙面のルール", base))
    story.append(P("本文中では、内容の性質に応じて次の5種類のボックスを使い分けています。色と見出しで役割がわかるようになっています。"))
    story.append(Panel("POINT", [P("その節でいちばん大事な考え方・判断基準をまとめています。時間がないときはここだけ拾い読みしても構いません。", "boxbody")], base))
    story.append(Panel("注意", [P("知らないと事故につながる項目です。権利関係・単価・納品トラブルなど、実務で損をしないための警告が入ります。", "boxbody")], WARN_C))
    story.append(Panel("コツ", [P("作業を速くする小ワザ、品質を一段上げるための工夫です。すぐ試せるものを厳選しています。", "boxbody")], TIP_C))
    story.append(Panel("実例", [P("実際の案件を想定したケーススタディです。金額・工数・やりとりの具体例を示します。", "boxbody")], CASE_C))
    story.append(Panel("プロンプト例", [P("そのままコピーして使える指示文のテンプレートです。〈　〉の部分を自分の案件に置き換えて使ってください。", "prompt")], PROMPT_C, bg=colors.HexColor("#F4F6FA"), dashed=True))

    story.append(Spacer(1, 4))
    study_theme = PART_COLORS[CFG.get("study_plan_theme_key", CFG["default_theme_key"])]
    story.append(Panel("学習の進め方",
                       [P(t, "boxbody") for t in CFG["study_plan"]],
                       study_theme))

    story.append(PageBreak())

    # 目次
    story.append(Paragraph(
        '<font name="%s" size="20" color="#1F2433">目次</font>' % FONT_B,
        ParagraphStyle("fh2", fontName=FONT_B, fontSize=20, leading=30, wordWrap="CJK")))
    story.append(Rule(base, thickness=2.4, space_after=12))
    for level, text, key, theme in doc.toc:
        page = pages.get(key)
        story.append(TocEntry(text, str(page) if page else "", level, theme))
    story.append(NextPageTemplate("body"))
    story.append(PageBreak())
    return story


# ---------------------------------------------------------------- ドキュメント

def draw_body_furniture(canvas, doc):
    """本文ページのヘッダー・フッター（ページ描画後に呼ばれる）。"""
    theme = STATE["theme"]
    page_no = canvas.getPageNumber() - STATE["page_offset"]
    canvas.saveState()
    # ヘッダー
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.6)
    canvas.line(M_LEFT, PAGE_H - 44, PAGE_W - M_RIGHT, PAGE_H - 44)
    canvas.setFillColor(theme)
    canvas.rect(M_LEFT, PAGE_H - 44.6, 46, 1.8, stroke=0, fill=1)
    canvas.setFont(FONT, 8.2)
    canvas.setFillColor(INK_MUTE)
    if STATE["part"]:
        canvas.drawString(M_LEFT, PAGE_H - 38, STATE["part"])
    if STATE["chapter"]:
        canvas.drawRightString(PAGE_W - M_RIGHT, PAGE_H - 38, STATE["chapter"])
    # フッター
    canvas.setFont(FONT, 8)
    canvas.setFillColor(INK_MUTE)
    canvas.drawString(M_LEFT, 32, TITLE)
    canvas.setFillColor(theme)
    canvas.roundRect(PAGE_W - M_RIGHT - 30, 26, 30, 15, 7.5, stroke=0, fill=1)
    canvas.setFillColor(colors.white)
    canvas.setFont(FONT_B, 8.6)
    canvas.drawCentredString(PAGE_W - M_RIGHT - 15, 31, str(page_no))
    canvas.restoreState()


def draw_plain_furniture(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 8)
    canvas.setFillColor(INK_MUTE)
    canvas.drawCentredString(PAGE_W / 2, 32, TITLE)
    canvas.restoreState()


def build(story_pages: dict, first_pass: bool) -> tuple[Doc, int]:
    files = sorted(glob.glob(os.path.join(CONTENT_DIR, "*.txt")))
    if not files:
        raise SystemExit("course/content にコンテンツがありません。")
    doc_model = parse_files(files, story_pages)

    doc = BaseDocTemplate(
        OUT_PATH, pagesize=A4,
        leftMargin=M_LEFT, rightMargin=M_RIGHT, topMargin=M_TOP, bottomMargin=M_BOTTOM,
        title=TITLE, author="マイワーク AIスクール", subject=SUBTITLE,
        creator="マイワーク AIスクール",
    )
    frame = Frame(M_LEFT, M_BOTTOM, FRAME_W, PAGE_H - M_TOP - M_BOTTOM, id="main",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[frame]),
        PageTemplate(id="plain", frames=[frame], onPageEnd=draw_plain_furniture),
        PageTemplate(id="part", frames=[frame]),
        PageTemplate(id="body", frames=[frame], onPageEnd=draw_body_furniture),
    ])

    front = front_matter(doc_model, story_pages)
    STATE["page_offset"] = 0
    story = front + doc_model.story

    # 前付け（表紙・使い方・目次）のページ数を数えてページ番号をリセットする
    doc.build(story)
    return doc_model, doc.page


def validate_glyphs() -> None:
    """フォントに存在しない文字が原稿に含まれていないか検査する。"""
    face = pdfmetrics.getFont(FONT).face
    missing: dict[str, str] = {}
    for path in sorted(glob.glob(os.path.join(CONTENT_DIR, "*.txt"))):
        for ch in open(path, encoding="utf-8").read():
            if ch in "\n\t":
                continue
            if ord(ch) not in face.charToGlyph:
                missing.setdefault(ch, os.path.basename(path))
    if missing:
        detail = "、".join(f"{ch!r}({src})" for ch, src in missing.items())
        raise SystemExit(f"フォントに存在しない文字が含まれています: {detail}")


def configure(cfg: dict) -> None:
    """教材固有の設定を反映する。build()/main() を呼ぶ前に必ず実行すること。"""
    global CFG, PART_COLORS, DEFAULT_THEME, TITLE, SUBTITLE, OUT_PATH, CONTENT_DIR
    CFG = cfg
    PART_COLORS = {k: colors.HexColor(v) for k, v in cfg["part_colors"].items()}
    DEFAULT_THEME = PART_COLORS[cfg["default_theme_key"]]
    STATE["theme"] = DEFAULT_THEME
    TITLE = cfg["title"]
    SUBTITLE = cfg["subtitle"]
    OUT_PATH = cfg["out_path"]
    CONTENT_DIR = cfg["content_dir"]


def main() -> None:
    if not CFG:
        raise SystemExit("configure() を先に呼び出してください。")
    register_fonts()
    validate_glyphs()
    S.update(make_styles())
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    pages: dict[str, int] = {}
    # 目次のページ番号が安定するまで繰り返しビルドする
    model, total = build(pages, first_pass=True)
    for _ in range(3):
        prev = dict(pages)
        model, total = build(pages, first_pass=False)
        if prev == pages:
            break

    size = os.path.getsize(OUT_PATH) / 1024 / 1024
    print(f"出力: {OUT_PATH}")
    print(f"本文文字数(記法込みソース): 約 {model.body_chars:,} 文字 / ページ数: {total} / {size:.1f} MB")


