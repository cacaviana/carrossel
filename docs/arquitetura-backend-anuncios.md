# Arquitetura Backend -- Modulo Anuncios (Google Ads Display)

Documento produzido pelo Agente 03 (Arquiteto IT Valley Backend).
Base: PRD (`docs/prd-anuncios.md`) + Telas (`docs/telas-anuncios.md`) + `CLAUDE.md` + codigo backend existente (`backend/`) + referencias `docs/ARQUITETURA_BACKEND.md` e `docs/arquitetura-backend-kanban.md`.

Fonte de verdade para o Agente 10 (Dev Backend).

---

## 1. Overview -- O que muda no backend

### 1.1 Contexto
O sistema hoje suporta os formatos `carrossel`, `post_unico`, `thumbnail_youtube`, `capa_reels`. O modulo Anuncios introduz o formato `anuncio` com caracteristicas proprias: **4 dimensoes por peca** (1200x628, 1080x1080, 300x600, 300x250), **copy com limites rigidos** (headline 30 chars / descricao 90 chars) e **pacote de export diferenciado** (4 PNGs + copy.txt, sem PDF).

### 1.2 Dominio novo
`Anuncio` com 5 casos de uso CRUD (nivel 5 IT Valley), alem de um caso de uso auxiliar de regeneracao individual por dimensao (RN-018) e um handler de export especifico.

### 1.3 O que sera **criado**
- Dominio **Anuncio** completo (dtos, model, factory, mapper, service, router, repository)
- Endpoint de regeneracao individual por dimensao (sub-rota `/api/anuncios/{id}/regenerar-dimensao`)
- Handler de export anuncio-especifico em `services/drive_service.py` (novo metodo `salvar_anuncio_drive`) + ZIP builder local em `services/anuncio_export_service.py`
- Integracao do formato `anuncio` no pipeline existente: ajuste dos agentes `copywriter` (limites 30/90), `art_director` (1 prompt base + 4 adaptacoes de aspect ratio) e `image_generator` (gera 4 imagens em paralelo, modelo por dimensao)
- Configuracao em `configs/dimensions.json` (array de 4 dimensoes para formato `anuncio`) e `configs/platform_rules.json` (plataforma "Google Ads Display") e `configs/formatos.json` (novo formato)
- Brand Gate adaptado por aspect ratio em `skills/brand_validator.py` (funcao ja existente, adicionar `aspect_ratio` param e desativar foto overlay para dimensoes pequenas)
- Brand overlay adaptado em `skills/brand_overlay.py` (desativa foto em dimensoes 300x600 e 300x250)

### 1.4 O que **NAO** muda
- Estrutura geral (tudo na raiz de `backend/`, sem pasta `app/`)
- Autenticacao JWT via `middleware/auth.py` ja existente
- Prefix `/api` em todos os routers
- Pipeline engine, agentes 1-6, Brand Gate core, Content Critic
- Camada `data/` (SQLAlchemy async + MSSQL). Repositorio de anuncio herda do `BaseSQLRepository`.
- Google Drive service account, pasta raiz, scope `https://www.googleapis.com/auth/drive`
- Kanban e Historico (so recebem registros do tipo `anuncio` como mais um formato)

### 1.5 Filosofia IT Valley aplicada
- **Camadas opacas:** `AnuncioRouter` e `AnuncioService` **NUNCA** conhecem campos do DTO. Delegam tudo para Factory + Mapper + Repository.
- **Factory dona das regras:** `AnuncioFactory` valida 30/90 chars, estado das 4 dimensoes, transicoes de status (`rascunho` -> `gerando` -> `parcial`/`completo` -> `erro`).
- **Mapper so converte:** Model <-> Response.
- **Tenant_id em toda query** (RN-009).
- **Soft delete** com `deleted_at` (RN-013).
- **Imports explicitos, sem barrel exports.**

---

## 2. Arvore de arquivos a criar/modificar

```text
backend/
  main.py                                    # MODIFICAR: registrar router anuncio

  dtos/
    anuncio/                                 # CRIAR (pasta nova)
      base.py                                # CRIAR -- AnuncioBase, DimensaoBase
      criar_anuncio/
        request.py                           # CRIAR -- CriarAnuncioRequest
        response.py                          # CRIAR -- CriarAnuncioResponse
      listar_anuncios/
        request.py                           # CRIAR -- ListarAnunciosRequest (filtros)
        response.py                          # CRIAR -- ListarAnunciosResponse
      obter_anuncio/
        response.py                          # CRIAR -- ObterAnuncioResponse
      editar_anuncio/
        request.py                           # CRIAR -- EditarAnuncioRequest
        response.py                          # CRIAR -- EditarAnuncioResponse
      excluir_anuncio/
        response.py                          # CRIAR -- ExcluirAnuncioResponse
      regenerar_dimensao/
        request.py                           # CRIAR -- RegenerarDimensaoRequest
        response.py                          # CRIAR -- RegenerarDimensaoResponse
      exportar_anuncio/
        request.py                           # CRIAR -- ExportarAnuncioRequest
        response.py                          # CRIAR -- ExportarAnuncioResponse

  models/
    anuncio.py                               # CRIAR -- AnuncioModel + AnuncioDimensaoModel

  factories/
    anuncio_factory.py                       # CRIAR -- regras de negocio

  mappers/
    anuncio_mapper.py                        # CRIAR -- conversoes DTO<->Model

  services/
    anuncio_service.py                       # CRIAR -- camada opaca
    anuncio_pipeline_service.py              # CRIAR -- integracao com pipeline existente
    anuncio_export_service.py                # CRIAR -- ZIP builder + copy.txt
    drive_service.py                         # MODIFICAR -- adicionar salvar_anuncio_drive()
    imagem_service.py                        # MODIFICAR -- _select_model adapta para formato=anuncio
    prompt_templates.py                      # MODIFICAR -- template dark mode por aspect ratio

  routers/
    anuncio.py                               # CRIAR -- endpoints /api/anuncios/*

  data/
    repositories/
      sql/
        anuncio_repository.py                # CRIAR -- queries especificas

  skills/
    brand_overlay.py                         # MODIFICAR -- desativar foto em 300x600 e 300x250
    brand_validator.py                       # MODIFICAR -- aceitar aspect_ratio por dimensao

  agents/
    copywriter.py                            # MODIFICAR -- limites Google Ads quando formato=anuncio
    art_director.py                          # MODIFICAR -- gera 1 prompt base + 4 adaptacoes
    image_generator.py                       # MODIFICAR -- gera 4 imagens em paralelo p/ anuncio

  configs/
    dimensions.json                          # MODIFICAR -- anuncio como array das 4 dimensoes
    formatos.json                            # MODIFICAR -- adicionar formato "anuncio" completo
    platform_rules.json                      # MODIFICAR -- adicionar plataforma "Google Ads Display"
    templates.json                           # MODIFICAR -- template do formato anuncio
```

---

## 3. DTOs de cada caso de uso

### 3.1 Base compartilhada

```python
# dtos/anuncio/base.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class DimensaoBase(BaseModel):
    """1 das 4 dimensoes do anuncio. Compartilhada por varios responses."""
    dimensao_id: str  # "1200x628" | "1080x1080" | "300x600" | "300x250"
    largura: int
    altura: int
    imagem_url: Optional[str] = None          # URL Drive ou base64 temporario
    modelo_usado: Optional[str] = None        # "gemini-3-pro-image-preview" | "gemini-2.5-flash-image"
    overlay_aplicado: str = "foto+logo"       # "foto+logo" | "so_logo"
    brand_gate_status: str = "nao_gerada"     # "nao_gerada" | "valido" | "revisao_manual" | "falhou"
    brand_gate_retries: int = 0               # 0, 1 ou 2 (RN-019)
    gerada_em: Optional[datetime] = None


class AnuncioBase(BaseModel):
    """Campos compartilhados entre responses de Anuncio."""
    id: str
    tenant_id: str
    titulo: str
    headline: str = Field(max_length=30)
    descricao: str = Field(max_length=90)
    status: str                               # rascunho|gerando|completo|parcial|erro|cancelado
    etapa_funil: Optional[str] = None         # topo|meio|fundo|avulso
    pipeline_id: Optional[str] = None
    pipeline_funil_id: Optional[str] = None
    drive_folder_link: Optional[str] = None
    dimensoes_ok_count: int = 0               # 0..4
    dimensoes: list[DimensaoBase] = []
    foto_criador_id: Optional[str] = None
    criado_por: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
```

