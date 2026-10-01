from app.domain.enums import StrategyType
from app.generation.context import GenerationContext
from app.generation.generation_plan import GenerationPlan
from app.generation.strategies.structured_strategy import StructuredStrategy


class StringStrategy(StructuredStrategy):

    def strategy_type(self) -> StrategyType:
        return StrategyType.STRING

    def generate(
        self,
        plan: GenerationPlan,
        context: GenerationContext,
    ) -> str:
        choices = plan.parameters.get("choices") or plan.parameters.get("options") or plan.parameters.get("values")
        if choices and isinstance(choices, list) and len(choices) > 0:
            import random
            return str(random.choice(choices))

        return self.provider.generate_string(
            min_length=plan.parameters.get("min_length"),
            max_length=plan.parameters.get("max_length"),
            column_name=plan.column_name,
        )