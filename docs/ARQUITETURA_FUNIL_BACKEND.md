# Arquitetura Backend -- Modo Funil

> Documento do Agente 03 (Arquiteto IT Valley Backend)
> Fonte: `docs/PRD-funil.md` + codebase existente
> Data: 2026-04-05

---

## 1. Visao Geral

O Modo Funil adiciona um **dominio novo (`funil`)** ao backend existente. O pipeline-pai orquestra N sub-pipelines independentes, cada um reaproveitando o pipeline de 6 etapas ja existente (strategist -> copywriter -> art_director -> image_generator -> brand_gate -> content_critic).

**Principio:** O funil NAO executa etapas -- ele so orquestra. Cada peca e um sub-pipeline completo e independente.

---

## 2. Estrutura de Arquivos (Novos)

```text
backend/
  dtos/
    funil/
      criar_funil/
        request.py                    <- CriarFunilRequest
        response.py                   <- CriarFunilResponse
      buscar_plano/
        response.py                   <- BuscarPlanoResponse (GET sem body)
      editar_plano/
        request.py                    <- EditarPlanoRequest
        response.py                   <- EditarPlanoResponse
      aprovar_plano/
        response.py                   <- AprovarPlanoResponse (POST sem body)
      rejeitar_plano/
        request.py                    <- RejeitarPlanoRequest
        response.py                   <- RejeitarPlanoResponse
      buscar_status/
        response.py                   <- BuscarStatusFunilResponse (GET sem body)
      executar_funil/
        response.py                   <- ExecutarFunilResponse (POST sem body)
      exportar_funil/
        response.py                   <- ExportarFunilResponse (POST sem body)
      base.py                        <- PecaBase, PlanoBase (campos compartilhados)
  routers/
    funil.py                          <- endpoints do funil (camada opaca)
  services/
    funil_service.py                  <- orquestracao (camada opaca)
  factories/
    funil_factory.py                  <- criacao de objetos + regras de negocio
  mappers/
    funil_mapper.py                   <- Model <-> Response (so conversao)
  models/
    funil.py                          <- FunilModel + FunilPecaModel (SQLAlchemy)
  agents/
    funnel_architect.py               <- implementacao do agente LLM

agents/
  funnel-architect.md                 <- system prompt do Funnel Architect
```

**Arquivos existentes que serao MODIFICADOS (minimamente):**

| Arquivo | Mudanca |
|---------|---------|
| `backend/main.py` | Adicionar `from routers import funil` + `app.include_router(funil.router, prefix="/api")` |
| `backend/services/pipeline_db_service.py` | Nenhuma -- sub-pipelines usam `criar_pipeline()` existente |
| `backend/services/pipeline_executor.py` | Nenhuma -- sub-pipelines usam `executar_proxima_etapa()` existente |

---

## 3. Modelo de Dados (Novas Tabelas)

### 3.1 carrossel.funil

```sql
CREATE TABLE carrossel.funil (
    id                  UNIQUEIDENTIFIER    NOT NULL PRIMARY KEY DEFAULT NEWID(),
    tenant_id           VARCHAR(50)         NOT NULL,
    pipeline_id         UNIQUEIDENTIFIER    NOT NULL,  -- FK carrossel.pipeline (pipeline pai)
    tema                NVARCHAR(500)       NOT NULL,
    brand_slug          VARCHAR(100)        NULL,
    avatar_mode         VARCHAR(20)         NOT NULL DEFAULT 'livre',
    plano               NVARCHAR(MAX)       NULL,      -- JSON do plano gerado pelo Funnel Architect
    plano_aprovado      NVARCHAR(MAX)       NULL,      -- JSON do plano com edicoes do usuario (imutavel apos aprovacao)
    status              VARCHAR(50)         NOT NULL DEFAULT 'pendente_plano',
    -- status: pendente_plano | plano_gerado | plano_aprovado | executando | completo | cancelado | erro
    feedback_rejeicao   NVARCHAR(MAX)       NULL,      -- ultimo feedback de rejeicao (para regeneracao)
    created_at          DATETIME2           NOT NULL DEFAULT GETUTCDATE(),
    approved_at         DATETIME2           NULL,
    updated_at          DATETIME2           NULL,
    deleted_at          DATETIME2           NULL,

    CONSTRAINT FK_funil_pipeline FOREIGN KEY (pipeline_id) REFERENCES carrossel.pipeline(id),
    INDEX IX_funil_tenant (tenant_id),
    INDEX IX_funil_pipeline (pipeline_id)
);
```

### 3.2 carrossel.funil_peca

```sql
CREATE TABLE carrossel.funil_peca (
    id                  UNIQUEIDENTIFIER    NOT NULL PRIMARY KEY DEFAULT NEWID(),
    funil_id            UNIQUEIDENTIFIER    NOT NULL,  -- FK carrossel.funil
    pipeline_id         UNIQUEIDENTIFIER    NULL,      -- FK carrossel.pipeline (sub-pipeline, NULL ate aprovacao do plano)
    ordem               INT                 NOT NULL,  -- 1-5
    etapa_funil         VARCHAR(20)         NOT NULL,  -- topo | meio | fundo | conversao
    titulo              NVARCHAR(200)       NOT NULL,
    formato             VARCHAR(50)         NOT NULL,  -- carrossel | post_unico | thumbnail_youtube | capa_reels
    angulo              NVARCHAR(500)       NOT NULL,
    resumo              NVARCHAR(1000)      NULL,
    gancho              NVARCHAR(500)       NULL,
    conexao_anterior    NVARCHAR(500)       NULL,
    cta_para_proxima    NVARCHAR(500)       NULL,
    created_at          DATETIME2           NOT NULL DEFAULT GETUTCDATE(),

    CONSTRAINT FK_funil_peca_funil FOREIGN KEY (funil_id) REFERENCES carrossel.funil(id),
    CONSTRAINT FK_funil_peca_pipeline FOREIGN KEY (pipeline_id) REFERENCES carrossel.pipeline(id),
    INDEX IX_funil_peca_funil (funil_id),
    INDEX IX_funil_peca_pipeline (pipeline_id)
);
```

### 3.3 Diagrama de Relacionamento

```
carrossel.pipeline (pai)
    |
    v
carrossel.funil (1:1 com pipeline pai)
    |
    v
carrossel.funil_peca (1:N, 3-5 pecas)
    |
    v (cada peca)
carrossel.pipeline (sub-pipeline, 1:1 com peca)
    |
    v
carrossel.pipeline_step (6 etapas por sub-pipeline)
```

---

## 4. Models (SQLAlchemy)

### backend/models/funil.py

