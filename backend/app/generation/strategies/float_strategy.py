from app.domain.enums import StrategyType
from app.generation.context import GenerationContext
from app.generation.generation_plan import GenerationPlan
from app.generation.strategies.structured_strategy import StructuredStrategy


class FloatStrategy(StructuredStrategy):

    def strategy_type(self) -> StrategyType:
        return StrategyType.FLOAT

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
        col_lower = (plan.column_name or "").lower().replace(" ", "_")

        default_min, default_max = 0.0, 100.0
        if "cgpa" in col_lower or "gpa" in col_lower:
            default_min, default_max = 0.0, 4.0
        elif "percentage" in col_lower or "percent" in col_lower:
            default_min, default_max = 0.0, 100.0
        elif "bonus" in col_lower or "amount" in col_lower:
            default_min, default_max = 500.0, 20000.0
        elif "score" in col_lower or "satisfaction" in col_lower:
            default_min, default_max = 1.0, 5.0

        minimum = self._get_val(plan.parameters, ["minimum", "min_value", "min"], default_min)
        maximum = self._get_val(plan.parameters, ["maximum", "max_value", "max"], default_max)

        if minimum > maximum:
            minimum, maximum = maximum, minimum

        return round(self.provider.generate_float(
            min_value=minimum,
            max_value=maximum,
        ), 2)