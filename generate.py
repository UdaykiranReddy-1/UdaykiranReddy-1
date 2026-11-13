#!/usr/bin/env python3
"""Generate four GitHub profile README concept previews (SVG + PNG)."""

from __future__ import annotations

import base64
import html as htmlmod
import math
import subprocess
import tempfile
from pathlib import Path

from PIL import ImageFont

OUT = Path(__file__).resolve().parent / "assets"
FONT_DIR = OUT / "fonts"
JB_PATH = FONT_DIR / "JetBrainsMono-Variable.ttf"
JB_ITALIC_PATH = FONT_DIR / "JetBrainsMono-Italic-Variable.ttf"
# Fallback when variable fonts are absent (local preview generation only).
JB_FALLBACK_DIR = Path("/usr/share/fonts/truetype/jetbrains-mono")
JB_MEDIUM_PATH = JB_FALLBACK_DIR / "JetBrainsMono-Medium.ttf"
JB_SEMIBOLD_PATH = JB_FALLBACK_DIR / "JetBrainsMono-SemiBold.ttf"

# --- palette (GitHub dark + restrained accents) ---
PAGE = "#0d1117"
CARD_BORDER = "#30363d"
HEADER_FG = "#e6edf3"
HEADER_MUTED = "#7d8590"
TEXT = "#e6edf3"
MUTED = "#8b949e"
DIM = "#6e7681"
FAINT = "#484f58"
LINK = "#58a6ff"
GREEN = "#3fb950"
GREEN_SOFT = "#7ee787"
YELLOW = "#e3b341"
ORANGE = "#ffa657"
CYAN = "#79c0ff"
NAME = "#f0f6fc"
TERM_BG = "#010409"
TERM_BAR = "#161b22"
TERM_BORDER = "#30363d"
PILL_BG = "#161b22"
PILL_BORDER = "#30363d"
RED_DOT = "#ff5f56"
YEL_DOT = "#ffbd2e"
GRN_DOT = "#27c93f"

W = 1200
CARD_X = 40
CARD_Y = 40
CARD_W = 1120
HEADER_H = 48
PAD_X = 64
CONTENT_W = CARD_W - PAD_X * 2  # 992
CONTENT_X = CARD_X + PAD_X

# Real content
FULL_NAME = "Uday Kiran Reddy"
TAGLINE = "I code and decode stuff"
LOCATION = "Bangalore, India"
ROLE = "Full-Stack Developer"
# Curated, short subset of the skillicons listed in his current README
STACK = ["TypeScript", "React", "Node.js", "Python", "PostgreSQL", "Docker", "AWS"]
NOW = "Side projects"
LEARNING = "Advanced System Design & Cloud"
GITHUB = "UdaykiranReddy-1"
EMAIL = "uday410ry@gmail.com"
LINKEDIN_LABEL = "LinkedIn"


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def font(size: float, weight: int = 400, italic: bool = False) -> ImageFont.FreeTypeFont:
    if italic and JB_ITALIC_PATH.exists():
        path = JB_ITALIC_PATH
    elif JB_PATH.exists():
        path = JB_PATH
    elif italic:
        path = JB_FALLBACK_DIR / "JetBrainsMono-Italic.ttf"
    elif weight >= 600:
        path = JB_SEMIBOLD_PATH
    elif weight >= 500:
        path = JB_MEDIUM_PATH
    else:
        path = JB_FALLBACK_DIR / "JetBrainsMono-Regular.ttf"
    f = ImageFont.truetype(str(path), size)
    if path == JB_PATH or path == JB_ITALIC_PATH:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def tw(text: str, size: float, weight: int = 400, italic: bool = False) -> float:
    return float(font(size, weight, italic).getlength(text))




def esc(s: str) -> str:
    return htmlmod.escape(s, quote=True)


def tspan_safe(s: str) -> str:
    return esc(s)


