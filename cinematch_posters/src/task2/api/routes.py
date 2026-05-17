# -*- coding: utf-8 -*-
"""Routes API REST pour la gÃ©nÃ©ration d'affiches de films"""

import time
import json
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, JSONResponse

from task2.api.models import (
    GenerateRequest,
    BatchGenerateRequest,
    GenerateResponse,
    BatchGenerateResponse,
    StatsResponse,
    ErrorResponse,
)
from task2.core.orchestrator import PosterOrchestrator
from task2.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Poster Generation"])

# Stockage en mÃ©moire des sessions d'orchestrateurs
_orchestrators: Dict[str, PosterOrchestrator] = {}
_default_orchestrator: Optional[PosterOrchestrator] = None


def _get_orchestrator(
    prompt_style: str = "minimal",
    enhancement_style: str = "minimal",
    enable_vision: bool = True,
) -> PosterOrchestrator:
    """RÃ©cupÃ¨re ou crÃ©e un orchestrateur avec les paramÃ¨tres donnÃ©s"""
    global _default_orchestrator
    key = f"{prompt_style}:{enhancement_style}:{enable_vision}"
    if key not in _orchestrators:
        _orchestrators[key] = PosterOrchestrator(
            prompt_style=prompt_style,
            enhancement_style=enhancement_style,
            enable_vision_analysis=enable_vision,
        )
    return _orchestrators[key]


def _movie_dict_from_request(movie_data) -> Dict:
    """Convertit un MovieRequest en dictionnaire compatible avec PosterOrchestrator"""
    return {
        "id": movie_data.id,
        "title": movie_data.title,
        "genres": movie_data.genres,
        "year": movie_data.year,
        "synopsis": movie_data.synopsis or movie_data.overview or "",
        "overview": movie_data.overview or movie_data.synopsis or "",
        "poster_path": movie_data.poster_path or movie_data.poster or "",
        "poster": movie_data.poster or movie_data.poster_path or "",
        "original_language": movie_data.original_language,
    }


def _result_to_response(result: Optional[Dict]) -> GenerateResponse:
    """Convertit le rÃ©sultat de l'orchestrateur en GenerateResponse"""
    if result is None:
        return GenerateResponse(
            success=False,
            movie_id=0,
            title="Unknown",
            error="Aucun rÃ©sultat retournÃ© par l'orchestrateur",
        )

    return GenerateResponse(
        success=result.get("success", False),
        movie_id=result.get("movie_id", 0),
        title=result.get("title", "Unknown"),
        source=result.get("source"),
        prompt_style=result.get("prompt_style"),
        enhancement_style=result.get("enhancement_style"),
        raw_path=result.get("raw_path"),
        final_path=result.get("final_path"),
        cloud_url=result.get("cloud_url"),
        art_brief=result.get("art_brief"),
        vision_analysis=result.get("vision_analysis"),
        duration_seconds=result.get("duration_seconds"),
        retry_count=result.get("retry_count"),
        error=result.get("error"),
        timestamp=result.get("timestamp"),
    )


# â”€â”€ Health / Status â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@router.get("/health", summary="VÃ©rification de santÃ© de l'API")
async def health_check():
    """Endpoint de health check pour monitoring"""
    return {
        "status": "healthy",
        "service": "cine-match-poster-api",
        "version": "0.1.0",
    }


@router.get("/stats", response_model=StatsResponse, summary="Statistiques de session")
async def get_stats(
    prompt_style: str = Query("minimal", description="Style de prompt"),
    enhancement_style: str = Query("minimal", description="Style d'amÃ©lioration"),
):
    """RÃ©cupÃ¨re les statistiques de la session en cours pour un orchestrateur donnÃ©"""
    try:
        orchestrator = _get_orchestrator(prompt_style, enhancement_style)
        stats = orchestrator.get_session_stats()
        return StatsResponse(**stats)
    except Exception as e:
        logger.exception("Erreur lors de la rÃ©cupÃ©ration des statistiques")
        raise HTTPException(status_code=500, detail=str(e))


# â”€â”€ Single Generation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@router.post(
    "/generate",
    response_model=GenerateResponse,
    summary="GÃ©nÃ©rer une affiche pour un film",
)
async def generate_poster(request: GenerateRequest):
    """
    GÃ©nÃ¨re une affiche de film unique via la pipeline complÃ¨te :

    1. **Analyse Vision** (optionnelle) : analyse du poster original TMDB via GPT-4o Vision
    2. **Brief crÃ©atif** : GPT-4o gÃ©nÃ¨re un concept visuel
    3. **GÃ©nÃ©ration** : DALL-E 3 gÃ©nÃ¨re l'image (fallback Canvas si Ã©chec)
    4. **Post-production** : Ajout texte, filtres, effets
    5. **Stockage** : Sauvegarde locale (et cloud optionnel)

    ---

    ### Styles de prompt disponibles :
    - `realistic` : Personnages rÃ©alistes, dÃ©tails peau/capture du regard
    - `abstract` : MÃ©taphores visuelles, compositions artistiques
    - `minimal` : Ã‰purÃ©, design Ã©purÃ©, impact maximal
    - `hybrid` : MÃ©lange de rÃ©alisme et d'abstraction

    ### Styles d'amÃ©lioration disponibles :
    - `cinematic` : Effets hollywoodiens (bloom, glow, particules)
    - `minimal` : Style Ã©purÃ©, peu d'effets
    - `vintage` : Grain sÃ©pia, rayures, style rÃ©tro
    - `neon` : Cyberpunk, lueurs nÃ©on, grilles
    - `neonoir` : Style noir et blanc avec des touches nÃ©on
    """
    try:
        start_time = time.time()
        movie_dict = _movie_dict_from_request(request.movie)

        orchestrator = _get_orchestrator(
            prompt_style=request.prompt_style,
            enhancement_style=request.enhancement_style,
        )

        logger.info(f"ðŸ“¨ RequÃªte API reÃ§ue pour: {request.movie.title}")

        result = await orchestrator.generate_poster(
            movie=movie_dict,
            save_local=request.save_local,
            enhance=request.enhance,
            upload_cloud=request.upload_cloud,
            generate_variations=request.generate_variations,
            analyze_original_poster=request.analyze_original_poster,
        )

        response = _result_to_response(result)
        logger.info(f"âœ… RÃ©ponse envoyÃ©e pour {request.movie.title} (durÃ©e: {time.time() - start_time:.1f}s)")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erreur lors de la gÃ©nÃ©ration pour {request.movie.title}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur de gÃ©nÃ©ration: {str(e)}",
        )