### 3.2 CriarAnuncio

```python
# dtos/anuncio/criar_anuncio/request.py
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CriarAnuncioRequest(BaseModel):
    titulo: str = Field(min_length=3, max_length=200)
    tema_ou_briefing: str = Field(min_length=20, max_length=5000)
    modo_entrada: str                         # "texto" | "disciplina"
    disciplina: Optional[str] = None
    tecnologia: Optional[str] = None
    etapa_funil: Optional[str] = "avulso"     # topo|meio|fundo|avulso
    pipeline_funil_id: Optional[str] = None   # se vier do Funnel Architect
    foto_criador_id: Optional[str] = None

    @field_validator("modo_entrada")
    @classmethod
    def modo_valido(cls, v: str) -> str:
        if v not in {"texto", "disciplina"}:
            raise ValueError("modo_entrada deve ser 'texto' ou 'disciplina'")
        return v

    @field_validator("etapa_funil")
    @classmethod
    def etapa_valida(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return "avulso"
        if v not in {"topo", "meio", "fundo", "avulso"}:
            raise ValueError("etapa_funil invalida")
        return v
```

```python
# dtos/anuncio/criar_anuncio/response.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CriarAnuncioResponse(BaseModel):
    id: str
    tenant_id: str
    titulo: str
    status: str                    # sempre "rascunho" ou "gerando" ao criar
    pipeline_id: str               # id do pipeline disparado
    etapa_funil: Optional[str]
    created_at: datetime
```

### 3.3 ListarAnuncios

```python
# dtos/anuncio/listar_anuncios/request.py
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class ListarAnunciosRequest(BaseModel):
    """Query params da listagem -- validados como Pydantic no router."""
    busca: Optional[str] = None
    status: Optional[str] = None              # em_andamento|concluido|parcial|erro|cancelado
    etapa_funil: Optional[str] = None         # topo|meio|fundo|avulso
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    incluir_excluidos: bool = False
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
```

```python
# dtos/anuncio/listar_anuncios/response.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AnuncioCardResponse(BaseModel):
    """Card compacto para listagem."""
    id: str
    titulo: str
    headline: str
    descricao_preview: str                    # truncado em 90
    thumbnail_1080: Optional[str] = None      # image_urls[1] ou None se nao gerada
    status: str
    etapa_funil: Optional[str] = None
    pipeline_id: Optional[str] = None
    drive_folder_link: Optional[str] = None
    dimensoes_ok_count: int = 0
    criado_em: datetime
    deleted_at: Optional[datetime] = None


class ListarAnunciosResponse(BaseModel):
    items: list[AnuncioCardResponse]
    total: int
    page: int
    page_size: int
```

### 3.4 ObterAnuncio

```python
# dtos/anuncio/obter_anuncio/response.py
from dtos.anuncio.base import AnuncioBase


class ObterAnuncioResponse(AnuncioBase):
    """Retorno completo com as 4 dimensoes hidratadas."""
    pass
```

### 3.5 EditarAnuncio

```python
# dtos/anuncio/editar_anuncio/request.py
from typing import Optional
from pydantic import BaseModel, Field


class EditarAnuncioRequest(BaseModel):
    """Edicao de metadados e copy. NAO regenera imagens -- usar RegenerarDimensao pra isso."""
    titulo: Optional[str] = Field(default=None, min_length=3, max_length=200)
    headline: Optional[str] = Field(default=None, min_length=1, max_length=30)
    descricao: Optional[str] = Field(default=None, min_length=1, max_length=90)
    etapa_funil: Optional[str] = None
```

```python
# dtos/anuncio/editar_anuncio/response.py
from dtos.anuncio.base import AnuncioBase


class EditarAnuncioResponse(AnuncioBase):
    pass
```

### 3.6 ExcluirAnuncio

```python
# dtos/anuncio/excluir_anuncio/response.py
from datetime import datetime
from pydantic import BaseModel


class ExcluirAnuncioResponse(BaseModel):
    id: str
    deleted_at: datetime
    success: bool = True
```

### 3.7 RegenerarDimensao (RN-018)

```python
# dtos/anuncio/regenerar_dimensao/request.py
from typing import Optional
from pydantic import BaseModel, Field, field_validator


DIMENSOES_VALIDAS = {"1200x628", "1080x1080", "300x600", "300x250"}


class RegenerarDimensaoRequest(BaseModel):
    """Dispara regeneracao de 1 ou mais dimensoes, mantendo as demais."""
    dimensoes_alvo: list[str] = Field(min_length=1, max_length=4)
    feedback_livre: Optional[str] = Field(default=None, max_length=500)

    @field_validator("dimensoes_alvo")
    @classmethod
    def dimensoes_validas(cls, v: list[str]) -> list[str]:
        invalidas = set(v) - DIMENSOES_VALIDAS
        if invalidas:
            raise ValueError(f"Dimensoes invalidas: {invalidas}")
        if len(v) != len(set(v)):
            raise ValueError("Dimensoes duplicadas em dimensoes_alvo")
        return v
```

```python
# dtos/anuncio/regenerar_dimensao/response.py
from pydantic import BaseModel


class RegenerarDimensaoResponse(BaseModel):
    id: str
    dimensoes_em_regeneracao: list[str]       # quais entraram em status "regenerando"
    message: str
```

### 3.8 ExportarAnuncio (download ZIP ou salvar Drive -- RN-007, RN-008)

```python
# dtos/anuncio/exportar_anuncio/request.py
from typing import Optional
from pydantic import BaseModel


class ExportarAnuncioRequest(BaseModel):
    destino: str                              # "zip" | "drive"
    drive_parent_folder_id: Optional[str] = None  # obrigatorio se destino="drive"
```

```python
# dtos/anuncio/exportar_anuncio/response.py
from typing import Optional
from pydantic import BaseModel


class ExportarAnuncioResponse(BaseModel):
    destino: str                              # "zip" | "drive"
    drive_folder_id: Optional[str] = None
    drive_folder_link: Optional[str] = None
    zip_base64: Optional[str] = None          # preenchido se destino="zip"
    arquivos_exportados: list[str]            # nomes dos arquivos gerados
    dimensoes_incluidas: int                  # 1..4 (RN-019: pode ser parcial)
    warning: Optional[str] = None             # ex: "3 de 4 dimensoes -- gere a faltante antes de publicar"
```

---

## 4. Model SQLAlchemy completo

### 4.1 AnuncioModel + AnuncioDimensaoModel

Decisao: usar **1 tabela principal** (`anuncios`) com metadados + copy + status e **1 tabela filha** (`anuncio_dimensoes`) com 1 linha por dimensao. Isso permite:
- Controle individual de status de Brand Gate por dimensao
- Regeneracao individual (RN-018) sem mexer nas demais
- Contagem de `dimensoes_ok_count` por query agregada
- Entrega parcial (RN-019) natural: dimensoes com status `falhou` ficam na tabela mas nao entram no export