def text(
    x,
    y,
    s,
    size,
    fill=TEXT,
    weight=400,
    family="JB",
    anchor="start",
    italic=False,
    letter_spacing=None,
    opacity=None,
):
    attrs = [
        f'x="{x:.2f}"',
        f'y="{y:.2f}"',
        f'fill="{fill}"',
        f'font-family="{family}"',
        f'font-size="{size}"',
        f'font-weight="{weight}"',
        f'text-anchor="{anchor}"',
    ]
    if italic:
        attrs.append('font-style="italic"')
    if letter_spacing is not None:
        attrs.append(f'letter-spacing="{letter_spacing}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    attrs.append('xml:space="preserve"')
    return f"<text {' '.join(attrs)}>{esc(s)}</text>"


def rect(x, y, w, h, fill="none", rx=0, stroke=None, sw=1, opacity=None, extra=""):
    attrs = [
        f'x="{x:.2f}"',
        f'y="{y:.2f}"',
        f'width="{w:.2f}"',
        f'height="{h:.2f}"',
        f'rx="{rx}"',
        f'fill="{fill}"',
    ]
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{sw}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    if extra:
        attrs.append(extra)
    return f"<rect {' '.join(attrs)} />"


def circle(cx, cy, r, fill):
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r}" fill="{fill}" />'


def line(x1, y1, x2, y2, stroke, sw=1, opacity=None):
    o = f' opacity="{opacity}"' if opacity is not None else ""
    return (
        f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
        f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"{o} />'
    )


# Simple monochrome icons (16x16 viewBox), official-ish marks
ICON_GITHUB = (
    "M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38"
    " 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13"
    "-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66"
    ".07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15"
    "-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0"
    " 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56"
    ".82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07"
    "-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"
)
ICON_LINKEDIN = (
    "M2 0h12a2 2 0 012 2v12a2 2 0 01-2 2H2a2 2 0 01-2-2V2a2 2 0 012-2zm2.5"
    " 13.5V6.2H2.2v7.3h2.3zM3.35 5.2c.8 0 1.3-.53 1.3-1.2-.02-.68-.5-1.2-1.28"
    "-1.2S2.07 3.32 2.07 4c0 .67.5 1.2 1.26 1.2h.02zM13.8 13.5V9.4c0-2.2-1.17"
    "-3.22-2.73-3.22-1.26 0-1.82.7-2.14 1.18V6.2H6.64c.03.66 0 7.3 0 7.3h2.3V9.54"
    "c0-.21.02-.42.08-.57.17-.42.56-.86 1.22-.86.86 0 1.2.66 1.2 1.62v3.77h2.36z"
)
ICON_MAIL = (
    "M1.75 3A1.75 1.75 0 000 4.75v6.5C0 12.216.784 13 1.75 13h12.5A1.75"
    " 1.75 0 0016 11.25v-6.5A1.75 1.75 0 0014.25 3H1.75zM1.5 4.75a.25.25"
    " 0 01.25-.25h12.5a.25.25 0 01.25.25v.43L8.22 8.92a.75.75 0 01-.44 0"
    "L1.5 5.18v-.43zm0 1.73l5.86 3.73a2.25 2.25 0 002.28 0l5.86-3.73v4.77"
    "a.25.25 0 01-.25.25H1.75a.25.25 0 01-.25-.25V6.48z"
)
ICON_MD = (
    "M14.85 3H1.15C.52 3 0 3.52 0 4.15v7.69C0 12.48.52 13 1.15 13h13.69c.64"
    " 0 1.15-.52 1.15-1.16V4.15C16 3.52 15.48 3 14.85 3zM9 11H7.5L5.5 8.5"
    " 3.5 11H2V5h1.5v4L5.5 6.5 7.5 9V5H9v6zm4.5-1.5h-1.25V5H11v4.5H9.75L12 11.25"
    " 14.25 9.5z"
)


def icon(d: str, x: float, y: float, size: float = 16, fill: str = LINK) -> str:
    s = size / 16
    return (
        f'<g transform="translate({x:.2f},{y:.2f}) scale({s:.4f})">'
        f'<path fill="{fill}" d="{d}"/></g>'
    )


def font_css() -> str:
    if JB_PATH.exists() and JB_ITALIC_PATH.exists():
        jb = b64(JB_PATH)
        jbi = b64(JB_ITALIC_PATH)
        return f"""
@font-face {{
  font-family: 'JB';
  src: url('data:font/truetype;base64,{jb}') format('truetype');
  font-weight: 100 800;
  font-style: normal;
  font-display: block;
}}
@font-face {{
  font-family: 'JB';
  src: url('data:font/truetype;base64,{jbi}') format('truetype');
  font-weight: 100 800;
  font-style: italic;
  font-display: block;
}}
text {{ font-synthesis: none; }}
"""
    faces = []
    reg = JB_FALLBACK_DIR / "JetBrainsMono-Regular.ttf"
    ital = JB_FALLBACK_DIR / "JetBrainsMono-Italic.ttf"
    for weight, path, style in (
        (400, reg, "normal"),
        (500, JB_MEDIUM_PATH, "normal"),
        (600, JB_SEMIBOLD_PATH, "normal"),
        (400, ital, "italic"),
    ):
        data = b64(path)
        faces.append(
            f"""@font-face {{
  font-family: 'JB';
  src: url('data:font/truetype;base64,{data}') format('truetype');
  font-weight: {weight};
  font-style: {style};
  font-display: block;
}}"""
        )
    return "\n".join(faces) + "\ntext { font-synthesis: none; }"


