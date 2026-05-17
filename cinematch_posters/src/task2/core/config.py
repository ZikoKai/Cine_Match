# -*- coding: utf-8 -*-
"""Configuration centralisÃ©e de l'application"""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AzureConfig:
    """Configuration Azure OpenAI"""
    endpoint: str = field(default_factory=lambda: os.getenv("AZURE_ENDPOINT", ""))
    api_key: str = field(default_factory=lambda: os.getenv("AZURE_API_KEY", ""))
    gpt_deployment: str = field(default_factory=lambda: os.getenv("AZURE_GPT4O_DEPLOYMENT", "gpt-4o"))
    dalle_deployment: str = field(default_factory=lambda: os.getenv("AZURE_DALLE_DEPLOYMENT", "gpt-image-1-mini"))
    
    def validate(self) -> bool:
        """Valide la configuration"""
        if not self.api_key:
            raise ValueError("AZURE_API_KEY manquante dans .env")
        if not self.endpoint:
            raise ValueError("AZURE_ENDPOINT manquant dans .env")
        return True


@dataclass
class VisionConfig:
    """Configuration GPT-4o Vision"""
    model: str = field(default_factory=lambda: os.getenv("AZURE_GPT4O_DEPLOYMENT", "gpt-4o"))


@dataclass
class StorageConfig:
    """Configuration du stockage"""
    mode: str = field(default_factory=lambda: os.getenv("STORAGE_MODE", "local"))
    local_path: str = field(default_factory=lambda: os.getenv("LOCAL_STORAGE_PATH", "generated_posters"))
    enhanced_path: str = field(default_factory=lambda: os.getenv("ENHANCED_STORAGE_PATH", "enhanced_posters"))

    def validate(self) -> bool:
        """Valide la configuration de stockage"""
        if self.mode not in ["local", "s3"]:
            raise ValueError("STORAGE_MODE doit Ãªtre 'local' ou 's3'")
        return True


@dataclass
class GenerationConfig:
    """Configuration de gÃ©nÃ©ration"""
    image_size: str = field(default_factory=lambda: os.getenv("IMAGE_SIZE", "1024x1024"))
    max_concurrent: int = field(default_factory=lambda: int(os.getenv("MAX_CONCURRENT", "2")))
    retry_count: int = field(default_factory=lambda: int(os.getenv("RETRY_COUNT", "3")))
    enable_enhancement: bool = field(default_factory=lambda: os.getenv("ENABLE_ENHANCEMENT", "true").lower() == "true")


@dataclass
class TMDBConfig:
    """Configuration TMDB"""
    base_url: str = field(default_factory=lambda: os.getenv("TMDB_IMAGE_BASE_URL", "https://image.tmdb.org/t/p/original"))


@dataclass
class Config:
    """Configuration principale"""
    azure: AzureConfig = field(default_factory=AzureConfig)
    vision: VisionConfig = field(default_factory=VisionConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    generation: GenerationConfig = field(default_factory=GenerationConfig)
    tmdb: TMDBConfig = field(default_factory=TMDBConfig)
    
    @classmethod
    def load(cls, validate_azure: bool = False) -> "Config":
        """Charge la configuration depuis les variables d'environnement"""
        config = cls()
        if validate_azure:
            config.azure.validate()
        return config

    def validate_all(self):
        """Valide toute la configuration - appelée lors de l'utilisation réelle"""
        self.azure.validate()
        self.storage.validate()


# Instance globale de configuration (validation différée)
config = Config.load(validate_azure=False)
