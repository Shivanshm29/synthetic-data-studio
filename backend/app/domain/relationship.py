
from pydantic import BaseModel, Field

from app.domain.enums import RelationshipType


class Relationship(BaseModel):
    source: str = Field(
        ...,
        description="Source column name"
    )

    target: str = Field(
        ...,
        description="Target column name"
    )

    type: RelationshipType = Field(
        ...,
        description="Relationship type"
    )