def defs() -> str:
    return f"""
<defs>
  <style type="text/css">{font_css()}</style>
  <filter id="cardShadow" x="-5%" y="-5%" width="110%" height="120%">
    <feDropShadow dx="0" dy="12" stdDeviation="18" flood-color="#010409" flood-opacity="0.55"/>
  </filter>
  <filter id="softShadow" x="-8%" y="-8%" width="116%" height="130%">
    <feDropShadow dx="0" dy="8" stdDeviation="14" flood-color="#000000" flood-opacity="0.45"/>
  </filter>
</defs>
"""


def readme_chrome(inner: str, content_h: float, bottom_extra: float = 0) -> tuple[str, int]:
    """Wrap content in a GitHub-dark profile README card. Returns (svg, height)."""
    # content_h is height of the inner block starting after the file header,
    # including top and bottom content padding already baked in by the caller
    # or we add padding here. Callers pass the height of their content only;
    # we add top/bottom padding.
    top_pad = 44
    bot_pad = 40 + bottom_extra
    card_h = HEADER_H + top_pad + content_h + bot_pad
    page_h = int(CARD_Y * 2 + card_h)
    # file header
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{page_h}" viewBox="0 0 {W} {page_h}">',
        defs(),
        rect(0, 0, W, page_h, PAGE),
        # README card
        rect(
            CARD_X,
            CARD_Y,
            CARD_W,
            card_h,
            PAGE,
            rx=6,
            stroke=CARD_BORDER,
            sw=1,
        ),
        # header bar fill (clip via a rect under the top of the rounded card)
        f"""
        <path d="M{CARD_X+6},{CARD_Y} h{CARD_W-12}
                 a6,6 0 0 1 6,6 v{HEADER_H-6} h{-CARD_W} v{-HEADER_H+6}
                 a6,6 0 0 1 6,-6 z" fill="#0d1117"/>
        """,
        line(CARD_X, CARD_Y + HEADER_H, CARD_X + CARD_W, CARD_Y + HEADER_H, CARD_BORDER, 1),
        icon(ICON_MD, CARD_X + 18, CARD_Y + 16, 16, HEADER_MUTED),
        text(CARD_X + 40, CARD_Y + 31, "README.md", 13, HEADER_FG, 500, family="JB"),
        # inner content translated
        f'<g transform="translate(0,{CARD_Y + HEADER_H + top_pad})">',
        inner,
        "</g>",
        "</svg>",
    ]
    return "\n".join(parts), page_h


def link_row(cx: float, y: float) -> tuple[str, float]:
    """Centered GitHub / LinkedIn / email row. Returns (svg, height)."""
    size = 13.5
    gap_icon = 7
    gap_item = 36
    icon_s = 15
    items = [
        (ICON_GITHUB, "GitHub"),
        (ICON_LINKEDIN, "LinkedIn"),
        (ICON_MAIL, EMAIL),
    ]
    widths = []
    for _, label in items:
        widths.append(icon_s + gap_icon + tw(label, size, 450))
    total = sum(widths) + gap_item * (len(items) - 1)
    x = cx - total / 2
    bits = []
    for i, ((d, label), w) in enumerate(zip(items, widths)):
        bits.append(icon(d, x, y - 11, icon_s, LINK))
        bits.append(text(x + icon_s + gap_icon, y, label, size, LINK, 450, family="JB"))
        x += w
        if i < len(items) - 1:
            # subtle mid dot between items, sitting in the gap
            dots_x = x + gap_item / 2
            bits.append(text(dots_x, y, "·", size, FAINT, 400, family="JB", anchor="middle"))
            x += gap_item
    return "\n".join(bits), 20


def stack_row(cx: float, y: float, size: float = 13, weight: int = 450, fill: str = MUTED) -> str:
    sep = "\u00a0\u00a0·\u00a0\u00a0"
    label = sep.join(STACK)
    return text(cx, y, label, size, fill, weight, family="JB", anchor="middle")


