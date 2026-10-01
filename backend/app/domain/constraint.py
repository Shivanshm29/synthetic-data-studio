from typing import Any

from pydantic import BaseModel

from app.domain.enums import ConstraintType


class Constraint(BaseModel):
    type: ConstraintType
    value: Any
    description: str | None = None