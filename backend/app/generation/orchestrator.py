from typing import Any
from app.domain.dataset import DatasetSpecification
from app.domain.enums import ConstraintType, StrategyType
from app.generation.context import GenerationContext
from app.generation.generation_plan import GenerationPlan
from app.generation.planners.base_planner import BasePlanner
from app.generation.registry import StrategyRegistry


class GenerationOrchestrator:

    def __init__(
        self,
        registry: StrategyRegistry,
        planner: BasePlanner,
    ) -> None:
        self._registry = registry
        self._planner = planner

    def _fallback_value(self, plan: GenerationPlan) -> Any:
        if plan.strategy == StrategyType.INTEGER:
            return 0
        elif plan.strategy == StrategyType.FLOAT:
            return 0.0
        elif plan.strategy == StrategyType.BOOLEAN:
            return False
        elif plan.strategy in {
            StrategyType.STRING, StrategyType.NAME, StrategyType.FIRST_NAME,
            StrategyType.LAST_NAME, StrategyType.EMAIL, StrategyType.PHONE,
            StrategyType.ADDRESS, StrategyType.COMPANY, StrategyType.UUID,
            StrategyType.TEXT, StrategyType.DATE, StrategyType.DATETIME,
            StrategyType.SALARY
        }:
            return ""
        return None

    def _topological_sort(self, plans: list[GenerationPlan]) -> list[GenerationPlan]:
        plan_dict = {plan.column_name: plan for plan in plans}
        visited = set()
        temp_mark = set()
        sorted_plans = []

        def visit(node_name: str):
            if node_name in temp_mark:
                return
            if node_name not in visited:
                temp_mark.add(node_name)
                plan = plan_dict.get(node_name)
                if plan and hasattr(plan, 'dependencies'):
                    for dep in plan.dependencies:
                        visit(dep)
                temp_mark.remove(node_name)
                visited.add(node_name)
                if plan:
                    sorted_plans.append(plan)

        for plan in plans:
            visit(plan.column_name)

        return sorted_plans

    def generate(
        self,
        dataset: DatasetSpecification,
    ) -> list[dict]:

        plans = self._planner.create_plan(dataset)
        plans = self._topological_sort(plans)

        rows: list[dict] = []
        is_unique = {c.name: (c.get_constraint(ConstraintType.UNIQUE) is not None) for c in dataset.columns}
        generated_values: dict[str, set] = {p.column_name: set() for p in plans if is_unique.get(p.column_name)}

        for _ in range(dataset.rows):
            row: dict = {}
            context = GenerationContext(
                current_row=row,
                generated_rows=rows,
            )

            for plan in plans:
                try:
                    strategy = self._registry.get(plan.strategy)
                    if is_unique.get(plan.column_name):
                        value = None
                        for attempt in range(10):
                            val = strategy.generate(plan=plan, context=context)
                            if val not in generated_values[plan.column_name]:
                                value = val
                                break
                        else:
                            val = strategy.generate(plan=plan, context=context)
                            value = f"{val}_{len(generated_values[plan.column_name])}"
                        generated_values[plan.column_name].add(value)
                    else:
                        value = strategy.generate(plan=plan, context=context)
                    row[plan.column_name] = value
                except Exception as err:
                    print(f"Warning: Generation failed for {plan.column_name}: {err}")
                    row[plan.column_name] = self._fallback_value(plan)

            rows.append(row)

        return rows

    def generate_missing(
        self,
        dataset: DatasetSpecification,
        existing_rows: list[dict],
        missing_column_names: list[str],
    ) -> list[dict]:
        """Generate only specific missing columns for pre-existing rows."""
        full_plans = self._planner.create_plan(dataset)
        missing_plans = [p for p in full_plans if p.column_name in missing_column_names]
        missing_plans = self._topological_sort(missing_plans)

        is_unique = {c.name: (c.get_constraint(ConstraintType.UNIQUE) is not None) for c in dataset.columns}
        generated_values: dict[str, set] = {p.column_name: set() for p in missing_plans if is_unique.get(p.column_name)}

        for p in missing_plans:
            if is_unique.get(p.column_name):
                for r in existing_rows:
                    if p.column_name in r and r[p.column_name] is not None:
                        generated_values[p.column_name].add(r[p.column_name])

        for row in existing_rows:
            context = GenerationContext(current_row=row, generated_rows=existing_rows)
            for plan in missing_plans:
                try:
                    strategy = self._registry.get(plan.strategy)
                    if is_unique.get(plan.column_name):
                        value = None
                        for attempt in range(10):
                            val = strategy.generate(plan=plan, context=context)
                            if val not in generated_values[plan.column_name]:
                                value = val
                                break
                        else:
                            val = strategy.generate(plan=plan, context=context)
                            value = f"{val}_{len(generated_values[plan.column_name])}"
                        generated_values[plan.column_name].add(value)
                    else:
                        value = strategy.generate(plan=plan, context=context)
                    row[plan.column_name] = value
                except Exception as err:
                    print(f"Gap fill fallback for {plan.column_name}: {err}")
                    row[plan.column_name] = self._fallback_value(plan)
        return existing_rows