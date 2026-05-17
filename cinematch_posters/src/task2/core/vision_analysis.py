# -*- coding: utf-8 -*-
"""Vision Analysis Service - Analyse de posters originaux TMDB avec GPT-4o Vision

Analyse les posters originaux (qualitÃ© maximale) via TMDB et extrait
toutes les caractÃ©ristiques visuelles structurÃ©es pour guider DALLÂ·E.
"""

from typing import Dict, List, Optional
import pandas as pd

from task2.core.config import config
from task2.core.gpt_client import GPT4oClient
from task2.utils.logger import get_logger

logger = get_logger(__name__)

# URL de base TMDB pour les images originales (pleine rÃ©solution)
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"


class VisionAnalyzer:
    """
    Service d'analyse visuelle utilisant GPT-4o Vision.
    Analyse le poster original TMDB en pleine rÃ©solution et extrait
    toutes les caractÃ©ristiques visuelles structurÃ©es :
    
    - description: str (description dÃ©taillÃ©e de la scÃ¨ne)
    - style_canvas: str (style artistique et technique photo)
    - color_palette: List[str] (palette de couleurs HEX)
    - lighting: str (description de l'Ã©clairage)
    - composition: str (technique de composition)
    - mood: str (ton Ã©motionnel)
    - characters: str (description des personnages)
    - key_visual_elements: List[str] (Ã©lÃ©ments visuels clÃ©s)
    """

    def __init__(self):
        """Initialise le VisionAnalyzer avec le client GPT-4o"""
        self.client = GPT4oClient(prompt_style="abstract")
        self.tmdb_base_url = config.tmdb.base_url

    async def analyze_from_path(self, poster_path: str) -> Dict:
        """
        Analyse un poster Ã  partir de son chemin relatif TMDB.
        Utilise l'URL originale pour une analyse en pleine rÃ©solution.
        
        Args:
            poster_path: Chemin relatif du poster TMDB (ex: /abc123.jpg)
            
        Returns:
            Dict avec toutes les caractÃ©ristiques visuelles structurÃ©es
        """
        if not poster_path or poster_path == "nan":
            logger.warning("Aucun poster_path fourni")
            return self._empty_result("No poster path provided")

        # Construire l'URL complÃ¨te vers l'image originale
        full_url = f"{self.tmdb_base_url}{poster_path}"
        logger.info(f"ðŸ”— Poster URL (original): {full_url}")

        return await self.analyze(full_url)

    async def analyze_from_dataframe(
        self,
        df: pd.DataFrame,
        column_path: str = "poster_path",
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Analyse les posters des films d'un DataFrame TMDB.
        
        Args:
            df: DataFrame TMDB avec colonne poster_path
            column_path: Nom de la colonne contenant le chemin du poster
            limit: Nombre maximum de films Ã  analyser
            
        Returns:
            Liste des rÃ©sultats d'analyse pour chaque film
        """
        results = []

        for idx, row in df.iterrows():
            if limit and idx >= limit:
                break

            poster_path = row.get(column_path, "")
            title = row.get("title", f"Film {idx}")

            if not poster_path or poster_path == "nan":
                logger.warning(f"Pas de poster pour {title}, analyse ignorÃ©e")
                continue

            logger.info(f"\n[{idx + 1}] Analyse du poster de : {title}")
            result = await self.analyze_from_path(poster_path)
            result["title"] = title
            result["movie_id"] = row.get("id", idx)
            results.append(result)

        return results

    async def analyze(self, image_url: str) -> Dict:
        """
        Analyse une image de poster depuis son URL complÃ¨te
        en utilisant GPT-4o Vision.
        
        Args:
            image_url: URL complÃ¨te de l'image Ã  analyser
            
        Returns:
            Dict avec toutes les caractÃ©ristiques visuelles structurÃ©es
        """
        logger.info(f"ðŸ” Analyse Vision: {image_url[:80]}...")

        # DÃ©lÃ©guer l'analyse au client GPT-4o Vision
        result = await self.client.analyze_image(image_url)

        if result.get("description", "").startswith("Failed"):
            logger.error(f"âŒ Ã‰chec de l'analyse: {result['description']}")
        else:
            logger.info("âœ… Analyse visuelle terminÃ©e avec succÃ¨s")
            logger.debug(f"   Style: {result.get('style_canvas', 'N/A')}")
            logger.debug(f"   Palette: {len(result.get('color_palette', []))} couleurs")
            logger.debug(f"   Mood: {result.get('mood', 'N/A')}")

        return result

    def _empty_result(self, reason: str = "No data") -> Dict:
        """Retourne un rÃ©sultat vide structurÃ©"""
        return {
            "description": f"Analysis skipped: {reason}",
            "style_canvas": "Unknown",
            "color_palette": [],
            "lighting": "Unknown",
            "composition": "Unknown",
            "mood": "Unknown",
            "characters": "",
            "key_visual_elements": []
        }

    @staticmethod
    def build_poster_url(
        poster_path: str,
        base_url: str = "https://image.tmdb.org/t/p/original"
    ) -> Optional[str]:
        """
        Construit l'URL complÃ¨te du poster TMDB en utilisant
        la rÃ©solution originale (pleine qualitÃ©).
        
        Args:
            poster_path: Chemin relatif du poster (/abc123.jpg)
            base_url: URL de base TMDB (original par dÃ©faut)
            
        Returns:
            URL complÃ¨te ou None si poster_path invalide
        
        Exemples:
            >>> VisionAnalyzer.build_poster_url("/abc123.jpg")
            'https://image.tmdb.org/t/p/original/abc123.jpg'
            
            # Alternative avec w500 si besoin
            >>> VisionAnalyzer.build_poster_url(
            ...     "/abc123.jpg",
            ...     "https://image.tmdb.org/t/p/w500"
            ... )
            'https://image.tmdb.org/t/p/w500/abc123.jpg'
        """
        if not poster_path or poster_path == "nan":
            return None

        # Nettoyer le chemin (enlever les slashes superflus)
        poster_path = poster_path.strip()
        if not poster_path.startswith("/"):
            poster_path = f"/{poster_path}"

        return f"{base_url.rstrip('/')}{poster_path}"