```python
# models/anuncio.py
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship

from models.base import Base, TenantMixin


class AnuncioModel(TenantMixin, Base):
    """Anuncio Google Ads Display -- 1 por registro, contem 4 dimensoes (filhas).

    Status:
      - rascunho: criado mas pipeline nao iniciou
      - gerando: pipeline em execucao (qualquer etapa)
      - completo: 4/4 dimensoes aprovadas no Brand Gate
      - parcial: 1..3 dimensoes aprovadas (RN-019)
      - erro: falha global (copy invalida, pipeline abortado)
      - cancelado: cancelado manualmente antes de concluir
    """
    __tablename__ = "anuncio"
    __table_args__ = (
        Index("ix_anuncio_tenant_status", "tenant_id", "status"),
        Index("ix_anuncio_tenant_pipeline", "tenant_id", "pipeline_id"),
        {"schema": "carrossel"},
    )

    # Relacionamento com o pipeline que gerou este anuncio
    pipeline_id = Column(
        UNIQUEIDENTIFIER,
        ForeignKey("carrossel.pipeline.id"),
        nullable=True,
    )
    # Se veio de um funil, aponta para o pipeline "mae" (funil)
    pipeline_funil_id = Column(UNIQUEIDENTIFIER, nullable=True)

    # Metadados
    titulo = Column(String(200), nullable=False)
    etapa_funil = Column(String(20), nullable=True)     # topo|meio|fundo|avulso
    tema_ou_briefing = Column(Text, nullable=True)      # armazenado para retomada
    modo_entrada = Column(String(20), nullable=True)    # texto|disciplina
    disciplina = Column(String(50), nullable=True)
    tecnologia = Column(String(100), nullable=True)
    foto_criador_id = Column(String(100), nullable=True)
    criado_por = Column(String(100), nullable=True)     # user_id do JWT

    # Copy (RN-002, RN-003, RN-017 -- unica por anuncio)
    headline = Column(String(30), nullable=True)
    descricao = Column(String(90), nullable=True)

    # Status e export
    status = Column(String(20), nullable=False, default="rascunho")
    drive_folder_id = Column(String(100), nullable=True)
    drive_folder_link = Column(Text, nullable=True)
    last_exported_at = Column(DateTime, nullable=True)

    dimensoes = relationship(
        "AnuncioDimensaoModel",
        back_populates="anuncio",
        cascade="all, delete-orphan",
        order_by="AnuncioDimensaoModel.ordem",
    )


class AnuncioDimensaoModel(Base):
    """1 linha por dimensao (sempre 4 linhas por anuncio no MVP)."""
    __tablename__ = "anuncio_dimensao"
    __table_args__ = (
        Index("ix_anuncio_dim_anuncio_dim", "anuncio_id", "dimensao_id"),
        {"schema": "carrossel"},
    )

    id = Column(UNIQUEIDENTIFIER, primary_key=True)
    anuncio_id = Column(
        UNIQUEIDENTIFIER,
        ForeignKey("carrossel.anuncio.id"),
        nullable=False,
    )
    dimensao_id = Column(String(20), nullable=False)    # "1200x628" etc.
    ordem = Column(Integer, nullable=False)              # 0..3 (ordem fixa)
    largura = Column(Integer, nullable=False)
    altura = Column(Integer, nullable=False)

    # Geracao
    modelo_usado = Column(String(50), nullable=True)    # gemini-3-pro-image-preview | gemini-2.5-flash-image
    overlay_aplicado = Column(String(20), nullable=False, default="foto+logo")  # foto+logo | so_logo

    # Imagem gerada
    imagem_url = Column(Text, nullable=True)            # URL Drive ou data URL
    imagem_base64 = Column(Text, nullable=True)          # cache local (pre-upload)

    # Brand Gate
    brand_gate_status = Column(String(20), nullable=False, default="nao_gerada")
    # Valores: nao_gerada | gerando | valido | revisao_manual | falhou
    brand_gate_retries = Column(Integer, nullable=False, default=0)  # 0,1,2 (RN-019)
    brand_gate_feedback = Column(Text, nullable=True)   # resumo do ultimo fail

    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    gerada_em = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    anuncio = relationship("AnuncioModel", back_populates="dimensoes")
```

### 4.2 Regras de ordem fixa

| ordem | dimensao_id | largura | altura | modelo_padrao | overlay |
|-------|------------|---------|--------|---------------|---------|
| 0 | 1200x628 | 1200 | 628 | gemini-3-pro-image-preview | foto+logo |
| 1 | 1080x1080 | 1080 | 1080 | gemini-2.5-flash-image | foto+logo |
| 2 | 300x600 | 300 | 600 | gemini-2.5-flash-image | so_logo |
| 3 | 300x250 | 300 | 250 | gemini-2.5-flash-image | so_logo |

A Factory (sec. 5) e dona dessas regras -- qualquer dimensao nova ou alteracao passa por ela.

---

## 5. Factory -- regras, metodos e assinaturas

A Factory e **dona das regras de negocio** do dominio Anuncio. O Service nunca conhece os campos; chama a Factory para criar/atualizar e confiar que o objeto e valido.

```python
# factories/anuncio_factory.py
from datetime import datetime, timezone
from typing import Optional
import uuid

from dtos.anuncio.criar_anuncio.request import CriarAnuncioRequest
from dtos.anuncio.editar_anuncio.request import EditarAnuncioRequest
from dtos.anuncio.regenerar_dimensao.request import RegenerarDimensaoRequest
from models.anuncio import AnuncioModel, AnuncioDimensaoModel


DIMENSOES_PADRAO = [
    ("1200x628", 1200, 628, "gemini-3-pro-image-preview", "foto+logo"),
    ("1080x1080", 1080, 1080, "gemini-2.5-flash-image", "foto+logo"),
    ("300x600",  300,  600,  "gemini-2.5-flash-image", "so_logo"),
    ("300x250",  300,  250,  "gemini-2.5-flash-image", "so_logo"),
]

STATUS_VALIDOS = {"rascunho", "gerando", "completo", "parcial", "erro", "cancelado"}
ETAPAS_VALIDAS = {"topo", "meio", "fundo", "avulso"}
DIMENSOES_VALIDAS = {"1200x628", "1080x1080", "300x600", "300x250"}

LIMITE_HEADLINE = 30   # RN-002
LIMITE_DESCRICAO = 90  # RN-003


class AnuncioFactory:
    """Cria e atualiza AnuncioModel aplicando regras de negocio.

    Responsabilidades:
    - Criar anuncio novo com 4 dimensoes obrigatorias (RN-001)
    - Validar copy headline<=30, descricao<=90 (RN-002, RN-003)
    - Calcular status derivado (parcial/completo/erro) a partir das dimensoes (RN-019)
    - Validar transicoes de status
    - Preparar regeneracao de dimensao individual (RN-018)
    """

    # -------- Criacao --------
    @staticmethod
    def criar(dto: CriarAnuncioRequest, tenant_id: str, criado_por: str,
              pipeline_id: Optional[str] = None) -> AnuncioModel:
        """Cria AnuncioModel novo + 4 AnuncioDimensaoModel filhas.
        Status inicial: rascunho. Copy vazia (sera preenchida pelo Copywriter).
        """
        ...

    @staticmethod
    def _criar_dimensoes_padrao(anuncio_id) -> list[AnuncioDimensaoModel]:
        """Retorna 4 dimensoes com defaults da tabela em sec. 4.2."""
        ...

    # -------- Edicao de copy/metadados --------
    @staticmethod
    def aplicar_edicao(anuncio: AnuncioModel, dto: EditarAnuncioRequest) -> AnuncioModel:
        """Aplica campos do dto no anuncio. Valida 30/90 chars. Nao toca em dimensoes."""
        ...

    # -------- Regras de copy --------
    @staticmethod
    def validar_copy(headline: str, descricao: str) -> None:
        """Levanta ValueError se ultrapassar limites RN-002/RN-003. Chamada pelo pipeline apos Copywriter."""
        ...

    @staticmethod
    def aplicar_copy_do_pipeline(anuncio: AnuncioModel, headline: str, descricao: str) -> None:
        """Chamado pelo pipeline apos AP-2 aprovada."""
        ...

    # -------- Regras de status (derivado das dimensoes) --------
    @staticmethod
    def recalcular_status(anuncio: AnuncioModel) -> str:
        """Retorna status derivado do estado das 4 dimensoes.

        - Se todas as 4 tem brand_gate_status == 'valido' -> 'completo'
        - Se 1..3 validas e resto falhou apos 2 retries -> 'parcial'
        - Se todas 'nao_gerada' ou 'gerando' -> 'gerando'
        - Se todas falharam -> 'erro'
        """
        ...

    @staticmethod
    def dimensoes_ok_count(anuncio: AnuncioModel) -> int:
        """Conta dimensoes com brand_gate_status='valido'."""
        ...

    # -------- Regeneracao individual (RN-018) --------
    @staticmethod
    def preparar_regeneracao(anuncio: AnuncioModel, dto: RegenerarDimensaoRequest) -> list[AnuncioDimensaoModel]:
        """Marca dimensoes alvo como 'gerando', reseta retries. Retorna lista das dimensoes alteradas."""
        ...

    # -------- Transicao de status no pipeline --------
    @staticmethod
    def marcar_dimensao_gerada(dimensao: AnuncioDimensaoModel, imagem_url: str, modelo: str) -> None:
        """Chamado pelo image_generator apos gerar imagem. Atualiza url, modelo, timestamp."""
        ...

    @staticmethod
    def marcar_brand_gate(dimensao: AnuncioDimensaoModel, status: str, feedback: Optional[str] = None) -> None:
        """Atualiza brand_gate_status. Incrementa retries se 'revisao_manual' e retries<2.
        Marca 'falhou' se retries>=2 apos revisao_manual (RN-019).
        """
        ...

    # -------- Exclusao --------
    @staticmethod
    def preparar_soft_delete(anuncio: AnuncioModel) -> None:
        """Preenche deleted_at (RN-013). NAO apaga dimensoes -- cascateia via ORM se necessario."""
        ...

    # -------- Validadores auxiliares --------
    @staticmethod
    def _validar_etapa_funil(etapa: Optional[str]) -> Optional[str]:
        ...

    @staticmethod
    def _validar_status(status: str) -> None:
        ...

    @staticmethod
    def _validar_transicao_status(atual: str, novo: str) -> None:
        """Permite: rascunho->gerando, gerando->completo|parcial|erro,
        completo<->parcial (regeneracao), qualquer->cancelado."""
        ...
```