def decoder_strip(cx: float, y: float, scale: float = 1.0) -> tuple[str, float]:
    """3-frame scramble → name annotation. Returns (svg, height used)."""
    frames = [
        ("U#4y K!r@n R3d*y", DIM, 0.9),
        ("Ud?y Ki?an Re??y", MUTED, 0.95),
        ("Uday Kiran Reddy", TEXT, 1.0),
    ]
    f_size = 13 * scale
    f_pad_x = 18 * scale
    f_h = 36 * scale
    f_w = tw(frames[0][0], 13, 450) * scale + f_pad_x * 2
    arrow_w = 28 * scale
    group_w = f_w * 3 + arrow_w * 2
    fx = cx - group_w / 2
    parts = []
    for i, (label, color, op) in enumerate(frames):
        parts.append(rect(fx, y, f_w, f_h, PILL_BG, rx=6, stroke=PILL_BORDER, sw=1, opacity=op))
        parts.append(
            text(
                fx + f_w / 2,
                y + f_h * 0.65,
                label,
                f_size,
                color,
                450,
                family="JB",
                anchor="middle",
                opacity=op,
            )
        )
        fx += f_w
        if i < 2:
            parts.append(
                text(
                    fx + arrow_w / 2,
                    y + f_h * 0.65,
                    "→",
                    14 * scale,
                    FAINT,
                    400,
                    family="JB",
                    anchor="middle",
                )
            )
            fx += arrow_w
    # frame labels
    lab_y = y + f_h + 16 * scale
    labels = ["scrambled", "settling", "final"]
    fx = cx - group_w / 2
    for i, lab in enumerate(labels):
        parts.append(
            text(
                fx + f_w / 2,
                lab_y,
                lab,
                10 * scale,
                FAINT,
                400,
                family="JB",
                anchor="middle",
                letter_spacing=0.4,
            )
        )
        fx += f_w + (arrow_w if i < 2 else 0)
    height = (lab_y + 2 * scale) - y
    return "\n".join(parts), height


def cursor_block(x, y, w=8, h=16, fill=GREEN):
    return rect(x, y, w, h, fill, rx=1)


# ---------------------------------------------------------------------------
# 1. Terminal card
# ---------------------------------------------------------------------------
def build_terminal() -> tuple[str, int]:
    term_w = 860
    term_x = CONTENT_X + (CONTENT_W - term_w) / 2
    bar_h = 44
    body_top = bar_h + 36
    body = []
    y = body_top
    px = term_x + 40
    body.append(text(px, y, "$", 16, GREEN, 500))
    body.append(text(px + 22, y, "whoami", 16, TEXT, 400))
    y += 38
    body.append(text(px, y, FULL_NAME, 28, NAME, 600))
    y += 44
    body.append(text(px, y, TAGLINE, 16, MUTED, 400, italic=True))
    y += 40
    body.append(line(px, y, term_x + term_w - 40, y, CARD_BORDER, 1, opacity=0.9))
    y += 36

    key_size = 13.5
    val_size = 13.5
    stack_line = "\u00a0\u00a0·\u00a0\u00a0".join(STACK)
    rows = [
        ("location", LOCATION),
        ("role", ROLE),
        ("stack", stack_line),
        ("now", NOW),
        ("learning", LEARNING),
    ]
    key_w = max(tw(k, key_size, 500) for k, _ in rows) + 4
    val_x = px + key_w + 28
    for key, val in rows:
        body.append(text(px, y, key, key_size, DIM, 500))
        body.append(text(val_x, y, val, val_size, TEXT, 400))
        y += 30
    y += 22
    body.append(text(px, y, "$", 16, GREEN, 500))
    body.append(cursor_block(px + 22, y - 12, 7, 15, GREEN))
    y += 36
    term_h = y

    window = [
        rect(term_x, 0, term_w, term_h, TERM_BG, rx=10, stroke=TERM_BORDER, sw=1, extra='filter="url(#softShadow)"'),
        f"""<path d="M{term_x+10},0 h{term_w-20} a10,10 0 0 1 10,10 v{bar_h-10}
             h{-term_w} v{-bar_h+10} a10,10 0 0 1 10,-10 z" fill="{TERM_BAR}"/>""",
        line(term_x, bar_h, term_x + term_w, bar_h, TERM_BORDER, 1),
        line(term_x + 10, 0.6, term_x + term_w - 10, 0.6, "#ffffff", 1, opacity=0.06),
        circle(term_x + 22, bar_h / 2, 6, RED_DOT),
        circle(term_x + 42, bar_h / 2, 6, YEL_DOT),
        circle(term_x + 62, bar_h / 2, 6, GRN_DOT),
        text(
            term_x + term_w / 2,
            bar_h / 2 + 5,
            "uday@bangalore:~",
            12,
            DIM,
            450,
            family="JB",
            anchor="middle",
        ),
    ]
    links, lh = link_row(CONTENT_X + CONTENT_W / 2, term_h + 44)
    inner = "\n".join(window + body + [links])
    content_h = term_h + 44 + lh
    return readme_chrome(inner, content_h)


