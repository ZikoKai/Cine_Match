# -*- coding: utf-8 -*-
"""Utilitaires de validation pour les données d'entrée"""

from typing import Dict, List, Optional


class MovieValidator:
    """Validation des donnÃ©es de films"""
    
    @staticmethod
    def validate_movie(movie: Dict) -> tuple[bool, Optional[str]]:
        """Valide un dictionnaire de film"""
        
        required_fields = ['id', 'title']
        
        for field in required_fields:
            if field not in movie:
                return False, f"Champ manquant: {field}"
        
        if not isinstance(movie.get('id'), int):
            return False, "L'ID doit Ãªtre un entier"
        
        if not movie.get('title') or not isinstance(movie['title'], str):
            return False, "Le titre est requis"
        
        if 'genres' in movie and not isinstance(movie['genres'], list):
            return False, "Les genres doivent Ãªtre une liste"
        
        if 'year' in movie and not isinstance(movie['year'], int):
            return False, "L'annÃ©e doit Ãªtre un entier"
        
        return True, None
    
    @staticmethod
    def sanitize_title(title: str) -> str:
        """Nettoie le titre pour le nom de fichier"""
        import re
        # Enlever les caractÃ¨res spÃ©ciaux
        sanitized = re.sub(r'[<>:"/\\|?*]', '', title)
        # Remplacer les espaces
        sanitized = sanitized.strip().replace(' ', '_')
        return sanitized


class ImageValidator:
    """Validation des images"""
    
    @staticmethod
    def validate_image_bytes(image_bytes: bytes) -> bool:
        """Valide que les bytes reprÃ©sentent une image valide"""
        if not image_bytes or len(image_bytes) < 100:
            return False
        
        # VÃ©rifier les signatures PNG/JPEG
        if image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            return True
        if image_bytes.startswith(b'\xff\xd8\xff'):
            return True
        
        return False