---

## 6. Mapper

```python
# mappers/anuncio_mapper.py
from models.anuncio import AnuncioModel, AnuncioDimensaoModel
from dtos.anuncio.base import AnuncioBase, DimensaoBase
from dtos.anuncio.criar_anuncio.response import CriarAnuncioResponse
from dtos.anuncio.listar_anuncios.response import AnuncioCardResponse, ListarAnunciosResponse
from dtos.anuncio.obter_anuncio.response import ObterAnuncioResponse
from dtos.anuncio.editar_anuncio.response import EditarAnuncioResponse
from dtos.anuncio.excluir_anuncio.response import ExcluirAnuncioResponse


class AnuncioMapper:
    """So converte. Nunca valida, nunca cria do zero."""

    # ---- Dimensao ----
    @staticmethod
    def dimensao_to_base(dim: AnuncioDimensaoModel) -> DimensaoBase:
        ...

    @staticmethod
    def dimensoes_to_base_list(dims: list[AnuncioDimensaoModel]) -> list[DimensaoBase]:
        ...

    # ---- Anuncio completo ----
    @staticmethod
    def to_base(anuncio: AnuncioModel) -> AnuncioBase:
        """Converte model + dimensoes hidratadas em AnuncioBase."""
        ...

    @staticmethod
    def to_obter_response(anuncio: AnuncioModel) -> ObterAnuncioResponse:
        ...

    @staticmethod
    def to_editar_response(anuncio: AnuncioModel) -> EditarAnuncioResponse:
        ...

    # ---- Criacao (resposta enxuta) ----
    @staticmethod
    def to_criar_response(anuncio: AnuncioModel) -> CriarAnuncioResponse:
        ...

    # ---- Listagem ----
    @staticmethod
    def to_card(anuncio: AnuncioModel) -> AnuncioCardResponse:
        """Thumbnail = dimensao 1080x1080 (ordem=1). Descricao truncada em 90."""
        ...

    @staticmethod
    def to_listar_response(anuncios: list[AnuncioModel], total: int, page: int, page_size: int) -> ListarAnunciosResponse:
        ...

    # ---- Exclusao ----
    @staticmethod
    def to_excluir_response(anuncio: AnuncioModel) -> ExcluirAnuncioResponse:
        ...
```

---

## 7. Service -- metodos com assinatura

Camada **opaca**. Nao acessa campos do DTO. Orquestra Factory + Mapper + Repository + servicos auxiliares.

```python
# services/anuncio_service.py
from typing import Optional

from fastapi import Depends, HTTPException

from data.connections.database import get_sql_session
from data.repositories.sql.anuncio_repository import AnuncioRepository
from data.repositories.sql.pipeline_repository import PipelineRepository
from factories.anuncio_factory import AnuncioFactory
from mappers.anuncio_mapper import AnuncioMapper

from dtos.anuncio.criar_anuncio.request import CriarAnuncioRequest
from dtos.anuncio.criar_anuncio.response import CriarAnuncioResponse
from dtos.anuncio.listar_anuncios.request import ListarAnunciosRequest
from dtos.anuncio.listar_anuncios.response import ListarAnunciosResponse
from dtos.anuncio.obter_anuncio.response import ObterAnuncioResponse
from dtos.anuncio.editar_anuncio.request import EditarAnuncioRequest
from dtos.anuncio.editar_anuncio.response import EditarAnuncioResponse
from dtos.anuncio.excluir_anuncio.response import ExcluirAnuncioResponse
from dtos.anuncio.regenerar_dimensao.request import RegenerarDimensaoRequest
from dtos.anuncio.regenerar_dimensao.response import RegenerarDimensaoResponse
from dtos.anuncio.exportar_anuncio.request import ExportarAnuncioRequest
from dtos.anuncio.exportar_anuncio.response import ExportarAnuncioResponse

from services.anuncio_pipeline_service import AnuncioPipelineService
from services.anuncio_export_service import AnuncioExportService


class AnuncioService:
    """Camada opaca. Nao acessa campos do DTO nem do Model. So delega."""

    def __init__(self, session=Depends(get_sql_session)):
        self.repo = AnuncioRepository(session)
        self.pipeline_repo = PipelineRepository(session)

    # ---- CriarAnuncio ----
    async def criar(self, dto: CriarAnuncioRequest, tenant_id: str, criado_por: str) -> CriarAnuncioResponse:
        """
        Fluxo:
        1. AnuncioPipelineService.iniciar_pipeline_anuncio() -> cria pipeline (formato=anuncio)
        2. AnuncioFactory.criar() cria AnuncioModel + 4 dimensoes default
        3. Repository.create()
        4. AnuncioMapper.to_criar_response()
        """
        ...

    # ---- ListarAnuncios ----
    async def listar(self, dto: ListarAnunciosRequest, tenant_id: str) -> ListarAnunciosResponse:
        """Delega filtros pro repository e mapeia resultado."""
        ...

    # ---- ObterAnuncio ----
    async def obter(self, anuncio_id: str, tenant_id: str) -> ObterAnuncioResponse:
        """Retorna 404 se nao encontrado ou deleted_at preenchido (exceto se caller incluir_excluidos)."""
        ...

    # ---- EditarAnuncio ----
    async def editar(self, anuncio_id: str, dto: EditarAnuncioRequest, tenant_id: str) -> EditarAnuncioResponse:
        """NAO regenera imagens. So persiste copy/metadados via Factory.aplicar_edicao."""
        ...

    # ---- ExcluirAnuncio (soft delete, RN-013) ----
    async def excluir(self, anuncio_id: str, tenant_id: str) -> ExcluirAnuncioResponse:
        """Soft delete via Factory.preparar_soft_delete + repo.soft_delete."""
        ...

    # ---- RegenerarDimensao (RN-018) ----
    async def regenerar_dimensao(
        self, anuncio_id: str, dto: RegenerarDimensaoRequest, tenant_id: str,
    ) -> RegenerarDimensaoResponse:
        """
        Fluxo:
        1. Carrega anuncio + dimensoes
        2. AnuncioFactory.preparar_regeneracao() -> marca dimensoes alvo como 'gerando', reseta retries
        3. AnuncioPipelineService.disparar_regeneracao(anuncio, dimensoes_alvo, feedback) ->
           executa image_generator + brand_gate APENAS para as dimensoes alvo
        4. Retorna RegenerarDimensaoResponse com lista das dimensoes em processamento
        """
        ...

    # ---- ExportarAnuncio (RN-007, RN-008, DT-A03) ----
    async def exportar(
        self, anuncio_id: str, dto: ExportarAnuncioRequest, tenant_id: str,
    ) -> ExportarAnuncioResponse:
        """
        Delega para AnuncioExportService.
        - destino=zip: AnuncioExportService.build_zip() -> base64
        - destino=drive: AnuncioExportService.salvar_drive() -> drive_folder_link
        Atualiza anuncio.drive_folder_link via Factory/repo.update.
        """
        ...
```

