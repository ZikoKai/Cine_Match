"""Configuration du logging - Version corrigÃ©e pour Windows"""

import logging
import sys
from pathlib import Path
from datetime import datetime

# CrÃ©er le dossier logs
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configuration du logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# Handler console avec encodage UTF-8 pour Windows
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Forcer l'encodage UTF-8 sur Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

console_handler.setFormatter(logging.Formatter(log_format, date_format))

# Handler fichier
file_handler = logging.FileHandler(log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log", encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(log_format, date_format))

# Configuration racine
logging.basicConfig(
    level=logging.INFO,
    handlers=[console_handler, file_handler]
)


def get_logger(name: str) -> logging.Logger:
    """RÃ©cupÃ¨re un logger configurÃ©"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