def build_decoder() -> tuple[str, int]:
    cx = CONTENT_X + CONTENT_W / 2
    parts = []
    y = 0

    parts.append(
        text(
            cx,
            y,
            "the name unscrambles on load",
            11.5,
            DIM,
            400,
            family="JB",
            anchor="middle",
            letter_spacing=0.6,
        )
    )
    y += 26
    strip, sh = decoder_strip(cx, y, scale=1.0)
    parts.append(strip)
    y += sh + 44

    rule_w = 72
    parts.append(line(cx - rule_w / 2, y, cx + rule_w / 2, y, CARD_BORDER, 1))
    y += 56

    parts.append(
        text(
            cx,
            y,
            FULL_NAME,
            44,
            NAME,
            600,
            family="JB",
            anchor="middle",
            letter_spacing=0.6,
        )
    )
    y += 38
    parts.append(
        text(cx, y, TAGLINE, 18, MUTED, 400, family="JB", anchor="middle", italic=True)
    )
    y += 42
    parts.append(stack_row(cx, y, size=13, weight=450, fill=DIM))
    y += 48
    links, lh = link_row(cx, y)
    parts.append(links)
    y += lh
    return readme_chrome("\n".join(parts), y)


def build_commit_log(include_decoder_header: bool = False) -> tuple[str, int]:
    cx = CONTENT_X + CONTENT_W / 2
    parts = []
    y = 0

    if include_decoder_header:
        parts.append(
            text(
                cx,
                y,
                "the name unscrambles on load",
                11.5,
                DIM,
                400,
                family="JB",
                anchor="middle",
                letter_spacing=0.6,
            )
        )
        y += 24
        strip, sh = decoder_strip(cx, y, scale=0.92)
        parts.append(strip)
        y += sh + 40
        parts.append(
            text(
                cx,
                y,
                FULL_NAME,
                40,
                NAME,
                600,
                family="JB",
                anchor="middle",
                letter_spacing=0.5,
            )
        )
        y += 36
        parts.append(
            text(cx, y, TAGLINE, 17, MUTED, 400, family="JB", anchor="middle", italic=True)
        )
        y += 26
        parts.append(
            text(cx, y, f"{ROLE}  ·  {LOCATION}", 13, DIM, 400, family="JB", anchor="middle")
        )
        y += 36
        rule_w = 72
        parts.append(line(cx - rule_w / 2, y, cx + rule_w / 2, y, CARD_BORDER, 1))
        y += 40
    else:
        parts.append(
            text(
                cx,
                y,
                FULL_NAME,
                28,
                NAME,
                600,
                family="JB",
                anchor="middle",
            )
        )
        y += 28
        parts.append(
            text(cx, y, TAGLINE, 16, MUTED, 400, family="JB", anchor="middle", italic=True)
        )
        y += 24
        parts.append(
            text(cx, y, f"{ROLE}  ·  {LOCATION}", 13, DIM, 400, family="JB", anchor="middle")
        )
        y += 36
        rule_w = 72
        parts.append(line(cx - rule_w / 2, y, cx + rule_w / 2, y, CARD_BORDER, 1))
        y += 40

    # git log — messages include years as specified; (HEAD) decorates the tip.
    # Columns: hash | decorate | type | message
    # so type+message stay vertically aligned.
    hash_size = 14
    msg_size = 14
    commits = [
        ("e4d07b2", "HEAD", "wip:", "full-stack + AI", ORANGE),
        ("8c2b91a", "", "feat:", "joined corporate role (2025)", GREEN_SOFT),
        ("a3f1c2e", "", "feat:", "started building software (2023)", GREEN_SOFT),
    ]
    hash_w = tw("e4d07b2", hash_size, 500)
    deco_w = tw("(HEAD)", 13, 450)
    type_w = tw("feat:", msg_size, 500)
    msg_w = max(tw(m, msg_size, 400) for *_, m, _ in commits)
    col_gap = 20
    col_w = hash_w + col_gap + deco_w + col_gap + type_w + 12 + msg_w
    col_x = cx - col_w / 2

    parts.append(text(col_x, y, "$", 14, GREEN, 500))
    parts.append(text(col_x + 20, y, "git log", 14, TEXT, 400))
    y += 36

    hash_x = col_x
    deco_x = hash_x + hash_w + col_gap
    type_x = deco_x + deco_w + col_gap
    msg_x = type_x + type_w + 12

    for hsh, deco, typ, msg, pcolor in commits:
        parts.append(text(hash_x, y, hsh, hash_size, YELLOW, 500))
        if deco:
            parts.append(text(deco_x, y, f"({deco})", 13, CYAN, 450))
        parts.append(text(type_x, y, typ, msg_size, pcolor, 500))
        parts.append(text(msg_x, y, msg, msg_size, TEXT, 400))
        y += 34

    y += 32
    parts.append(stack_row(cx, y, size=12.5, weight=450, fill=DIM))
    y += 44

    links, lh = link_row(cx, y)
    parts.append(links)
    y += lh
    return readme_chrome("\n".join(parts), y)


