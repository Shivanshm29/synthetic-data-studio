# ⚙ Synthetic Data Studio - Backend

High-performance Python backend powered by FastAPI, Pydantic v2, and hybrid AI/algorithmic synthetic generation engines.

---

## 🏗 Architecture & Modules

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

## 🚀 Getting Started

### 1. Create Environment

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Configure `.env`

Copy `.env.example` to `.env` and provide your LLM API key:

```bash
cp .env.example .env
```

Example for Google Gemini:
```env
LLM_API_KEY=your_gemini_api_key_here
LLM_MODEL=gemini-1.5-flash
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
```

### 4. Run Server

```bash
uvicorn app.main:app --reload --port 8000
```

Access OpenAPI documentation at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Tests

Execute the unit test suite:

```bash
python -m unittest discover -s tests -p "test_*.py"
```
