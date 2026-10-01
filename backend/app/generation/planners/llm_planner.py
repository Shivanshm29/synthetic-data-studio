from openai import OpenAI

from app.core.config import settings
from app.domain.dataset import DatasetSpecification
from app.generation.generation_plan import GenerationPlan
from app.generation.planners.base_planner import BasePlanner
from app.generation.planners.planner_schema import PlannerResponse
from app.generation.planners.prompt_builder import PromptBuilder


from app.generation.planners.rule_based_planner import RuleBasedPlanner


class LLMPlanner(BasePlanner):

    def __init__(self) -> None:

        self._client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )

        self._prompt_builder = PromptBuilder()

    def create_plan(
        self,
        dataset: DatasetSpecification,
    ) -> list[GenerationPlan]:

        messages = self._prompt_builder.build(dataset)

        models_to_try = [
            settings.LLM_MODEL,
            "openrouter/auto",
        ]

        content = None
        for model in models_to_try:
            try:
                response = self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0,
                    response_format={
                        "type": "json_object",
                    },
                )
                if response and hasattr(response, "choices") and response.choices and response.choices[0].message and response.choices[0].message.content:
                    content = response.choices[0].message.content.strip()
                    if content:
                        break
            except Exception as e:
                print(f"Planner model {model} failed: {e}")
                continue

        if not content:
            print("Fallback to RuleBasedPlanner")
            return RuleBasedPlanner().create_plan(dataset)

        try:
            planner_response = PlannerResponse.model_validate_json(content)
        except Exception:
            return RuleBasedPlanner().create_plan(dataset)

        col_map = {col.name: col for col in dataset.columns}

        plans = []
        for column in planner_response.columns:
            params = {k: v for k, v in column.parameters.items() if v is not None}
            col_spec = col_map.get(column.column_name)
            if col_spec:
                for constraint in col_spec.constraints:
                    c_type = constraint.type.value if hasattr(constraint.type, "value") else str(constraint.type)
                    if constraint.value is not None and (c_type not in params or params[c_type] is None):
                        params[c_type] = constraint.value

            plans.append(
                GenerationPlan(
                    column_name=column.column_name,
                    strategy=column.strategy,
                    parameters=params,
                    dependencies=column.dependencies,
                )
            )

        return plans