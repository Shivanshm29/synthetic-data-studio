from app.domain.enums import StrategyType
from app.generation.context import GenerationContext
from app.generation.generation_plan import GenerationPlan
from app.generation.strategies.structured_strategy import StructuredStrategy


class PhoneStrategy(StructuredStrategy):

    def strategy_type(self) -> StrategyType:
        return StrategyType.PHONE

    def generate(
        self,
        plan: GenerationPlan,
        context: GenerationContext,
    ) -> str:

        return self.provider.generate_phone()