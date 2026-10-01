from app.core.exceptions import (
    DuplicateStrategyError,
    StrategyNotFoundError,
)
from app.domain.enums import StrategyType
from app.generation.strategies.base_strategy import BaseStrategy


class StrategyRegistry:

    def __init__(self):
        self._strategies: dict[StrategyType, BaseStrategy] = {}

    def register(
        self,
        strategy: BaseStrategy,
    ) -> None:

        strategy_type = strategy.strategy_type()

        if strategy_type in self._strategies:
            raise DuplicateStrategyError(
                f"Strategy already registered for '{strategy_type.value}'."
            )

        self._strategies[strategy_type] = strategy

    def get(
        self,
        strategy: StrategyType,
    ) -> BaseStrategy:

        try:
            return self._strategies[strategy]

        except KeyError as e:
            print(f"Warning: Strategy not found for '{strategy.value}'. Falling back to STRING strategy.")
            if StrategyType.STRING in self._strategies:
                return self._strategies[StrategyType.STRING]
            else:
                raise StrategyNotFoundError(
                    f"No strategy registered for '{strategy.value}' and fallback STRING strategy is missing."
                ) from e

    def available_fields(
        self,
    ) -> set[StrategyType]:

        return set(self._strategies.keys())