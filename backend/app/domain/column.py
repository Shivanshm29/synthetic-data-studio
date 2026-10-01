from typing import Any

from pydantic import BaseModel, Field

from app.domain.constraint import Constraint
from app.domain.enums import ColumnType, ConstraintType


class Column(BaseModel):
    name: str = Field(...)
    type: ColumnType = Field(...)
    constraints: list[Constraint] = Field(default_factory=list)
    description: str | None = None
    example: Any | None = None

    def get_constraint(
        self,
        constraint_type: ConstraintType,
    ) -> Constraint | None:
        for constraint in self.constraints:
            if constraint.type == constraint_type:
                return constraint
        return None

    def get_constraint_value(
        self,
        constraint_type: ConstraintType,
    ):
        constraint = self.get_constraint(constraint_type)
        return constraint.value if constraint else None