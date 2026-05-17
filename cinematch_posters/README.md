# CineMatch Poster Generation API

AI-powered movie poster generation service using Azure OpenAI (GPT-4o Vision + DALL-E 3) with post-production image enhancement and cloud storage support.

## Features

- **🎬 Single Poster Generation** — Full pipeline: Vision analysis → GPT-4o concept → DALL-E 3 generation → Image enhancement → Storage
- **📦 Batch Processing** — Parallel generation for multiple movies with configurable concurrency
- **👁️ GPT-4o Vision Analysis** — Analyze original TMDB posters to extract color palettes, composition, lighting, mood, and visual elements
- **🎨 Multiple Prompt Styles** — realistic, abstract, minimal, hybrid
- **✨ Post-Production Enhancement** — cinematic, minimal, vintage, neon, neonoir
- **🔄 Automatic Fallback** — Canvas-generated poster if DALL-E fails
- **💾 Local & Cloud Storage** — Save locally and/or upload to Cloudflare R2 (S3-compatible)
- **📊 Session Metrics** — Track generation stats, success rates, and performance

## Architecture

```
ai_project/
├── main.py                  # Entry point — run the API server
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── src/
    └── task2/
        ├── api/             # FastAPI routes, models, and app
        ├── core/            # OpenAI clients, orchestrator, config, vision analysis
        ├── enhancement/     # Image post-processing (filters, text overlay)
        ├── prompts/         # GPT-4o system prompts and user templates
        ├── storage/         # Local filesystem + Cloudflare R2 storage
        └── utils/           # Logging, metrics, validation
```

## Prerequisites

- Python 3.10+
- An [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) resource with deployments for:
  - GPT-4o (for concept generation and Vision analysis)
  - DALL-E 3 (`gpt-image-1-mini`, for image generation)
- (Optional) [Cloudflare R2](https://www.cloudflare.com/products/r2/) bucket for cloud storage

## Quick Start

### 1. Clone and navigate

```bash
cd ai_project
```

### 2. Set up environment

```bash
# Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

### 3. Run the API server

```bash
python main.py
```

By default the server starts on **http://localhost:8000**.

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `0.0.0.0` | Bind address |
| `--port` | `8000` | Server port |
| `--reload` | — | Enable auto-reload (development) |
| `--log-level` | `info` | Logging level |
| `--workers` | `1` | Number of worker processes |

**Examples:**
```bash
python main.py --reload                          # Dev mode with hot-reload
python main.py --port 8001 --log-level debug     # Custom port + verbose logs
python main.py --host 127.0.0.1 --workers 4      # Production-like
```

## API Endpoints

Once the server is running, visit **http://localhost:8000/docs** for the interactive Swagger UI.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Home: service info and endpoint list |
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/stats` | Session statistics |
| `POST` | `/api/v1/generate` | Generate a single poster |
| `POST` | `/api/v1/generate/batch` | Generate posters for multiple movies |
| `GET` | `/api/v1/images/` | List available generated images |
| `GET` | `/api/v1/images/{movie_id}` | Serve a generated image |
| `POST` | `/api/v1/orchestrator/reset` | Reset orchestrator state |

### Generate a Poster

```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "movie": {
      "id": 550,
      "title": "Fight Club",
      "genres": ["Drama", "Thriller"],
      "year": "1999",
      "synopsis": "A depressed man forms an underground fight club..."
    },
    "prompt_style": "minimal",
    "enhancement_style": "neonoir",
    "save_local": true,
    "enhance": true
  }'
```

## Environment Variables

All configuration is loaded from a `.env` file in the project root. See [`.env.example`](.env.example) for a complete reference.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AZURE_ENDPOINT` | ✅ | — | Azure OpenAI endpoint URL |
| `AZURE_API_KEY` | ✅ | — | Azure OpenAI API key |
| `AZURE_GPT4O_DEPLOYMENT` | — | `gpt-4o` | GPT-4o deployment name |
| `AZURE_DALLE_DEPLOYMENT` | — | `gpt-image-1-mini` | DALL-E deployment name |
| `STORAGE_MODE` | — | `local` | Storage mode (`local` or `s3`) |
| `IMAGE_SIZE` | — | `1024x1024` | DALL-E image size |
| `R2_ACCOUNT_ID` | for R2 | — | Cloudflare R2 account ID |
| `R2_ACCESS_KEY` | for R2 | — | Cloudflare R2 access key |
| `R2_SECRET_KEY` | for R2 | — | Cloudflare R2 secret key |

## Prompt Styles

| Style | Description |
|-------|-------------|
| `realistic` | Photorealistic characters, skin details, eye capture |
| `abstract` | Visual metaphors, artistic compositions |
| `minimal` | Clean, minimalist design, maximum impact |
| `hybrid` | Blend of realism and abstraction |

## Enhancement Styles

| Style | Description |
|-------|-------------|
| `cinematic` | Hollywood effects: bloom, glow, particles |
| `minimal` | Clean look, minimal effects |
| `vintage` | Sepia grain, scratches, retro feel |
| `neon` | Cyberpunk: neon glows, grids |
| `neonoir` | Black & white with neon accents |

## Pipeline

1. **Vision Analysis** (optional) — GPT-4o Vision analyzes the original TMDB poster (color palette, composition, mood, lighting)
2. **Concept Creation** — GPT-4o generates a cinematic visual concept based on movie metadata
3. **Image Generation** — DALL-E 3 generates the raw image (auto-fallback to Canvas if DALL-E fails)
4. **Post-Production** — Add title text, year, genres, visual effects, and color grading
5. **Storage** — Save locally and optionally upload to Cloudflare R2

## License

This project is part of the CineMatch application suite.