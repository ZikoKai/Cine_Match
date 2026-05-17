"""Fallback Canvas quand DALLÂ·E Ã©choue"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import List, Tuple, Optional
import random
import math
from io import BytesIO
import os
from task2.utils.logger import get_logger

logger = get_logger(__name__)


class CanvasFallback:
    """GÃ©nÃ©rateur d'affiches de secours avec design stylisÃ©"""
    
    GENRE_COLORS = {
        "Action": "#FF4444",
        "Comedy": "#FFD700",
        "Drama": "#4A4A4A",
        "Horror": "#2B0000",
        "Sci-Fi": "#00BFFF",
        "Romance": "#FF69B4",
        "Thriller": "#1A1A1A",
        "Fantasy": "#9B59B6",
        "Documentary": "#E67E22",
        "Crime": "#2C3E50",
        "Adventure": "#27AE60",
        "Animation": "#FF6B9D",
        "Mystery": "#5D4E99",
        "default": "#34495E"
    }
    
    # Formes gÃ©omÃ©triques pour le design
    SHAPES = ['circle', 'line', 'triangle', 'diamond']
    
    def __init__(self):
        """Initialise le gÃ©nÃ©rateur avec recherche de polices"""
        self.font_path = self._find_font()
        
    def _find_font(self) -> str:
        """Trouve une police systÃ¨me disponible"""
        possible_fonts = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:\\Windows\\Fonts\\Arial.ttf",
            "arial.ttf"
        ]
        
        for font in possible_fonts:
            if os.path.exists(font):
                return font
        return None
    
    def _get_color(self, hex_color: str) -> Tuple[int, int, int]:
        """Convertit hex en RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _draw_gradient(
        self, 
        draw: ImageDraw.Draw, 
        width: int, 
        height: int, 
        start_color: Tuple[int, int, int],
        end_color: Tuple[int, int, int]
    ):
        """Dessine un dÃ©gradÃ© vertical"""
        for y in range(height):
            ratio = y / height
            r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
            g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
            b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    def _draw_shape(
        self, 
        draw: ImageDraw.Draw, 
        width: int, 
        height: int,
        color: Tuple[int, int, int, int]
    ):
        """Dessine une forme gÃ©omÃ©trique alÃ©atoire"""
        shape = random.choice(self.SHAPES)
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(50, 300)
        
        if shape == 'circle':
            draw.ellipse(
                [x - size//2, y - size//2, x + size//2, y + size//2],
                outline=color,
                width=random.randint(2, 8)
            )
        elif shape == 'line':
            x2 = x + random.randint(-200, 200)
            y2 = y + random.randint(-200, 200)
            draw.line([(x, y), (x2, y2)], fill=color, width=random.randint(2, 10))
        elif shape == 'triangle':
            points = [
                (x, y - size//2),
                (x - size//2, y + size//2),
                (x + size//2, y + size//2)
            ]
            draw.polygon(points, outline=color, width=random.randint(2, 6))
        elif shape == 'diamond':
            points = [
                (x, y - size//2),
                (x + size//2, y),
                (x, y + size//2),
                (x - size//2, y)
            ]
            draw.polygon(points, outline=color, width=random.randint(2, 6))
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Coupe le texte pour qu'il tienne dans la largeur donnÃ©e"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    async def generate(self, title: str, genres: List[str], size: Tuple[int, int] = (1024, 1536)) -> bytes:
        """
        GÃ©nÃ¨re une affiche stylisÃ©e de secours
        
        Args:
            title: Titre du film
            genres: Liste des genres
            size: Dimensions (width, height)
        """
        logger.info(f"ðŸŽ¨ Fallback Canvas pour: {title} (Genres: {', '.join(genres[:2])})")
        
        width, height = size
        img = Image.new('RGB', (width, height), color='#000000')
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Couleur principale basÃ©e sur le premier genre
        main_genre = genres[0] if genres else "default"
        accent_color = self.GENRE_COLORS.get(main_genre, self.GENRE_COLORS["default"])
        start_rgb = self._get_color(accent_color)
        
        # DÃ©gradÃ© sophistiquÃ© (accent -> noir)
        end_rgb = (min(start_rgb[0] // 4, 30), 
                   min(start_rgb[1] // 4, 30), 
                   min(start_rgb[2] // 4, 30))
        
        self._draw_gradient(draw, width, height, start_rgb, end_rgb)
        
        # Effet de vignette
        for i in range(100):
            alpha = int(100 * (1 - i/100))
            draw.ellipse(
                [width//2 - width//2 * (1 - i/100), 
                 height//2 - height//2 * (1 - i/100),
                 width//2 + width//2 * (1 - i/100),
                 height//2 + height//2 * (1 - i/100)],
                outline=(0, 0, 0, alpha),
                width=2
            )
        
        # Ã‰lÃ©ments dÃ©coratifs
        accent_alpha = (255, 255, 255, random.randint(30, 60))
        shape_count = random.randint(8, 15)
        for _ in range(shape_count):
            self._draw_shape(draw, width, height, accent_alpha)
        
        # Cercles lumineux
        for _ in range(random.randint(3, 7)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            r = random.randint(20, 80)
            alpha = random.randint(10, 30)
            draw.ellipse([x-r, y-r, x+r, y+r], fill=(255, 255, 255, alpha))
        
        # Configuration des polices
        title_font_size = min(80, width // 15)
        genre_font_size = min(40, width // 25)
        
        try:
            if self.font_path:
                title_font = ImageFont.truetype(self.font_path, title_font_size)
                genre_font = ImageFont.truetype(self.font_path, genre_font_size)
            else:
                title_font = ImageFont.load_default()
                genre_font = ImageFont.load_default()
        except Exception:
            title_font = ImageFont.load_default()
            genre_font = ImageFont.load_default()
        
        # Titre (wrap si nÃ©cessaire)
        max_title_width = width - 100
        title_lines = self._wrap_text(title.upper(), title_font, max_title_width)
        title_total_height = len(title_lines) * title_font_size
        title_y = (height // 2) - (title_total_height // 2)
        
        for i, line in enumerate(title_lines):
            bbox = title_font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (width - text_width) // 2
            y = title_y + (i * title_font_size)
            
            # Ombre
            for offset in [(2, 2), (1, 1)]:
                draw.text((x + offset[0], y + offset[1]), line, fill=(0, 0, 0), font=title_font)
            
            # Texte principal avec effet de contour lÃ©ger
            draw.text((x, y), line, fill=(255, 255, 255), font=title_font)
            
            # Petit contour avec couleur d'accent
            accent_color_rgb = self._get_color(accent_color)
            draw.text((x-1, y), line, fill=accent_color_rgb, font=title_font)
            draw.text((x+1, y), line, fill=accent_color_rgb, font=title_font)
            draw.text((x, y-1), line, fill=accent_color_rgb, font=title_font)
            draw.text((x, y+1), line, fill=accent_color_rgb, font=title_font)
            draw.text((x, y), line, fill=(255, 255, 255), font=title_font)
        
        # Genres en bas
        if genres:
            genres_text = " â€¢ ".join(g.upper() for g in genres[:4])
            bbox = genre_font.getbbox(genres_text)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = height - 120
            
            # Fond sombre pour les genres
            padding = 20
            draw.rectangle(
                [x - padding, y - 15, x + text_width + padding, y + 40],
                fill=(0, 0, 0, 180),
                outline=accent_color_rgb,
                width=2
            )
            
            draw.text((x, y), genres_text, fill=(255, 255, 255), font=genre_font)
        
        # Petite bande cinÃ©ma en bas
        band_height = 8
        draw.rectangle([0, height - band_height, width, height], fill=accent_color_rgb)
        
        # Convertir en bytes
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG', optimize=True)
        
        logger.info(f"  âœ… Affiche gÃ©nÃ©rÃ©e: {width}x{height}")
        return img_buffer.getvalue()
