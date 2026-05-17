"""Style vintage / rÃ©tro"""

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from typing import List, Optional
import random

from task2.enhancement.styles.base_style import BaseEnhancementStyle
from task2.utils.logger import get_logger

logger = get_logger(__name__)


class VintageStyle(BaseEnhancementStyle):
    """Style vintage avec grain et sÃ©pia"""
    
    async def enhance(self, img: Image.Image, title: str, genres: List[str], year: Optional[int] = None) -> Image.Image:
        """Applique le style vintage"""
        
        img = self._resize_cinematic(img)
        img = self._apply_vintage_grading(img)
        img = self._apply_film_grain(img, intensity=0.05)
        img = img.convert("RGBA")  # Ensure RGBA for alpha_composite operations
        img = self._add_vignette(img, intensity=150)
        
        text_layer = self._add_vintage_typography(img, title, year, genres)
        text_layer = self._add_vintage_scratches(text_layer)
        
        return Image.alpha_composite(img, text_layer).convert("RGB")
    
    def _apply_vintage_grading(self, img: Image.Image) -> Image.Image:
        """Ã‰talonnage vintage sÃ©pia"""
        # Convert to RGB first so Image.blend works with RGB sepia layer
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        sepia = Image.new('RGB', img.size, (210, 180, 140))
        img = Image.blend(img, sepia, 0.15)
        img = ImageEnhance.Color(img).enhance(0.85)
        img = ImageEnhance.Contrast(img).enhance(1.1)
        return img
    
    def _add_vintage_typography(self, img: Image.Image, title: str, year: Optional[int], genres: List[str]) -> Image.Image:
        """Typographie vintage"""
        width, height = img.size
        layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        
        fonts = self._get_fonts(width)
        
        # Bordure dÃ©corative
        border = 30
        draw.rectangle([(border, border), (width - border, height - border)], 
                       outline=(255, 215, 0), width=2)
        
        # Titre
        title_upper = title.upper()
        title_bbox = draw.textbbox((0, 0), title_upper, font=fonts["title"])
        tw, th = title_bbox[2] - title_bbox[0], title_bbox[3] - title_bbox[1]
        
        tx, ty = (width - tw) // 2, height - 200
        
        # Effet vieilli sur le texte
        draw.text((tx + 2, ty + 2), title_upper, font=fonts["title"], fill=(100, 60, 20, 200))
        draw.text((tx, ty), title_upper, font=fonts["title"], fill=(218, 165, 32, 255))
        
        # AnnÃ©e en bas
        if year:
            year_text = str(year)
            year_bbox = draw.textbbox((0, 0), year_text, font=fonts["info"])
            yw = year_bbox[2] - year_bbox[0]
            draw.text(((width - yw) // 2, height - 80), year_text, font=fonts["info"], fill=(255, 215, 0, 200))
        
        return layer
    
    def _add_vintage_scratches(self, layer: Image.Image, count: int = 8) -> Image.Image:
        """Ajoute des rayures vintage"""
        draw = ImageDraw.Draw(layer)
        width, height = layer.size
        
        for _ in range(count):
            x = random.randint(0, width)
            y1 = random.randint(0, height)
            y2 = random.randint(y1, min(y1 + 80, height))
            alpha = random.randint(15, 50)
            draw.line([(x, y1), (x, y2)], fill=(255, 255, 255, alpha), width=random.randint(1, 2))
        
        return layer
