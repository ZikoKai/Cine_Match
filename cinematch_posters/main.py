"""
Entry point for the CineMatch Poster Generation API.

Usage:
    python main.py                   # Start server with default settings
    python main.py --reload          # Development mode with auto-reload
    python main.py --port 8001       # Custom port
    python main.py --host 0.0.0.0    # Bind to all interfaces
"""

import sys
import argparse
from pathlib import Path

# Ensure `src/` is on sys.path so `from task2 import ...` works
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def main():
    parser = argparse.ArgumentParser(
        description="CineMatch Poster Generation API Server",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Logging level (default: info)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1, ignored when --reload is set)",
    )

    args = parser.parse_args()

    # Import the FastAPI app after path is set up
    from src.task2.api.app import app

    import uvicorn

    uvicorn.run(
        "src.task2.api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level,
        workers=1 if args.reload else args.workers,
    )


if __name__ == "__main__":
    main()