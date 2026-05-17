"""Classe de base pour tous les styles d'amÃ©lioration"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
from typing import List, Optional, Tuple
from pathlib import Path
import numpy as np
import random
import os
import math

from task2.utils.logger import get_logger

logger = get_logger(__name__)


class BaseEnhancementStyle:
    """Classe de base pour les styles d'amÃ©lioration"""
    
    def __init__(self):
        self.genre_palettes = self._init_genre_palettes()
        self.fonts_dir = Path("fonts")
        self.fonts_dir.mkdir(exist_ok=True)
    
    def _init_genre_palettes(self) -> dict:
        """Initialise les palettes de couleurs par genre"""
        return {
            "Sci-Fi": {
                "overlay": (0, 120, 255, 35),
                "glow": (0, 200, 255),
                "text": (220, 240, 255),
            },
            "Horror": {
                "overlay": (120, 0, 0, 45),
                "glow": (255, 0, 0),
                "text": (255, 220, 220),
            },
            "Fantasy": {
                "overlay": (120, 90, 20, 35),
                "glow": (255, 210, 100),
                "text": (255, 245, 220),
            },
            "Action": {
                "overlay": (255, 120, 0, 30),
                "glow": (255, 170, 0),
                "text": (255, 255, 255),
            },
            "Drama": {
                "overlay": (50, 50, 80, 40),
                "glow": (180, 180, 220),
                "text": (240, 240, 255),
            },
            "Romance": {
                "overlay": (255, 100, 150, 30),
                "glow": (255, 150, 200),
                "text": (255, 240, 245),
            },
            "Thriller": {
                "overlay": (30, 40, 60, 50),
                "glow": (100, 150, 200),
                "text": (220, 230, 255),
            },
            "Comedy": {
                "overlay": (255, 200, 50, 25),
                "glow": (255, 220, 100),
                "text": (255, 255, 240),
            },
            "Crime": {
                "overlay": (40, 40, 60, 45),
                "glow": (150, 150, 180),
                "text": (230, 230, 250),
            },
            "Adventure": {
                "overlay": (255, 140, 0, 30),
                "glow": (255, 180, 80),
                "text": (255, 255, 230),
            }
        }
    
    async def enhance(self, img: Image.Image, title: str, genres: List[str], year: Optional[int] = None) -> Image.Image:
        """MÃ©thode principale Ã  implÃ©menter par chaque style"""
        raise NotImplementedError
    
    def _resize_cinematic(self, img: Image.Image, size: Tuple[int, int] = (1000, 1500)) -> Image.Image:
        """Redimensionne au format cinÃ©matique"""
        return img.resize(size, Image.LANCZOS)
    
    def _get_fonts(self, width: int) -> dict:
        """Charge les polices professionnelles"""
        possible_fonts = [
            "fonts/BebasNeue-Regular.ttf",
            "fonts/Anton-Regular.ttf",
            "fonts/Montserrat-ExtraBold.ttf",
            "fonts/PlayfairDisplay-Bold.ttf",
            "C:\\Windows\\Fonts\\arialbd.ttf",
            "C:\\Windows\\Fonts\\impact.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]

        font_path = None
        for path in possible_fonts:
            if os.path.exists(path):
                font_path = path
                break

        if font_path:
            try:
                return {
                    "title": ImageFont.truetype(font_path, int(width * 0.065)),
                    "info": ImageFont.truetype(font_path, int(width * 0.022))
                }
            except Exception as e:
                logger.warning(f"Erreur chargement police: {e}")

        return {
            "title": ImageFont.load_default(),
            "info": ImageFont.load_default()
        }
    
    def _add_vignette(self, img: Image.Image, intensity: int = 170) -> Image.Image:
        """Ajoute une vignette"""
        width, height = img.size
        vignette = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(vignette)
        
        max_dim = max(width, height)
        for i in range(max_dim):
            alpha = int(255 * (1 - i / max_dim) ** 2.5)
            draw.ellipse((-i, -i, width + i, height + i), fill=alpha)
        
        vignette = vignette.filter(ImageFilter.GaussianBlur(100))
        black = Image.new("RGBA", (width, height), (0, 0, 0, intensity))
        black.putalpha(vignette)
        
        return Image.alpha_composite(img, black)
    
    def _apply_film_grain(self, img: Image.Image, intensity: float = 0.03) -> Image.Image:
        """Ajoute du grain film"""
        if img.mode == 'RGBA':
            rgb_img = img.convert('RGB')
        else:
            rgb_img = img
        
        arr = np.array(rgb_img).astype(np.int16)
        noise = np.random.normal(0, 255 * intensity, arr.shape)
        noise += np.random.randint(-12, 12, arr.shape) * intensity
        arr = np.clip(arr + noise, 0, 255)
        
        result = Image.fromarray(arr.astype(np.uint8))
        
        if img.mode == 'RGBA':
            result = result.convert('RGBA')
            result.putalpha(img.getchannel('A'))
        
        return result
