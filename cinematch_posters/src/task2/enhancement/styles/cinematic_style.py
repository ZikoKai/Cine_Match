"""Style cinÃ©matique classique (Netflix, Marvel, IMAX)"""

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
from typing import List, Optional
import random

from task2.enhancement.styles.base_style import BaseEnhancementStyle
from task2.utils.logger import get_logger

logger = get_logger(__name__)


class CinematicStyle(BaseEnhancementStyle):
    """Style cinÃ©matique Ã©pique avec effets hollywoodiens"""
    
    async def enhance(self, img: Image.Image, title: str, genres: List[str], year: Optional[int] = None) -> Image.Image:
        """Applique le style cinÃ©matique"""
        
        # Redimensionnement
        img = self._resize_cinematic(img)
        
        # Color grading
        img = self._apply_color_grading(img, genres)
        
        # Effets cinÃ©matographiques
        img = self._add_cinematic_overlay(img, genres)
        img = self._add_bloom(img)
        img = self._add_light_glow(img)
        img = self._add_depth_blur(img)
        img = self._apply_film_grain(img, intensity=0.03)
        img = self._add_vignette(img, intensity=170)
        img = self._add_lens_distortion(img)
        
        # Typographie
        text_layer = self._add_cinematic_typography(img, title, year, genres)
        
        # Particules
        text_layer = self._add_particles(text_layer, count=160)
        text_layer = self._add_sparks(text_layer)
        
        # Fusion finale
        return Image.alpha_composite(img, text_layer).convert("RGB")
    
    def _apply_color_grading(self, img: Image.Image, genres: List[str]) -> Image.Image:
        """Applique l'Ã©talonnage couleur"""
        img = ImageEnhance.Contrast(img).enhance(1.2)
        img = ImageEnhance.Sharpness(img).enhance(1.15)
        img = ImageEnhance.Color(img).enhance(1.1)
        img = ImageEnhance.Brightness(img).enhance(0.98)
        
        genre_grading = {
            "Horror": (0.7, 1.3, 0.85),
            "Sci-Fi": (1.35, 1.25, 1.0),
            "Fantasy": (1.2, 1.0, 1.05),
            "Action": (1.0, 1.35, 1.4),
            "Drama": (0.9, 1.15, 0.95),
        }
        
        for genre in genres:
            if genre in genre_grading:
                color, contrast, sharpness = genre_grading[genre]
                img = ImageEnhance.Color(img).enhance(color)
                img = ImageEnhance.Contrast(img).enhance(contrast)
                img = ImageEnhance.Sharpness(img).enhance(sharpness)
                break
        
        return img
    
    def _add_cinematic_overlay(self, img: Image.Image, genres: List[str]) -> Image.Image:
        """Ajoute un overlay colorÃ©"""
        overlay_color = (10, 15, 25, 35)
        for genre in genres:
            if genre in self.genre_palettes:
                overlay_color = self.genre_palettes[genre]["overlay"]
                break
        overlay = Image.new("RGBA", img.size, overlay_color)
        return Image.alpha_composite(img, overlay)
    
    def _add_bloom(self, img: Image.Image, radius: int = 18, intensity: float = 0.16) -> Image.Image:
        """Effet bloom"""
        blur = img.filter(ImageFilter.GaussianBlur(radius))
        return Image.blend(img, blur, intensity)
    
    def _add_light_glow(self, img: Image.Image, radius: int = 45, intensity: float = 0.08) -> Image.Image:
        """Lueur lumineuse"""
        glow = img.filter(ImageFilter.GaussianBlur(radius))
        return Image.blend(img, glow, intensity)
    
    def _add_depth_blur(self, img: Image.Image, radius: int = 3, intensity: float = 0.08) -> Image.Image:
        """Flou de profondeur"""
        blurred = img.filter(ImageFilter.GaussianBlur(radius))
        return Image.blend(img, blurred, intensity)
    
    def _add_lens_distortion(self, img: Image.Image) -> Image.Image:
        """Distorsion de lentille"""
        r, g, b, a = img.split()
        r_offset = ImageChops.offset(r, 2, 0)
        b_offset = ImageChops.offset(b, -2, 0)
        chromatic = Image.merge('RGBA', (r_offset, g, b_offset, a))
        return Image.blend(img, chromatic, 0.08)
    
    def _add_cinematic_typography(self, img: Image.Image, title: str, year: Optional[int], genres: List[str]) -> Image.Image:
        """Typographie cinÃ©matique"""
        width, height = img.size
        layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        
        # Gradient bottom
        gradient_height = int(height * 0.42)
        for y in range(gradient_height):
            t = y / gradient_height
            alpha = int(240 * (t ** 1.8))
            draw.line([(0, height - y), (width, height - y)], fill=(0, 0, 0, alpha))
        
        fonts = self._get_fonts(width)
        
        # Titre avec espacement
        title_upper = title.upper()
        if len(title_upper) < 10:
            spaced_title = "   ".join(title_upper)
        elif len(title_upper) < 15:
            spaced_title = "  ".join(title_upper)
        else:
            spaced_title = " ".join(title_upper)
        
        title_bbox = draw.textbbox((0, 0), spaced_title, font=fonts["title"])
        tw, th = title_bbox[2] - title_bbox[0], title_bbox[3] - title_bbox[1]
        tx, ty = (width - tw) // 2, height - int(height * 0.19) - (th // 2)
        
        # Glow
        glow_layer = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        glow_color = (255, 255, 255, 120)
        for genre in genres:
            if genre in self.genre_palettes:
                glow_color = self.genre_palettes[genre]["glow"] + (100,)
                break
        glow_draw.text((tx, ty), spaced_title, font=fonts["title"], fill=glow_color)
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(15))
        layer = Image.alpha_composite(layer, glow_layer)
        
        draw = ImageDraw.Draw(layer)
        draw.text((tx + 3, ty + 3), spaced_title, font=fonts["title"], fill=(0, 0, 0, 200))
        
        title_color = (255, 255, 255, 255)
        for genre in genres:
            if genre in self.genre_palettes:
                title_color = self.genre_palettes[genre]["text"] + (255,)
                break
        draw.text((tx, ty), spaced_title, font=fonts["title"], fill=title_color)
        
        # Info text
        info_parts = [str(year)] if year else []
        info_parts.append("â€¢".join(genres[:3]).upper())
        info_text = "   â€¢   ".join(info_parts)
        
        info_bbox = draw.textbbox((0, 0), info_text, font=fonts["info"])
        iw = info_bbox[2] - info_bbox[0]
        ix, iy = (width - iw) // 2, height - int(height * 0.09)
        
        draw.text((ix + 2, iy + 2), info_text, font=fonts["info"], fill=(0, 0, 0, 180))
        draw.text((ix, iy), info_text, font=fonts["info"], fill=(210, 210, 210, 240))
        
        return layer
    
    def _add_particles(self, layer: Image.Image, count: int = 160) -> Image.Image:
        """Ajoute des particules"""
        draw = ImageDraw.Draw(layer)
        width, height = layer.size
        
        for _ in range(count):
            x, y = random.randint(0, width), random.randint(0, height)
            radius = random.uniform(0.5, 2.5)
            alpha = random.randint(10, 60)
            if y > height * 0.7:
                alpha = min(alpha + 20, 80)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(255, 255, 255, alpha))
        
        return layer
    
    def _add_sparks(self, layer: Image.Image, count: int = 30) -> Image.Image:
        """Ajoute des Ã©tincelles"""
        draw = ImageDraw.Draw(layer)
        width, height = layer.size
        
        for _ in range(count):
            x, y = random.randint(0, width), random.randint(int(height * 0.4), int(height * 0.8))
            size, alpha = random.randint(2, 4), random.randint(80, 180)
            draw.line([(x - size, y), (x + size, y)], fill=(255, 200, 100, alpha), width=1)
            draw.line([(x, y - size), (x, y + size)], fill=(255, 200, 100, alpha), width=1)
        
        return layer
