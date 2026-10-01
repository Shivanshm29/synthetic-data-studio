from app.generation.registry import StrategyRegistry
from app.generation.strategies.integer_strategy import IntegerStrategy


class StrategyLoader:

    def __init__(self, provider):
        self.provider = provider

    def load(self):

        registry = StrategyRegistry()

        registry.register(
            IntegerStrategy(self.provider)
        )

        return registry