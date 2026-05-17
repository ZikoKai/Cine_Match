"""Module principal d'amÃ©lioration d'images - Version refactorisÃ©e"""

from PIL import Image
from typing import List, Optional
from pathlib import Path

from task2.enhancement.styles.cinematic_style import CinematicStyle
from task2.enhancement.styles.minimal_style import MinimalStyle
from task2.enhancement.styles.vintage_style import VintageStyle
from task2.enhancement.styles.neon_style import NeonStyle
from task2.enhancement.styles.neo_noir_style import NeoNoirStyle
from task2.utils.logger import get_logger

logger = get_logger(__name__)


class ImageEnhancer:
    """
    PROFESSIONAL CINEMATIC POSTER ENGINE
    Styles disponibles: cinematic, minimal, vintage, neon, neonoir
    """
    
    def __init__(self):
        self.output_dir = Path("enhanced_posters")
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialiser les styles
        self.styles = {
            "cinematic": CinematicStyle(),
            "minimal": MinimalStyle(),
            "vintage": VintageStyle(),
            "neon": NeonStyle(),
            "neo_noir": NeoNoirStyle()
        }
    
    async def enhance_poster(
        self,
        image_path: str,
        title: str,
        genres: List[str],
        year: Optional[int] = None,
        style: str = "cinematic"
    ) -> Optional[str]:
        """
        AmÃ©liore l'affiche avec le style choisi
        
        Args:
            image_path: Chemin de l'image source
            title: Titre du film
            genres: Liste des genres
            year: AnnÃ©e de sortie
            style: Style ("cinematic", "minimal", "vintage", "neon", "neonoir")
        """
        try:
            logger.info(f"ðŸŽ¬ Enhancement: {title} (style: {style})")
            logger.info(f"   Genres: {', '.join(genres[:3])}")
            
            # VÃ©rifier que le style existe
            if style not in self.styles:
                logger.warning(f"Style '{style}' inconnu, utilisation de 'cinematic'")
                style = "cinematic"
            
            # Charger l'image
            with Image.open(image_path).convert("RGBA") as img:
                # Appliquer le style
                style_instance = self.styles[style]
                final_img = await style_instance.enhance(img, title, genres, year)
                
                # Sauvegarder
                style_suffix = f"_{style}" if style != "cinematic" else ""
                output_path = self.output_dir / f"final_{Path(image_path).stem}{style_suffix}.jpg"
                
                final_img.save(output_path, "JPEG", quality=95, optimize=True)
                
                size_kb = output_path.stat().st_size / 1024
                logger.info(f"âœ¨ Poster ready: {output_path} ({size_kb:.1f} KB)")
                
                return str(output_path)
                
        except Exception as e:
            logger.error(f"âŒ Enhancement error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_available_styles(self) -> List[str]:
        """Retourne la liste des styles disponibles"""
        return list(self.styles.keys())

