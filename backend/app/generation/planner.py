from app.domain.column import Column
from app.generation.generation_plan import GenerationPlan


class Planner:

    def create_plan(
        self,
        column: Column,
    ) -> GenerationPlan:

        return GenerationPlan(
            column_name=column.name,
            column_type=column.type,
            constraints=column.constraints,
        )