```python
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship

from models.base import Base, TenantMixin


class FunilModel(TenantMixin, Base):
    __tablename__ = "funil"
    __table_args__ = {"schema": "carrossel"}

    pipeline_id = Column(UNIQUEIDENTIFIER, ForeignKey("carrossel.pipeline.id"), nullable=False)
    tema = Column(Text, nullable=False)
    brand_slug = Column(String(100), nullable=True)
    avatar_mode = Column(String(20), nullable=False, default="livre")
    plano = Column(Text, nullable=True)               # JSON
    plano_aprovado = Column(Text, nullable=True)       # JSON
    status = Column(String(50), nullable=False, default="pendente_plano")
    feedback_rejeicao = Column(Text, nullable=True)
    approved_at = Column(DateTime, nullable=True)

    pipeline = relationship("PipelineModel", foreign_keys=[pipeline_id])
    pecas = relationship("FunilPecaModel", back_populates="funil", cascade="all, delete-orphan")


class FunilPecaModel(Base):
    __tablename__ = "funil_peca"
    __table_args__ = {"schema": "carrossel"}

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    funil_id = Column(UNIQUEIDENTIFIER, ForeignKey("carrossel.funil.id"), nullable=False)
    pipeline_id = Column(UNIQUEIDENTIFIER, ForeignKey("carrossel.pipeline.id"), nullable=True)
    ordem = Column(Integer, nullable=False)
    etapa_funil = Column(String(20), nullable=False)
    titulo = Column(String(200), nullable=False)
    formato = Column(String(50), nullable=False)
    angulo = Column(String(500), nullable=False)
    resumo = Column(String(1000), nullable=True)
    gancho = Column(String(500), nullable=True)
    conexao_anterior = Column(String(500), nullable=True)
    cta_para_proxima = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    funil = relationship("FunilModel", back_populates="pecas")
    pipeline = relationship("PipelineModel", foreign_keys=[pipeline_id])
```

---

## 5. DTOs -- Request e Response por Caso de Uso

### 5.1 backend/dtos/funil/base.py

```python
from pydantic import BaseModel
from typing import Optional


class PecaBase(BaseModel):
    ordem: int
    titulo: str
    etapa_funil: str       # topo | meio | fundo | conversao
    formato: str           # carrossel | post_unico | thumbnail_youtube | capa_reels
    angulo: str
    resumo: Optional[str] = None
    gancho: Optional[str] = None
    conexao_anterior: Optional[str] = None
    cta_para_proxima: Optional[str] = None


class PlanoBase(BaseModel):
    tema_principal: str
    objetivo_campanha: str
    narrativa_geral: str
    pecas: list[PecaBase]
```

### 5.2 dtos/funil/criar_funil/request.py

```python
from pydantic import BaseModel, field_validator
from typing import Optional


class CriarFunilRequest(BaseModel):
    tema: str
    brand_slug: Optional[str] = None
    avatar_mode: Optional[str] = "livre"

    @field_validator("tema")
    @classmethod
    def tema_minimo(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 20:
            raise ValueError("Tema deve ter no minimo 20 caracteres")
        return v
```

### 5.3 dtos/funil/criar_funil/response.py

```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class CriarFunilResponse(BaseModel):
    id: UUID                    # id do funil
    pipeline_id: UUID           # id do pipeline pai
    tema: str
    status: str                 # pendente_plano
    created_at: datetime
```

### 5.4 dtos/funil/buscar_plano/response.py

```python
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

from dtos.funil.base import PlanoBase


class BuscarPlanoResponse(BaseModel):
    funil_id: UUID
    pipeline_id: UUID
    status: str
    plano: Optional[PlanoBase] = None
    feedback_anterior: Optional[str] = None
```

### 5.5 dtos/funil/editar_plano/request.py

```python
from pydantic import BaseModel
from dtos.funil.base import PlanoBase


class EditarPlanoRequest(BaseModel):
    plano: PlanoBase
```

### 5.6 dtos/funil/editar_plano/response.py

```python
from pydantic import BaseModel
from uuid import UUID

from dtos.funil.base import PlanoBase


class EditarPlanoResponse(BaseModel):
    funil_id: UUID
    status: str
    plano: PlanoBase
    mensagem: str
```

### 5.7 dtos/funil/aprovar_plano/response.py

```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class SubPipelineCriado(BaseModel):
    peca_ordem: int
    pipeline_id: UUID
    formato: str
    titulo: str


class AprovarPlanoResponse(BaseModel):
    funil_id: UUID
    status: str                              # plano_aprovado
    sub_pipelines: list[SubPipelineCriado]
    approved_at: datetime
    mensagem: str
```

### 5.8 dtos/funil/rejeitar_plano/request.py

```python
from pydantic import BaseModel, field_validator


class RejeitarPlanoRequest(BaseModel):
    feedback: str

    @field_validator("feedback")
    @classmethod
    def feedback_minimo(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 10:
            raise ValueError("Feedback deve ter no minimo 10 caracteres")
        return v
```

### 5.9 dtos/funil/rejeitar_plano/response.py

```python
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

from dtos.funil.base import PlanoBase


class RejeitarPlanoResponse(BaseModel):
    funil_id: UUID
    status: str                              # pendente_plano (regenerando)
    plano_novo: Optional[PlanoBase] = None   # preenchido apos regeneracao
    mensagem: str
```

### 5.10 dtos/funil/buscar_status/response.py

```python
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class PecaStatusItem(BaseModel):
    ordem: int
    titulo: str
    etapa_funil: str
    formato: str
    pipeline_id: Optional[UUID] = None
    status: str                          # pendente | executando | aguardando_aprovacao | completo | erro
    etapa_atual: Optional[str] = None    # agente atual do sub-pipeline
    progresso_imagem: Optional[dict] = None  # {atual, total, mensagem}


class BuscarStatusFunilResponse(BaseModel):
    funil_id: UUID
    status: str                          # status geral do funil
    total_pecas: int
    pecas_completas: int
    pecas: list[PecaStatusItem]
```

### 5.11 dtos/funil/executar_funil/response.py

```python
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class PecaExecutada(BaseModel):
    peca_ordem: int
    pipeline_id: UUID
    etapa: str
    status: str


class ExecutarFunilResponse(BaseModel):
    funil_id: UUID
    pecas_executadas: list[PecaExecutada]
    pecas_na_fila: int
    mensagem: str
```

### 5.12 dtos/funil/exportar_funil/response.py

```python
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class PecaExportada(BaseModel):
    peca_ordem: int
    titulo: str
    formato: str
    pdf_url: Optional[str] = None          # URL no Google Drive
    total_slides: int


class ExportarFunilResponse(BaseModel):
    funil_id: UUID
    pasta_drive: Optional[str] = None      # nome da subpasta criada
    pecas: list[PecaExportada]
    mensagem: str
```

---

## 6. Factory -- Regras de Negocio

### backend/factories/funil_factory.py

