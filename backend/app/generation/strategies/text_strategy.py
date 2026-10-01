from app.domain.enums import StrategyType
from app.generation.context import GenerationContext
from app.generation.generation_plan import GenerationPlan
from app.generation.llm.llm_generator import LLMGenerator
from app.generation.planners.prompt_builder import PromptBuilder
from app.generation.providers.base_provider import BaseProvider
from app.generation.strategies.base_strategy import BaseStrategy


class TextStrategy(BaseStrategy):

    def __init__(
        self,
        llm: LLMGenerator,
        provider: BaseProvider | None = None,
    ) -> None:

        self.llm = llm
        self.provider = provider
        self.prompt_builder = PromptBuilder()
        self._cache: dict[str, list[str]] = {}

    def strategy_type(
        self,
    ) -> StrategyType:

        return StrategyType.TEXT

    def generate(
        self,
        plan: GenerationPlan,
        context: GenerationContext,
    ) -> str:
        choices = plan.parameters.get("choices") or plan.parameters.get("options") or plan.parameters.get("values")
        if choices and isinstance(choices, list) and len(choices) > 0:
            import random
            return str(random.choice(choices))

        cache_key = plan.column_name
        if cache_key in self._cache and len(self._cache[cache_key]) > 0:
            return self._cache[cache_key].pop(0)

        try:
            prompt = self.prompt_builder.build_value_prompt(
                plan,
                context,
            )
            # Fetch a batch of 10 items at once to speed up local LLM calls
            batch = self.llm.generate_batch_text(prompt, count=10)
            if batch and len(batch) > 0:
                val = batch.pop(0)
                if batch:
                    self._cache[cache_key] = batch
                return val
            return self.llm.generate_text(prompt)
        except Exception as err:
            print(f"TextStrategy generation fallback for {plan.column_name}: {err}")
            if self.provider:
                return self.provider.generate_text_content(column_name=plan.column_name)
            from faker import Faker
            return Faker().paragraph()
