from app.domain.enums import StrategyType
from app.generation.context import GenerationContext
from app.generation.generation_plan import GenerationPlan
from app.generation.strategies.structured_strategy import StructuredStrategy


class IntegerStrategy(StructuredStrategy):

    def strategy_type(self) -> StrategyType:
        return StrategyType.INTEGER

    def _get_val(self, params: dict, keys: list[str], default: int) -> int:
        for k in keys:
            v = params.get(k)
            if v is not None:
                try:
                    return int(v)
                except (ValueError, TypeError):
                    pass
        return default

    def generate(
        self,
        plan: GenerationPlan,
        context: GenerationContext,
    ) -> int:
        col_lower = (plan.column_name or "").lower().replace(" ", "_")

        default_min, default_max = 0, 100
        if any(k in col_lower for k in ["employee_id", "emp_id", "user_id", "customer_id", "student_id", "advisor_id", "manager_id"]):
            default_min, default_max = 1000, 9999
        elif "age" in col_lower:
            default_min, default_max = 18, 65
        elif any(k in col_lower for k in ["year", "experience", "exp"]):
            default_min, default_max = 1, 35
        elif any(k in col_lower for k in ["rating", "score", "performance"]):
            default_min, default_max = 1, 5
        elif any(k in col_lower for k in ["count", "projects", "project"]):
            default_min, default_max = 1, 10
        elif "semester" in col_lower:
            default_min, default_max = 1, 8

        minimum = self._get_val(plan.parameters, ["minimum", "min_value", "min"], default_min)
        maximum = self._get_val(plan.parameters, ["maximum", "max_value", "max"], default_max)

        if minimum > maximum:
            minimum, maximum = maximum, minimum

        return self.provider.generate_integer(
            min_value=minimum,
            max_value=maximum,
        )