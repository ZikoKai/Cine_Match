# -*- coding: utf-8 -*-
"""Client pour l'API DALLÂ·E 3 (gpt-image-1-mini) sur Azure"""

import base64
import httpx
from openai import OpenAI
from typing import Optional, Tuple
from task2.core.config import config
from task2.utils.logger import get_logger

logger = get_logger(__name__)


class AzureDalleClient:
    """Client pour gÃ©nÃ©rer des images avec DALLÂ·E sur Azure"""
    
    def __init__(self):
        self.client = OpenAI(
            base_url=config.azure.endpoint,
            api_key=config.azure.api_key
        )
        self.deployment = config.azure.dalle_deployment
        self.image_size = config.generation.image_size
    
    async def generate(self, prompt: str) -> Optional[Tuple[bytes, str]]:
        """
        GÃ©nÃ¨re une image Ã  partir d'un prompt
        
        Args:
            prompt: Description textuelle de l'image Ã  gÃ©nÃ©rer
            
        Returns:
            Tuple (image_bytes, mime_type) ou None si Ã©chec
        """
        try:
            logger.info(f"GÃ©nÃ©ration DALLÂ·E: {prompt[:100]}...")
            
            response = self.client.images.generate(
                model=self.deployment,
                prompt=prompt,
                n=1,
                size=self.image_size
            )
            
            if not response.data:
                logger.error("Aucune donnÃ©e dans la rÃ©ponse")
                return None
            
            img_data = response.data[0]
            
            # Cas 1: Base64 (notre cas)
            if hasattr(img_data, 'b64_json') and img_data.b64_json:
                image_bytes = base64.b64decode(img_data.b64_json)
                logger.info(f"Image gÃ©nÃ©rÃ©e (base64): {len(image_bytes)} bytes")
                return (image_bytes, "image/png")
            
            # Cas 2: URL
            elif hasattr(img_data, 'url') and img_data.url:
                async with httpx.AsyncClient() as client:
                    img_response = await client.get(img_data.url, timeout=30.0)
                    img_response.raise_for_status()
                    image_bytes = img_response.content
                logger.info(f"Image gÃ©nÃ©rÃ©e (URL): {len(image_bytes)} bytes")
                return (image_bytes, "image/png")
            
            else:
                logger.error("Format de rÃ©ponse non reconnu")
                return None
                
        except Exception as e:
            logger.error(f"Erreur DALLÂ·E: {e}")
            return None
    
    async def generate_and_save(self, prompt: str, output_path: str) -> Optional[str]:
        """GÃ©nÃ¨re et sauvegarde l'image localement"""
        result = await self.generate(prompt)
        if result:
            image_bytes, _ = result
            with open(output_path, "wb") as f:
                f.write(image_bytes)
            logger.info(f"Image sauvegardÃ©e: {output_path}")
            return output_path
        return None
