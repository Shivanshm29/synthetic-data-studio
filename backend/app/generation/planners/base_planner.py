from abc import ABC, abstractmethod

from app.domain.dataset import DatasetSpecification
from app.generation.generation_plan import GenerationPlan


class BasePlanner(ABC):

    @abstractmethod
    def create_plan(
        self,
        dataset: DatasetSpecification,
    ) -> list[GenerationPlan]:
        ...