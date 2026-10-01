from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_orchestrator
from app.domain.dataset import DatasetSpecification
from app.generation.orchestrator import GenerationOrchestrator
from app.api.schemas.responses import DatasetResponse

router = APIRouter(
    prefix="/generate",
    tags=["Generation"],
)


@router.post(
    "",
    response_model=DatasetResponse,
)
def generate_dataset(
    dataset: DatasetSpecification,
    orchestrator: GenerationOrchestrator = Depends(
        get_orchestrator,
    ),
) -> DatasetResponse:
    try:
        rows = orchestrator.generate(dataset)
        return DatasetResponse(
            rows=rows,
            count=len(rows),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dataset generation failed: {str(e)}")