### 7.1 AnuncioPipelineService -- cola com o pipeline existente

```python
# services/anuncio_pipeline_service.py
from typing import Optional
from models.anuncio import AnuncioModel
from models.pipeline import PipelineModel


class AnuncioPipelineService:
    """Integra o dominio Anuncio com o pipeline de 6 agentes ja existente.
    NAO e um pipeline novo -- e cola.
    """

    def __init__(self, session):
        self.session = session

    async def iniciar_pipeline_anuncio(
        self,
        tema: str,
        modo_entrada: str,
        disciplina: Optional[str],
        tecnologia: Optional[str],
        foto_criador_id: Optional[str],
        etapa_funil: Optional[str],
        pipeline_funil_id: Optional[str],
        tenant_id: str,
        criado_por: str,
    ) -> PipelineModel:
        """Chama PipelineService existente com formato='anuncio'."""
        ...

    async def disparar_regeneracao(
        self,
        anuncio: AnuncioModel,
        dimensoes_alvo: list[str],
        feedback_livre: Optional[str],
    ) -> None:
        """
        Roda image_generator + brand_gate para dimensoes alvo (paralelo).
        Persistencia de resultado: marcar_dimensao_gerada + marcar_brand_gate via Factory.
        Apos cada batch, recalcula status do anuncio (Factory.recalcular_status).
        """
        ...

    async def aplicar_copy_do_pipeline(
        self,
        anuncio_id: str,
        headline: str,
        descricao: str,
        tenant_id: str,
    ) -> None:
        """Chamado pelo Copywriter apos AP-2 aprovada. Valida 30/90 via Factory.validar_copy."""
        ...
```

### 7.2 AnuncioExportService -- ZIP e Drive

```python
# services/anuncio_export_service.py
import base64
import io
import zipfile
from typing import Optional

from models.anuncio import AnuncioModel
from services.drive_service import salvar_anuncio_drive  # nova funcao em drive_service


class AnuncioExportService:
    """RN-007, RN-008, DT-A03: pacote 4 PNGs + copy.txt.
    Em status parcial, exporta so as dimensoes 'valido' e inclui nota no copy.txt.
    """

    @staticmethod
    def montar_copy_txt(anuncio: AnuncioModel, dimensoes_incluidas: int) -> str:
        """
        Conteudo:
            HEADLINE (ate 30 chars):
            <headline>

            DESCRICAO (ate 90 chars):
            <descricao>

            {se parcial: NOTA: 3 de 4 dimensoes -- gere a faltante antes de publicar}
        """
        ...

    @staticmethod
    async def build_zip(anuncio: AnuncioModel) -> tuple[str, list[str], int, Optional[str]]:
        """
        Retorna: (zip_base64, arquivos_incluidos, dimensoes_incluidas, warning).
        Nome dos arquivos: ad-1200x628.png, ad-1080x1080.png, ad-300x600.png, ad-300x250.png, copy.txt.
        Soh inclui dimensoes com brand_gate_status='valido' (RN-019, DT-A03).
        """
        ...

    @staticmethod
    async def salvar_drive(
        anuncio: AnuncioModel,
        parent_folder_id: str,
        credentials_json: str,
    ) -> tuple[str, str, list[str], int, Optional[str]]:
        """
        Retorna: (drive_folder_id, drive_folder_link, arquivos, dimensoes_incluidas, warning).
        Delega para drive_service.salvar_anuncio_drive (sec. 9.2).
        """
        ...
```

---

## 8. Router -- endpoints

```python
# routers/anuncio.py
from fastapi import APIRouter, Depends, Query, HTTPException

from middleware.auth import get_current_user, CurrentUser, require_role
from services.anuncio_service import AnuncioService

from dtos.anuncio.criar_anuncio.request import CriarAnuncioRequest
from dtos.anuncio.criar_anuncio.response import CriarAnuncioResponse
from dtos.anuncio.listar_anuncios.request import ListarAnunciosRequest
from dtos.anuncio.listar_anuncios.response import ListarAnunciosResponse
from dtos.anuncio.obter_anuncio.response import ObterAnuncioResponse
from dtos.anuncio.editar_anuncio.request import EditarAnuncioRequest
from dtos.anuncio.editar_anuncio.response import EditarAnuncioResponse
from dtos.anuncio.excluir_anuncio.response import ExcluirAnuncioResponse
from dtos.anuncio.regenerar_dimensao.request import RegenerarDimensaoRequest
from dtos.anuncio.regenerar_dimensao.response import RegenerarDimensaoResponse
from dtos.anuncio.exportar_anuncio.request import ExportarAnuncioRequest
from dtos.anuncio.exportar_anuncio.response import ExportarAnuncioResponse


router = APIRouter(prefix="/anuncios", tags=["Anuncios"])


@router.post("", response_model=CriarAnuncioResponse, status_code=201)
async def criar_anuncio(
    dto: CriarAnuncioRequest,
    current_user: CurrentUser = Depends(require_role("admin", "copywriter", "designer")),
    service: AnuncioService = Depends(),
):
    return await service.criar(dto, current_user.tenant_id, current_user.user_id)


@router.get("", response_model=ListarAnunciosResponse)
async def listar_anuncios(
    filtros: ListarAnunciosRequest = Depends(),
    current_user: CurrentUser = Depends(get_current_user),
    service: AnuncioService = Depends(),
):
    return await service.listar(filtros, current_user.tenant_id)


@router.get("/{anuncio_id}", response_model=ObterAnuncioResponse)
async def obter_anuncio(
    anuncio_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    service: AnuncioService = Depends(),
):
    return await service.obter(anuncio_id, current_user.tenant_id)


@router.put("/{anuncio_id}", response_model=EditarAnuncioResponse)
async def editar_anuncio(
    anuncio_id: str,
    dto: EditarAnuncioRequest,
    current_user: CurrentUser = Depends(require_role("admin", "copywriter", "designer")),
    service: AnuncioService = Depends(),
):
    return await service.editar(anuncio_id, dto, current_user.tenant_id)


@router.delete("/{anuncio_id}", response_model=ExcluirAnuncioResponse)
async def excluir_anuncio(
    anuncio_id: str,
    current_user: CurrentUser = Depends(require_role("admin", "copywriter", "designer")),
    service: AnuncioService = Depends(),
):
    return await service.excluir(anuncio_id, current_user.tenant_id)


@router.post("/{anuncio_id}/regenerar-dimensao", response_model=RegenerarDimensaoResponse)
async def regenerar_dimensao(
    anuncio_id: str,
    dto: RegenerarDimensaoRequest,
    current_user: CurrentUser = Depends(require_role("admin", "copywriter", "designer")),
    service: AnuncioService = Depends(),
):
    return await service.regenerar_dimensao(anuncio_id, dto, current_user.tenant_id)


@router.post("/{anuncio_id}/exportar", response_model=ExportarAnuncioResponse)
async def exportar_anuncio(
    anuncio_id: str,
    dto: ExportarAnuncioRequest,
    current_user: CurrentUser = Depends(require_role("admin", "copywriter", "designer")),
    service: AnuncioService = Depends(),
):
    return await service.exportar(anuncio_id, dto, current_user.tenant_id)
```

### 8.1 Tabela de endpoints