# â”€â”€ Batch Generation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@router.post(
    "/generate/batch",
    response_model=BatchGenerateResponse,
    summary="GÃ©nÃ©rer des affiches pour plusieurs films",
)
async def generate_batch(request: BatchGenerateRequest):
    """
    GÃ©nÃ¨re des affiches pour plusieurs films en parallÃ¨le.

    - Jusqu'Ã  50 films par requÃªte
    - Chaque film peut surcharger les styles par dÃ©faut
    - RÃ©sultats individuels disponibles dans `results`
    - Statistiques globales dans `total`, `success_count`, `success_rate`
    """
    try:
        start_time = time.time()
        logger.info(f"ðŸ“¦ RequÃªte batch API reÃ§ue: {len(request.movies)} films")

        movies: List[Dict] = []
        for item in request.movies:
            movie_dict = _movie_dict_from_request(item.movie)
            movies.append(movie_dict)

        # Utiliser un orchestrateur unique avec les styles par dÃ©faut
        orchestrator = _get_orchestrator(
            prompt_style=request.default_prompt_style,
            enhancement_style=request.default_enhancement_style,
        )

        results = await orchestrator.generate_batch(
            movies=movies,
            save_local=request.save_local,
            enhance=request.enhance,
            upload_cloud=request.upload_cloud,
            max_concurrent=request.max_concurrent,
            analyze_original_posters=request.analyze_original_posters,
        )

        response_results = [_result_to_response(r) for r in results]
        success_count = sum(1 for r in response_results if r.success)
        failed_count = len(response_results) - success_count
        total_duration = time.time() - start_time

        return BatchGenerateResponse(
            total=len(response_results),
            success_count=success_count,
            failed_count=failed_count,
            success_rate=round(success_count / max(1, len(response_results)) * 100, 1),
            results=response_results,
            total_duration_seconds=round(total_duration, 2),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Erreur lors de la gÃ©nÃ©ration batch")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur batch: {str(e)}",
        )


# â”€â”€ Image Serving â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@router.get("/images/{movie_id:path}", summary="Servir une image gÃ©nÃ©rÃ©e")
async def serve_image(movie_id: str, enhanced: bool = Query(False, description="Utiliser l'image amÃ©liorÃ©e")):
    """
    Sert une image gÃ©nÃ©rÃ©e depuis le stockage local.

    - `movie_id` : nom du fichier ou ID du film
    - `enhanced=true` : cherche dans `enhanced_posters/`
    - `enhanced=false` : cherche dans `generated_posters/`
    """
    base_dir = Path("enhanced_posters" if enhanced else "generated_posters")

    if not base_dir.exists():
        raise HTTPException(status_code=404, detail="Aucune image trouvÃ©e")

    # Chercher par nom exact ou par pattern
    files = list(base_dir.glob(f"*{movie_id}*"))
    if not files:
        files = list(base_dir.glob(f"*{movie_id}*.png"))
    if not files:
        files = list(base_dir.glob(f"*{movie_id}*.jpg"))

    if not files:
        raise HTTPException(
            status_code=404,
            detail=f"Aucune image trouvÃ©e pour l'identifiant '{movie_id}'",
        )

    image_path = files[0]
    media_type = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
    return FileResponse(str(image_path), media_type=media_type)


@router.get("/images/", summary="Lister les images disponibles")
async def list_images(
    enhanced: bool = Query(False, description="Lister les images amÃ©liorÃ©es"),
    limit: int = Query(20, description="Nombre maximum d'images", ge=1, le=100),
):
    """
    Liste les images gÃ©nÃ©rÃ©es disponibles dans le stockage local.
    """
    base_dir = Path("enhanced_posters" if enhanced else "generated_posters")

    if not base_dir.exists():
        return {"images": [], "count": 0, "directory": str(base_dir)}

    files = sorted(base_dir.glob("*.*"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    images = [
        {
            "filename": f.name,
            "path": f"/api/v1/images/{f.stem}?enhanced={str(enhanced).lower()}",
            "size_bytes": f.stat().st_size,
            "modified": f.stat().st_mtime,
        }
        for f in files
        if f.suffix.lower() in (".png", ".jpg", ".jpeg")
    ]

    return {"images": images, "count": len(images), "directory": str(base_dir)}


# â”€â”€ Orchestrator Management â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@router.post("/orchestrator/reset", summary="RÃ©initialiser les orchestrateurs")
async def reset_orchestrators():
    """RÃ©initialise tous les orchestrateurs et leurs statistiques"""
    global _orchestrators, _default_orchestrator
    _orchestrators.clear()
    _default_orchestrator = None
    logger.info("ðŸ”„ Tous les orchestrateurs ont Ã©tÃ© rÃ©initialisÃ©s")
    return {"message": "Tous les orchestrateurs ont Ã©tÃ© rÃ©initialisÃ©s", "status": "ok"}
