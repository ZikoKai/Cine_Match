"""Stockage local des images gÃ©nÃ©rÃ©es"""

from pathlib import Path
from typing import Optional
from datetime import datetime
from task2.utils.logger import get_logger

logger = get_logger(__name__)


class LocalStorage:
    """Gestionnaire de stockage local"""
    
    def __init__(self, base_path: str = "generated_posters"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        logger.info(f"Stockage local: {self.base_path.absolute()}")
    
    async def save(self, image_bytes: bytes, movie_id: int, title: str = "") -> Optional[str]:
        """Sauvegarde une image localement"""
        try:
            safe_title = "".join(c for c in title if c.isalnum() or c in " .-_")[:50].replace(" ", "_")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if safe_title:
                filename = f"{movie_id}_{safe_title}_{timestamp}.png"
            else:
                filename = f"poster_{movie_id}_{timestamp}.png"
            
            filepath = self.base_path / filename
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            
            logger.info(f"SauvegardÃ©: {filepath}")
            return str(filepath.absolute())
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde: {e}")
            return None
    
    async def get(self, movie_id: int) -> Optional[Path]:
        """RÃ©cupÃ¨re la derniÃ¨re affiche pour un film"""
        posters = list(self.base_path.glob(f"{movie_id}_*.png"))
        if posters:
            return max(posters, key=lambda p: p.stat().st_mtime)
        return None