| Metodo | Rota | Auth | Perfis | Descricao |
|--------|------|------|--------|-----------|
| POST | `/api/anuncios` | JWT | admin, copywriter, designer | Cria anuncio + dispara pipeline com formato=anuncio. Retorna pipeline_id. |
| GET | `/api/anuncios` | JWT | todos | Lista anuncios do tenant com filtros (busca, status, etapa_funil, data, incluir_excluidos, page, page_size). |
| GET | `/api/anuncios/{id}` | JWT | todos | Detalhe do anuncio + 4 dimensoes hidratadas. 404 se soft deleted e nao for admin. |
| PUT | `/api/anuncios/{id}` | JWT | admin, copywriter, designer | Edita copy (headline<=30, descricao<=90), titulo, etapa_funil. NAO regenera imagens. |
| DELETE | `/api/anuncios/{id}` | JWT | admin, copywriter, designer | Soft delete (RN-013). Preenche deleted_at. Arquivos Drive permanecem. |
| POST | `/api/anuncios/{id}/regenerar-dimensao` | JWT | admin, copywriter, designer | Regenera 1+ dimensoes individualmente (RN-018). Mantem as demais intactas. |
| POST | `/api/anuncios/{id}/exportar` | JWT | admin, copywriter, designer | Gera ZIP local (destino=zip) ou salva Drive (destino=drive). Respeita status parcial (DT-A03). |

---

## 9. Integracoes com pipeline, Drive, Brand Gate

### 9.1 Pipeline existente -- arquivos a tocar

| Arquivo | Mudanca |
|---------|---------|
| `configs/formatos.json` | Adicionar objeto `formato=anuncio` completo (vide sec. 10.2). |
| `configs/dimensions.json` | Mudar valor de `"anuncio"` (hoje objeto unico) para array das 4 dimensoes (RN-011). |
| `configs/platform_rules.json` | Adicionar plataforma "Google Ads Display" com headline_max=30, descricao_max=90. |
| `configs/templates.json` | Adicionar templates por dimensao do formato anuncio (dark mode premium + 4 aspect ratios). |
| `services/prompt_templates.py` | Adicionar funcao `build_anuncio_prompt(dimensao, tema, copy, brand_palette)` que gera prompt Gemini especifico por dimensao. |
| `services/imagem_service.py` | `_select_model(formato, dimensao)` -- se formato=anuncio, retorna Pro para dimensao="1200x628" e Flash nas outras (RN-015). |
| `agents/copywriter.py` | Se formato=anuncio, passar ao Claude system prompt dizendo "headline max 30, descricao max 90" e validar saida; se passar, regerar (RN-002, RN-003). |
| `agents/art_director.py` | Se formato=anuncio, gerar 1 prompt base + 4 adaptacoes de aspect ratio (nao gerar prompts totalmente diferentes -- mesma ideia visual, so muda composicao). |
| `agents/image_generator.py` | Se formato=anuncio, executar 4 chamadas Gemini em paralelo (asyncio.gather), 1 por dimensao, modelo selecionado via `_select_model`. Persistir resultado na `AnuncioDimensaoModel` de cada dimensao. |

### 9.2 Drive -- novo metodo em `services/drive_service.py`

```python
# services/drive_service.py (acrescimo)

async def salvar_anuncio_drive(
    credentials_json: str,
    parent_folder_id: str,
    title: str,
    data_str: str,           # YYYY-MM-DD (RN-008)
    dimensoes: list[dict],   # [{nome_arquivo, imagem_base64}, ...] -- apenas dimensoes 'valido'
    copy_txt_content: str,   # gerado pelo AnuncioExportService.montar_copy_txt
) -> dict:
    """Cria subpasta '{title} - {data_str}' e faz upload de:
       - ad-1200x628.png, ad-1080x1080.png, ad-300x600.png, ad-300x250.png (soh as 'valido')
       - copy.txt
    Retorna { folder_id, folder_link, files: [{name, file_id, web_view_link}] }.
    """
    ...
```

Reaproveita `_build_service`, `_create_folder_sync`, `_upload_bytes_sync` ja existentes. Scope permanece `https://www.googleapis.com/auth/drive`.

### 9.3 Brand Gate -- adaptacao por aspect ratio

`skills/brand_validator.py` ja valida imagem 1 a 1. Adicionar parametro `aspect_ratio` (ou `dimensao_id`):

```python
# skills/brand_validator.py (assinatura nova)
def validate(
    image_base64: str,
    brand_palette: dict,
    aspect_ratio: str = "portrait",       # portrait | landscape | square | small_landscape
    exige_foto_criador: bool = True,       # False quando dimensao e 300x600 ou 300x250 (RN-016, RN-020)
    exige_logo: bool = True,
) -> dict:
    """Aplica regras de cores, tipografia, contraste.
    Desativa check de foto se exige_foto_criador=False.
    Retorna {status, feedback, retries_sugeridos}.
    """
    ...
```

### 9.4 Brand Overlay -- adaptacao por dimensao

`skills/brand_overlay.py` recebe dimensao e decide se aplica foto ou so logo:

```python
# skills/brand_overlay.py (assinatura nova)
def apply_overlay(
    image_base64: str,
    foto_criador_url: Optional[str],
    logo_path: str,
    dimensao_id: str,           # "1200x628" | "1080x1080" | "300x600" | "300x250"
) -> str:
    """Se dimensao_id in ('300x600', '300x250'): aplica SO logo (canto inferior direito).
       Caso contrario: foto redonda + logo (RN-016).
    Retorna imagem base64 final."""
    ...
```

---

## 10. Migrations SQL sugeridas

### 10.1 Schema MSSQL

```sql
-- SCHEMA carrossel ja existe. Tabela anuncio + anuncio_dimensao.

CREATE TABLE carrossel.anuncio (
    id                  UNIQUEIDENTIFIER    NOT NULL PRIMARY KEY,
    tenant_id           VARCHAR(50)         NOT NULL,
    pipeline_id         UNIQUEIDENTIFIER    NULL,
    pipeline_funil_id   UNIQUEIDENTIFIER    NULL,
    titulo              VARCHAR(200)        NOT NULL,
    etapa_funil         VARCHAR(20)         NULL,
    tema_ou_briefing    NVARCHAR(MAX)       NULL,
    modo_entrada        VARCHAR(20)         NULL,
    disciplina          VARCHAR(50)         NULL,
    tecnologia          VARCHAR(100)        NULL,
    foto_criador_id     VARCHAR(100)        NULL,
    criado_por          VARCHAR(100)        NULL,
    headline            VARCHAR(30)         NULL,
    descricao           VARCHAR(90)         NULL,
    status              VARCHAR(20)         NOT NULL DEFAULT 'rascunho',
    drive_folder_id     VARCHAR(100)        NULL,
    drive_folder_link   NVARCHAR(MAX)       NULL,
    last_exported_at    DATETIME2           NULL,
    created_at          DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at          DATETIME2           NULL,
    deleted_at          DATETIME2           NULL,
    CONSTRAINT FK_anuncio_pipeline FOREIGN KEY (pipeline_id) REFERENCES carrossel.pipeline(id)
);

CREATE INDEX ix_anuncio_tenant_id       ON carrossel.anuncio (tenant_id);
CREATE INDEX ix_anuncio_tenant_status   ON carrossel.anuncio (tenant_id, status);
CREATE INDEX ix_anuncio_tenant_pipeline ON carrossel.anuncio (tenant_id, pipeline_id);
CREATE INDEX ix_anuncio_deleted_at      ON carrossel.anuncio (deleted_at) WHERE deleted_at IS NULL;


CREATE TABLE carrossel.anuncio_dimensao (
    id                      UNIQUEIDENTIFIER    NOT NULL PRIMARY KEY,
    anuncio_id              UNIQUEIDENTIFIER    NOT NULL,
    dimensao_id             VARCHAR(20)         NOT NULL,   -- "1200x628" etc.
    ordem                   INT                 NOT NULL,    -- 0..3
    largura                 INT                 NOT NULL,
    altura                  INT                 NOT NULL,
    modelo_usado            VARCHAR(50)         NULL,
    overlay_aplicado        VARCHAR(20)         NOT NULL DEFAULT 'foto+logo',
    imagem_url              NVARCHAR(MAX)       NULL,
    imagem_base64           NVARCHAR(MAX)       NULL,
    brand_gate_status       VARCHAR(20)         NOT NULL DEFAULT 'nao_gerada',
    brand_gate_retries      INT                 NOT NULL DEFAULT 0,
    brand_gate_feedback     NVARCHAR(MAX)       NULL,
    created_at              DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
    gerada_em               DATETIME2           NULL,
    updated_at              DATETIME2           NULL,
    CONSTRAINT FK_anuncio_dim_anuncio FOREIGN KEY (anuncio_id)
        REFERENCES carrossel.anuncio(id) ON DELETE CASCADE
);

CREATE INDEX ix_anuncio_dim_anuncio_dim ON carrossel.anuncio_dimensao (anuncio_id, dimensao_id);
CREATE UNIQUE INDEX uq_anuncio_dim_anuncio_ordem ON carrossel.anuncio_dimensao (anuncio_id, ordem);
```

