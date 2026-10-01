from app.datascout.datascout_schema import (
    DataScoutResponse,
    ExistingDataset,
    QualityEstimate,
    SyntheticPlan,
)

from app.datascout.integrations.hf_search import search_huggingface_datasets
from app.datascout.integrations.kaggle_search import search_kaggle_datasets


class DataScoutEngine:
    """
    Pure API-search based dataset discovery engine.
    No LLM calls — searches HuggingFace and Kaggle APIs directly.
    """

    # Common stopwords to filter out from search queries
    _STOP_WORDS = frozenset({
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "must",
        "i", "me", "my", "we", "our", "you", "your", "he", "she", "it",
        "they", "them", "their", "this", "that", "these", "those",
        "and", "or", "but", "if", "then", "so", "because", "as", "of",
        "in", "on", "at", "to", "for", "with", "by", "from", "up", "about",
        "into", "through", "during", "before", "after", "between", "out",
        "above", "below", "all", "each", "every", "both", "few", "more",
        "most", "other", "some", "such", "no", "not", "only", "own", "same",
        "than", "too", "very", "just", "also", "how", "what", "which", "who",
        "when", "where", "why", "here", "there", "again", "once",
        # Dataset generation specific stopwords
        "generate", "create", "make", "build", "produce", "give", "want",
        "dataset", "data", "set", "table", "rows", "columns", "records",
        "include", "including", "contain", "containing", "like", "similar",
        "sound", "look", "looking", "find", "get", "show", "list",
        "detailed", "realistic", "real", "fake", "synthetic", "sample",
        "mix", "variety", "different", "various", "multiple",
        "please", "thanks", "thank", "help", "using", "use",
    })

    @staticmethod
    def _extract_search_keywords(prompt: str) -> list[str]:
        """
        Extract meaningful search keywords from a natural language prompt.
        Returns a list of keyword combinations to try (best first).
        
        Example: 'Generate a dataset of 30 product reviews similar to the 
                  Amazon Reviews dataset on Hugging Face'
        Returns: ['amazon product reviews', 'product reviews', 'amazon reviews']
        """
        import re

        # Normalize: lowercase, remove punctuation except hyphens
        text = prompt.lower()
        text = re.sub(r"[^\w\s-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        # Remove numeric-only tokens (like "30", "1000")
        words = [w for w in text.split() if not w.isdigit()]

        # Filter stopwords
        meaningful = [w for w in words if w not in DataScoutEngine._STOP_WORDS and len(w) > 1]

        if not meaningful:
            # Fallback: use original prompt trimmed
            return [prompt.strip()[:50]]

        # Strategy 1: All meaningful keywords joined (max 5 words for API effectiveness)
        primary = " ".join(meaningful[:5])

        # Strategy 2: Look for known platform/dataset names as anchors
        anchors = []
        known_names = ["amazon", "imdb", "yelp", "twitter", "kaggle", "hugging", "face",
                       "mnist", "cifar", "imagenet", "titanic", "iris", "wine", "boston",
                       "spotify", "netflix", "uber", "airbnb", "stackoverflow"]
        for name in known_names:
            if name in text:
                # Build query around the anchor
                anchor_words = [name] + [w for w in meaningful if w != name][:3]
                anchors.append(" ".join(anchor_words))

        # Strategy 3: First 3 meaningful words (short query)
        short = " ".join(meaningful[:3])

        # Strategy 4: Bigrams of meaningful words for focused search
        bigrams = []
        for i in range(len(meaningful) - 1):
            bigrams.append(f"{meaningful[i]} {meaningful[i+1]}")

        # Deduplicate and order: anchored queries > primary > short > bigrams
        seen = set()
        queries = []
        for q in anchors + [primary, short] + bigrams[:2]:
            q = q.strip()
            if q and q not in seen:
                seen.add(q)
                queries.append(q)

        return queries[:4]  # Max 4 search attempts

    def analyze(self, prompt: str) -> DataScoutResponse:
        # Step 1: Extract search keywords from natural language prompt
        search_queries = self._extract_search_keywords(prompt)

        # Step 2: Search with multiple queries for better recall
        combined: list[ExistingDataset] = []
        seen_ids: set[str] = set()

        for query in search_queries:
            hf_results = search_huggingface_datasets(query, limit=5)
            kaggle_results = search_kaggle_datasets(query, limit=5)

            for ds in hf_results + kaggle_results:
                ds_key = f"{ds.source_platform}:{ds.dataset_id}"
                if ds_key not in seen_ids:
                    seen_ids.add(ds_key)
                    combined.append(ds)

            # Stop searching if we have enough results
            if len(combined) >= 10:
                break

        # Step 3: Merge with heuristic fallback matches (for well-known datasets)
        heuristic_matches = self._heuristic_matches(prompt)
        existing_names = {d.name for d in combined}
        for ds in heuristic_matches:
            if ds.name not in existing_names:
                combined.append(ds)
                existing_names.add(ds.name)

        # Step 4: Filter to only fetchable datasets
        fetchable = [
            d for d in combined
            if d.source_platform in ("huggingface", "kaggle") and d.dataset_id
        ]

        # Step 5: Sort by quality × similarity (best first)
        fetchable.sort(key=lambda d: d.quality_score * d.similarity_score, reverse=True)

        # Step 6: Build response — no LLM needed
        if fetchable:
            return DataScoutResponse(
                strategy="Existing Dataset",
                confidence=0.95,
                domain=self._infer_domain(prompt),
                industry="General",
                use_case="Dataset Discovery",
                existing_datasets=fetchable,
                reasoning=f"Found {len(fetchable)} verified public datasets on HuggingFace & Kaggle matching '{prompt}'.",
            )
        else:
            return DataScoutResponse(
                strategy="Fully Synthetic Generation",
                confidence=0.88,
                domain=self._infer_domain(prompt),
                industry="General",
                use_case="Synthetic Data Generation",
                synthetic_plan=SyntheticPlan(
                    deterministic_columns=["id", "name", "email", "date", "status"],
                    llm_columns=["description"],
                    business_constraints=["Deterministic Faker for standard fields, LLM for text fields"],
                ),
                quality_estimate=QualityEstimate(
                    realism_score=0.92,
                    completeness_score=0.96,
                    privacy_risk="Low",
                ),
                reasoning=f"No matching public datasets found for '{prompt}'. Generating fully synthetic dataset.",
            )

    @staticmethod
    def pick_best_dataset(datasets: list[ExistingDataset]) -> ExistingDataset | None:
        """Select the best dataset by quality_score × similarity_score."""
        if not datasets:
            return None
        return max(datasets, key=lambda d: d.quality_score * d.similarity_score)

    @staticmethod
    def _infer_domain(prompt: str) -> str:
        """Simple keyword-based domain inference — no LLM needed."""
        lower = prompt.lower()
        domain_keywords = {
            "Finance": ["finance", "bank", "credit", "loan", "stock", "trading", "investment", "fraud"],
            "Healthcare": ["health", "medical", "patient", "hospital", "disease", "clinical", "pharma", "drug"],
            "E-Commerce": ["ecommerce", "e-commerce", "product", "shopping", "order", "retail", "customer review"],
            "HR & People": ["employee", "hr", "salary", "attrition", "workforce", "hiring", "recruitment"],
            "Education": ["student", "school", "university", "education", "grade", "exam", "course"],
            "Technology": ["software", "iot", "sensor", "network", "cybersecurity", "log", "server"],
            "Marketing": ["marketing", "campaign", "ad", "click", "conversion", "social media"],
            "Real Estate": ["real estate", "property", "housing", "rent", "mortgage"],
            "Transportation": ["transport", "logistics", "fleet", "delivery", "route", "shipping"],
            "Entertainment": ["movie", "music", "game", "review", "rating", "entertainment", "imdb"],
        }
        for domain, keywords in domain_keywords.items():
            if any(kw in lower for kw in keywords):
                return domain
        return "General"

    @staticmethod
    def _heuristic_matches(prompt: str) -> list[ExistingDataset]:
        """Return well-known dataset matches for common queries."""
        lower = prompt.lower()
        matches: list[ExistingDataset] = []

        known_public_datasets = [
            {
                "keywords": ["titanic", "passenger", "survived"],
                "dataset": ExistingDataset(
                    name="Titanic - Machine Learning from Disaster",
                    description="Classic Kaggle dataset containing passenger demographics and survival outcomes.",
                    estimated_rows=891,
                    estimated_columns=12,
                    license="CC0: Public Domain",
                    format="CSV",
                    download_source="https://www.kaggle.com/c/titanic/data",
                    quality_score=0.98,
                    similarity_score=0.96,
                    advantages=["Clean benchmarks", "Standard ML tutorial dataset"],
                    limitations=["Small sample size"],
                    source_platform="kaggle",
                    dataset_id="c/titanic",
                ),
            },
            {
                "keywords": ["credit card", "fraud", "transaction"],
                "dataset": ExistingDataset(
                    name="Credit Card Fraud Detection Dataset",
                    description="Kaggle dataset of European cardholder transactions with labeled fraud events.",
                    estimated_rows=284807,
                    estimated_columns=31,
                    license="DbCL v1.0",
                    format="CSV",
                    download_source="https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud",
                    quality_score=0.95,
                    similarity_score=0.92,
                    advantages=["Real-world transaction distribution"],
                    limitations=["Anonymized PCA features V1-V28"],
                    source_platform="kaggle",
                    dataset_id="mlg-ulb/creditcardfraud",
                ),
            },
            {
                "keywords": ["mnist", "digit", "handwritten"],
                "dataset": ExistingDataset(
                    name="MNIST Handwritten Digits",
                    description="Yann LeCun's benchmark dataset of 70,000 28x28 grayscale digit images.",
                    estimated_rows=70000,
                    estimated_columns=785,
                    license="CC BY-SA 3.0",
                    format="CSV / NPZ",
                    download_source="http://yann.lecun.com/exdb/mnist/",
                    quality_score=0.99,
                    similarity_score=0.95,
                    advantages=["Standard computer vision benchmark"],
                    limitations=["Grayscale only"],
                    source_platform="huggingface",
                    dataset_id="ylecun/mnist",
                ),
            },
        ]

        for entry in known_public_datasets:
            if any(kw in lower for kw in entry["keywords"]):
                matches.append(entry["dataset"])

        return matches
