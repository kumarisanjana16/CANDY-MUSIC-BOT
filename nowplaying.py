"""
Video ke thumbnail ke upar ek chhota music-player jaisa overlay banata hai
(title + progress bar) — screenshot mein dikhne wale "now playing" card jaisa.
Yeh sirf ek static image hai; asli controls neeche wale inline buttons hain.
"""

import io
import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from clients import LOGGER

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _load_font(size: int):
    for path in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


async def _download_image(url: str) -> "Image.Image | None":
    if not url:
        return None
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    return None
                data = await resp.read()
        return Image.open(io.BytesIO(data)).convert("RGB")
    except Exception as e:
        LOGGER.warning(f"Thumbnail download fail: {e}")
        return None


async def generate_now_playing_card(thumbnail_url: str, title: str, duration_str: str) -> "io.BytesIO | None":
    """Returns a BytesIO PNG buffer, ya None agar generate nahi ho paaya (fallback ke liye)."""
    base = await _download_image(thumbnail_url)
    if base is None:
        return None

    try:
        W, H = 900, 500
        # background: blurred + darkened thumbnail, full bleed
        bg = base.resize((W, H)).filter(ImageFilter.GaussianBlur(8))
        overlay = Image.new("RGB", (W, H), (0, 0, 0))
        bg = Image.blend(bg, overlay, 0.35)

        # foreground: sharp thumbnail card, centered
        card_w, card_h = 620, 300
        fg = base.copy()
        fw, fh = fg.size
        target_ratio = card_w / card_h
        src_ratio = fw / fh
        if src_ratio > target_ratio:
            new_w = int(fh * target_ratio)
            x0 = (fw - new_w) // 2
            fg = fg.crop((x0, 0, x0 + new_w, fh))
        else:
            new_h = int(fw / target_ratio)
            y0 = (fh - new_h) // 2
            fg = fg.crop((0, y0, fw, y0 + new_h))
        fg = fg.resize((card_w, card_h))

        card_x, card_y = (W - card_w) // 2, 40
        bg.paste(fg, (card_x, card_y))

        draw = ImageDraw.Draw(bg, "RGBA")

        # rounded border around thumbnail card
        draw.rectangle(
            [card_x, card_y, card_x + card_w, card_y + card_h],
            outline=(255, 255, 255, 180), width=3,
        )

        # bottom info panel
        panel_y = card_y + card_h + 20
        title_font = _load_font(28)
        small_font = _load_font(18)

        display_title = title if len(title) <= 45 else title[:42] + "..."
        draw.text((card_x, panel_y), display_title, font=title_font, fill=(255, 255, 255, 255))

        # progress bar
        bar_y = panel_y + 55
        bar_x0, bar_x1 = card_x, card_x + card_w
        draw.line([(bar_x0, bar_y), (bar_x1, bar_y)], fill=(255, 255, 255, 90), width=6)
        draw.ellipse([bar_x0 - 6, bar_y - 6, bar_x0 + 6, bar_y + 6], fill=(255, 60, 60, 255))

        draw.text((bar_x0, bar_y + 15), "00:00", font=small_font, fill=(230, 230, 230, 255))
        dur_text = str(duration_str) if duration_str else "??:??"
        dw = draw.textlength(dur_text, font=small_font)
        draw.text((bar_x1 - dw, bar_y + 15), dur_text, font=small_font, fill=(230, 230, 230, 255))

        # simple control glyphs (decorative only)
        controls = "⏮   ⏯   ⏭   🔁"
        cf = _load_font(30)
        cw = draw.textlength(controls, font=cf)
        draw.text(((W - cw) / 2, bar_y + 50), controls, font=cf, fill=(255, 255, 255, 255))

        buf = io.BytesIO()
        buf.name = "now_playing.png"
        bg.save(buf, format="PNG")
        buf.seek(0)
        return buf
    except Exception as e:
        LOGGER.warning(f"Now playing card generation fail: {e}")
        return None
