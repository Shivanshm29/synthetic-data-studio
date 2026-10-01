from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

from app.datascout.datascout_engine import DataScoutEngine
from app.datascout.datascout_schema import DataScoutResponse, FetchResult, GapAnalysis
from app.datascout.integrations.hf_fetch import fetch_hf_preview, fetch_hf_full
from app.datascout.integrations.kaggle_fetch import fetch_kaggle_preview, fetch_kaggle_full
from app.datascout.profiler import DatasetProfileReport, DatasetProfiler

router = APIRouter(
    prefix="/datascout",
    tags=["DataScout AI"],
)

engine = DataScoutEngine()


class DataScoutRequest(BaseModel):
    prompt: str


@router.post("/analyze", response_model=DataScoutResponse)
def analyze_request(request: DataScoutRequest) -> DataScoutResponse:
    return engine.analyze(request.prompt)


@router.post("/profile", response_model=DatasetProfileReport)
async def profile_dataset_file(file: UploadFile = File(...)) -> DatasetProfileReport:
    content = await file.read()
    return DatasetProfiler.profile_file(file.filename or "uploaded_dataset.csv", content)


class DataScoutFetchRequest(BaseModel):
    source_platform: str
    dataset_id: str
    max_rows: int = 100

@router.post("/fetch", response_model=FetchResult)
def fetch_dataset(request: DataScoutFetchRequest) -> FetchResult:
    if request.source_platform == "huggingface":
        if request.max_rows <= 100:
            return fetch_hf_preview(request.dataset_id)
        else:
            return fetch_hf_full(request.dataset_id, request.max_rows)
    elif request.source_platform == "kaggle":
        if request.max_rows <= 100:
            return fetch_kaggle_preview(request.dataset_id)
        else:
            return fetch_kaggle_full(request.dataset_id, request.max_rows)
    else:
        return FetchResult()


class GapAnalysisRequest(BaseModel):
    prompt: str
    fetched_columns: list[str]

@router.post("/analyze-gaps", response_model=GapAnalysis)
def analyze_gaps(request: GapAnalysisRequest) -> GapAnalysis:
    # Use SchemaGenerator to infer required columns from the prompt
    from app.api.dependencies import get_schema_generator
    schema_gen = get_schema_generator()
    try:
        spec = schema_gen.generate(request.prompt)
        required_cols = [col.name for col in spec.columns]
    except Exception:
        # If schema generation fails, just return no gaps
        return GapAnalysis(
            fetched_columns=request.fetched_columns,
            required_columns=request.fetched_columns,
            missing_columns=[],
            has_gaps=False,
        )
    
    # Find missing columns (case-insensitive comparison)
    fetched_lower = {c.lower() for c in request.fetched_columns}
    missing = [c for c in required_cols if c.lower() not in fetched_lower]
    
    return GapAnalysis(
        fetched_columns=request.fetched_columns,
        required_columns=required_cols,
        missing_columns=missing,
        has_gaps=len(missing) > 0,
    )

