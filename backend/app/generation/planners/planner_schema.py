from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import StrategyType


class PlannerColumn(BaseModel):
    column_name: str
    strategy: StrategyType
    parameters: dict[str, Any] = Field(default_factory=dict)
    dependencies: list[str] = Field(default_factory=list)


class PlannerResponse(BaseModel):
    columns: list[PlannerColumn]