def build_combo() -> tuple[str, int]:
    return build_commit_log(include_decoder_header=True)


GITHUB_URL = "https://github.com/UdaykiranReddy-1"
LINKEDIN_URL = "https://www.linkedin.com/in/uday-kiran-reddy-n-7845b0280/"
MAIL_URL = f"mailto:{EMAIL}"
LINK_GAP_BEFORE = 44


def build_combo_profile_inner() -> tuple[str, float]:
    """Combo layout (decoder + git log + stack) without links; combo coordinates."""
    cx = CONTENT_X + CONTENT_W / 2
    parts: list[str] = []
    y = 0.0

    parts.append(
        text(
            cx,
            y,
            "the name unscrambles on load",
            11.5,
            DIM,
            400,
            family="JB",
            anchor="middle",
            letter_spacing=0.6,
        )
    )
    y += 24
    strip, sh = decoder_strip(cx, y, scale=0.92)
    parts.append(strip)
    y += sh + 40
    parts.append(
        text(
            cx,
            y,
            FULL_NAME,
            40,
            NAME,
            600,
            family="JB",
            anchor="middle",
            letter_spacing=0.5,
        )
    )
    y += 36
    parts.append(
        text(cx, y, TAGLINE, 17, MUTED, 400, family="JB", anchor="middle", italic=True)
    )
    y += 26
    parts.append(
        text(cx, y, f"{ROLE}  ·  {LOCATION}", 13, DIM, 400, family="JB", anchor="middle")
    )
    y += 36
    rule_w = 72
    parts.append(line(cx - rule_w / 2, y, cx + rule_w / 2, y, CARD_BORDER, 1))
    y += 40

    hash_size = 14
    msg_size = 14
    commits = [
        ("e4d07b2", "HEAD", "wip:", "full-stack + AI", ORANGE),
        ("8c2b91a", "", "feat:", "joined corporate role (2025)", GREEN_SOFT),
        ("a3f1c2e", "", "feat:", "started building software (2023)", GREEN_SOFT),
    ]
    hash_w = tw("e4d07b2", hash_size, 500)
    deco_w = tw("(HEAD)", 13, 450)
    type_w = tw("feat:", msg_size, 500)
    msg_w = max(tw(m, msg_size, 400) for *_, m, _ in commits)
    col_gap = 20
    col_w = hash_w + col_gap + deco_w + col_gap + type_w + 12 + msg_w
    col_x = cx - col_w / 2

    parts.append(text(col_x, y, "$", 14, GREEN, 500))
    parts.append(text(col_x + 20, y, "git log", 14, TEXT, 400))
    y += 36

    hash_x = col_x
    deco_x = hash_x + hash_w + col_gap
    type_x = deco_x + deco_w + col_gap
    msg_x = type_x + type_w + 12

    for hsh, deco, typ, msg, pcolor in commits:
        parts.append(text(hash_x, y, hsh, hash_size, YELLOW, 500))
        if deco:
            parts.append(text(deco_x, y, f"({deco})", 13, CYAN, 450))
        parts.append(text(type_x, y, typ, msg_size, pcolor, 500))
        parts.append(text(msg_x, y, msg, msg_size, TEXT, 400))
        y += 34

    y += 32
    parts.append(stack_row(cx, y, size=12.5, weight=450, fill=DIM))

    return "\n".join(parts), y