### 10.2 Seeds de configuracoes

**`configs/dimensions.json`** (modificar formato `anuncio` para array):
```json
{
  "carrossel": { "width": 1080, "height": 1350 },
  "post_unico": { "width": 1080, "height": 1350 },
  "capa_reels": { "width": 1080, "height": 1920 },
  "thumbnail_youtube": { "width": 1280, "height": 720 },
  "anuncio": [
    { "dimensao_id": "1200x628",  "width": 1200, "height": 628,  "ratio": "landscape",        "ordem": 0 },
    { "dimensao_id": "1080x1080", "width": 1080, "height": 1080, "ratio": "square",           "ordem": 1 },
    { "dimensao_id": "300x600",   "width": 300,  "height": 600,  "ratio": "half_page",        "ordem": 2 },
    { "dimensao_id": "300x250",   "width": 300,  "height": 250,  "ratio": "medium_rectangle", "ordem": 3 }
  ]
}
```

**`configs/platform_rules.json`** (acrescimo):
```json
{
  "nome": "Google Ads Display",
  "max_caracteres": 120,
  "hashtags_max": 0,
  "headline_max": 30,
  "descricao_max": 90,
  "specs": "4 dimensoes obrigatorias: 1200x628, 1080x1080, 300x600, 300x250. Headline ate 30 chars. Descricao ate 90 chars."
}
```

**`configs/formatos.json`** (acrescimo):
```json
{
  "id": "anuncio",
  "nome": "Anuncio Google Ads",
  "multi_dimensao": true,
  "dimensoes": [
    {"dimensao_id": "1200x628",  "width": 1200, "height": 628,  "ratio": "landscape",        "overlay": "foto+logo", "modelo": "gemini-3-pro-image-preview"},
    {"dimensao_id": "1080x1080", "width": 1080, "height": 1080, "ratio": "square",           "overlay": "foto+logo", "modelo": "gemini-2.5-flash-image"},
    {"dimensao_id": "300x600",   "width": 300,  "height": 600,  "ratio": "half_page",        "overlay": "so_logo",   "modelo": "gemini-2.5-flash-image"},
    {"dimensao_id": "300x250",   "width": 300,  "height": 250,  "ratio": "medium_rectangle", "overlay": "so_logo",   "modelo": "gemini-2.5-flash-image"}
  ],
  "layout_rules": [
    "Mesma identidade visual dark mode premium dos demais formatos.",
    "Composicao adaptada por aspect ratio, mantendo a mesma ideia visual.",
    "Copy NAO e impressa na imagem -- copy vai no copy.txt separado."
  ],
  "copy_rules": {
    "headline_max": 30,
    "descricao_max": 90,
    "copy_unica_por_anuncio": true
  },
  "tem_rodape": false,
  "tem_paginacao": false,
  "ativo": true
}
```

---

## 11. Codigo-base por modulo (esqueletos)

### 11.1 Repository

```python
# data/repositories/sql/anuncio_repository.py
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from data.repositories.sql.base_sql_repository import BaseSQLRepository
from models.anuncio import AnuncioModel, AnuncioDimensaoModel


class AnuncioRepository(BaseSQLRepository[AnuncioModel]):

    def __init__(self, session):
        super().__init__(session, AnuncioModel)

    async def get_by_id(self, id: str, tenant_id: str) -> Optional[AnuncioModel]:
        """Hidrata dimensoes via selectinload."""
        result = await self._session.execute(
            select(AnuncioModel)
            .options(selectinload(AnuncioModel.dimensoes))
            .where(
                AnuncioModel.id == id,
                AnuncioModel.tenant_id == tenant_id,
                AnuncioModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_incluindo_excluidos(self, id: str, tenant_id: str) -> Optional[AnuncioModel]:
        """Usado em admin views para mostrar soft deleted."""
        ...

    async def list_paginado(
        self, tenant_id: str, filters: dict, page: int, page_size: int,
    ) -> tuple[list[AnuncioModel], int]:
        """Retorna (items, total). Aplica filtros: busca, status, etapa_funil, data_inicio, data_fim, incluir_excluidos."""
        ...

    async def buscar_dimensao(
        self, anuncio_id: str, dimensao_id: str, tenant_id: str,
    ) -> Optional[AnuncioDimensaoModel]:
        """Busca 1 dimensao especifica (usado em regeneracao individual)."""
        ...

    async def atualizar_dimensao(self, dimensao: AnuncioDimensaoModel) -> AnuncioDimensaoModel:
        """Flush simples -- commit e responsabilidade do database.py."""
        ...
```

### 11.2 Registro no `main.py`

```python
# main.py (diff)
from routers import (
    conteudo, imagem, drive, config, agentes, historico, pipeline,
    foto_overlay, visual_preference, design_system, prompt_layer,
    auth, kanban_board, kanban_card, kanban_comment, kanban_notification,
    tenant,
    anuncio,   # NOVO
)
# ...
app.include_router(anuncio.router, prefix="/api")
```

### 11.3 Factory (esqueleto detalhado)