```python
import uuid
import json
from datetime import datetime, timezone
from typing import Optional

from models.funil import FunilModel, FunilPecaModel
from models.pipeline import PipelineModel
from dtos.funil.criar_funil.request import CriarFunilRequest
from dtos.funil.base import PlanoBase, PecaBase

from utils.dimensions import FORMATS

FORMATOS_VALIDOS = list(FORMATS.keys())
ETAPAS_FUNIL_VALIDAS = ("topo", "meio", "fundo", "conversao")
MIN_PECAS = 2       # minimo apos edicao do usuario (PRD: US-002)
MAX_PECAS = 5       # maximo gerado pelo agente (PRD: RN-002)
MIN_PECAS_GERADAS = 3  # minimo gerado pelo agente (PRD: RN-002)
MAX_SIMULTANEOS = 2    # limite de sub-pipelines simultaneos (PRD: RN-007)


class FunilFactory:

    @staticmethod
    def criar_funil(dto: CriarFunilRequest, pipeline_id: uuid.UUID, tenant_id: str) -> FunilModel:
        """Cria o FunilModel a partir do request. Pipeline pai ja deve existir."""
        return FunilModel(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            pipeline_id=pipeline_id,
            tema=dto.tema.strip(),
            brand_slug=dto.brand_slug,
            avatar_mode=dto.avatar_mode or "livre",
            status="pendente_plano",
            created_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def salvar_plano_gerado(funil: FunilModel, plano_json: dict) -> None:
        """Salva o plano gerado pelo Funnel Architect no funil."""
        FunilFactory._validar_plano(plano_json)
        funil.plano = json.dumps(plano_json, ensure_ascii=False)
        funil.status = "plano_gerado"

    @staticmethod
    def aplicar_edicao_plano(funil: FunilModel, plano: PlanoBase) -> None:
        """Aplica edicoes do usuario ao plano. Valida regras de negocio."""
        if funil.status not in ("plano_gerado", "pendente_plano"):
            raise ValueError(f"Plano nao pode ser editado no status '{funil.status}'")

        plano_dict = plano.model_dump()
        FunilFactory._validar_plano({"plano": plano_dict})
        funil.plano = json.dumps({"plano": plano_dict}, ensure_ascii=False)
        funil.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def aprovar_plano(funil: FunilModel) -> list[FunilPecaModel]:
        """Aprova o plano e cria os FunilPecaModel. Retorna as pecas criadas.
        NAO cria os sub-pipelines -- isso e responsabilidade do Service via pipeline_db_service.
        """
        if funil.status not in ("plano_gerado",):
            raise ValueError(f"Plano nao pode ser aprovado no status '{funil.status}'")

        if not funil.plano:
            raise ValueError("Nenhum plano para aprovar")

        plano_data = json.loads(funil.plano)
        plano = plano_data.get("plano", plano_data)
        pecas_data = plano.get("pecas", [])

        if len(pecas_data) < MIN_PECAS:
            raise ValueError(f"Plano deve ter no minimo {MIN_PECAS} pecas")

        now = datetime.now(timezone.utc)
        funil.plano_aprovado = funil.plano
        funil.status = "plano_aprovado"
        funil.approved_at = now
        funil.updated_at = now

        pecas = []
        for p in pecas_data:
            peca = FunilPecaModel(
                id=uuid.uuid4(),
                funil_id=funil.id,
                pipeline_id=None,   # preenchido quando sub-pipeline for criado
                ordem=p["ordem"],
                etapa_funil=p["etapa_funil"],
                titulo=p["titulo"],
                formato=p["formato"],
                angulo=p["angulo"],
                resumo=p.get("resumo"),
                gancho=p.get("gancho"),
                conexao_anterior=p.get("conexao_anterior"),
                cta_para_proxima=p.get("cta_para_proxima"),
                created_at=now,
            )
            pecas.append(peca)

        return pecas

    @staticmethod
    def preparar_rejeicao(funil: FunilModel, feedback: str) -> None:
        """Prepara o funil para regeneracao do plano."""
        if funil.status not in ("plano_gerado",):
            raise ValueError(f"Plano nao pode ser rejeitado no status '{funil.status}'")

        funil.feedback_rejeicao = feedback.strip()
        funil.status = "pendente_plano"
        funil.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def calcular_proximas_execucoes(pecas: list[dict], max_simultaneos: int = MAX_SIMULTANEOS) -> list[dict]:
        """Retorna ate max_simultaneos pecas pendentes que podem ser executadas.

        Regra RN-007: max 2 sub-pipelines simultaneos.
        Regra RN-008: pecas independentes -- uma nao bloqueia outra.
        """
        executando = [p for p in pecas if p["status"] == "executando"]
        vagas = max_simultaneos - len(executando)
        if vagas <= 0:
            return []

        pendentes = [p for p in pecas if p["status"] in ("pendente", "erro")]
        return pendentes[:vagas]

    @staticmethod
    def montar_tema_peca(tema_principal: str, angulo: str) -> str:
        """Monta o tema composto para o sub-pipeline de cada peca.

        Regra RN-013: tema = tema_principal + angulo especifico.
        """
        return f"{tema_principal}\n\nANGULO ESPECIFICO DESTA PECA: {angulo}"

    # --- Regras de validacao (privadas) ---

    @staticmethod
    def _validar_plano(plano_json: dict) -> None:
        """Valida o plano gerado ou editado contra as regras de negocio."""
        plano = plano_json.get("plano", plano_json)
        pecas = plano.get("pecas", [])

        # RN-002: entre 2 e 5 pecas (2 = minimo apos edicao, 5 = maximo)
        if len(pecas) < MIN_PECAS:
            raise ValueError(f"Plano deve ter no minimo {MIN_PECAS} pecas")
        if len(pecas) > MAX_PECAS:
            raise ValueError(f"Plano deve ter no maximo {MAX_PECAS} pecas")

        # RN-003: pelo menos 2 etapas diferentes
        etapas = set(p.get("etapa_funil") for p in pecas)
        if len(etapas) < 2:
            raise ValueError("Plano deve cobrir pelo menos 2 etapas diferentes do funil")

        # Validar cada peca
        for p in pecas:
            if p.get("etapa_funil") not in ETAPAS_FUNIL_VALIDAS:
                raise ValueError(f"Etapa invalida: {p.get('etapa_funil')}. Validas: {ETAPAS_FUNIL_VALIDAS}")
            if p.get("formato") not in FORMATOS_VALIDOS:
                raise ValueError(f"Formato invalido: {p.get('formato')}. Validos: {FORMATOS_VALIDOS}")
            if not p.get("titulo", "").strip():
                raise ValueError(f"Peca {p.get('ordem')}: titulo obrigatorio")
            if not p.get("angulo", "").strip():
                raise ValueError(f"Peca {p.get('ordem')}: angulo obrigatorio")
```

---

## 7. Mapper -- Conversao entre Camadas

### backend/mappers/funil_mapper.py

