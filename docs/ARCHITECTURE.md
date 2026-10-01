# 🏛 System Architecture Specification

This document details the architectural design, component interactions, and data lifecycle of **Synthetic Data Studio**.

---

## 1. High-Level Architecture Overview

Synthetic Data Studio consists of an interactive Next.js frontend and an extensible FastAPI backend delivering four primary capabilities:

1. **Intelligent Dataset Discovery (DataScout)**: Searches Hugging Face and Kaggle repositories before synthesising from scratch.
2. **Schema Inference & RAG Grounding**: Converts user requirements into formal domain schemas guided by indexed reference templates.
3. **Hybrid Generation Engine**: Blends deterministic, high-throughput Faker algorithms for standard data types with LLM synthesis for complex semantic columns.
4. **Data Profiling & Gap Augmentation**: Detects gaps, missing values, or incomplete schemas and synthesizes missing attributes.

```mermaid
flowchart TD
    subgraph Client [Frontend - Next.js 15]
        UI[Studio Interface]
        State[React State & Hooks]
        ClientExporter[Client-Side Exporters CSV/JSON/JSONL]
    end

    subgraph API [FastAPI Service Layer]
        Router[API Routers]
        Config[Pydantic Settings]
    end

    subgraph Core [Synthetic Data Engine]
        DataScout[DataScout Discovery Engine]
        RAG[RAG Hybrid Vector Engine]
        SchemaGen[Schema Generator]
        Planner[Generation Planner]
        Orchestrator[Generation Orchestrator]
    end

    subgraph Providers [Generation Providers]
        FakerProv[Deterministic Faker Provider]
        LLMProv[LLM Semantic Provider]
    end

    subgraph External [External Services]
        HF[Hugging Face Hub]
        Kaggle[Kaggle Datasets API]
        LLMAPI[OpenAI / Gemini / OpenRouter / Ollama]
    end

    UI --> State
    State -->|HTTP REST| Router
    State --> ClientExporter

    Router --> DataScout
    Router --> Orchestrator
    Router --> RAG

    DataScout --> HF
    DataScout --> Kaggle

    Orchestrator --> SchemaGen
    SchemaGen --> RAG
    RAG --> LLMAPI

    Orchestrator --> Planner
    Planner --> FakerProv
    Planner --> LLMProv

    LLMProv --> LLMAPI
```

---

## 2. Component Breakdown

### 2.1 DataScout Engine (`app.datascout`)

The DataScout engine minimizes unnecessary compute by discovering verified public datasets that already meet the user's criteria:

- **Keyword Extraction**: Cleanses stopwords and extracts key entity tokens from prompts.
- **Search Execution**: Queries Hugging Face Hub API and Kaggle Datasets API concurrently.
- **Quality & Similarity Scoring**: Computes composite relevance scores based on downloads, upvotes, and textual similarity.
- **Heuristic Matching**: Fast-path cache for foundational benchmark datasets (e.g., Titanic, Credit Card Fraud, MNIST).

### 2.2 RAG Knowledge Engine (`app.rag`)

Ensures generated datasets adhere to industry standard naming conventions, data types, and realistic relationships:

- **Knowledge Base**: Curated catalog of production-grade schemas spanning Finance, Healthcare, E-Commerce, SaaS, and Telemetry.
- **Hybrid Retrieval**: Combines BM25 lexical token matching with dense cosine similarity calculated against cached vector embeddings.
- **Prompt Injection**: Injects top-matching domain schemas into the LLM system prompt as few-shot guides.

### 2.3 Generation Orchestrator (`app.generation`)

The generation orchestrator follows a multi-phase lifecycle:

1. **Schema Generation**: Infers column names, data types, constraints, and dependencies from prompt and RAG context.
2. **Strategy Planning**: Assigns optimal strategy per column:
   - *Deterministic*: Handled by Faker (e.g., Email, Name, Address, Phone, Date, UUID, Integer, Float).
   - *Semantic*: Handled by LLM with batched completion calls (e.g., product reviews, customer feedback, diagnostic notes).
3. **Execution & Assembly**: Generates columns respecting row dependencies (e.g., `first_name` + `last_name` driving `email`).
4. **Validation**: Verifies bounds, constraints, and non-null guarantees prior to serialization.

---

## 3. Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend
    participant API as FastAPI Router
    participant DataScout
    participant Orchestrator
    participant LLM as LLM Provider

    User->>Frontend: Enters natural language prompt
    Frontend->>API: POST /datascout/analyze
    API->>DataScout: Analyze prompt & search repositories
    DataScout-->>API: Return strategy & dataset matches
    API-->>Frontend: Display discovery options

    alt User Chooses Synthetic Generation
        Frontend->>API: POST /generate/prompt (prompt, row_count)
        API->>Orchestrator: Generate dataset
        Orchestrator->>LLM: Infer schema using RAG templates
        LLM-->>Orchestrator: Return Column Schema
        Orchestrator->>Orchestrator: Partition columns (Faker vs LLM)
        Orchestrator->>LLM: Batch generate semantic columns
        LLM-->>Orchestrator: Return text batches
        Orchestrator->>Orchestrator: Generate deterministic fields via Faker
        Orchestrator-->>API: Return generated tabular rows
        API-->>Frontend: Stream / return payload
        Frontend->>User: Render interactive data table
    end
```
