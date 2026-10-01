from dataclasses import dataclass
from typing import Any

from app.domain.enums import StrategyType


@dataclass(slots=True)
class GenerationPlan:

    column_name: str

    strategy: StrategyType

    

    parameters: dict[str, Any]

    dependencies: list[str]