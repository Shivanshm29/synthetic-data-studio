from pydantic import BaseModel

from app.domain.dataset import DatasetSpecification


class SchemaResponse(BaseModel):
    dataset: DatasetSpecification