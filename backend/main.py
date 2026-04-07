import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

load_dotenv()

from routers import (
    conteudo, imagem, drive, config, agentes, historico, pipeline,
    foto_overlay, visual_preference, design_system, prompt_layer,
)
from middleware.rate_limiter import limiter, rate_limit_handler

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:4173",
).split(",")

app = FastAPI(title="Carrossel System API", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(conteudo.router, prefix="/api")
app.include_router(imagem.router, prefix="/api")
app.include_router(drive.router, prefix="/api")
app.include_router(config.router, prefix="/api")
app.include_router(agentes.router, prefix="/api")
app.include_router(historico.router, prefix="/api")
app.include_router(pipeline.router, prefix="/api")
app.include_router(foto_overlay.router, prefix="/api")
app.include_router(visual_preference.router, prefix="/api")
app.include_router(design_system.router, prefix="/api")
app.include_router(prompt_layer.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
