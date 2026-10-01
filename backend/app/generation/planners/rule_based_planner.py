from app.domain.dataset import DatasetSpecification
from app.generation.generation_plan import GenerationPlan
from app.generation.planners.base_planner import BasePlanner
from app.domain.enums import StrategyType

class RuleBasedPlanner(BasePlanner):

    def create_plan(
        self,
        dataset: DatasetSpecification,
    ) -> list[GenerationPlan]:

        plans = []

        for column in dataset.columns:
            col_name_lower = column.name.lower().replace(" ", "_")
            c_type = column.type.value if hasattr(column.type, "value") else str(column.type)

            try:
                strategy = StrategyType(c_type)
            except ValueError:
                strategy = StrategyType.STRING

            if any(k in col_name_lower for k in ["first_name", "firstname", "first", "fname", "given_name"]):
                strategy = StrategyType.FIRST_NAME
            elif any(k in col_name_lower for k in ["last_name", "lastname", "lname", "surname", "family_name"]):
                strategy = StrategyType.LAST_NAME
            elif "email" in col_name_lower:
                strategy = StrategyType.EMAIL
            elif "phone" in col_name_lower:
                strategy = StrategyType.PHONE
            elif any(k in col_name_lower for k in ["description", "review", "comment", "feedback", "summary", "bio", "details", "notes", "article"]):
                strategy = StrategyType.TEXT

            plans.append(
                GenerationPlan(
                    column_name=column.name,
                    strategy=strategy,
                    parameters={},
                    dependencies=[],
                )
            )

        return plans