```python
# factories/anuncio_factory.py  (esqueleto completo com metodos)
from datetime import datetime, timezone
import uuid
from typing import Optional

from dtos.anuncio.criar_anuncio.request import CriarAnuncioRequest
from dtos.anuncio.editar_anuncio.request import EditarAnuncioRequest
from dtos.anuncio.regenerar_dimensao.request import RegenerarDimensaoRequest
from models.anuncio import AnuncioModel, AnuncioDimensaoModel


DIMENSOES_PADRAO = [
    ("1200x628",  1200, 628,  0, "gemini-3-pro-image-preview", "foto+logo"),
    ("1080x1080", 1080, 1080, 1, "gemini-2.5-flash-image",     "foto+logo"),
    ("300x600",   300,  600,  2, "gemini-2.5-flash-image",     "so_logo"),
    ("300x250",   300,  250,  3, "gemini-2.5-flash-image",     "so_logo"),
]

STATUS_VALIDOS = {"rascunho", "gerando", "completo", "parcial", "erro", "cancelado"}
ETAPAS_VALIDAS = {"topo", "meio", "fundo", "avulso"}
DIMENSOES_VALIDAS = {"1200x628", "1080x1080", "300x600", "300x250"}

LIMITE_HEADLINE = 30
LIMITE_DESCRICAO = 90


class AnuncioFactory:

    @staticmethod
    def criar(
        dto: CriarAnuncioRequest,
        tenant_id: str,
        criado_por: str,
        pipeline_id: Optional[str] = None,
    ) -> AnuncioModel:
        """Cria AnuncioModel com 4 AnuncioDimensaoModel filhas. Status='rascunho'."""
        etapa = AnuncioFactory._validar_etapa_funil(dto.etapa_funil)
        anuncio = AnuncioModel(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            pipeline_id=pipeline_id,
            pipeline_funil_id=dto.pipeline_funil_id,
            titulo=dto.titulo.strip(),
            etapa_funil=etapa,
            tema_ou_briefing=dto.tema_ou_briefing,
            modo_entrada=dto.modo_entrada,
            disciplina=dto.disciplina,
            tecnologia=dto.tecnologia,
            foto_criador_id=dto.foto_criador_id,
            criado_por=criado_por,
            status="rascunho",
            created_at=datetime.now(timezone.utc),
        )
        anuncio.dimensoes = AnuncioFactory._criar_dimensoes_padrao()
        return anuncio

    @staticmethod
    def _criar_dimensoes_padrao() -> list[AnuncioDimensaoModel]:
        ...  # itera DIMENSOES_PADRAO e retorna lista de AnuncioDimensaoModel

    @staticmethod
    def aplicar_edicao(anuncio: AnuncioModel, dto: EditarAnuncioRequest) -> AnuncioModel:
        ...  # aplica campos nao-None, valida copy se presente, atualiza updated_at

    @staticmethod
    def validar_copy(headline: str, descricao: str) -> None:
        if len(headline) > LIMITE_HEADLINE:
            raise ValueError(f"Headline excede {LIMITE_HEADLINE} caracteres")
        if len(descricao) > LIMITE_DESCRICAO:
            raise ValueError(f"Descricao excede {LIMITE_DESCRICAO} caracteres")
        if not headline.strip():
            raise ValueError("Headline obrigatoria")
        if not descricao.strip():
            raise ValueError("Descricao obrigatoria")

    @staticmethod
    def aplicar_copy_do_pipeline(anuncio: AnuncioModel, headline: str, descricao: str) -> None:
        AnuncioFactory.validar_copy(headline, descricao)
        anuncio.headline = headline
        anuncio.descricao = descricao
        anuncio.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def recalcular_status(anuncio: AnuncioModel) -> str:
        ok = sum(1 for d in anuncio.dimensoes if d.brand_gate_status == "valido")
        gerando = any(d.brand_gate_status in {"nao_gerada", "gerando"} for d in anuncio.dimensoes)
        if ok == 4:
            novo = "completo"
        elif gerando:
            novo = "gerando"
        elif ok == 0:
            novo = "erro"
        else:
            novo = "parcial"
        AnuncioFactory._validar_transicao_status(anuncio.status, novo)
        anuncio.status = novo
        anuncio.updated_at = datetime.now(timezone.utc)
        return novo

    @staticmethod
    def dimensoes_ok_count(anuncio: AnuncioModel) -> int:
        return sum(1 for d in anuncio.dimensoes if d.brand_gate_status == "valido")

    @staticmethod
    def preparar_regeneracao(
        anuncio: AnuncioModel,
        dto: RegenerarDimensaoRequest,
    ) -> list[AnuncioDimensaoModel]:
        alvo = set(dto.dimensoes_alvo)
        alteradas: list[AnuncioDimensaoModel] = []
        for d in anuncio.dimensoes:
            if d.dimensao_id in alvo:
                d.brand_gate_status = "gerando"
                d.brand_gate_retries = 0
                d.brand_gate_feedback = None
                d.updated_at = datetime.now(timezone.utc)
                alteradas.append(d)
        if not alteradas:
            raise ValueError("Nenhuma dimensao alvo encontrada")
        anuncio.status = "gerando"
        return alteradas

    @staticmethod
    def marcar_dimensao_gerada(
        dimensao: AnuncioDimensaoModel, imagem_url: str, modelo: str,
    ) -> None:
        dimensao.imagem_url = imagem_url
        dimensao.modelo_usado = modelo
        dimensao.gerada_em = datetime.now(timezone.utc)
        dimensao.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def marcar_brand_gate(
        dimensao: AnuncioDimensaoModel, status: str, feedback: Optional[str] = None,
    ) -> None:
        if status == "revisao_manual":
            dimensao.brand_gate_retries += 1
            if dimensao.brand_gate_retries >= 2:
                dimensao.brand_gate_status = "falhou"  # RN-019
            else:
                dimensao.brand_gate_status = "revisao_manual"
        elif status in {"valido", "falhou", "nao_gerada", "gerando"}:
            dimensao.brand_gate_status = status
        else:
            raise ValueError(f"Status brand gate invalido: {status}")
        dimensao.brand_gate_feedback = feedback
        dimensao.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def preparar_soft_delete(anuncio: AnuncioModel) -> None:
        anuncio.deleted_at = datetime.now(timezone.utc)
        if anuncio.status != "cancelado":
            anuncio.status = "cancelado"

    @staticmethod
    def _validar_etapa_funil(etapa: Optional[str]) -> Optional[str]:
        if etapa is None:
            return "avulso"
        if etapa not in ETAPAS_VALIDAS:
            raise ValueError(f"Etapa funil invalida: {etapa}")
        return etapa

    @staticmethod
    def _validar_status(status: str) -> None:
        if status not in STATUS_VALIDOS:
            raise ValueError(f"Status invalido: {status}")

    @staticmethod
    def _validar_transicao_status(atual: str, novo: str) -> None:
        """Permite transicoes validas.
        rascunho -> gerando, erro, cancelado
        gerando -> completo, parcial, erro, cancelado, gerando (regeneracao)
        completo -> gerando (regeneracao), parcial (regeneracao que falha), cancelado
        parcial -> gerando, completo, erro, cancelado
        erro -> gerando, cancelado
        cancelado -> (terminal)
        """
        ...
```

---

## 12. Duvidas tecnicas novas

Nenhum bloqueio arquitetural novo identificado. O PRD e as telas ja resolveram as 10 decisoes confirmadas pela cliente + 6 DT-A tecnicas. As decisoes abaixo foram assumidas de forma explicita nesta arquitetura e podem ser validadas pelo Agente 08 (P.O.) antes do Dev Backend comecar:

| ID | Decisao assumida | Justificativa | Impacto se reverter |
|----|------------------|---------------|---------------------|
| AR-01 | Modelo de dados: **2 tabelas** (`anuncio` + `anuncio_dimensao`) ao inves de campo JSON `image_urls[]` numa tabela so. | Permite regeneracao individual (RN-018), contagem por query, entrega parcial (RN-019) e historico de Brand Gate por dimensao sem precisar ler/reescrever JSON. | Se decidir-se por 1 tabela + JSON, simplificar factory e mapper; perde-se query facil de "dimensoes validas". |
| AR-02 | Criar um **service dedicado** `AnuncioPipelineService` para integracao com pipeline existente, ao inves de acoplar logica em `PipelineService`. | Mantem `PipelineService` generico. Anuncio tem comportamento especifico (4 dimensoes em paralelo + regeneracao individual) que justifica isolamento. | Se preferir, mover logica pra `PipelineService._executar_formato_anuncio()` (menor isolamento). |
| AR-03 | Endpoint de regeneracao dedicado: `POST /api/anuncios/{id}/regenerar-dimensao`. | Semantica CRUD fica limpa (PUT edita copy; POST /regenerar-dimensao e acao especifica). Alternativa seria sobrecarregar PUT com campo `regenerar_dimensoes=[...]` -- mais acoplado. | Se preferir 1 endpoint so, mover logica pro PUT e diferenciar via flag no body. |
| AR-04 | Export em endpoint **dedicado** `POST /api/anuncios/{id}/exportar` com body `{ destino: "zip"|"drive" }`. | ZIP e base64 inline (evita download com Auth), Drive e chamada async para Drive API. Unificar facilita manutencao. | Se a cliente preferir 2 endpoints (`/exportar/zip`, `/exportar/drive`), trivial separar. |
| AR-05 | **Foto do criador** e referenciada por `foto_criador_id` (string). No MVP esse id aponta para arquivos ja existentes no store `fotoCriador` do frontend. | Mantem consistencia com fluxo ja em uso nos outros formatos. | Se foto vier como upload direto, adicionar endpoint de upload separado (fora desta arquitetura). |
| AR-06 | Historico **nao ganha tabela propria** -- view SQL/consulta que une `conteudo` (legado), `pipeline`, `anuncio` via `formato`. | Consistente com RN-014 (historico unificado). | Se performance virar gargalo, criar view materializada. |
| AR-07 | Editar copy **nao** cria "version history" no MVP. Alteracao sobrescreve registro. | RN nao pede versionamento. | Se precisar auditoria, adicionar tabela `anuncio_copy_history` fora do MVP. |

---

*Documento produzido pelo Agente 03 (Arquiteto IT Valley Backend).*
*Pronto para o Agente 10 (Dev Backend) implementar caso de uso por caso de uso.*
*Ordem sugerida de desenvolvimento:*
1. *Migrations SQL + models + repository (fundacao)*
2. *DTOs + Factory + Mapper*
3. *Service (opaca) + Router (CRUD basico sem pipeline)*
4. *AnuncioPipelineService + ajustes em copywriter/art_director/image_generator*
5. *AnuncioExportService + salvar_anuncio_drive*
6. *Regeneracao individual (RN-018)*
7. *Testes unitarios em Factory (regras), Mapper (conversao) e Repository (queries)*
