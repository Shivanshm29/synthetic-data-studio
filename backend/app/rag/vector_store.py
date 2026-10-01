import json
import math
from pathlib import Path
from typing import Any
from openai import OpenAI

from app.core.config import settings


def cosine_similarity(v1: list[float], v2: list[float]) -> float:
    """Calculate cosine similarity between two float vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot / (norm1 * norm2)


class VectorStore:
    """
    Vector Database & Lookup Store for RAG dataset templates.
    Generates, caches, and searches dense vector embeddings using Cosine Similarity k-NN search.
    """

    def __init__(self, cache_path: Path | str | None = None) -> None:
        if cache_path is None:
            cache_path = Path(__file__).resolve().parent / "vector_cache.json"
        self.cache_path = Path(cache_path)
        self.vector_cache: dict[str, list[float]] = {}
        self.client = None

        try:
            self.client = OpenAI(
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL,
                timeout=15.0,
            )
        except Exception:
            self.client = None

        self._load_cache()

    def _load_cache(self) -> None:
        try:
            if self.cache_path.exists():
                with open(self.cache_path, "r", encoding="utf-8") as f:
                    self.vector_cache = json.load(f)
            else:
                self.vector_cache = {}
        except Exception as err:
            print(f"[VectorStore] Warning loading vector cache: {err}")
            self.vector_cache = {}

    def _save_cache(self) -> None:
        try:
            with open(self.cache_path, "w", encoding="utf-8") as f:
                json.dump(self.vector_cache, f)
        except Exception as err:
            print(f"[VectorStore] Warning saving vector cache: {err}")

    def get_embedding(self, text: str) -> list[float]:
        """
        Generate vector embedding for input text using OpenAI / OpenRouter embedding API,
        with fallback to a deterministic dense vector representation.
        """
        if not text.strip():
            return []

        # Try API embedding if client is available
        if self.client and settings.LLM_API_KEY:
            try:
                # Try standard embedding models
                models = ["text-embedding-3-small", "text-embedding-ada-002", settings.LLM_MODEL]
                for model in models:
                    try:
                        res = self.client.embeddings.create(input=text, model=model)
                        if res and res.data and len(res.data) > 0:
                            return res.data[0].embedding
                    except Exception:
                        continue
            except Exception as err:
                print(f"[VectorStore] Embedding API call skipped: {err}")

        # Local Fallback Vector Generator (32-dimensional hash-based pseudo-embedding)
        return self._generate_local_vector(text)

    def _generate_local_vector(self, text: str, dim: int = 64) -> list[float]:
        """
        Generates a deterministic local vector embedding using character n-gram hashing
        when online embedding APIs are unavailable.
        """
        words = text.lower().split()
        vector = [0.0] * dim
        for w in words:
            # Hash word into dimension indices
            h = hash(w)
            idx = abs(h) % dim
            val = ((h >> 8) & 0xFF) / 255.0
            vector[idx] += val

        # Normalize vector
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]
        return vector

    def index_templates(self, templates: list[dict[str, Any]], force: bool = False) -> None:
        """
        Computes and caches vector embeddings for all knowledge base templates.
        """
        updated = False
        for tmpl in templates:
            tmpl_id = tmpl.get("id")
            if not tmpl_id:
                continue

            if not force and tmpl_id in self.vector_cache:
                continue

            # Construct representative text for vector embedding
            repr_text = f"Domain: {tmpl.get('domain')} | Industry: {tmpl.get('industry')} | Title: {tmpl.get('title')} | Description: {tmpl.get('description')} | Keywords: {', '.join(tmpl.get('keywords', []))}"
            emb = self.get_embedding(repr_text)
            if emb:
                self.vector_cache[tmpl_id] = emb
                updated = True

        if updated:
            self._save_cache()

    def search_vector_similarity(
        self,
        query: str,
        templates: list[dict[str, Any]],
        top_k: int = 2
    ) -> list[tuple[float, dict[str, Any]]]:
        """
        Performs vector k-NN lookup using Cosine Similarity between query embedding vector
        and cached template embedding vectors.
        """
        if not query.strip() or not templates:
            return []

        # Ensure all templates are indexed in vector cache
        self.index_templates(templates)

        query_vector = self.get_embedding(query)
        if not query_vector:
            return []

        results: list[tuple[float, dict[str, Any]]] = []
        for tmpl in templates:
            tmpl_id = tmpl.get("id")
            tmpl_vector = self.vector_cache.get(tmpl_id)
            if not tmpl_vector:
                # Generate if missing
                repr_text = f"Domain: {tmpl.get('domain')} | Title: {tmpl.get('title')} | Description: {tmpl.get('description')} | Keywords: {', '.join(tmpl.get('keywords', []))}"
                tmpl_vector = self.get_embedding(repr_text)
                if tmpl_vector and tmpl_id:
                    self.vector_cache[tmpl_id] = tmpl_vector
                    self._save_cache()

            if tmpl_vector:
                sim = cosine_similarity(query_vector, tmpl_vector)
                results.append((sim, tmpl))

        # Sort descending by cosine similarity score
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:top_k]
