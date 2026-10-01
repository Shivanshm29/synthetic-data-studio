import json
import math
import re
from pathlib import Path
from typing import Any


from app.rag.vector_store import VectorStore


class RAGEngine:
    """
    RAG (Retrieval-Augmented Generation) Engine with Vector Database & Vector Cosine Similarity Lookup.
    Retrieves production dataset templates from knowledge_base.json using dense vector embeddings + hybrid keyword matching.
    """

    _instance = None

    def __init__(self, kb_path: Path | str | None = None) -> None:
        if kb_path is None:
            kb_path = Path(__file__).resolve().parent / "knowledge_base.json"
        self.kb_path = Path(kb_path)
        self.templates: list[dict[str, Any]] = []
        self._load_knowledge_base()
        self.vector_store = VectorStore()

    @classmethod
    def get_instance(cls) -> "RAGEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_knowledge_base(self) -> None:
        try:
            if self.kb_path.exists():
                with open(self.kb_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Check for v3.0.0 knowledge_collections or legacy templates
                    if "knowledge_collections" in data:
                        collections = data.get("knowledge_collections", {})
                        flattened = []
                        for col_name, records in collections.items():
                            if isinstance(records, list):
                                for r in records:
                                    if isinstance(r, dict):
                                        # Fill default fields for smooth retrieval
                                        if "title" not in r:
                                            r["title"] = r.get("domain") or r.get("semantic_type") or r.get("id", "Knowledge Record")
                                        if "description" not in r:
                                            r["description"] = r.get("retrieval_text") or str(r.get("use_cases") or "")
                                        flattened.append(r)
                        self.templates = flattened
                    else:
                        self.templates = data.get("templates", [])
            else:
                self.templates = []
        except Exception as err:
            print(f"[RAGEngine] Warning: Failed to load knowledge base from {self.kb_path}: {err}")
            self.templates = []

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        text = re.sub(r"[^\w\s-]", " ", text)
        words = [w.strip() for w in text.split() if len(w.strip()) > 1]
        return words

    def _score_template(self, prompt_tokens: set[str], template: dict[str, Any]) -> float:
        """
        Calculate BM25 / TF-IDF style similarity score between prompt tokens and a template.
        """
        if not prompt_tokens:
            return 0.0

        score = 0.0

        title_tokens = set(self._tokenize(template.get("title", "")))
        domain_tokens = set(self._tokenize(template.get("domain", "")))
        industry_tokens = set(self._tokenize(template.get("industry", "")))
        keywords = set([k.lower() for k in template.get("keywords", [])])

        title_overlap = len(prompt_tokens.intersection(title_tokens))
        domain_overlap = len(prompt_tokens.intersection(domain_tokens))
        industry_overlap = len(prompt_tokens.intersection(industry_tokens))
        keyword_overlap = len(prompt_tokens.intersection(keywords))

        score += title_overlap * 4.0
        score += keyword_overlap * 3.0
        score += domain_overlap * 2.5
        score += industry_overlap * 2.0

        desc_tokens = set(self._tokenize(template.get("description", "")))
        desc_overlap = len(prompt_tokens.intersection(desc_tokens))
        score += desc_overlap * 1.0

        cols = [col.get("name", "").lower() for col in template.get("columns", [])]
        col_tokens = set(self._tokenize(" ".join(cols)))
        col_overlap = len(prompt_tokens.intersection(col_tokens))
        score += col_overlap * 1.5

        return score

    def retrieve(self, prompt: str, top_k: int = 2) -> list[dict[str, Any]]:
        """
        Retrieve top-K most relevant dataset production templates using dense vector lookup + BM25 hybrid ranking.
        """
        if not self.templates:
            return []

        # 1. Perform Dense Vector Cosine Similarity Search
        vector_results = self.vector_store.search_vector_similarity(prompt, self.templates, top_k=len(self.templates))
        vec_score_map = {tmpl.get("id"): sim for sim, tmpl in vector_results}

        # 2. Perform Keyword BM25 Scoring
        prompt_tokens = set(self._tokenize(prompt))

        hybrid_scored: list[tuple[float, dict[str, Any]]] = []
        for tmpl in self.templates:
            tmpl_id = tmpl.get("id")
            v_score = vec_score_map.get(tmpl_id, 0.0)
            k_score = self._score_template(prompt_tokens, tmpl) / 10.0  # normalize keyword score

            # Combined Hybrid Score (70% Vector Cosine Sim + 30% Keyword Match)
            hybrid_score = (0.7 * v_score) + (0.3 * k_score)
            if hybrid_score > 0:
                hybrid_scored.append((hybrid_score, tmpl))

        # Sort descending by hybrid vector similarity score
        hybrid_scored.sort(key=lambda item: item[0], reverse=True)

        if not hybrid_scored:
            return self.templates[:min(top_k, len(self.templates))]

        return [tmpl for _, tmpl in hybrid_scored[:top_k]]

    def format_rag_context(self, prompt: str, top_k: int = 2) -> str:
        """
        Format retrieved reference templates as markdown few-shot guidelines for LLM prompts.
        """
        matches = self.retrieve(prompt, top_k=top_k)
        if not matches:
            return ""

        context_lines = [
            "## FEW-SHOT REFERENCE PRODUCTION TEMPLATES (RAG CONTEXT)",
            "The following production-grade dataset design templates are retrieved from our knowledge base.",
            "Use these reference examples to infer realistic column choices, data types, constraints, descriptions, and examples:\n"
        ]

        for idx, tmpl in enumerate(matches, 1):
            context_lines.append(f"### Reference Template {idx}: {tmpl.get('title')} ({tmpl.get('domain')})")
            context_lines.append(f"- **Description**: {tmpl.get('description')}")
            context_lines.append(f"- **Production Type**: {tmpl.get('production_type')}")
            context_lines.append("- **Recommended Columns & Constraints**:")

            for col in tmpl.get("columns", [])[:8]:  # Top 8 columns per template to keep context concise
                c_name = col.get("name")
                c_type = col.get("type")
                c_desc = col.get("description")
                c_ex = col.get("example")
                c_constraints = json.dumps(col.get("constraints", []))
                context_lines.append(
                    f"  - `{c_name}` ({c_type}): {c_desc} | Constraints: {c_constraints} | Example: \"{c_ex}\""
                )

            context_lines.append("")

        return "\n".join(context_lines)
