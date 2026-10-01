from typing import Any, Literal
from pydantic import BaseModel, Field


class ExistingDataset(BaseModel):
    name: str = Field(..., description="Dataset Name")
    description: str = Field(..., description="Brief summary of dataset content and suitability")
    estimated_rows: int = Field(..., description="Estimated row count")
    estimated_columns: int = Field(..., description="Estimated column count")
    license: str = Field(..., description="Data license, e.g. CC-BY 4.0, MIT, Open Database License")
    format: str = Field(..., description="File format, e.g. CSV, Parquet, JSON, SQL")
    download_source: str = Field(..., description="Direct link or platform source, e.g. Kaggle, HuggingFace, UCI")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Overall dataset quality score (0.0 - 1.0)")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Relevance to user request (0.0 - 1.0)")
    advantages: list[str] = Field(default_factory=list, description="Key advantages of using this dataset")
    limitations: list[str] = Field(default_factory=list, description="Known limitations or missing attributes")
    source_platform: str = Field(default="unknown", description="Platform: 'huggingface' or 'kaggle'")
    dataset_id: str = Field(default="", description="Platform-specific dataset identifier for fetching")


class FetchResult(BaseModel):
    rows: list[dict[str, Any]] = Field(default_factory=list)
    count: int = 0
    columns: list[str] = Field(default_factory=list)
    source_platform: str = ""
    dataset_name: str = ""
    truncated: bool = False
    total_available: int = 0
    requires_auth: bool = False


class GapAnalysis(BaseModel):
    fetched_columns: list[str] = Field(default_factory=list)
    required_columns: list[str] = Field(default_factory=list)
    missing_columns: list[str] = Field(default_factory=list)
    has_gaps: bool = False


class AugmentationPlan(BaseModel):
    base_dataset: str | None = None
    missing_columns: list[str] = Field(default_factory=list)
    derived_features: list[str] = Field(default_factory=list)
    encoding_steps: list[str] = Field(default_factory=list)
    cleaning_steps: list[str] = Field(default_factory=list)


class SyntheticPlan(BaseModel):
    columns: list[dict[str, Any]] = Field(default_factory=list)
    deterministic_columns: list[str] = Field(default_factory=list)
    llm_columns: list[str] = Field(default_factory=list)
    distribution_hints: dict[str, str] = Field(default_factory=dict)
    business_constraints: list[str] = Field(default_factory=list)


class QualityEstimate(BaseModel):
    realism_score: float = Field(default=0.9, ge=0.0, le=1.0)
    completeness_score: float = Field(default=0.95, ge=0.0, le=1.0)
    privacy_risk: str = Field(default="Low")


StrategyType = Literal[
    "Existing Dataset",
    "Dataset Augmentation",
    "Dataset Merge",
    "Synthetic Expansion",
    "Schema Learning",
    "Fully Synthetic Generation",
]


class DataScoutResponse(BaseModel):
    strategy: StrategyType = Field(..., description="Selected strategy")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in chosen strategy")
    domain: str = Field(default="General", description="Extracted domain")
    industry: str = Field(default="General", description="Extracted industry")
    use_case: str = Field(default="Synthetic Dataset Generation", description="Extracted use case")
    existing_datasets: list[ExistingDataset] = Field(default_factory=list)
    augmentation_plan: AugmentationPlan = Field(default_factory=AugmentationPlan)
    synthetic_plan: SyntheticPlan = Field(default_factory=SyntheticPlan)
    quality_estimate: QualityEstimate = Field(default_factory=QualityEstimate)
    reasoning: str = Field(..., description="Step-by-step reasoning behind strategy selection")
