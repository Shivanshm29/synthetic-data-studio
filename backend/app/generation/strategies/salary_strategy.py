from app.domain.enums import StrategyType
from app.generation.context import GenerationContext
from app.generation.generation_plan import GenerationPlan
from app.generation.strategies.structured_strategy import StructuredStrategy


class SalaryStrategy(StructuredStrategy):

    def strategy_type(self) -> StrategyType:
        return StrategyType.SALARY

    def _get_val(self, params: dict, keys: list[str], default: float) -> float:
        for k in keys:
            v = params.get(k)
            if v is not None:
                try:
                    return float(v)
                except (ValueError, TypeError):
                    pass
        return default

    def generate(
        self,
        plan: GenerationPlan,
        context: GenerationContext,
    ) -> float:

        minimum = self._get_val(plan.parameters, ["minimum", "min_value", "min"], 30000.0)
        maximum = self._get_val(plan.parameters, ["maximum", "max_value", "max"], 250000.0)

        if minimum > maximum:
            minimum, maximum = maximum, minimum

        return round(self.provider.generate_float(
            min_value=minimum,
            max_value=maximum,
        ), 2)
