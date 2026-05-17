# -*- coding: utf-8 -*-
"""Application FastAPI principale pour l'API de gÃ©nÃ©ration d'affiches"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from task2.api.routes import router
from task2.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    logger.info("ðŸš€ DÃ©marrage de l'API CineMatch Poster Generation")
    logger.info(f"   Python: {sys.version}")
    yield
    logger.info("ðŸ›‘ ArrÃªt de l'API CineMatch Poster Generation")


app = FastAPI(
    title="CineMatch - API de GÃ©nÃ©ration d'Affiches",
    description="""
    API REST pour la gÃ©nÃ©ration automatique d'affiches de films.
    
    ## FonctionnalitÃ©s
    
    - **GÃ©nÃ©ration unique** : Affiche complÃ¨te pour un film avec analyse Vision + DALL-E + post-production
    - **GÃ©nÃ©ration batch** : Traitement parallÃ¨le de plusieurs films
    - **Gestion d'images** : Service et listing des images gÃ©nÃ©rÃ©es
    - **Monitoring** : Health check et statistiques de session
    
    ## Pipeline de gÃ©nÃ©ration
    
    1. Analyse du poster original TMDB via GPT-4o Vision (optionnel)
    2. CrÃ©ation du concept visuel par GPT-4o
    3. GÃ©nÃ©ration de l'image par DALL-E 3 (fallback Canvas si Ã©chec)
    4. Post-production : ajout titre, annÃ©e, genres, effets visuels
    5. Sauvegarde locale et/ou cloud
    
    ## Styles disponibles
    
    **Prompt** : `realistic`, `abstract`, `minimal`, `hybrid`  
    **AmÃ©lioration** : `cinematic`, `minimal`, `vintage`, `neon`, `neonoir`
    """,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS - autorise les requÃªtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Enregistrement des routes
app.include_router(router)


@app.get("/", tags=["Root"])
async def root():
    """Page d'accueil avec liens rapides"""
    return {
        "service": "CineMatch - API de GÃ©nÃ©ration d'Affiches",
        "version": "0.1.0",
        "documentation": "/docs",
        "openapi_spec": "/openapi.json",
        "endpoints": {
            "health": "GET /api/v1/health",
            "stats": "GET /api/v1/stats",
            "generate_single": "POST /api/v1/generate",
            "generate_batch": "POST /api/v1/generate/batch",
            "list_images": "GET /api/v1/images/",
            "serve_image": "GET /api/v1/images/{movie_id}",
            "reset_orchestrator": "POST /api/v1/orchestrator/reset",
        },
    }