```python
import json
from typing import Optional

from models.funil import FunilModel, FunilPecaModel
from dtos.funil.base import PlanoBase, PecaBase
from dtos.funil.criar_funil.response import CriarFunilResponse
from dtos.funil.buscar_plano.response import BuscarPlanoResponse
from dtos.funil.editar_plano.response import EditarPlanoResponse
from dtos.funil.aprovar_plano.response import AprovarPlanoResponse, SubPipelineCriado
from dtos.funil.rejeitar_plano.response import RejeitarPlanoResponse
from dtos.funil.buscar_status.response import BuscarStatusFunilResponse, PecaStatusItem
from dtos.funil.executar_funil.response import ExecutarFunilResponse, PecaExecutada
from dtos.funil.exportar_funil.response import ExportarFunilResponse, PecaExportada


class FunilMapper:

    @staticmethod
    def to_criar_response(funil: FunilModel) -> CriarFunilResponse:
        return CriarFunilResponse(
            id=funil.id,
            pipeline_id=funil.pipeline_id,
            tema=funil.tema,
            status=funil.status,
            created_at=funil.created_at,
        )

    @staticmethod
    def to_plano_response(funil: FunilModel) -> BuscarPlanoResponse:
        plano = None
        if funil.plano:
            plano_data = json.loads(funil.plano)
            plano_inner = plano_data.get("plano", plano_data)
            plano = PlanoBase(
                tema_principal=plano_inner.get("tema_principal", ""),
                objetivo_campanha=plano_inner.get("objetivo_campanha", ""),
                narrativa_geral=plano_inner.get("narrativa_geral", ""),
                pecas=[PecaBase(**p) for p in plano_inner.get("pecas", [])],
            )
        return BuscarPlanoResponse(
            funil_id=funil.id,
            pipeline_id=funil.pipeline_id,
            status=funil.status,
            plano=plano,
            feedback_anterior=funil.feedback_rejeicao,
        )

    @staticmethod
    def to_editar_response(funil: FunilModel, plano: PlanoBase) -> EditarPlanoResponse:
        return EditarPlanoResponse(
            funil_id=funil.id,
            status=funil.status,
            plano=plano,
            mensagem="Plano atualizado com sucesso",
        )

    @staticmethod
    def to_aprovar_response(funil: FunilModel, pecas_criadas: list[dict]) -> AprovarPlanoResponse:
        subs = [
            SubPipelineCriado(
                peca_ordem=p["ordem"],
                pipeline_id=p["pipeline_id"],
                formato=p["formato"],
                titulo=p["titulo"],
            )
            for p in pecas_criadas
        ]
        return AprovarPlanoResponse(
            funil_id=funil.id,
            status=funil.status,
            sub_pipelines=subs,
            approved_at=funil.approved_at,
            mensagem=f"Plano aprovado. {len(subs)} sub-pipelines criados.",
        )

    @staticmethod
    def to_rejeitar_response(funil: FunilModel, plano_novo: Optional[PlanoBase]) -> RejeitarPlanoResponse:
        return RejeitarPlanoResponse(
            funil_id=funil.id,
            status=funil.status,
            plano_novo=plano_novo,
            mensagem="Plano rejeitado. Novo plano gerado com base no feedback.",
        )

    @staticmethod
    def to_status_response(funil: FunilModel, pecas_status: list[dict]) -> BuscarStatusFunilResponse:
        items = [
            PecaStatusItem(
                ordem=p["ordem"],
                titulo=p["titulo"],
                etapa_funil=p["etapa_funil"],
                formato=p["formato"],
                pipeline_id=p.get("pipeline_id"),
                status=p["status"],
                etapa_atual=p.get("etapa_atual"),
                progresso_imagem=p.get("progresso_imagem"),
            )
            for p in pecas_status
        ]
        completas = sum(1 for p in pecas_status if p["status"] == "completo")
        return BuscarStatusFunilResponse(
            funil_id=funil.id,
            status=funil.status,
            total_pecas=len(items),
            pecas_completas=completas,
            pecas=items,
        )

    @staticmethod
    def to_executar_response(funil_id, pecas_executadas: list[dict], na_fila: int) -> ExecutarFunilResponse:
        items = [
            PecaExecutada(
                peca_ordem=p["peca_ordem"],
                pipeline_id=p["pipeline_id"],
                etapa=p["etapa"],
                status=p["status"],
            )
            for p in pecas_executadas
        ]
        return ExecutarFunilResponse(
            funil_id=funil_id,
            pecas_executadas=items,
            pecas_na_fila=na_fila,
            mensagem=f"{len(items)} pecas executadas, {na_fila} na fila.",
        )

    @staticmethod
    def to_exportar_response(funil_id, pasta_drive: Optional[str], pecas: list[dict]) -> ExportarFunilResponse:
        items = [
            PecaExportada(
                peca_ordem=p["peca_ordem"],
                titulo=p["titulo"],
                formato=p["formato"],
                pdf_url=p.get("pdf_url"),
                total_slides=p["total_slides"],
            )
            for p in pecas
        ]
        return ExportarFunilResponse(
            funil_id=funil_id,
            pasta_drive=pasta_drive,
            pecas=items,
            mensagem="Funil exportado com sucesso." if pasta_drive else "Funil exportado localmente.",
        )
```

---

## 8. Service -- Orquestracao (Camada Opaca)

### backend/services/funil_service.py

