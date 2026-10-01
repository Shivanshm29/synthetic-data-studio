from pydantic import BaseModel, Field, PositiveInt
    
from app.domain.column import Column
from app.domain.relationship import Relationship
from app.domain.metadata import Metadata

class DatasetSpecification(BaseModel):
    rows: PositiveInt = Field(
        ...,
        description="Number of rows to generate"
    )

    columns: list[Column] = Field(
        ...,
        min_length=1,
        description="Ordered list of dataset columns"
    )

    relationships: list[Relationship] = Field(
        default_factory=list,
        description="Relationships between columns"
    )

    metadata: Metadata | None = Field(
        default=None,
        description="Optional dataset metadata"
    )