from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from routers import conteudo, imagem, drive, config, agentes

app = FastAPI(title="Carrossel System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conteudo.router, prefix="/api")
app.include_router(imagem.router, prefix="/api")
app.include_router(drive.router, prefix="/api")
app.include_router(config.router, prefix="/api")
app.include_router(agentes.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
