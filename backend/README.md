# Synthetic Data Studio - Backend Service

High-performance Python backend service built on FastAPI and Pydantic v2, featuring hybrid deterministic (Faker) and LLM-driven synthetic data generation pipelines, automated dataset discovery, and RAG-guided schema modeling.

---

## Architecture & Modules

```
backend/app/
├── api/
│   ├── routes/
│   │   ├── health.py             # Uptime & health check probes
│   │   ├── generate.py           # Core schema-to-dataset generation
│   │   ├── prompt_generation.py  # Prompt-to-dataset pipeline
│   │   ├── datascout_router.py   # Dataset search, analysis, & fetch routes
│   │   ├── fill_gaps.py          # Gap analysis & augmentation routes
│   │   └── rag_router.py         # Knowledge base & vector retrieval
│   └── schemas/                  # Pydantic v2 request/response models
├── core/
│   ├── config.py                 # Pydantic Settings & environment validation
│   └── exceptions.py             # Domain-specific error handling
├── datascout/                    # Discovery & profiling engine
│   ├── integrations/             # Hugging Face & Kaggle search/fetch clients
│   ├── datascout_engine.py       # Heuristic & API multi-query search orchestrator
│   └── profiler.py               # Column profiling & schema extractor
├── domain/                       # Core abstractions (Column, Dataset, Constraint)
├── generation/
│   ├── orchestrator.py           # Coordinates schema -> plan -> generation pipeline
│   ├── gap_filler.py             # Imputes missing columns in existing datasets
│   ├── planners/                 # LLM and rule-based generation planners
│   ├── providers/                # Deterministic Faker & LLM generation providers
│   ├── schema/                   # RAG-augmented schema inference engine
│   └── strategies/               # Specialized column generators (Email, Date, etc.)
├── rag/                          # Retrieval-Augmented Generation
│   ├── knowledge_base.json       # Production domain schema templates
│   ├── rag_engine.py             # Hybrid BM25 + dense vector matching
│   └── vector_store.py           # Local embedding cache & cosine similarity store
└── main.py                       # FastAPI application factory & CORS configuration
```

---

## Getting Started

### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\Activate.ps1

# On Linux / macOS:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and configure your LLM provider credentials:

```bash
cp .env.example .env
```

**Recommended Configuration (Google Gemini):**
```env
LLM_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-2.5-flash
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

> **Note on Model Selection**: `gemini-2.5-flash` provides the optimal balance of speed, cost efficiency, and structured output adherence. For demanding domain-specific reasoning, `gemini-2.5-pro` can also be specified. The backend includes automatic fallback mechanisms between verified production models.

### 4. Start Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

Interactive API documentation:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Running Verification Tests

Run the full backend test suite:

```bash
python -m unittest discover -s tests -p "test_*.py"
```
