from app.domain.enums import StrategyType
from app.generation.context import GenerationContext
from app.generation.generation_plan import GenerationPlan
from app.generation.strategies.structured_strategy import StructuredStrategy


class NameStrategy(StructuredStrategy):

    def strategy_type(self) -> StrategyType:
        return StrategyType.NAME

    def generate(
        self,
        plan: GenerationPlan,
        context: GenerationContext,
    ) -> str:
        col_lower = (plan.column_name or "").lower().replace(" ", "_")

        if any(k in col_lower for k in ["first_name", "firstname", "first", "fname", "given_name"]):
            return self.provider.generate_first_name()

        if any(k in col_lower for k in ["last_name", "lastname", "lname", "surname", "family_name"]):
            return self.provider.generate_last_name()

        return self.provider.generate_name()