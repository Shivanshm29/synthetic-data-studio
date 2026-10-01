from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (
    get_orchestrator,
    get_schema_generator,
)
from app.generation.orchestrator import GenerationOrchestrator
from app.generation.schema.schema_generator import SchemaGenerator
from app.api.schemas.prompt_generation import PromptGenerationRequest

router = APIRouter(
    prefix="/generate-from-prompt",
    tags=["Prompt Generation"],
)


@router.post("")
def generate_from_prompt(
    request: PromptGenerationRequest,
    schema_generator: SchemaGenerator = Depends(get_schema_generator),
    orchestrator: GenerationOrchestrator = Depends(get_orchestrator),
):
    try:
        dataset = schema_generator.generate(
            request.prompt,
            request.rows,
        )

        rows = orchestrator.generate(dataset)

        return {
            "rows": rows,
            "count": len(rows),
        }

    except Exception as e:
        print(f"Generate from prompt error: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")