```python
import json

from factories.funil_factory import FunilFactory
from mappers.funil_mapper import FunilMapper
from services.pipeline_db_service import criar_pipeline, buscar_pipeline
from services.pipeline_executor import executar_proxima_etapa
from data.connections.database import get_sql_session_context

from config import settings


class FunilService:
    """Service opaco: NAO acessa campos de DTO. Delega para Factory e Mapper."""

    @staticmethod
    async def criar(dto, tenant_id: str):
        """Cria pipeline pai + funil + executa Funnel Architect."""
        # 1. Criar pipeline pai (formato generico, modo_funil=true)
        pipeline_result = await criar_pipeline(
            tema=dto.tema,
            formato="carrossel",      # formato default do pipeline pai (nao usado nas pecas)
            modo_funil=True,
            tenant_id=tenant_id,
            brand_slug=dto.brand_slug,
            avatar_mode=dto.avatar_mode,
        )
        pipeline_id = pipeline_result["id"]

        # 2. Factory cria o funil
        funil = FunilFactory.criar_funil(dto, pipeline_id, tenant_id)

        # 3. Persistir funil
        async with get_sql_session_context() as session:
            session.add(funil)
            # (commit automatico pelo context manager)

        # 4. Executar Funnel Architect (agente novo)
        from agents.funnel_architect import executar as executar_funnel_architect
        brand_ctx = _get_brand_context(dto.brand_slug)
        plano_json = await executar_funnel_architect(
            tema=dto.tema,
            brand_context=brand_ctx,
        )

        # 5. Factory salva plano gerado
        FunilFactory.salvar_plano_gerado(funil, plano_json)

        # 6. Persistir plano
        async with get_sql_session_context() as session:
            # atualizar funil com plano
            from sqlalchemy import text
            await session.execute(
                text("UPDATE carrossel.funil SET plano = :plano, status = :status WHERE id = :id"),
                {"plano": funil.plano, "status": funil.status, "id": str(funil.id)},
            )

        # 7. Mapper converte para response
        return FunilMapper.to_criar_response(funil)

    @staticmethod
    async def buscar_plano(pipeline_id: str, tenant_id: str):
        """Retorna o plano do funil associado ao pipeline pai."""
        funil = await _buscar_funil_por_pipeline(pipeline_id, tenant_id)
        return FunilMapper.to_plano_response(funil)

    @staticmethod
    async def editar_plano(pipeline_id: str, dto, tenant_id: str):
        """Aplica edicoes do usuario ao plano."""
        funil = await _buscar_funil_por_pipeline(pipeline_id, tenant_id)
        FunilFactory.aplicar_edicao_plano(funil, dto.plano)
        await _persistir_funil(funil)
        return FunilMapper.to_editar_response(funil, dto.plano)

    @staticmethod
    async def aprovar_plano(pipeline_id: str, tenant_id: str):
        """Aprova plano, cria sub-pipelines e inicia execucao."""
        funil = await _buscar_funil_por_pipeline(pipeline_id, tenant_id)

        # Factory aprova e cria pecas
        pecas = FunilFactory.aprovar_plano(funil)

        # Criar sub-pipelines via pipeline_db_service existente
        pecas_criadas = []
        for peca in pecas:
            tema_peca = FunilFactory.montar_tema_peca(funil.tema, peca.angulo)
            sub = await criar_pipeline(
                tema=tema_peca,
                formato=peca.formato,
                modo_funil=False,
                tenant_id=tenant_id,
                brand_slug=funil.brand_slug,
                avatar_mode=funil.avatar_mode,
            )
            peca.pipeline_id = sub["id"]
            pecas_criadas.append({
                "ordem": peca.ordem,
                "pipeline_id": sub["id"],
                "formato": peca.formato,
                "titulo": peca.titulo,
            })

        # Persistir funil + pecas
        await _persistir_funil_com_pecas(funil, pecas)

        # Atualizar status do funil para executando
        funil.status = "executando"
        await _persistir_funil(funil)

        # Iniciar execucao das primeiras pecas (max 2 simultaneas)
        await FunilService._executar_proximas(funil, pecas_criadas, tenant_id)

        return FunilMapper.to_aprovar_response(funil, pecas_criadas)

    @staticmethod
    async def rejeitar_plano(pipeline_id: str, dto, tenant_id: str):
        """Rejeita plano, regenera via Funnel Architect."""
        funil = await _buscar_funil_por_pipeline(pipeline_id, tenant_id)

        # Factory prepara rejeicao
        FunilFactory.preparar_rejeicao(funil, dto.feedback)

        # Re-executar Funnel Architect com feedback
        from agents.funnel_architect import executar as executar_funnel_architect
        brand_ctx = _get_brand_context(funil.brand_slug)
        plano_anterior = funil.plano
        plano_json = await executar_funnel_architect(
            tema=funil.tema,
            brand_context=brand_ctx,
            feedback=dto.feedback,
            plano_anterior=plano_anterior,
        )

        FunilFactory.salvar_plano_gerado(funil, plano_json)
        await _persistir_funil(funil)

        plano_response = FunilMapper.to_plano_response(funil)
        return FunilMapper.to_rejeitar_response(funil, plano_response.plano)

    @staticmethod
    async def buscar_status(pipeline_id: str, tenant_id: str):
        """Retorna status de todas as pecas do funil (polling)."""
        funil = await _buscar_funil_por_pipeline(pipeline_id, tenant_id)
        pecas_status = await _buscar_status_pecas(funil, tenant_id)

        # Verificar se todas completas -> atualizar funil
        todas_completas = all(p["status"] == "completo" for p in pecas_status)
        if todas_completas and funil.status == "executando":
            funil.status = "completo"
            await _persistir_funil(funil)

        return FunilMapper.to_status_response(funil, pecas_status)

    @staticmethod
    async def executar(pipeline_id: str, tenant_id: str):
        """Executa proximas etapas pendentes (max 2 simultaneas)."""
        funil = await _buscar_funil_por_pipeline(pipeline_id, tenant_id)
        pecas_status = await _buscar_status_pecas(funil, tenant_id)

        proximas = FunilFactory.calcular_proximas_execucoes(pecas_status)

        pecas_executadas = []
        for p in proximas:
            try:
                result = await executar_proxima_etapa(p["pipeline_id"], tenant_id)
                pecas_executadas.append({
                    "peca_ordem": p["ordem"],
                    "pipeline_id": p["pipeline_id"],
                    "etapa": result.get("etapa", ""),
                    "status": result.get("status", ""),
                })
            except Exception:
                pass  # erros individuais nao bloqueiam as demais

        na_fila = len([p for p in pecas_status if p["status"] == "pendente"]) - len(pecas_executadas)
        return FunilMapper.to_executar_response(funil.id, pecas_executadas, max(0, na_fila))

    @staticmethod
    async def exportar(pipeline_id: str, tenant_id: str):
        """Exporta todas as pecas para Drive."""
        funil = await _buscar_funil_por_pipeline(pipeline_id, tenant_id)

        if funil.status != "completo":
            raise ValueError("Funil ainda nao esta completo. Todas as pecas devem estar finalizadas.")

        # Delegar para drive_service existente, 1 export por peca
        # (implementacao detalhada no dev feature)
        pecas_exportadas = []
        # ... logica de export via drive_service ...

        pasta_drive = f"{funil.tema[:50]} - Funil - {funil.approved_at.strftime('%Y-%m-%d')}"
        return FunilMapper.to_exportar_response(funil.id, pasta_drive, pecas_exportadas)

    @staticmethod
    async def _executar_proximas(funil, pecas_criadas, tenant_id):
        """Inicia execucao das primeiras pecas apos aprovacao."""
        proximas = pecas_criadas[:FunilFactory.MAX_SIMULTANEOS]
        for p in proximas:
            try:
                await executar_proxima_etapa(p["pipeline_id"], tenant_id)
            except Exception:
                pass


# --- Funcoes auxiliares (fora da classe, usam SQL direto como o resto do projeto) ---

async def _buscar_funil_por_pipeline(pipeline_id: str, tenant_id: str):
    """Busca o funil associado a um pipeline pai."""
    from sqlalchemy import text
    async with get_sql_session_context() as session:
        result = await session.execute(
            text("SELECT * FROM carrossel.funil WHERE pipeline_id = :pid AND tenant_id = :tid AND deleted_at IS NULL"),
            {"pid": pipeline_id, "tid": tenant_id},
        )
        row = result.mappings().first()
        if not row:
            raise ValueError("Funil nao encontrado para este pipeline")

        funil = FunilModel(
            id=row["id"],
            tenant_id=row["tenant_id"],
            pipeline_id=row["pipeline_id"],
            tema=row["tema"],
            brand_slug=row.get("brand_slug"),
            avatar_mode=row.get("avatar_mode", "livre"),
            plano=row.get("plano"),
            plano_aprovado=row.get("plano_aprovado"),
            status=row["status"],
            feedback_rejeicao=row.get("feedback_rejeicao"),
            approved_at=row.get("approved_at"),
            created_at=row["created_at"],
        )
        return funil


async def _persistir_funil(funil):
    """Atualiza o funil no banco."""
    from sqlalchemy import text
    async with get_sql_session_context() as session:
        await session.execute(
            text("""UPDATE carrossel.funil
                SET plano = :plano, plano_aprovado = :plano_aprovado, status = :status,
                    feedback_rejeicao = :feedback, approved_at = :approved_at, updated_at = :updated_at
                WHERE id = :id"""),
            {
                "plano": funil.plano,
                "plano_aprovado": funil.plano_aprovado,
                "status": funil.status,
                "feedback": funil.feedback_rejeicao,
                "approved_at": funil.approved_at,
                "updated_at": funil.updated_at,
                "id": str(funil.id),
            },
        )


async def _persistir_funil_com_pecas(funil, pecas):
    """Persiste funil atualizado + pecas novas."""
    from sqlalchemy import text
    async with get_sql_session_context() as session:
        await _persistir_funil.__wrapped__(funil, session)  # nao encadeado -- usar inline
        # Inserir pecas
        for peca in pecas:
            await session.execute(
                text("""INSERT INTO carrossel.funil_peca
                    (id, funil_id, pipeline_id, ordem, etapa_funil, titulo, formato, angulo, resumo, gancho, conexao_anterior, cta_para_proxima, created_at)
                    VALUES (:id, :funil_id, :pipeline_id, :ordem, :etapa_funil, :titulo, :formato, :angulo, :resumo, :gancho, :conexao_anterior, :cta_para_proxima, :created_at)"""),
                {
                    "id": str(peca.id),
                    "funil_id": str(peca.funil_id),
                    "pipeline_id": str(peca.pipeline_id) if peca.pipeline_id else None,
                    "ordem": peca.ordem,
                    "etapa_funil": peca.etapa_funil,
                    "titulo": peca.titulo,
                    "formato": peca.formato,
                    "angulo": peca.angulo,
                    "resumo": peca.resumo,
                    "gancho": peca.gancho,
                    "conexao_anterior": peca.conexao_anterior,
                    "cta_para_proxima": peca.cta_para_proxima,
                    "created_at": peca.created_at,
                },
            )


async def _buscar_status_pecas(funil, tenant_id: str) -> list[dict]:
    """Busca status de cada peca consultando seus sub-pipelines."""
    from sqlalchemy import text
    async with get_sql_session_context() as session:
        result = await session.execute(
            text("SELECT * FROM carrossel.funil_peca WHERE funil_id = :fid ORDER BY ordem"),
            {"fid": str(funil.id)},
        )
        pecas = result.mappings().all()

        status_list = []
        for peca in pecas:
            peca_status = {
                "ordem": peca["ordem"],
                "titulo": peca["titulo"],
                "etapa_funil": peca["etapa_funil"],
                "formato": peca["formato"],
                "pipeline_id": str(peca["pipeline_id"]) if peca.get("pipeline_id") else None,
                "status": "pendente",
                "etapa_atual": None,
                "progresso_imagem": None,
            }

            if peca.get("pipeline_id"):
                sub = await buscar_pipeline(str(peca["pipeline_id"]), tenant_id)
                if sub:
                    peca_status["status"] = sub["status"]
                    peca_status["etapa_atual"] = sub.get("etapa_atual")
                    # Progresso de imagem se aplicavel
                    for etapa in sub.get("etapas", []):
                        if etapa.get("agente") == "image_generator" and etapa.get("progresso"):
                            peca_status["progresso_imagem"] = etapa["progresso"]

            status_list.append(peca_status)

        return status_list


def _get_brand_context(brand_slug: str | None) -> str:
    """Reutiliza o mesmo builder de brand context do pipeline_executor."""
    if not brand_slug:
        return ""
    from services.pipeline_executor import _get_brand_context
    return _get_brand_context(brand_slug)
```

