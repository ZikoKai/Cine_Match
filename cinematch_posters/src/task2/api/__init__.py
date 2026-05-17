"""API REST pour la génération d'affiches de films"""

from task2.api.models import (
    MovieRequest,
    GenerateRequest,
    BatchGenerateRequest,
    GenerateResponse,
    BatchGenerateResponse,
    StatsResponse,
    ErrorResponse,
)
from task2.api.routes import router

__all__ = [
    "MovieRequest",
    "GenerateRequest",
    "BatchGenerateRequest",
    "GenerateResponse",
    "BatchGenerateResponse",
    "StatsResponse",
    "ErrorResponse",
    "router",
]
