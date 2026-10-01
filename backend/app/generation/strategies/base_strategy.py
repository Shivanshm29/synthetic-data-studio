from app.domain.column import Column
from app.domain.enums import ColumnType, StrategyType
from abc import ABC, abstractmethod
from typing import Any
from app.generation.context import GenerationContext
from app.generation.generation_plan import GenerationPlan
from app.domain.enums import StrategyType

class BaseStrategy(ABC):

    


    @abstractmethod
    def strategy_type(self) -> StrategyType:
        ...

    @abstractmethod
    

    def generate(
    self,
    plan: GenerationPlan,
    context: GenerationContext,
    )-> Any:
        ...