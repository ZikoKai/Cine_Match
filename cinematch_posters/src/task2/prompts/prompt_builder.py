# -*- coding: utf-8 -*-
"""Module pour construire les prompts finaux DALLÂ·E à partir du concept GPT-4o"""

from typing import Dict, Optional


class FinalPromptBuilder:
    """Construit les prompts finaux optimisÃ©s pour DALLÂ·E"""
    
    # QualitÃ© de base pour tous les prompts
    QUALITY_BOOSTERS = {
        "realistic": (
            "masterpiece photography, shot on Panavision 70mm, f/2.8 aperture, "
            "depth of field, sharp facial details, realistic skin textures, "
            "micro-expressions, authentic film grain, volumetric cinematic lighting, "
            "hyper-realistic, 8k resolution, professional color grading"
        ),
        "abstract": (
            "masterpiece, award-winning cinematography, shot on 70mm IMAX film, "
            "ultra-detailed textures, hyper-realistic lighting, 8k resolution, "
            "professional color grading, cinematic depth of field, "
            "breathtaking composition, evocative mood, atmospheric fog, "
            "dramatic shadows, premium quality, gallery-worthy"
        ),
        "minimal": (
            "minimalist masterpiece, clean composition, professional photography, "
            "high contrast, sharp details, cinematic quality"
        )
    }
    
    # Styles par genre
    GENRE_STYLES = {
        "Action": "high-energy dynamic composition, explosive visual impact",
        "Drama": "emotional depth, intimate framing, powerful minimalist aesthetic",
        "Sci-Fi": "futuristic elements, neon accents, sleek technological design",
        "Horror": "dark atmospheric tension, unsettling shadows, gothic texture",
        "Comedy": "vibrant colors, lively composition, whimsical details",
        "Romance": "soft ethereal lighting, warm tones, intimate close framing",
        "Thriller": "suspenseful atmosphere, dramatic contrast, sharp angular lines",
        "Fantasy": "magical elements, ethereal glow, mythical textures",
        "Documentary": "authentic natural lighting, truthful composition",
        "Crime": "noir aesthetic, dramatic shadows, gritty textures",
        "Adventure": "epic scale, grand composition, vibrant natural lighting",
        "Horror,Thriller": "dark psychological tension, unsettling atmosphere, clinical precision"
    }
    
    @classmethod
    def build_final_prompt(
        cls, 
        visuals: str, 
        title: str, 
        genres: str, 
        style: str = "realistic"
    ) -> str:
        """
        Construit le prompt final pour DALLÂ·E
        
        Args:
            visuals: Description visuelle gÃ©nÃ©rÃ©e par GPT-4o
            title: Titre du film (non utilisÃ© dans le prompt final)
            genres: Genres du film
            style: Style du prompt ("realistic", "abstract", "minimal")
        """
        # RÃ©cupÃ©rer les boosters de qualitÃ©
        quality = cls.QUALITY_BOOSTERS.get(style, cls.QUALITY_BOOSTERS["realistic"])
        
        # DÃ©tecter le genre principal
        main_genre = genres.split(",")[0].strip() if genres else "Drama"
        genre_style = cls.GENRE_STYLES.get(main_genre, "cinematic excellence, professional composition")
        
        # Construction selon le style
        if style == "realistic":
            return cls._build_realistic_prompt(visuals, genre_style, quality)
        elif style == "abstract":
            return cls._build_abstract_prompt(visuals, genre_style, quality)
        else:
            return cls._build_minimal_prompt(visuals, genre_style, quality)
    
    @classmethod
    def _build_realistic_prompt(cls, visuals: str, genre_style: str, quality: str) -> str:
        """Prompt pour style rÃ©aliste avec personnages"""
        return f"""Authentic cinematic film still photograph, {quality}.

SUBJECT & SCENE:
{visuals}

TECHNICAL SPECIFICATIONS:
Shot on 85mm prime lens, f/1.8 aperture, creamy bokeh background, 
tactile realism, hyper-realistic photography.

ATMOSPHERE:
{genre_style}
Cinematic mood, professional studio lighting, deep shadows, rich color science.

COMPOSITION:
Balanced movie poster layout, rule of thirds, negative space for text overlay.

CRITICAL CONSTRAINTS:
- NO text, NO letters, NO subtitles
- NO logos, NO watermarks
- Original characters only (no celebrities)
- NOT a screenshot, a professional photograph"""
    
    @classmethod
    def _build_abstract_prompt(cls, visuals: str, genre_style: str, quality: str) -> str:
        """Prompt pour style abstrait/artistique"""
        return f"""IMAX cinematic movie poster illustration, {quality}.

VISUAL CONCEPT:
{visuals}

ARTISTIC DIRECTION:
{genre_style}
Dramatic professional lighting, masterful color palette, cinematic atmosphere, emotional resonance.

CRITICAL CONSTRAINTS:
- ABSOLUTELY NO text, letters, words, titles, or subtitles
- NO logos, watermarks, signatures, or branding
- NO specific character faces or recognizable celebrities
- NO copyright characters or franchise elements
- The image must stand alone as pure visual art

QUALITY REQUIREMENTS:
- Professional movie poster composition
- Academy Award quality cinematography
- Museum-grade artistic value
- Captivating and memorable imagery"""
    
    @classmethod
    def _build_minimal_prompt(cls, visuals: str, genre_style: str, quality: str) -> str:
        """Prompt pour style minimaliste"""
        return f"""Minimalist movie poster, {quality}.

DESIGN:
{visuals}

STYLE:
Clean composition, {genre_style}, strong visual impact.

CONSTRAINTS:
No text, no logos, minimal elements, high contrast.

QUALITY:
Professional design, gallery-quality print, timeless aesthetic."""
    
    @classmethod
    def fallback_prompt(cls, title: str = "Film", style: str = "realistic") -> str:
        """Prompt de secours"""
        if style == "realistic":
            return f"""Professional cinematic photograph for '{title}' movie poster.
A compelling character in dramatic lighting, authentic film still quality,
85mm lens, shallow depth of field, natural skin texture, emotional expression.
Cinematic color grading, professional composition.
NO text, NO logos, original character only."""
        
        return f"""Professional cinematic movie poster for '{title}', 
        award-winning cinematography, dramatic atmospheric lighting, 
        emotional depth, masterful composition, ultra-detailed textures, 
        8k resolution, cinematic color grading, 
        NO text, NO logos, pure visual storytelling."""


# Instance globale
final_prompt_builder = FinalPromptBuilder()