def build_profile_main_svg() -> tuple[str, int]:
    inner, content_bottom = build_combo_profile_inner()
    h = math.ceil(content_bottom + LINK_GAP_BEFORE)
    w = CONTENT_W
    svg = "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="{CONTENT_X:.0f} 0 {w} {h}">',
            defs(),
            rect(CONTENT_X, 0, w, h, PAGE),
            inner,
            "</svg>",
        ]
    )
    return svg, h


def build_link_item_svg(icon_d: str, label: str) -> tuple[str, int, int]:
    size = 13.5
    gap_icon = 7
    icon_s = 15
    text_w = tw(label, size, 450)
    w = int(icon_s + gap_icon + text_w + 1)
    h = 24
    y_text = 18.0
    svg = "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">',
            defs(),
            icon(icon_d, 0, y_text - 11, icon_s, LINK),
            text(icon_s + gap_icon, y_text, label, size, LINK, 450, family="JB"),
            "</svg>",
        ]
    )
    return svg, w, h


def build_link_sep_svg() -> tuple[str, int, int]:
    gap_item = 36
    size = 13.5
    h = 24
    svg = "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{gap_item}" height="{h}" viewBox="0 0 {gap_item} {h}">',
            defs(),
            text(gap_item / 2, 18, "·", size, FAINT, 400, family="JB", anchor="middle"),
            "</svg>",
        ]
    )
    return svg, gap_item, h


