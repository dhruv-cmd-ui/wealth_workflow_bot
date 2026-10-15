"""Renders a branded square card image for a piece of content using Pillow.

Uses the DejaVuSans font bundled inside the `matplotlib` package's data
directory, so no font download/licensing step is needed.
"""
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CARD_SIZE = (1080, 1080)
MARGIN = 80

CATEGORY_COLORS = {
    "market_recap": ("#0F2027", "#2C5364"),
    "terms": ("#1A2980", "#26D0CE"),
    "tips": ("#11998E", "#38EF7D"),
    "myths": ("#8E2DE2", "#4A00E0"),
    "tax_tips": ("#4B6CB7", "#182848"),
    "quotes": ("#232526", "#414345"),
    "did_you_know": ("#2980B9", "#6DD5FA"),
    "sip_mutual_funds": ("#134E5E", "#71B280"),
    "qna": ("#C31432", "#240B36"),
}

CATEGORY_LABELS = {
    "market_recap": "MARKET SNAPSHOT",
    "terms": "TERM OF THE DAY",
    "tips": "MONEY TIP",
    "myths": "MYTH VS FACT",
    "tax_tips": "TAX & RULES",
    "quotes": "FINANCE QUOTE",
    "did_you_know": "DID YOU KNOW?",
    "sip_mutual_funds": "SIP / MUTUAL FUNDS",
    "qna": "ASK A QUESTION",
}


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    try:
        import matplotlib
        base = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        return ImageFont.truetype(str(base / name), size)
    except Exception:
        return ImageFont.load_default()


def _lerp_color(c1: str, c2: str, t: float) -> tuple:
    def hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    a, b = hex_to_rgb(c1), hex_to_rgb(c2)
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _draw_gradient_background(draw: ImageDraw.ImageDraw, size, color1: str, color2: str):
    width, height = size
    for y in range(height):
        t = y / height
        color = _lerp_color(color1, color2, t)
        draw.line([(0, y), (width, y)], fill=color)


def _wrap_and_draw(draw, text, font, x, y, max_width, fill, line_spacing=1.3):
    avg_char_width = font.getbbox("M")[2] or 1
    wrap_width = max(10, int(max_width / avg_char_width))
    lines = []
    for paragraph in text.split("\n"):
        lines.extend(textwrap.wrap(paragraph, width=wrap_width) or [""])

    line_height = int((font.getbbox("Mg")[3] - font.getbbox("Mg")[1]) * line_spacing)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def render_card(category: str, heading: str, body: str, footer: str, out_path: str) -> str:
    color1, color2 = CATEGORY_COLORS.get(category, ("#1A2980", "#26D0CE"))
    img = Image.new("RGB", CARD_SIZE, color=color1)
    draw = ImageDraw.Draw(img)
    _draw_gradient_background(draw, CARD_SIZE, color1, color2)

    label = CATEGORY_LABELS.get(category, category.upper())
    label_font = _font(34, bold=True)
    draw.text((MARGIN, MARGIN), label, font=label_font, fill="#FFFFFF")
    draw.line(
        [(MARGIN, MARGIN + 60), (CARD_SIZE[0] - MARGIN, MARGIN + 60)],
        fill="#FFFFFF",
        width=3,
    )

    content_width = CARD_SIZE[0] - 2 * MARGIN
    y = MARGIN + 110

    if heading:
        heading_font = _font(52, bold=True)
        y = _wrap_and_draw(draw, heading, heading_font, MARGIN, y, content_width, "#FFFFFF")
        y += 30

    body_font = _font(38)
    y = _wrap_and_draw(draw, body, body_font, MARGIN, y, content_width, "#F2F2F2")

    footer_font = _font(24)
    footer_lines = textwrap.wrap(footer, width=70)
    footer_y = CARD_SIZE[1] - MARGIN - (len(footer_lines) * 32)
    for line in footer_lines:
        draw.text((MARGIN, footer_y), line, font=footer_font, fill="#DADADA")
        footer_y += 32

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG")
    return str(out)
