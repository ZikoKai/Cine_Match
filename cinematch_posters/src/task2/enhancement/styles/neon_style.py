"""Style nÃ©on / cyberpunk"""

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from typing import List, Optional
import random

from task2.enhancement.styles.base_style import BaseEnhancementStyle
from task2.utils.logger import get_logger

logger = get_logger(__name__)


class NeonStyle(BaseEnhancementStyle):
    """Style nÃ©on cyberpunk pour Sci-Fi/Action"""
    
    async def enhance(self, img: Image.Image, title: str, genres: List[str], year: Optional[int] = None) -> Image.Image:
        """Applique le style nÃ©on"""
        
        img = self._resize_cinematic(img)
        img = self._apply_neon_grading(img)
        img = ImageEnhance.Contrast(img).enhance(1.3)
        img = ImageEnhance.Color(img).enhance(1.4)
        
        text_layer = self._add_neon_typography(img, title, year, genres)
        text_layer = self._add_neon_grid(text_layer)
        text_layer = self._add_neon_particles(text_layer)
        
        return Image.alpha_composite(img, text_layer).convert("RGB")
    
    def _apply_neon_grading(self, img: Image.Image) -> Image.Image:
        """Ã‰talonnage cyberpunk"""
        img = ImageEnhance.Color(img).enhance(1.35)
        img = ImageEnhance.Contrast(img).enhance(1.25)
        return img
    
    def _add_neon_typography(self, img: Image.Image, title: str, year: Optional[int], genres: List[str]) -> Image.Image:
        """Typographie nÃ©on"""
        width, height = img.size
        layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        
        fonts = self._get_fonts(width)
        
        # Grille de fond
        grid_spacing = 50
        neon_color = (0, 200, 255)
        for x in range(0, width, grid_spacing):
            draw.line([(x, 0), (x, height)], fill=(neon_color[0], neon_color[1], neon_color[2], 30), width=1)
        for y in range(0, height, grid_spacing):
            draw.line([(0, y), (width, y)], fill=(neon_color[0], neon_color[1], neon_color[2], 30), width=1)
        
        # Titre nÃ©on
        title_upper = title.upper()
        title_bbox = draw.textbbox((0, 0), title_upper, font=fonts["title"])
        tw, th = title_bbox[2] - title_bbox[0], title_bbox[3] - title_bbox[1]
        
        tx, ty = (width - tw) // 2, height - 200
        
        # Effet nÃ©on (multiples couches)
        for offset, alpha, blur in [(4, 50, 8), (2, 100, 4), (0, 255, 0)]:
            glow_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_layer)
            glow_draw.text((tx + offset, ty + offset), title_upper, 
                          font=fonts["title"], fill=(neon_color[0], neon_color[1], neon_color[2], alpha))
            if blur > 0:
                glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(blur))
            layer = Image.alpha_composite(layer, glow_layer)
        
        return layer
    
    def _add_neon_grid(self, layer: Image.Image) -> Image.Image:
        """Ajoute une grille cyberpunk"""
        draw = ImageDraw.Draw(layer)
        width, height = layer.size
        
        # Cercles nÃ©on
        for _ in range(3):
            cx, cy = random.randint(0, width), random.randint(0, height)
            radius = random.randint(100, 300)
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], 
                        outline=(0, 200, 255, 80), width=2)
        
        return layer
    
    def _add_neon_particles(self, layer: Image.Image) -> Image.Image:
        """Ajoute des particules lumineuses"""
        draw = ImageDraw.Draw(layer)
        width, height = layer.size
        
        for _ in range(100):
            x, y = random.randint(0, width), random.randint(0, height)
            radius = random.uniform(1, 3)
            alpha = random.randint(50, 150)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), 
                        fill=(0, 200, 255, alpha))
        
        return layer
