import json

from openai.types.chat import ChatCompletionMessageParam

from app.domain.dataset import DatasetSpecification
from app.domain.enums import StrategyType
from app.generation.context import GenerationContext
from app.generation.generation_plan import GenerationPlan


class PromptBuilder:

    _SYSTEM_PROMPT = """
You are an expert synthetic dataset planning engine.

Your task is NOT to generate dataset rows.

Your task is to convert a dataset specification into an execution plan.

Keep the values aligned with real world data , realistic and orderly not random generation, the constraints should be properly decided upon so as to keep the data realistic.

For every column:

1. Choose the most appropriate generation strategy.
2. Infer useful generation parameters whenever possible (e.g. choices, minimum, maximum).
3. Preserve all explicit constraints (especially choices arrays).
4. Infer dependencies between columns.
5. Never generate sample data.

Infer sensible defaults whenever constraints are missing.

Examples:

- salary → float with minimum and maximum
- age → integer with sensible range
- email → email strategy
- name → name strategy
- first_name → first_name strategy
- last_name → last_name strategy
- phone → phone strategy
- address → address strategy
- company → company strategy
- description → text strategy
- review → text strategy
- comments → text strategy

Return ONLY valid JSON matching the required schema.
"""

    _OUTPUT_SCHEMA = """
{
    "columns": [
        {
            "column_name": "age",
            "strategy": "integer",
            "parameters": {
                "minimum": 18,
                "maximum": 60
            },
            "dependencies": []
        }
    ]
}
"""

    def build(
        self,
        dataset: DatasetSpecification,
    ) -> list[ChatCompletionMessageParam]:

        supported_strategies = "\n".join(
            f"- {strategy.value}"
            for strategy in StrategyType
        )

        dataset_json = json.dumps(
            dataset.model_dump(mode="json"),
            indent=2,
        )

        system_prompt = (
            self._SYSTEM_PROMPT
            + "\n\nSupported strategies:\n"
            + supported_strategies
        )

        user_prompt = f"""
Dataset Specification

{dataset_json}

Return an execution plan matching this JSON schema:

{self._OUTPUT_SCHEMA}
"""

        return [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

    def build_value_prompt(
        self,
        plan: GenerationPlan,
        context: GenerationContext,
    ) -> str:

        return f"""
You are generating ONE value for a synthetic dataset.

Column:
{plan.column_name}

Strategy:
{plan.strategy.value}

Requirements:
{plan.parameters}

Current row:
{context.current_row}

Previously generated rows:
{len(context.generated_rows)}

Return exactly ONE value.

Do not explain.
Do not use markdown.
Do not use quotes.
Return only the generated value.
""".strip()