**Nota:** O Service segue o mesmo padrao do `pipeline_service.py` existente, usando SQL direto via `text()` em vez de ORM completo. Isso mantem consistencia com o codebase atual. As funcoes auxiliares (`_buscar_funil_por_pipeline`, etc.) ficam fora da classe, igual ao padrao `pipeline_db_service.py`.

---

## 9. Router -- Endpoints (Camada Opaca)

### backend/routers/funil.py

```python
from fastapi import APIRouter, HTTPException, Request

from dtos.funil.criar_funil.request import CriarFunilRequest
from dtos.funil.editar_plano.request import EditarPlanoRequest
from dtos.funil.rejeitar_plano.request import RejeitarPlanoRequest
from middleware.rate_limiter import limiter
from services.funil_service import FunilService

from config import settings

router = APIRouter(prefix="/pipelines", tags=["Funil"])


@router.post("/funil", status_code=201)
async def criar_funil(dto: CriarFunilRequest):
    """Cria pipeline pai + funil + executa Funnel Architect."""
    try:
        return await FunilService.criar(dto, tenant_id=settings.TENANT_ID)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pipeline_id}/funil/plano")
async def buscar_plano(pipeline_id: str):
    """Retorna plano gerado pelo Funnel Architect."""
    try:
        return await FunilService.buscar_plano(pipeline_id, tenant_id=settings.TENANT_ID)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{pipeline_id}/funil/plano")
async def editar_plano(pipeline_id: str, dto: EditarPlanoRequest):
    """Salva plano editado pelo usuario."""
    try:
        return await FunilService.editar_plano(pipeline_id, dto, tenant_id=settings.TENANT_ID)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{pipeline_id}/funil/plano/aprovar")
async def aprovar_plano(pipeline_id: str):
    """Aprova plano e cria N sub-pipelines."""
    try:
        return await FunilService.aprovar_plano(pipeline_id, tenant_id=settings.TENANT_ID)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{pipeline_id}/funil/plano/rejeitar")
@limiter.limit("10/minute")
async def rejeitar_plano(request: Request, pipeline_id: str, dto: RejeitarPlanoRequest):
    """Rejeita plano com feedback, regenera via Funnel Architect."""
    try:
        return await FunilService.rejeitar_plano(pipeline_id, dto, tenant_id=settings.TENANT_ID)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pipeline_id}/funil/status")
async def buscar_status(pipeline_id: str):
    """Retorna status de todas as pecas (polling a cada 3s no frontend)."""
    try:
        return await FunilService.buscar_status(pipeline_id, tenant_id=settings.TENANT_ID)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{pipeline_id}/funil/executar")
@limiter.limit("15/minute")
async def executar_funil(request: Request, pipeline_id: str):
    """Executa proximas etapas pendentes (max 2 simultaneas)."""
    try:
        return await FunilService.executar(pipeline_id, tenant_id=settings.TENANT_ID)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{pipeline_id}/funil/exportar")
async def exportar_funil(pipeline_id: str):
    """Exporta todas as pecas para Drive (1 PDF por peca)."""
    try:
        return await FunilService.exportar(pipeline_id, tenant_id=settings.TENANT_ID)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 10. Agente -- Funnel Architect

### 10.1 System Prompt: agents/funnel-architect.md

```markdown
# Funnel Architect -- System Prompt

Voce e o Funnel Architect da Content Factory IT Valley School. Sua missao e criar planos
estrategicos de funil de conteudo para redes sociais.

## Contexto
- Voce trabalha para a IT Valley School (ou para a marca indicada no brand context).
- Um funil de conteudo e uma sequencia de 3-5 pecas visuais que levam o publico
  de "nao conheço" ate "quero comprar/participar".
- Cada peca deve funcionar SOZINHA (para quem ve so ela) e como PARTE DO FUNIL
  (para quem acompanha a sequencia).

## Entrada
- Tema proposto pelo usuario
- Brand context (identidade da marca)
- Feedback do usuario (se rejeitou plano anterior)
- Plano anterior (se rejeitado)

## Saida (JSON obrigatorio -- sem texto antes ou depois)
{
  "plano": {
    "tema_principal": "string -- tema unificador do funil",
    "objetivo_campanha": "string -- o que a campanha como um todo quer alcançar",
    "narrativa_geral": "string -- fio condutor que conecta todas as pecas",
    "pecas": [
      {
        "ordem": 1,
        "titulo": "string -- titulo da peca",
        "etapa_funil": "topo | meio | fundo | conversao",
        "formato": "carrossel | post_unico | thumbnail_youtube | capa_reels",
        "angulo": "string -- abordagem especifica desta peca",
        "resumo": "string -- 1-2 frases sobre o conteudo",
        "gancho": "string -- frase de scroll-stop para esta peca",
        "conexao_anterior": "string | null -- como esta peca conecta com a anterior",
        "cta_para_proxima": "string | null -- como direciona para a proxima peca"
      }
    ]
  }
}

## Regras
1. Gerar entre 3 e 5 pecas por funil
2. Cobrir pelo menos 2 etapas diferentes do funil
3. A primeira peca DEVE ser topo de funil (atrair atencao)
4. A ultima peca DEVE ser fundo ou conversao (levar a acao)
5. Variar formatos quando possivel (nao fazer 5 carrosseis)
6. Cada peca deve funcionar sozinha E como parte do funil
7. A narrativa deve ter um fio condutor claro entre as pecas
8. Respeitar identidade da marca (brand context injetado)
9. Tom IT Valley: tecnico + acessivel. NUNCA guru, hack, truque, milagre
10. Responder APENAS em JSON valido, sem texto antes ou depois

## Distribuicao ideal de etapas
- Topo: atrair atencao, gerar curiosidade (1-2 pecas)
- Meio: aprofundar, mostrar autoridade, resolver duvida (1-2 pecas)
- Fundo: convencer, mostrar prova, comparar (0-1 peca)
- Conversao: CTA direto, oferta, proximo passo (1 peca)

