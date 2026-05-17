"""ModÃ¨les Pydantic pour l'API de gÃ©nÃ©ration d'affiches"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class MovieRequest(BaseModel):
    """DonnÃ©es d'un film pour la gÃ©nÃ©ration d'affiche"""
    id: int = Field(..., description="Identifiant unique du film")
    title: str = Field(..., description="Titre du film")
    genres: List[str] = Field(default_factory=list, description="Genres du film")
    year: str = Field(default="Unknown", description="AnnÃ©e de sortie")
    synopsis: Optional[str] = Field(None, description="Synopsis / overview du film")
    overview: Optional[str] = Field(None, description="Synopsis (alias)")
    poster_path: Optional[str] = Field(None, description="URL du poster original TMDB")
    poster: Optional[str] = Field(None, description="URL du poster (alias)")
    original_language: str = Field(default="en", description="Langue originale")
    vision_analysis: Optional[Dict[str, Any]] = Field(None, description="Analyse vision prÃ©existante (optionnel)")


class GenerateRequest(BaseModel):
    """RequÃªte de gÃ©nÃ©ration d'une seule affiche"""
    movie: MovieRequest = Field(..., description="DonnÃ©es du film")
    prompt_style: str = Field(default="minimal", description="Style de prompt (realistic, abstract, minimal, hybrid)")
    enhancement_style: str = Field(default="minimal", description="Style d'amÃ©lioration (cinematic, minimal, vintage, neon, neonoir)")
    save_local: bool = Field(default=True, description="Sauvegarder localement")
    enhance: bool = Field(default=True, description="Appliquer la post-production")
    upload_cloud: bool = Field(default=False, description="Upload vers Cloudflare R2")
    generate_variations: bool = Field(default=False, description="GÃ©nÃ©rer des variations")
    analyze_original_poster: bool = Field(default=True, description="Analyser le poster original TMDB avec Vision")


class BatchItem(BaseModel):
    """Un film dans une requÃªte batch"""
    movie: MovieRequest = Field(..., description="DonnÃ©es du film")
    prompt_style: Optional[str] = Field(None, description="Style de prompt (surcharge)")
    enhancement_style: Optional[str] = Field(None, description="Style d'amÃ©lioration (surcharge)")


class BatchGenerateRequest(BaseModel):
    """RequÃªte de gÃ©nÃ©ration batch"""
    movies: List[BatchItem] = Field(..., description="Liste des films Ã  gÃ©nÃ©rer", min_length=1, max_length=50)
    default_prompt_style: str = Field(default="minimal", description="Style de prompt par dÃ©faut")
    default_enhancement_style: str = Field(default="minimal", description="Style d'amÃ©lioration par dÃ©faut")
    save_local: bool = Field(default=True, description="Sauvegarder localement")
    enhance: bool = Field(default=True, description="Appliquer la post-production")
    upload_cloud: bool = Field(default=False, description="Upload vers Cloudflare R2")
    max_concurrent: int = Field(default=2, description="Nombre max de gÃ©nÃ©rations parallÃ¨les", ge=1, le=10)
    analyze_original_posters: bool = Field(default=True, description="Analyser les posters originaux")


class GenerateResponse(BaseModel):
    """RÃ©ponse de gÃ©nÃ©ration d'une affiche"""
    success: bool = Field(..., description="SuccÃ¨s de la gÃ©nÃ©ration")
    movie_id: int = Field(..., description="Identifiant du film")
    title: str = Field(..., description="Titre du film")
    source: Optional[str] = Field(None, description="Source de gÃ©nÃ©ration (dalle, fallback)")
    prompt_style: Optional[str] = Field(None, description="Style de prompt utilisÃ©")
    enhancement_style: Optional[str] = Field(None, description="Style d'amÃ©lioration utilisÃ©")
    raw_path: Optional[str] = Field(None, description="Chemin de l'image brute gÃ©nÃ©rÃ©e")
    final_path: Optional[str] = Field(None, description="Chemin de l'image finale amÃ©liorÃ©e")
    cloud_url: Optional[str] = Field(None, description="URL cloud si uploadÃ©")
    art_brief: Optional[str] = Field(None, description="Extrait du prompt artistique")
    vision_analysis: Optional[Dict[str, Any]] = Field(None, description="RÃ©sultat de l'analyse vision")
    duration_seconds: Optional[float] = Field(None, description="DurÃ©e de gÃ©nÃ©ration en secondes")
    retry_count: Optional[int] = Field(None, description="Nombre de tentatives")
    error: Optional[str] = Field(None, description="Message d'erreur en cas d'Ã©chec")
    timestamp: Optional[str] = Field(None, description="Horodatage de la gÃ©nÃ©ration")


class BatchGenerateResponse(BaseModel):
    """RÃ©ponse de gÃ©nÃ©ration batch"""
    total: int = Field(..., description="Nombre total de films")
    success_count: int = Field(..., description="Nombre de succÃ¨s")
    failed_count: int = Field(..., description="Nombre d'Ã©checs")
    success_rate: float = Field(..., description="Taux de succÃ¨s en pourcentage")
    results: List[GenerateResponse] = Field(default_factory=list, description="RÃ©sultats individuels")
    total_duration_seconds: float = Field(..., description="DurÃ©e totale du batch en secondes")


class StatsResponse(BaseModel):
    """Statistiques de session de l'orchestrateur"""
    session_duration_seconds: float = Field(..., description="DurÃ©e de la session")
    total_generations: int = Field(..., description="Nombre total de gÃ©nÃ©rations")
    successful_generations: int = Field(..., description="GÃ©nÃ©rations rÃ©ussies")
    failed_generations: int = Field(..., description="GÃ©nÃ©rations Ã©chouÃ©es")
    success_rate: float = Field(..., description="Taux de succÃ¨s (%)")
    dalle_usage: int = Field(..., description="Nombre d'utilisations de DALL-E")
    fallback_usage: int = Field(..., description="Nombre d'utilisations du fallback Canvas")
    vision_analyses: int = Field(..., description="Nombre d'analyses vision effectuÃ©es")
    avg_generation_time: float = Field(..., description="Temps moyen de gÃ©nÃ©ration (secondes)")
    prompt_style: str = Field(..., description="Style de prompt actif")
    enhancement_style: str = Field(..., description="Style d'amÃ©lioration actif")


class ErrorResponse(BaseModel):
    """RÃ©ponse d'erreur standard"""
    detail: str = Field(..., description="Description dÃ©taillÃ©e de l'erreur")
    error_code: Optional[str] = Field(None, description="Code d'erreur optionnel")
