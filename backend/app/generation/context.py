from dataclasses import dataclass


@dataclass
class GenerationContext:
    current_row: dict
    generated_rows: list[dict]
    def get(self, column_name: str):
        return self.current_row.get(column_name)

    def set(self, column_name: str, value) -> None:
        self.current_row[column_name] = value