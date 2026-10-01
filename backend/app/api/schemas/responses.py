from typing import Any

from pydantic import BaseModel


class DatasetResponse(BaseModel):
    rows: list[dict[str, Any]]
    count: int