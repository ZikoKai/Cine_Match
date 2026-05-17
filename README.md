# CineMatch

AI-powered movie recommendation platform. Describe what you want to watch in natural language and get personalized recommendations with AI-generated posters.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Project](#running-the-project)
- [User Workflow](#user-workflow)
- [Features](#features)
- [API Overview](#api-overview)

---

## Overview

CineMatch is composed of three independent services that work together:

| Service | Description | Port |
|---|---|---|
| `cinematch_frontend` | Next.js web application | `3000` |
| `cinematch_recommendation` | FastAPI recommendation engine | `8001` |
| `cinematch_posters` | FastAPI AI poster generation | `8000` |

All three must be running simultaneously for the full experience.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      User Browser                       │
│                   localhost:3000                        │
└───────────────────────┬─────────────────────────────────┘
                        │ Next.js (App Router)
                        │
          ┌─────────────┴──────────────┐
          │                            │
          ▼                            ▼
┌─────────────────┐          ┌─────────────────┐
│  Recommendation │          │     Poster      │
│     Engine      │          │   Generation    │
│  localhost:8001 │          │  localhost:8000 │
│                 │          │                 │
│  FastAPI        │          │  FastAPI        │
│  PostgreSQL     │          │  DALL-E 3       │
│  pgvector       │          │  GPT-4o Vision  │
│  Azure OpenAI   │          │  Azure OpenAI   │
└─────────────────┘          └─────────────────┘
          │
          ▼
┌─────────────────┐
│   PostgreSQL    │
│   + pgvector    │
│  (Azure / local)│
└─────────────────┘
```

### Recommendation Flow

1. User sends a natural language prompt (e.g. *"A dark psychological thriller set in the 90s"*)
2. Azure OpenAI Chat (GPT-4.1-mini) parses the prompt and extracts structured metadata (keywords, genres, themes, emotions, specificity score)
3. Azure OpenAI Embeddings converts the normalized query into a vector
4. PostgreSQL + pgvector retrieves the top semantic candidates
5. The ranking service re-scores candidates using vector similarity, keyword matching, vote counts, and prompt specificity
6. Top 6 movies are returned to the frontend
7. In parallel, the poster service generates custom AI posters for each movie via DALL-E 3

---

## Tech Stack

### Frontend — `cinematch_frontend`
| Layer | Technology |
|---|---|
| Framework | Next.js 16 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS v4 + inline styles |
| Auth | NextAuth.js v4 (JWT, credentials provider) |
| Fonts | Inter Tight, Public Sans (Google Fonts) |
| State | React `useState` / `useEffect` |
| Persistence | `localStorage` (history, favorites, watchlist, pins) |

### Recommendation Backend — `cinematch_recommendation`
| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Language | Python 3.10+ |
| Database | PostgreSQL + pgvector |
| AI | Azure OpenAI (GPT-4.1-mini + text-embedding-3-small) |
| Auth | JWT (python-jose) |
| DB Driver | asyncpg |

### Poster Backend — `cinematch_posters`
| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Language | Python 3.10+ |
| AI | Azure OpenAI (GPT-4o Vision + DALL-E 3) |
| Storage | Local filesystem + Cloudflare R2 (optional) |
| Enhancement | Custom image post-processing pipeline |

---

## Project Structure

```
CineMatch/
├── cinematch_frontend/          # Next.js application
│   ├── app/
│   │   ├── page.tsx             # Landing page
│   │   ├── layout.tsx           # Root layout + SessionProvider
│   │   ├── globals.css          # Global styles + scrollbar
│   │   ├── icon.svg             # Favicon
│   │   ├── (auth)/
│   │   │   ├── login/           # Login page
│   │   │   └── register/        # Register page
│   │   ├── recommend/           # Main app (recommendations)
│   │   ├── favorites/           # Favorites list
│   │   ├── watchlist/           # Watchlist
│   │   ├── onboarding/          # First-time user preferences
│   │   ├── components/
│   │   │   ├── AppSidebar.tsx   # Shared sidebar (favorites/watchlist pages)
│   │   │   └── SettingsModal.tsx # Settings popup
│   │   ├── lib/
│   │   │   └── types.ts         # Shared types + localStorage helpers
│   │   └── api/
│   │       └── auth/            # NextAuth + register API route
│   ├── middleware.ts             # Route protection
│   └── package.json
│
├── cinematch_recommendation/    # Recommendation FastAPI
│   ├── main.py
│   └── app/
│       ├── clients/             # Azure OpenAI clients
│       ├── controllers/         # API routes
│       ├── core/                # Config + app factory
│       ├── db/                  # PostgreSQL connection
│       ├── models/              # Pydantic schemas
│       ├── repositories/        # SQL queries
│       ├── services/            # Business logic (ranking, recommendation)
│       └── validators/          # Input validation
│
└── cinematch_posters/           # Poster generation FastAPI
    ├── main.py
    └── src/task2/
        ├── api/                 # FastAPI routes + models
        ├── core/                # OpenAI clients + orchestrator
        ├── enhancement/         # Image post-processing
        ├── prompts/             # GPT-4o prompt templates
        ├── storage/             # Local + R2 storage
        └── utils/               # Logging + metrics
```

---

## Prerequisites

- **Node.js** 18+ and **npm**
- **Python** 3.10+
- **PostgreSQL** with the `pgvector` extension (or Azure Database for PostgreSQL)
- An **Azure OpenAI** resource with the following deployments:
  - `text-embedding-3-small` (embeddings)
  - `gpt-4.1-mini` (prompt analysis)
  - `gpt-4o` (poster concept generation + vision)
  - `dall-e-3` / `gpt-image-1-mini` (image generation)

---

## Installation

### 1. Frontend

```powershell
cd cinematch_frontend
npm install
```

Copy and fill in the environment file:

```powershell
Copy-Item .env.example .env.local
```

### 2. Recommendation Backend

```powershell
cd cinematch_recommendation
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### 3. Poster Backend

```powershell
cd cinematch_posters
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

---

## Environment Variables

### `cinematch_frontend/.env.local`

```env
# NextAuth
NEXTAUTH_SECRET=your_secret_here
NEXTAUTH_URL=http://localhost:3000

# Backend URLs
NEXT_PUBLIC_RECOMMEND_API_URL=http://localhost:8001
NEXT_PUBLIC_POSTER_API_URL=http://localhost:8000
```

### `cinematch_recommendation/.env`

```env
# Azure OpenAI — Embeddings
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
AZURE_OPENAI_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_API_VERSION=2024-02-01

# Azure OpenAI — Chat (prompt analysis)
AZURE_OPENAI_CHAT_ENDPOINT=
AZURE_OPENAI_CHAT_KEY=
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4.1-mini
AZURE_OPENAI_CHAT_MODEL=gpt-4.1-mini
AZURE_OPENAI_CHAT_API_VERSION=2024-12-01-preview

# PostgreSQL
AZURE_PG_HOST=
AZURE_PG_DB=
AZURE_PG_USER=
AZURE_PG_PASS=
AZURE_PG_PORT=5432

# JWT Auth
JWT_SECRET=your_jwt_secret_here

# Ranking tuning
VECTOR_CANDIDATE_LIMIT=20
MIN_FINAL_RESULTS=6
MAX_FINAL_RESULTS=20
```

### `cinematch_posters/.env`

```env
# Azure OpenAI — GPT-4o (concept + vision)
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_KEY=
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Azure OpenAI — DALL-E 3
AZURE_DALLE_ENDPOINT=
AZURE_DALLE_KEY=
AZURE_DALLE_DEPLOYMENT=gpt-image-1-mini

# Storage (optional — Cloudflare R2)
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
```

---

## Running the Project

Open **three separate terminals** and run each service:

**Terminal 1 — Frontend**
```powershell
cd cinematch_frontend
npm run dev
# → http://localhost:3000
```

**Terminal 2 — Recommendation Backend**
```powershell
cd cinematch_recommendation
.venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 127.0.0.1 --port 8001
# → http://localhost:8001/docs
```

**Terminal 3 — Poster Backend**
```powershell
cd cinematch_posters
.venv\Scripts\Activate.ps1
python main.py
# → http://localhost:8000/docs
```

---

## User Workflow

```
/ (Landing page)
    │
    ├── "Log in"           →  /login  →  /recommend
    │
    └── "Sign up" /
        "Get started"      →  /register
                                  │
                                  ▼
                            /onboarding
                            (genre preferences,
                             dislikes, duration)
                                  │
                            Transition screen
                            "Creating your profile..."
                            "Memorizing your preferences..."
                            "Learning your taste..."
                                  │
                                  ▼
                            /recommend  ←────────────────┐
                            (main app)                   │
                                  │                      │
                            ┌─────┴──────┐               │
                            │            │               │
                        /favorites   /watchlist          │
                            │            │               │
                            └─────┬──────┘               │
                                  │                      │
                            Click "CineMatch" ───────────┘
```

### In `/recommend`

1. User types a prompt or clicks a suggestion chip
2. "Searching..." messages rotate while the API processes the request (minimum 8 seconds for UX)
3. Movie cards appear with shimmer placeholders for posters
4. "Generating your posters..." messages rotate while DALL-E generates artwork
5. Posters fade in as they load
6. "Here are your picks, [Name]!" — personalized heading appears
7. User can open any movie for details, navigate with ← → arrows, add to favorites/watchlist

---

## Features

### Recommendation
- Natural language prompt → up to 6 AI-ranked movie recommendations
- Semantic search via pgvector + intelligent re-ranking
- Conversation history with sidebar navigation
- Pin, rename, delete conversations
- Stale-while-revalidate: instant display from cache, refresh from API in background

### AI Posters
- Custom poster generated per movie via DALL-E 3
- GPT-4o Vision analyzes original TMDB posters for style guidance
- Multiple styles: realistic, hybrid, minimal, abstract
- Post-production enhancement pipeline
- Shimmer placeholder until poster loads

### User Account
- Register / Login with JWT authentication
- Onboarding questionnaire (liked genres, disliked genres, preferred duration)
- Favorites and Watchlist synced to database
- Settings modal: profile, security, preferences, account
- Sign out from settings

### UX Details
- Suggestion chips (6 random from a pool of 20, shuffled on each load)
- Personalized headings (5 rotating phrases with first name)
- Prev/Next navigation in movie detail modal (keyboard ← →)
- Backdrop blur on detail modal
- Auto-growing textarea input (Shift+Enter for newline, Enter to send)
- Gold scrollbar, send button spring animation

---

## API Overview

### Recommendation API (`localhost:8001`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/recommend` | Get movie recommendations from a prompt |
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive JWT |
| `GET` | `/lists/conversations` | Get user conversation history |
| `POST` | `/lists/conversations` | Save a conversation |
| `PATCH` | `/lists/conversations/{id}` | Update conversation (poster URLs, title) |
| `DELETE` | `/lists/conversations/{id}` | Delete a conversation |
| `GET` | `/lists/favorites` | Get user favorites |
| `POST` | `/lists/favorites` | Add to favorites |
| `DELETE` | `/lists/favorites/{id}` | Remove from favorites |
| `GET` | `/lists/watchlist` | Get user watchlist |
| `POST` | `/lists/watchlist` | Add to watchlist |
| `DELETE` | `/lists/watchlist/{id}` | Remove from watchlist |
| `GET` | `/health` | Health check |

Full interactive docs: `http://localhost:8001/docs`

### Poster API (`localhost:8000`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/generate` | Generate a poster for a single movie |
| `POST` | `/api/v1/generate/batch` | Generate posters for multiple movies |
| `GET` | `/api/v1/images/{movie_id}` | Serve a generated poster |
| `GET` | `/health` | Health check |

Full interactive docs: `http://localhost:8000/docs`
