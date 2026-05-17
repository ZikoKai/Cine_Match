"""
Dark Neo-Noir Cinematic Poster Style
"""

from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageOps
)

from typing import List, Optional

from task2.enhancement.styles.base_style import BaseEnhancementStyle
from task2.utils.logger import get_logger

logger = get_logger(__name__)


class NeoNoirStyle(BaseEnhancementStyle):
    """
    Dark neo-noir cinematic poster style
    """

    async def enhance(
        self,
        img: Image.Image,
        title: str,
        genres: List[str],
        year: Optional[int] = None
    ) -> Image.Image:

        # ---------------------------------------------------
        # Base
        # ---------------------------------------------------

        img = self._resize_cinematic(img).convert("RGBA")

        # ---------------------------------------------------
        # Neo-noir grading
        # ---------------------------------------------------

        img = self._apply_neonoir_grading(img)

        # ---------------------------------------------------
        # Atmosphere
        # ---------------------------------------------------

        img = self._add_dark_gradient(img)
        img = self._add_bloom(img)
        img = self._apply_film_grain(img, intensity=0.03)

        # ---------------------------------------------------
        # Typography
        # ---------------------------------------------------

        text_layer = self._add_noir_typography(
            img,
            title,
            year,
            genres
        )

        # ---------------------------------------------------
        # Composite
        # ---------------------------------------------------

        final = Image.alpha_composite(img, text_layer)

        return final.convert("RGB")

    # =====================================================
    # NEO-NOIR GRADING
    # =====================================================

    def _apply_neonoir_grading(self, img: Image.Image) -> Image.Image:

        img = ImageEnhance.Contrast(img).enhance(1.35)
        img = ImageEnhance.Color(img).enhance(0.85)
        img = ImageEnhance.Sharpness(img).enhance(1.15)

        r, g, b, a = img.split()

        # Boost blue channel slightly
        b = ImageEnhance.Brightness(b).enhance(1.15)

        # Slight red neon tint
        r = ImageEnhance.Brightness(r).enhance(1.08)

        return Image.merge("RGBA", (r, g, b, a))

    # =====================================================
    # DARK GRADIENT
    # =====================================================

    def _add_dark_gradient(self, img: Image.Image) -> Image.Image:

        width, height = img.size

        gradient = Image.new("L", (1, height))

        for y in range(height):
            value = int(255 * (y / height))
            gradient.putpixel((0, y), value)

        gradient = gradient.resize((width, height))

        overlay = Image.new(
            "RGBA",
            (width, height),
            (0, 0, 0, 180)
        )

        overlay.putalpha(gradient)

        return Image.alpha_composite(img, overlay)

    # =====================================================
    # BLOOM EFFECT
    # =====================================================

    def _add_bloom(self, img: Image.Image) -> Image.Image:

        blurred = img.filter(
            ImageFilter.GaussianBlur(radius=8)
        )

        return Image.blend(img, blurred, alpha=0.18)

    # =====================================================
    # TYPOGRAPHY
    # =====================================================

    def _add_noir_typography(
        self,
        img: Image.Image,
        title: str,
        year: Optional[int],
        genres: List[str]
    ) -> Image.Image:

        width, height = img.size

        layer = Image.new(
            "RGBA",
            (width, height),
            (0, 0, 0, 0)
        )

        draw = ImageDraw.Draw(layer)

        fonts = self._get_fonts(width)

        # ---------------------------------------------------
        # TITLE
        # ---------------------------------------------------

        title = title.upper()

        bbox = draw.textbbox(
            (0, 0),
            title,
            font=fonts["title"]
        )

        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        tx = (width - tw) // 2
        ty = int(height * 0.78)

        # red glow shadow
        draw.text(
            (tx + 4, ty + 4),
            title,
            font=fonts["title"],
            fill=(255, 40, 40, 120)
        )

        # white main title
        draw.text(
            (tx, ty),
            title,
            font=fonts["title"],
            fill=(245, 245, 245, 255)
        )

        # ---------------------------------------------------
        # INFO
        # ---------------------------------------------------

        info = []

        if year:
            info.append(str(year))

        if genres:
            info.append(" â€¢ ".join(genres[:2]).upper())

        info_text = "   ".join(info)

        info_bbox = draw.textbbox(
            (0, 0),
            info_text,
            font=fonts["info"]
        )

        iw = info_bbox[2] - info_bbox[0]

        ix = (width - iw) // 2
        iy = ty + th + 25

        draw.text(
            (ix, iy),
            info_text,
            font=fonts["info"],
            fill=(180, 180, 180, 180)
        )

        return layer
