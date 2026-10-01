from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.generate import router as generate_router
from app.api.routes.health import router as health_router
from app.api.routes.prompt_generation import router as prompt_generation_router
from app.api.routes.datascout_router import router as datascout_router
from app.api.routes.fill_gaps import router as fill_gaps_router
from app.api.routes.rag_router import router as rag_router

app = FastAPI(
    title="Synthetic Data Studio",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(generate_router)
app.include_router(prompt_generation_router)
app.include_router(datascout_router)
app.include_router(fill_gaps_router)
app.include_router(rag_router)