from abc import ABC, abstractmethod
from datetime import date


class BaseProvider(ABC):

    @abstractmethod
    def generate_integer(
        self,
        min_value: int,
        max_value: int,
    ) -> int:
        ...

    @abstractmethod
    def generate_float(
        self,
        min_value: float,
        max_value: float,
    ) -> float:
        ...

    @abstractmethod
    def generate_boolean(self) -> bool:
        ...

    @abstractmethod
    def generate_string(
        self,
        min_length: int | None = None,
        max_length: int | None = None,
        column_name: str | None = None,
    ) -> str:
        ...

    @abstractmethod
    def generate_name(self) -> str:
        ...

    @abstractmethod
    def generate_first_name(self) -> str:
        ...

    @abstractmethod
    def generate_last_name(self) -> str:
        ...

    @abstractmethod
    def generate_email(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> str:
        ...

    @abstractmethod
    def generate_text_content(
        self,
        column_name: str | None = None,
    ) -> str:
        ...

    @abstractmethod
    def generate_phone(self) -> str:
        ...

    @abstractmethod
    def generate_uuid(self) -> str:
        ...

    @abstractmethod
    def generate_date(
        self,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> date:
        ...

    @abstractmethod
    def generate_address(self) -> str:
        ...

    @abstractmethod
    def generate_company(self) -> str:
        ...

    @abstractmethod
    def generate_datetime(self) -> str:
        ...