## Distribuicao ideal de formatos
- Carrossel: conteudo educativo, passo-a-passo, listas
- Post unico: dados impactantes, citacoes, provocacoes
- Thumbnail YouTube: atrair cliques para video
- Capa Reels: atrair views para video curto

## Se rejeitado com feedback
- Ler o feedback com atencao
- Ler o plano anterior para entender o que nao agradou
- Gerar um plano COMPLETAMENTE DIFERENTE que enderece o feedback
- NAO repetir a mesma estrutura/angulo rejeitados
```

### 10.2 Implementacao: backend/agents/funnel_architect.py

```python
from pathlib import Path

import anthropic

from utils.json_parser import parse_llm_json


PROMPT_PATH = Path(__file__).parent / "funnel_architect.md"
if not PROMPT_PATH.exists():
    PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "agents" / "funnel-architect.md"


async def executar(
    tema: str,
    brand_context: str = "",
    feedback: str = "",
    plano_anterior: str = "",
    claude_api_key: str = "",
) -> dict:
    """Executa o Funnel Architect: gera plano estrategico de funil.

    Retorna: dict com o plano completo (tema_principal, objetivo, narrativa, pecas[]).
    """
    import os
    if not claude_api_key:
        claude_api_key = os.getenv("CLAUDE_API_KEY", "")

    system_prompt = ""
    if PROMPT_PATH.exists():
        system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    user_prompt = (
        f"TEMA DO FUNIL (obrigatorio, nao mude): {tema}\n\n"
        f"Gere um plano de funil de conteudo com 3-5 pecas para esse tema.\n"
    )

    if brand_context:
        user_prompt += (
            f"\n=== CONTEXTO DA MARCA (OBRIGATORIO) ===\n"
            f"{brand_context}\n"
            f"Crie o plano para ESTA marca. Use o tom e identidade dela.\n"
            f"=== FIM CONTEXTO DA MARCA ===\n"
        )

    if feedback and plano_anterior:
        user_prompt += (
            f"\n=== PLANO ANTERIOR REJEITADO ===\n"
            f"{plano_anterior}\n"
            f"=== FIM PLANO ANTERIOR ===\n\n"
            f"FEEDBACK DO USUARIO: {feedback}\n"
            f"GERE um plano COMPLETAMENTE DIFERENTE, seguindo o feedback acima.\n"
            f"NAO repita a mesma estrutura ou angulos rejeitados.\n"
        )

    user_prompt += "\nResposta OBRIGATORIAMENTE em JSON valido. Sem texto antes ou depois."

    client = anthropic.AsyncAnthropic(api_key=claude_api_key)
    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    result = parse_llm_json(message.content[0].text)
    if "raw_text" in result:
        raise ValueError(f"Funnel Architect retornou texto invalido: {result['raw_text'][:200]}")
    return result
```

**Nota sobre symlink do prompt:** O agente tenta carregar de `backend/agents/funnel_architect.md` primeiro, e faz fallback para `agents/funnel-architect.md` (na raiz do projeto). Isso segue o mesmo padrao do `strategist.py` existente.

---

## 11. Tabela de Endpoints

| Metodo | Rota | Auth | Descricao |
|--------|------|------|-----------|
| POST | `/api/pipelines/funil` | tenant_id | Cria pipeline pai + funil + executa Funnel Architect |
| GET | `/api/pipelines/{id}/funil/plano` | tenant_id | Retorna plano gerado pelo Funnel Architect |
| PUT | `/api/pipelines/{id}/funil/plano` | tenant_id | Salva plano editado pelo usuario |
| POST | `/api/pipelines/{id}/funil/plano/aprovar` | tenant_id | Aprova plano, cria N sub-pipelines, inicia execucao |
| POST | `/api/pipelines/{id}/funil/plano/rejeitar` | tenant_id | Rejeita plano com feedback, regenera via Funnel Architect |
| GET | `/api/pipelines/{id}/funil/status` | tenant_id | Status de todas as pecas (polling a cada 3s) |
| POST | `/api/pipelines/{id}/funil/executar` | tenant_id | Executa proximas etapas pendentes (max 2 simultaneas) |
| POST | `/api/pipelines/{id}/funil/exportar` | tenant_id | Exporta todos os PDFs + salva no Drive |

**Nota sobre autenticacao:** O projeto atual usa `settings.TENANT_ID` (fixo em config) em vez de JWT. Os endpoints seguem esse padrao. Quando JWT for implementado, basta adicionar `Depends(get_current_user)` e extrair `tenant_id` do token.

---

## 12. Fluxo de Execucao Completo

```
1. POST /api/pipelines/funil
   ├── pipeline_db_service.criar_pipeline(modo_funil=True)  -> pipeline pai
   ├── FunilFactory.criar_funil()                           -> FunilModel
   ├── agents.funnel_architect.executar()                   -> plano JSON (3-5 pecas)
   ├── FunilFactory.salvar_plano_gerado()                   -> valida + salva no funil
   └── retorna CriarFunilResponse (status: plano_gerado)

2. GET /api/pipelines/{id}/funil/plano
   └── retorna BuscarPlanoResponse com plano + pecas

3. PUT /api/pipelines/{id}/funil/plano  (opcional, usuario edita)
   ├── FunilFactory.aplicar_edicao_plano()  -> valida regras (min 2 pecas, 2+ etapas)
   └── retorna EditarPlanoResponse

4. POST /api/pipelines/{id}/funil/plano/aprovar
   ├── FunilFactory.aprovar_plano()           -> cria FunilPecaModel[]
   ├── Para CADA peca:
   │   ├── FunilFactory.montar_tema_peca()    -> tema_principal + angulo
   │   └── pipeline_db_service.criar_pipeline() -> sub-pipeline completo (6 etapas)
   ├── _persistir_funil_com_pecas()           -> salva funil + pecas no banco
   ├── executar_proxima_etapa() x 2           -> inicia 2 primeiros sub-pipelines
   └── retorna AprovarPlanoResponse

5. GET /api/pipelines/{id}/funil/status  (polling a cada 3s)
   ├── Para CADA peca:
   │   └── buscar_pipeline(sub_pipeline_id)   -> status, etapa_atual, progresso
   ├── Se todas completas -> funil.status = "completo"
   └── retorna BuscarStatusFunilResponse

6. POST /api/pipelines/{id}/funil/executar  (chamado pelo frontend ou automaticamente)
   ├── FunilFactory.calcular_proximas_execucoes()  -> ate 2 vagas
   ├── Para CADA vaga:
   │   └── executar_proxima_etapa(sub_pipeline_id) -> executa proximo agente
   └── retorna ExecutarFunilResponse

7. /pipeline/{pecaId}/copy, /visual, etc  (fluxo existente, sem mudancas)
   └── Usuario aprova/rejeita etapas de cada peca individualmente

8. POST /api/pipelines/{id}/funil/exportar
   ├── Verifica funil.status == "completo"
   ├── Para CADA peca:
   │   └── drive_service.salvar()  -> PDF + PNGs na subpasta do funil
   └── retorna ExportarFunilResponse
```

### Diagrama de Estados do Funil

```
pendente_plano ──[Funnel Architect executa]──> plano_gerado
       ^                                           |
       |                                    [Usuario edita]
       |                                           |
       +──[Rejeita com feedback]──────────── plano_gerado
                                                   |
                                            [Aprova plano]
                                                   |
                                                   v
                                             plano_aprovado
                                                   |
                                            [Cria sub-pipelines]
                                                   |
                                                   v
                                              executando
                                                   |
                                            [Todas pecas completas]
                                                   |
                                                   v
                                              completo
