"""
Minimal Cinematic Poster Style
Premium clean poster aesthetic
"""

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
from typing import List, Optional


from task2.enhancement.styles.base_style import BaseEnhancementStyle
from task2.utils.logger import get_logger

logger = get_logger(__name__)


class MinimalStyle(BaseEnhancementStyle):
    """
    Premium minimalist cinematic poster style
    Inspired by:
    - A24 posters
    - Netflix key art
    - Modern theatrical one-sheets
    """

    async def enhance(
        self,
        img: Image.Image,
        title: str,
        genres: List[str],
        year: Optional[int] = None
    ) -> Image.Image:

        # ---------------------------------------------------
        # Base cinematic resize
        # ---------------------------------------------------

        img = self._resize_cinematic(img).convert("RGBA")

        # ---------------------------------------------------
        # Cinematic grading
        # ---------------------------------------------------

        img = self._apply_color_grading(img, genres)

        # ---------------------------------------------------
        # Atmospheric polish
        # ---------------------------------------------------

        img = self._add_vignette(img, strength=0.18)
        img = self._apply_film_grain(img, intensity=0.015)

        # ---------------------------------------------------
        # Typography
        # ---------------------------------------------------

        text_layer = self._add_minimal_typography(
            img,
            title,
            year,
            genres
        )

        # ---------------------------------------------------
        # Final composite
        # ---------------------------------------------------

        final = Image.alpha_composite(img, text_layer)

        return final.convert("RGB")

    # =====================================================
    # COLOR GRADING
    # =====================================================

    def _apply_color_grading(
        self,
        img: Image.Image,
        genres: List[str]
    ) -> Image.Image:
        """
        Soft cinematic grading
        """

        img = ImageEnhance.Contrast(img).enhance(1.12)
        img = ImageEnhance.Color(img).enhance(0.95)
        img = ImageEnhance.Brightness(img).enhance(1.02)
        img = ImageEnhance.Sharpness(img).enhance(1.08)

        return img

    # =====================================================
    # VIGNETTE
    # =====================================================

    def _add_vignette(
        self,
        img: Image.Image,
        strength: float = 0.15
    ) -> Image.Image:
        """
        Subtle cinematic vignette
        """

        width, height = img.size

        vignette = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(vignette)

        margin = int(min(width, height) * 0.08)

        draw.ellipse(
            (-margin, -margin, width + margin, height + margin),
            fill=255
        )

        vignette = vignette.filter(ImageFilter.GaussianBlur(radius=width // 5))

        overlay = Image.new(
            "RGBA",
            (width, height),
            (0, 0, 0, int(255 * strength))
        )

        overlay.putalpha(
            ImageOps.invert(vignette)
        )

        return Image.alpha_composite(img, overlay)

    # =====================================================
    # TYPOGRAPHY
    # =====================================================

    def _add_minimal_typography(
        self,
        img: Image.Image,
        title: str,
        year: Optional[int],
        genres: List[str]
    ) -> Image.Image:

        width, height = img.size

        layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)

        fonts = self._get_fonts(width)

        # ---------------------------------------------------
        # TITLE
        # ---------------------------------------------------

        title_upper = title.upper()

        title_bbox = draw.textbbox(
            (0, 0),
            title_upper,
            font=fonts["title"]
        )

        tw = title_bbox[2] - title_bbox[0]
        th = title_bbox[3] - title_bbox[1]

        tx = (width - tw) // 2
        ty = int(height * 0.72)

        # subtle shadow
        draw.text(
            (tx + 3, ty + 3),
            title_upper,
            font=fonts["title"],
            fill=(0, 0, 0, 120)
        )

        # clean title
        draw.text(
            (tx, ty),
            title_upper,
            font=fonts["title"],
            fill=(255, 255, 255, 245)
        )

        # ---------------------------------------------------
        # SUB INFO
        # ---------------------------------------------------

        info_parts = []

        if year:
            info_parts.append(str(year))

        if genres:
            info_parts.append(" â€¢ ".join(genres[:2]).upper())

        info_text = "   ".join(info_parts)

        info_bbox = draw.textbbox(
            (0, 0),
            info_text,
            font=fonts["info"]
        )

        iw = info_bbox[2] - info_bbox[0]

        ix = (width - iw) // 2
        iy = ty + th + 30

        draw.text(
            (ix, iy),
            info_text,
            font=fonts["info"],
            fill=(220, 220, 220, 180)
        )

        # ---------------------------------------------------
        # TOP ACCENT LINE
        # ---------------------------------------------------

        line_width = int(width * 0.18)

        lx1 = (width - line_width) // 2
        lx2 = lx1 + line_width

        ly = ty - 40

        draw.line(
            [(lx1, ly), (lx2, ly)],
            fill=(255, 255, 255, 120),
            width=2
        )

        return layer
