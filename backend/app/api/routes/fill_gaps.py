from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Any

from app.api.dependencies import get_orchestrator, get_schema_generator
from app.generation.gap_filler import GapFiller

router = APIRouter(tags=["Generation"])


class FillGapsRequest(BaseModel):
    prompt: str
    existing_rows: list[dict[str, Any]]
    missing_columns: list[str]


class FillGapsResponse(BaseModel):
    rows: list[dict[str, Any]]
    count: int
    filled_columns: list[str]


@router.post("/generate/fill-gaps", response_model=FillGapsResponse)
def fill_gaps(request: FillGapsRequest) -> FillGapsResponse:
    orchestrator = get_orchestrator()
    schema_gen = get_schema_generator()
    filler = GapFiller(orchestrator, schema_gen)
    
    try:
        augmented_rows = filler.fill_gaps(
            prompt=request.prompt,
            existing_rows=request.existing_rows,
            missing_columns=request.missing_columns,
        )
        return FillGapsResponse(
            rows=augmented_rows,
            count=len(augmented_rows),
            filled_columns=request.missing_columns,
        )
    except Exception as err:
        print(f"Gap filling failed: {err}")
        # Return original rows unchanged on failure
        return FillGapsResponse(
            rows=request.existing_rows,
            count=len(request.existing_rows),
            filled_columns=[],
        )
