from abc import ABC
from typing import Any

from app.generation.providers.base_provider import BaseProvider
from app.generation.strategies.base_strategy import BaseStrategy


class StructuredStrategy(BaseStrategy, ABC):

    def __init__(self, provider: BaseProvider):
        self.provider = provider