from app.domain.enums import StrategyType
from app.generation.context import GenerationContext
from app.generation.generation_plan import GenerationPlan
from app.generation.strategies.structured_strategy import StructuredStrategy


class EmailStrategy(StructuredStrategy):

    def strategy_type(self) -> StrategyType:
        return StrategyType.EMAIL

    def generate(
        self,
        plan: GenerationPlan,
        context: GenerationContext,
    ) -> str:
        first_name = None
        last_name = None

        for k, v in context.current_row.items():
            if not isinstance(v, str) or not v.strip():
                continue
            k_lower = k.lower().replace(" ", "_")

            if any(key in k_lower for key in ["first_name", "firstname", "first", "fname", "given_name"]):
                first_name = v.strip()
            elif any(key in k_lower for key in ["last_name", "lastname", "lname", "surname", "family_name"]):
                last_name = v.strip()
            elif any(key in k_lower for key in ["full_name", "customer_name", "employee_name", "user_name", "name"]) and not first_name and not last_name:
                parts = v.strip().split()
                if len(parts) >= 2:
                    first_name = parts[0]
                    last_name = parts[-1]
                elif len(parts) == 1:
                    first_name = parts[0]

        return self.provider.generate_email(
            first_name=first_name,
            last_name=last_name,
        )