def write_readme_md(dest: Path) -> None:
    link_row = (
        '<span style="font-size:0;line-height:0;white-space:nowrap;">'
        f'<a href="{GITHUB_URL}"><img src="assets/link-github.svg" height="24" alt="GitHub" style="vertical-align:middle;border:0;" /></a>'
        f'<img src="assets/link-sep.svg" height="24" alt="" style="vertical-align:middle;border:0;" />'
        f'<a href="{LINKEDIN_URL}"><img src="assets/link-linkedin.svg" height="24" alt="LinkedIn" style="vertical-align:middle;border:0;" /></a>'
        f'<img src="assets/link-sep.svg" height="24" alt="" style="vertical-align:middle;border:0;" />'
        f'<a href="{MAIL_URL}"><img src="assets/link-email.svg" height="24" alt="{EMAIL}" style="vertical-align:middle;border:0;" /></a>'
        "</span>"
    )
    dest.write_text(
        "\n".join(
            [
                '<div align="center">',
                f'<img src="assets/profile-main.svg" width="{CONTENT_W}" alt="" style="display:block;margin:0 auto;border:0;" />',
                link_row,
                "</div>",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def build_profile_assets(out_dir: Path | None = None) -> None:
    out_dir = out_dir or OUT
    out_dir.mkdir(parents=True, exist_ok=True)
    repo_root = Path(__file__).resolve().parent

    main_svg, _ = build_profile_main_svg()
    (out_dir / "profile-main.svg").write_text(main_svg, encoding="utf-8")

    for name, icon_d, label in (
        ("link-github.svg", ICON_GITHUB, "GitHub"),
        ("link-linkedin.svg", ICON_LINKEDIN, "LinkedIn"),
        ("link-email.svg", ICON_MAIL, EMAIL),
    ):
        svg, _, _ = build_link_item_svg(icon_d, label)
        (out_dir / name).write_text(svg, encoding="utf-8")

    sep, _, _ = build_link_sep_svg()
    (out_dir / "link-sep.svg").write_text(sep, encoding="utf-8")

    write_readme_md(repo_root / "README.md")
    print(f"Wrote profile assets under {out_dir}")


def render_readme_preview(
    repo_root: Path, dest: Path, page_w: int = 1012, scale: int = 2
) -> None:
    """Render README.md like GitHub profile (dark, ~1012px content column)."""
    from PIL import Image

    readme = repo_root / "README.md"
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  html, body {{
    margin: 0;
    padding: 24px 0;
    width: {page_w}px;
    background: {PAGE};
    color-scheme: dark;
  }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  }}
  .markdown-body {{
    max-width: {page_w}px;
    margin: 0 auto;
    padding: 0 10px;
    box-sizing: border-box;
  }}
  img {{ border: none; vertical-align: middle; }}
</style>
</head>
<body>
<div class="markdown-body">
{readme.read_text(encoding="utf-8")}
</div>
</body>
</html>
"""
    html_path = repo_root / "_readme_preview.html"
    html_path.write_text(html, encoding="utf-8")
    png_tmp = dest.with_suffix(".raw.png")
    chrome = Path("/opt/google/chrome/chrome")
    if not chrome.exists():
        chrome = Path("google-chrome")
    cmd = [
        str(chrome),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--allow-file-access-from-files",
        f"--force-device-scale-factor={scale}",
        f"--window-size={page_w},620",
        "--default-background-color=0d1117",
        "--virtual-time-budget=15000",
        "--run-all-compositor-stages-before-draw",
        f"--screenshot={png_tmp}",
        f"file://{html_path}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(repo_root), timeout=90)
    if r.returncode != 0 or not png_tmp.exists():
        raise RuntimeError(f"chrome failed: {r.returncode}\n{r.stdout}\n{r.stderr}")
    im = Image.open(png_tmp)
    im.save(dest, "PNG", optimize=True)
    png_tmp.unlink(missing_ok=True)
    html_path.unlink(missing_ok=True)
    print(f"readme preview: {dest} {im.size}")


def render_svg(svg: str, height: int, dest: Path, scale: int = 2) -> None:
    dest = Path(dest)
    svg_path = dest.with_suffix(".svg")
    svg_path.write_text(svg, encoding="utf-8")

    # Render via headless Chrome, loading the SVG as an image so HTML
    # whitespace collapsing cannot touch the text nodes.
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  html, body {{
    margin: 0;
    padding: 0;
    width: {W}px;
    height: {height}px;
    background: {PAGE};
    overflow: hidden;
  }}
  img {{ display: block; width: {W}px; height: {height}px; }}
</style>
</head>
<body>
<img src="{svg_path.name}" width="{W}" height="{height}" alt="preview"/>
</body>
</html>
"""
    html_path = dest.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")
    png_tmp = dest.with_suffix(".raw.png")
    chrome = Path("/opt/google/chrome/chrome")
    if not chrome.exists():
        chrome = Path("google-chrome")
    cmd = [
        str(chrome),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        "--allow-file-access-from-files",
        f"--force-device-scale-factor={scale}",
        f"--window-size={W},{height}",
        "--default-background-color=0d1117",
        f"--screenshot={png_tmp}",
        f"file://{html_path}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not png_tmp.exists():
        raise RuntimeError(f"chrome failed: {r.returncode}\n{r.stdout}\n{r.stderr}")
    # Trim any unexpected chrome pixel rounding, ensure exact size
    from PIL import Image

    im = Image.open(png_tmp)
    target = (W * scale, height * scale)
    if im.size != target:
        # crop to target if slightly larger, or leave if close
        im = im.crop((0, 0, min(im.width, target[0]), min(im.height, target[1])))
        if im.size != target:
            canvas = Image.new("RGB", target, (13, 17, 23))
            canvas.paste(im, (0, 0))
            im = canvas
    im.save(dest, "PNG", optimize=True)
    png_tmp.unlink(missing_ok=True)
    html_path.unlink(missing_ok=True)
    print(f"wrote {svg_path} ({svg_path.stat().st_size/1e6:.2f} MB) and {dest} {im.size}")


def main():
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "profile":
        build_profile_assets()
        return
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        repo = Path(__file__).resolve().parent
        artifact = Path("/opt/cursor/artifacts/readme-profile-verify.png")
        artifact.parent.mkdir(parents=True, exist_ok=True)
        render_readme_preview(repo, artifact)
        ref = Path(
            "/home/ubuntu/.cursor/projects/agent-repos-UdaykiranReddy-1/assets/04-combo.png"
        )
        if ref.exists():
            combo_svg, combo_h = build_combo()
            combo_png = artifact.with_name("combo-reference-render.png")
            render_svg(combo_svg, combo_h, combo_png, scale=2)
            from PIL import Image

            got = Image.open(artifact).convert("RGB")
            # Crop reference card interior (no chrome header): x=208..2190 at 2x
            ref_im = Image.open(ref).convert("RGB")
            inner = ref_im.crop((208, 264, 208 + 1984, ref_im.height - 80))
            print(f"reference inner crop: {inner.size}, readme render: {got.size}")
        return
    builds = [
        ("01-terminal-card.png", build_terminal),
        ("02-decoder-line.png", build_decoder),
        ("03-commit-log-bio.png", build_commit_log),
        ("04-combo.png", build_combo),
    ]
    for name, fn in builds:
        svg, h = fn()
        render_svg(svg, h, OUT / name, scale=2)


if __name__ == "__main__":
    main()
