# -*- coding: utf-8 -*-
"""Stockage sur Cloudflare R2 / S3 compatible"""

import os
import boto3
from botocore.config import Config
from typing import Optional
from pathlib import Path
from task2.core.config import config
from task2.utils.logger import get_logger

logger = get_logger(__name__)


class R2Storage:
    """Client pour Cloudflare R2"""
    
    def __init__(self):
        self.enabled = False
        self.client = None
        self.bucket = None
        self.public_url = None
        
        try:
            # Lire les credentials
            account_id = os.getenv("R2_ACCOUNT_ID")
            access_key = os.getenv("R2_ACCESS_KEY")
            secret_key = os.getenv("R2_SECRET_KEY")
            self.bucket = os.getenv("R2_BUCKET_NAME", "cinematch-posters")
            self.public_url = os.getenv("R2_PUBLIC_URL", f"https://{account_id}.r2.cloudflarestorage.com")
            
            if account_id and access_key and secret_key:
                endpoint = f"https://{account_id}.r2.cloudflarestorage.com"
                
                self.client = boto3.client(
                    's3',
                    endpoint_url=endpoint,
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key,
                    config=Config(signature_version='s3v4')
                )
                
                # VÃ©rifier que le bucket existe
                try:
                    self.client.head_bucket(Bucket=self.bucket)
                except:
                    # CrÃ©er le bucket s'il n'existe pas
                    self.client.create_bucket(Bucket=self.bucket)
                    logger.info(f"Bucket crÃ©Ã©: {self.bucket}")
                
                self.enabled = True
                logger.info(f"âœ… R2 configurÃ©: {self.bucket}")
            else:
                logger.warning("âš ï¸ R2 non configurÃ©")
                
        except Exception as e:
            logger.error(f"âŒ Erreur R2: {e}")
    
    async def upload(self, file_path: str, key: str, public: bool = True) -> Optional[str]:
        """Upload un fichier vers R2"""
        if not self.enabled:
            logger.warning("R2 non disponible")
            return None
        
        try:
            # Upload du fichier
            with open(file_path, 'rb') as f:
                self.client.upload_fileobj(
                    f,
                    self.bucket,
                    key,
                    ExtraArgs={'ContentType': 'image/png'}
                )
            
            # URL publique
            if public:
                url = f"{self.public_url}/{key}"
            else:
                url = f"https://{self.bucket}.{self.public_url}/{key}"
            
            logger.info(f"UploadÃ©: {key} -> {url}")
            return url
            
        except Exception as e:
            logger.error(f"Erreur upload: {e}")
            return None
    
    async def upload_bytes(self, image_bytes: bytes, key: str) -> Optional[str]:
        """Upload des bytes directement vers R2"""
        if not self.enabled:
            return None
        
        try:
            import io
            file_obj = io.BytesIO(image_bytes)
            
            self.client.upload_fileobj(
                file_obj,
                self.bucket,
                key,
                ExtraArgs={'ContentType': 'image/png'}
            )
            
            url = f"{self.public_url}/{key}"
            logger.info(f"UploadÃ© (bytes): {key}")
            return url
            
        except Exception as e:
            logger.error(f"Erreur upload bytes: {e}")
            return None
    
    async def list_files(self, prefix: str = "") -> list:
        """Liste les fichiers dans R2"""
        if not self.enabled:
            return []
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    })
            
            return files
            
        except Exception as e:
            logger.error(f"Erreur listage: {e}")
            return []
    
    async def delete(self, key: str) -> bool:
        """Supprime un fichier"""
        if not self.enabled:
            return False
        
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"SupprimÃ©: {key}")
            return True
        except Exception as e:
            logger.error(f"Erreur suppression: {e}")
            return False