```

### Paralelismo de Sub-Pipelines

```
Aprovacao do plano (5 pecas):
  t=0   [Peca 1: executando] [Peca 2: executando] [Peca 3: fila] [Peca 4: fila] [Peca 5: fila]
  t=1   [Peca 1: aprovacao]  [Peca 2: executando] [Peca 3: executando] [P4: fila] [P5: fila]
  t=2   [Peca 1: completa]   [Peca 2: aprovacao]  [Peca 3: executando] [P4: executando] [P5: fila]
  ...
```

**Regra RN-007:** Max 2 simultaneos. Quando uma peca libera vaga (vai para `aguardando_aprovacao` ou `completo`), a proxima da fila entra.

**Regra RN-008:** Pecas sao independentes. Se Peca 2 der erro, Peca 3 continua normalmente.

---

## 13. Mudanca em main.py

```python
# Adicionar ao bloco de imports:
from routers import funil

# Adicionar ao bloco de include_router:
app.include_router(funil.router, prefix="/api")
```

---

## 14. Dev Features (Unidades de Trabalho)

Cada dev feature e 1 caso de uso completo, de ponta a ponta:

### DF-001: CriarFunil
```
CRIA:     dtos/funil/criar_funil/request.py
CRIA:     dtos/funil/criar_funil/response.py
CRIA:     dtos/funil/base.py
CRIA:     models/funil.py
CRIA:     factories/funil_factory.py      <- criar_funil() + salvar_plano_gerado()
CRIA:     mappers/funil_mapper.py         <- to_criar_response()
CRIA:     services/funil_service.py       <- criar()
CRIA:     routers/funil.py               <- POST /api/pipelines/funil
CRIA:     agents/funnel_architect.py      <- executar()
CRIA:     agents/funnel-architect.md      <- system prompt
MODIFICA: main.py                        <- include_router(funil.router)
```

### DF-002: BuscarPlano
```
CRIA:     dtos/funil/buscar_plano/response.py
ADICIONA: mappers/funil_mapper.py         <- to_plano_response()
ADICIONA: services/funil_service.py       <- buscar_plano()
ADICIONA: routers/funil.py               <- GET /{id}/funil/plano
```

### DF-003: EditarPlano
```
CRIA:     dtos/funil/editar_plano/request.py
CRIA:     dtos/funil/editar_plano/response.py
ADICIONA: factories/funil_factory.py      <- aplicar_edicao_plano() + _validar_plano()
ADICIONA: mappers/funil_mapper.py         <- to_editar_response()
ADICIONA: services/funil_service.py       <- editar_plano()
ADICIONA: routers/funil.py               <- PUT /{id}/funil/plano
```

### DF-004: AprovarPlano
```
CRIA:     dtos/funil/aprovar_plano/response.py
ADICIONA: factories/funil_factory.py      <- aprovar_plano() + montar_tema_peca()
ADICIONA: mappers/funil_mapper.py         <- to_aprovar_response()
ADICIONA: services/funil_service.py       <- aprovar_plano() + _executar_proximas()
ADICIONA: routers/funil.py               <- POST /{id}/funil/plano/aprovar
```

### DF-005: RejeitarPlano
```
CRIA:     dtos/funil/rejeitar_plano/request.py
CRIA:     dtos/funil/rejeitar_plano/response.py
ADICIONA: factories/funil_factory.py      <- preparar_rejeicao()
ADICIONA: mappers/funil_mapper.py         <- to_rejeitar_response()
ADICIONA: services/funil_service.py       <- rejeitar_plano()
ADICIONA: routers/funil.py               <- POST /{id}/funil/plano/rejeitar
```

### DF-006: BuscarStatusFunil
```
CRIA:     dtos/funil/buscar_status/response.py
ADICIONA: factories/funil_factory.py      <- calcular_proximas_execucoes()
ADICIONA: mappers/funil_mapper.py         <- to_status_response()
ADICIONA: services/funil_service.py       <- buscar_status()
ADICIONA: routers/funil.py               <- GET /{id}/funil/status
```

### DF-007: ExecutarFunil
```
CRIA:     dtos/funil/executar_funil/response.py
ADICIONA: services/funil_service.py       <- executar()
ADICIONA: mappers/funil_mapper.py         <- to_executar_response()
ADICIONA: routers/funil.py               <- POST /{id}/funil/executar
```

### DF-008: ExportarFunil
```
CRIA:     dtos/funil/exportar_funil/response.py
ADICIONA: services/funil_service.py       <- exportar()
ADICIONA: mappers/funil_mapper.py         <- to_exportar_response()
ADICIONA: routers/funil.py               <- POST /{id}/funil/exportar
```

---

## 15. Trade-offs Aceitos

| Mudanca | Impacto | Esforco |
|---------|---------|---------|
| Adicionar campo numa peca | DTO + Model + Factory + Mapper (4 arquivos, 1 linha cada) | 2 min |
| Mudar regra de negocio do funil | So Factory (1 arquivo) | isolado |
| Mudar limite de simultaneos | So Factory (1 constante) | 30 seg |
| Trocar banco (SQL -> Mongo) | So funcoes auxiliares do Service | isolado |
| Novo formato de peca | Adicionar em FORMATS do utils/dimensions | 1 min |

---

## 16. Duvidas Tecnicas em Aberto

| ID | Duvida | Impacto | Sugestao |
|----|--------|---------|----------|
| DT-001 | O endpoint de criacao do funil deve ser `POST /api/pipelines/funil` (separado) ou `POST /api/pipelines/` com `modo_funil=true` (existente)? | Rota do router. PRD sugere o segundo, mas o primeiro isola melhor. | Usar rota separada `POST /api/pipelines/funil` para manter o router do funil opaco e independente. O pipeline existente nao precisa mudar. |
| DT-002 | O polling do frontend (`GET /funil/status`) faz N queries (1 por peca). Com 5 pecas, sao 5 `buscar_pipeline()` por request. Precisa otimizar com JOIN? | Performance do polling (chamado a cada 3s). | Aceitavel no MVP com 5 pecas max. Se necessario, criar query unica com JOIN no futuro. |
| DT-003 | O `executar_proxima_etapa()` do pipeline_executor e sincrono (await). Para execucao paralela real, precisa de `asyncio.gather()` ou fila (Celery, ARQ). | Paralelismo real vs sequencial-com-polling. | MVP usa polling do frontend: frontend chama `POST /funil/executar` repetidamente. O Service executa 1 etapa por vez, mas em pecas diferentes. Paralelismo real fica para v2. |
| DT-004 | O symlink do system prompt (backend/agents/ vs agents/) segue qual padrao para o funnel_architect? | Organizacao de arquivos. | Seguir mesmo padrao do strategist.py: prompt na raiz `agents/funnel-architect.md`, agente em `backend/agents/funnel_architect.py` com fallback path. |
| DT-005 | DA-005 do PRD: exportar parcial (sem pecas com erro) ou exigir todas completas? | Logica de export. | MVP exige todas completas. Factory valida `funil.status == "completo"`. |

---

*Documento gerado em 2026-04-05 pelo Agente 03 (Arquiteto IT Valley Backend).*
*Fonte de verdade para: Agente 07 (SQL), Agente 10 (Dev Backend), Agentes 11-14 (QA).*
*PRD de referencia: `docs/PRD-funil.md`.*
