from pydantic import BaseModel, Field, PositiveInt
    
from app.domain.column import Column
from app.domain.relationship import Relationship
from app.domain.metadata import Metadata
from backend.app.domain.dataset import DatasetSpecification
from backend.app.domain.enums import  OutputFormat

class GenerationRequest(BaseModel):
    specification: DatasetSpecification

    provider: str

    model: str | None = None

    output_format: OutputFormat

    locale: str = "en_US"

    seed: int | None = None

    prompt: str | None = None