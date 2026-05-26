# ARQUITETURA BACKEND -- Content Factory v3

Documento de arquitetura backend gerado pelo Agente 03 (Arquiteto IT Valley Backend).
Base: PRD Content Factory v3 + TELAS.md + codigo backend existente.

---

## 1. Visao Geral da Refatoracao

O backend existente funciona mas nao segue a arquitetura IT Valley completa. A refatoracao preserva o que existe e adiciona as camadas ausentes.

### O que existe hoje

| Camada | Status | Observacao |
|--------|--------|------------|
| `main.py` | Existe | Registra routers com prefix `/api` |
| `routers/` | Existe | conteudo, imagem, drive, config, agentes, historico |
| `services/` | Existe | conteudo_service, imagem_service, drive_service, db_service |
| `factories/` | Existe | conteudo_factory, imagem_factory, config_factory |
| `mappers/` | Existe | conteudo_mapper, imagem_mapper, drive_mapper |
| `dtos/` | Existe | Por caso de uso (conteudo, imagem, drive, config) |
| `models/` | NAO existe | db_service usa pymssql direto sem SQLAlchemy |
| `data/` | NAO existe | Sem camada de repositorio, sem interfaces |

### O que muda na v3

1. **Novos dominios:** Pipeline, Agente, Skill, Score, VisualPreference, CreatorEntry
2. **Refatoracao dos existentes:** Conteudo, Imagem, Drive, Config, Historico
3. **Camada data completa:** interfaces + repositories + connections (SQLAlchemy async)
4. **Camada models:** SQLAlchemy models para todas as entidades
5. **Pipeline como orquestrador:** Novo dominio central que coordena agentes e skills

### O que NAO muda

- Posicao dos arquivos (tudo na raiz de `backend/`, sem pasta `app/`)
- Prefix `/api` nos routers
- Logica de geracao de conteudo via Claude API/CLI (sera encapsulada no agente Copywriter)
- Logica de geracao de imagem via Gemini (sera encapsulada no agente Image Generator)
- Integracao Google Drive (permanece como esta, refatorada para usar repository)

---

## 2. Dominios Identificados

| Dominio | Descricao | Fonte (PRD) | Status |
|---------|-----------|-------------|--------|
| Pipeline | Orquestra execucao do pipeline de agentes | Modulo Pipeline | Novo |
| Conteudo | Conteudo final gerado (texto + metadados) | Modulo Conteudo | Refatorar |
| Imagem | Imagens geradas por slide/campo | Modulo Imagem | Refatorar |
| Agente | Agentes LLM e skills deterministicas | Modulo Agentes | Refatorar |
| Score | Score do Content Critic | Entidade Score | Novo |
| Config | Chaves de API, brand palette, creator registry, platform rules | Modulo Configuracoes | Refatorar |
| Drive | Export e salvamento no Google Drive | Modulo Export | Refatorar |
| Historico | Registro de conteudos gerados | Modulo Historico | Refatorar |
| VisualPreference | Preferencias visuais persistidas | Skill visual_memory | Novo |
| CreatorEntry | Creator registry | Config / trend_scanner | Novo |

---

## 3. Casos de Uso por Dominio

### 3.1 Pipeline

| Caso de Uso | Metodo | Rota | Descricao |
|-------------|--------|------|-----------|
| CriarPipeline | POST | `/api/pipelines` | Cria pipeline com tema + formato(s) + modo_funil |
| BuscarPipeline | GET | `/api/pipelines/{id}` | Retorna pipeline com status de todas as etapas |
| ListarPipelines | GET | `/api/pipelines` | Lista pipelines do tenant com filtros |
| AprovarEtapa | POST | `/api/pipelines/{id}/etapas/{etapa}/aprovar` | Aprova etapa com dados editados (AP-1 a AP-4) |
| RejeitarEtapa | POST | `/api/pipelines/{id}/etapas/{etapa}/rejeitar` | Rejeita etapa com feedback para re-execucao |
| RetomarPipeline | POST | `/api/pipelines/{id}/retomar` | Retoma pipeline de etapa com erro |
| CancelarPipeline | POST | `/api/pipelines/{id}/cancelar` | Cancela pipeline |
| BuscarEtapa | GET | `/api/pipelines/{id}/etapas/{etapa}` | Retorna detalhes de uma etapa especifica |
| ExecutarProximaEtapa | POST | `/api/pipelines/{id}/executar` | Executa proxima etapa pendente do pipeline |

### 3.2 Conteudo (legado -- manter)

| Caso de Uso | Metodo | Rota | Descricao |
|-------------|--------|------|-----------|
| GerarConteudo | POST | `/api/gerar-conteudo` | Gera conteudo via Claude API (legado) |
| GerarConteudoCli | POST | `/api/gerar-conteudo-cli` | Gera conteudo via Claude Code CLI (legado) |

### 3.3 Imagem (legado -- manter)

| Caso de Uso | Metodo | Rota | Descricao |
|-------------|--------|------|-----------|
| GerarImagem | POST | `/api/gerar-imagem` | Gera imagens de todos os slides (legado) |
| GerarImagemSlide | POST | `/api/gerar-imagem-slide` | Gera imagem de 1 slide (legado) |

### 3.4 Agente

| Caso de Uso | Metodo | Rota | Descricao |
|-------------|--------|------|-----------|
| ListarAgentes | GET | `/api/agentes` | Lista 6 agentes LLM + 6 skills com metadados |
| BuscarAgente | GET | `/api/agentes/{slug}` | Retorna detalhes + system prompt de 1 agente |
| ExecutarAgente | POST | `/api/agentes/{slug}/executar` | Executa agente individual (fora do pipeline, para debug) |

### 3.5 Score

| Caso de Uso | Metodo | Rota | Descricao |
|-------------|--------|------|-----------|
| BuscarScore | GET | `/api/pipelines/{pipeline_id}/score` | Retorna score do Content Critic |

### 3.6 Config

| Caso de Uso | Metodo | Rota | Descricao |
|-------------|--------|------|-----------|
| SalvarConfig | POST | `/api/config` | Salva chaves de API (existente) |
| BuscarConfig | GET | `/api/config` | Retorna status das chaves (existente) |
| SalvarBrandPalette | PUT | `/api/config/brand-palette` | Salva brand_palette.json |
| BuscarBrandPalette | GET | `/api/config/brand-palette` | Retorna brand_palette.json |
| SalvarCreatorRegistry | PUT | `/api/config/creator-registry` | Salva creator_registry.json |
| BuscarCreatorRegistry | GET | `/api/config/creator-registry` | Retorna creator_registry.json |
| SalvarPlatformRules | PUT | `/api/config/platform-rules` | Salva platform_rules.json |
| BuscarPlatformRules | GET | `/api/config/platform-rules` | Retorna platform_rules.json |

### 3.7 Drive (manter existente + refatorar)

| Caso de Uso | Metodo | Rota | Descricao |
|-------------|--------|------|-----------|
| SalvarCarrosselDrive | POST | `/api/google-drive/carrossel` | Salva carrossel no Drive (existente) |
| ListarPastasDrive | GET | `/api/drive/pastas` | Lista pastas (existente) |
| ListarDesignSystems | GET | `/api/drive/design-systems` | Lista design systems (existente) |
| UploadDesignSystem | POST | `/api/drive/design-systems` | Upload design system (existente) |
| BuscarDesignSystem | GET | `/api/drive/design-systems/{file_id}` | Busca conteudo (existente) |
| DeletarDesignSystem | DELETE | `/api/drive/design-systems/{file_id}` | Deleta (existente) |
| SalvarConteudoDrive | POST | `/api/google-drive/conteudo` | Salva conteudo v3 (PDF + PNGs) no Drive |

### 3.8 Historico

| Caso de Uso | Metodo | Rota | Descricao |
|-------------|--------|------|-----------|
| ListarHistorico | GET | `/api/historico` | Lista historico com filtros (refatorar) |
| DeletarHistorico | DELETE | `/api/historico/{id}` | Deleta item (existente) |
| BuscarHistorico | GET | `/api/historico/{id}` | Busca item individual (novo) |

### 3.9 VisualPreference

| Caso de Uso | Metodo | Rota | Descricao |
|-------------|--------|------|-----------|
| SalvarPreferencia | POST | `/api/visual-preferences` | Salva preferencia visual apos AP-4 |
| ListarPreferencias | GET | `/api/visual-preferences` | Lista preferencias do tenant |

### 3.10 CreatorEntry

Gerenciado via Config (creator_registry.json). Sem rotas separadas no MVP.

---

## 4. Estrutura de Pastas Completa

```text
backend/
  main.py
  config.py                          <- Settings (Pydantic BaseSettings)
  requirements.txt

  dtos/
    pipeline/
      criar_pipeline/
        request.py                   <- CriarPipelineRequest
        response.py                  <- CriarPipelineResponse
      buscar_pipeline/
        response.py                  <- BuscarPipelineResponse
      listar_pipelines/
        request.py                   <- ListarPipelinesFiltros (query params)
        response.py                  <- ListarPipelinesResponse
      aprovar_etapa/
        request.py                   <- AprovarEtapaRequest
        response.py                  <- AprovarEtapaResponse
      rejeitar_etapa/
        request.py                   <- RejeitarEtapaRequest
        response.py                  <- RejeitarEtapaResponse
      buscar_etapa/
        response.py                  <- BuscarEtapaResponse
      base.py                       <- PipelineBase, EtapaBase

    conteudo/
      gerar_conteudo/
        request.py                   <- GerarConteudoRequest (existente)
        response.py                  <- GerarConteudoResponse (existente)
      base.py                       <- SlideResponse (existente)

    imagem/
      gerar_imagem/
        request.py                   <- GerarImagemRequest (existente)
        response.py                  <- GerarImagemResponse (existente)

    agente/
      listar_agentes/
        response.py                  <- ListarAgentesResponse
      buscar_agente/
        response.py                  <- BuscarAgenteResponse
      executar_agente/
        request.py                   <- ExecutarAgenteRequest
        response.py                  <- ExecutarAgenteResponse
      base.py                       <- AgenteBase

    score/
      buscar_score/
        response.py                  <- BuscarScoreResponse
      base.py                       <- ScoreBase

    config/
      request.py                     <- SaveConfigRequest (existente)
      response.py                    <- ConfigStatusResponse (existente)
      salvar_brand_palette/
        request.py                   <- SalvarBrandPaletteRequest
        response.py                  <- SalvarBrandPaletteResponse
      buscar_brand_palette/
        response.py                  <- BuscarBrandPaletteResponse
      salvar_creator_registry/
        request.py                   <- SalvarCreatorRegistryRequest
        response.py                  <- SalvarCreatorRegistryResponse
      buscar_creator_registry/
        response.py                  <- BuscarCreatorRegistryResponse
      salvar_platform_rules/
        request.py                   <- SalvarPlatformRulesRequest
        response.py                  <- SalvarPlatformRulesResponse
      buscar_platform_rules/
        response.py                  <- BuscarPlatformRulesResponse

    drive/
      salvar_drive/
        request.py                   <- SaveCarrosselDriveRequest (existente)
        response.py                  <- SaveCarrosselDriveResponse (existente)
      salvar_conteudo_drive/
        request.py                   <- SalvarConteudoDriveRequest
        response.py                  <- SalvarConteudoDriveResponse

    historico/
      listar_historico/
        request.py                   <- ListarHistoricoFiltros
        response.py                  <- ListarHistoricoResponse
      buscar_historico/
        response.py                  <- BuscarHistoricoResponse
      base.py                       <- HistoricoItemBase

    visual_preference/
      salvar_preferencia/
        request.py                   <- SalvarPreferenciaRequest
        response.py                  <- SalvarPreferenciaResponse
      listar_preferencias/
        response.py                  <- ListarPreferenciasResponse
      base.py                       <- VisualPreferenceBase

  routers/
    pipeline.py
    conteudo.py                      <- existente (manter)
    imagem.py                        <- existente (manter)
    agente.py                        <- refatorar (era agentes.py)
    config.py                        <- refatorar (adicionar brand/creator/platform)
    drive.py                         <- existente (manter)
    historico.py                     <- refatorar (adicionar filtros)
    visual_preference.py

  services/
    pipeline_service.py
    conteudo_service.py              <- existente (manter)
    conteudo_cli_service.py          <- existente (manter)
    conteudo_openai_service.py       <- existente (manter)
    imagem_service.py                <- existente (manter)
    agente_service.py
    config_service.py
    drive_service.py                 <- existente (manter)
    historico_service.py
    visual_preference_service.py
    prompt_templates.py              <- existente (manter)

  factories/
    pipeline_factory.py
    conteudo_factory.py              <- existente (manter)
    imagem_factory.py                <- existente (manter)
    agente_factory.py
    config_factory.py                <- existente (refatorar)
    historico_factory.py
    visual_preference_factory.py

  mappers/
    pipeline_mapper.py
    conteudo_mapper.py               <- existente (manter)
    imagem_mapper.py                 <- existente (manter)
    agente_mapper.py
    score_mapper.py
    config_mapper.py
    drive_mapper.py                  <- existente (manter)
    historico_mapper.py
    visual_preference_mapper.py

  models/
    pipeline.py                      <- PipelineModel + PipelineStepModel
    conteudo.py                      <- ConteudoModel
    imagem.py                        <- ImagemModel
    score.py                         <- ScoreModel
    historico.py                     <- HistoricoModel (refatorar db_service)
    visual_preference.py             <- VisualPreferenceModel
    base.py                          <- BaseModel (campos comuns: id, tenant_id, timestamps)

  data/
    interfaces/
      base_repository.py             <- contrato abstrato puro
    repositories/
      sql/
        base_sql_repository.py       <- CRUD generico SQLAlchemy
        pipeline_repository.py
        conteudo_repository.py
        imagem_repository.py
        score_repository.py
        historico_repository.py
        visual_preference_repository.py
    connections/
      sql_connection.py              <- engine + session factory (MSSQL)
      database.py                    <- Depends: get_sql_session

  skills/
    brand_overlay.py                 <- Pillow: foto + logo
    brand_validator.py               <- Pillow: valida cores, ratio, elementos
    visual_memory.py                 <- Persiste preferencias
    variation_engine.py              <- 3 variacoes de prompt (sem LLM)
    tone_guide.py                    <- Valida vocabulario IT Valley
    trend_scanner.py                 <- Busca tendencias (dev.to, HN, YouTube RSS)

  agents/
    strategist.py                    <- Agente 1: briefing com funil
    copywriter.py                    <- Agente 2: headline, narrativa, CTA
    hook_specialist.py               <- Agente 3: 3 hooks A/B/C
    art_director.py                  <- Agente 4: prompt de imagem
    image_generator.py               <- Agente 5: Gemini API
    content_critic.py                <- Agente 6: score final

  configs/
    dimensions.json
    templates.json
    brand_palette.json
    platform_rules.json
    creator_registry.json
```

---

## 5. Models (SQLAlchemy)

### 5.1 BaseModel (campos comuns)

```python
# models/base.py
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class TenantMixin:
    """Mixin para tenant_id + timestamps + soft delete."""
    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(50), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
```

### 5.2 PipelineModel + PipelineStepModel

```python
# models/pipeline.py
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship

from models.base import Base, TenantMixin


class PipelineModel(TenantMixin, Base):
    __tablename__ = "pipeline"
    __table_args__ = {"schema": "carrossel"}

    tema = Column(Text, nullable=False)
    formato = Column(String(50), nullable=False)           # carrossel, post_unico, thumbnail_youtube
    modo_funil = Column(Boolean, default=False)
    status = Column(String(30), nullable=False, default="pendente")
    # Status: pendente, em_execucao, aguardando_aprovacao, completo, cancelado, erro
    etapa_atual = Column(String(50), nullable=True)
    modo_entrada = Column(String(20), nullable=True)       # texto, disciplina
    disciplina = Column(String(50), nullable=True)
    tecnologia = Column(String(100), nullable=True)
    foto_criador = Column(Text, nullable=True)

    etapas = relationship("PipelineStepModel", back_populates="pipeline", cascade="all, delete-orphan")


class PipelineStepModel(Base):
    __tablename__ = "pipeline_step"
    __table_args__ = {"schema": "carrossel"}

    id = Column(UNIQUEIDENTIFIER, primary_key=True)
    pipeline_id = Column(UNIQUEIDENTIFIER, ForeignKey("carrossel.pipeline.id"), nullable=False)
    agente = Column(String(50), nullable=False)
    # Agentes: strategist, copywriter, hook_specialist, art_director,
    #          image_generator, brand_gate, content_critic
    ordem = Column(Integer, nullable=False)
    entrada = Column(Text, nullable=True)                  # JSON serializado
    saida = Column(Text, nullable=True)                    # JSON serializado
    status = Column(String(30), nullable=False, default="pendente")
    # Status: pendente, em_execucao, aguardando_aprovacao, aprovado, rejeitado, erro
    erro_mensagem = Column(Text, nullable=True)
    aprovado_por = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)

    pipeline = relationship("PipelineModel", back_populates="etapas")
```

### 5.3 ConteudoModel

```python
# models/conteudo.py
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

from models.base import Base, TenantMixin


class ConteudoModel(TenantMixin, Base):
    __tablename__ = "conteudo"
    __table_args__ = {"schema": "carrossel"}

    pipeline_id = Column(UNIQUEIDENTIFIER, ForeignKey("carrossel.pipeline.id"), nullable=True)
    formato = Column(String(50), nullable=False)
    titulo = Column(String(500), nullable=False)
    headline = Column(Text, nullable=True)
    narrativa = Column(Text, nullable=True)
    hook = Column(Text, nullable=True)
    cta = Column(Text, nullable=True)
    copy_completa = Column(Text, nullable=True)            # JSON com sequencia de slides
    legenda_linkedin = Column(Text, nullable=True)
    disciplina = Column(String(50), nullable=True)
    tecnologia_principal = Column(String(100), nullable=True)
```

### 5.4 ImagemModel

```python
# models/imagem.py
from sqlalchemy import Column, String, Text, Integer, Boolean, Float, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

from models.base import Base, TenantMixin


class ImagemModel(TenantMixin, Base):
    __tablename__ = "imagem"
    __table_args__ = {"schema": "carrossel"}

    conteudo_id = Column(UNIQUEIDENTIFIER, ForeignKey("carrossel.conteudo.id"), nullable=False)
    slide_index = Column(Integer, nullable=False)
    variacao = Column(Integer, nullable=False)             # 1, 2 ou 3
    url_drive = Column(Text, nullable=True)
    image_base64 = Column(Text, nullable=True)
    modelo_gemini = Column(String(50), nullable=True)      # gemini-3-pro, gemini-2.5-flash
    brand_gate_status = Column(String(30), nullable=True)  # valido, invalido, revisao_manual
    brand_gate_retries = Column(Integer, default=0)
    selecionada = Column(Boolean, default=False)
```

### 5.5 ScoreModel

```python
# models/score.py
from sqlalchemy import Column, Float, String, Text, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER

from models.base import Base, TenantMixin


class ScoreModel(TenantMixin, Base):
    __tablename__ = "score"
    __table_args__ = {"schema": "carrossel"}

    conteudo_id = Column(UNIQUEIDENTIFIER, ForeignKey("carrossel.conteudo.id"), nullable=False)
    clarity = Column(Float, nullable=False)
    impact = Column(Float, nullable=False)
    originality = Column(Float, nullable=False)
    scroll_stop = Column(Float, nullable=False)
    cta_strength = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)
    decision = Column(String(30), nullable=False)          # approved, needs_revision
    best_variation = Column(String(10), nullable=True)
    feedback = Column(Text, nullable=True)
```

### 5.6 HistoricoModel

```python
# models/historico.py
from sqlalchemy import Column, String, Integer, Text, Float

from models.base import Base, TenantMixin


class HistoricoModel(TenantMixin, Base):
    __tablename__ = "historico"
    __table_args__ = {"schema": "carrossel"}

    titulo = Column(String(500), nullable=False)
    formato = Column(String(50), nullable=True, default="carrossel")
    status = Column(String(30), nullable=True, default="completo")
    disciplina = Column(String(50), nullable=True)
    tecnologia_principal = Column(String(100), nullable=True)
    tipo_carrossel = Column(String(30), nullable=True)
    total_slides = Column(Integer, nullable=True)
    final_score = Column(Float, nullable=True)
    legenda_linkedin = Column(Text, nullable=True)
    google_drive_link = Column(Text, nullable=True)
    google_drive_folder_name = Column(String(500), nullable=True)
    pipeline_id = Column(String(36), nullable=True)
```

### 5.7 VisualPreferenceModel

```python
# models/visual_preference.py
from sqlalchemy import Column, String, Boolean, Text

from models.base import Base, TenantMixin


class VisualPreferenceModel(TenantMixin, Base):
    __tablename__ = "visual_preference"
    __table_args__ = {"schema": "carrossel"}

    estilo = Column(String(200), nullable=False)           # descricao do estilo
    aprovado = Column(Boolean, nullable=False)             # True = aprovado, False = rejeitado
    contexto = Column(Text, nullable=True)                 # JSON: formato, tema, etc.
```

---

## 6. DTOs -- Codigo Completo por Dominio

### 6.1 Pipeline

```python
# dtos/pipeline/base.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class EtapaBase(BaseModel):
    agente: str
    ordem: int
    status: str
    erro_mensagem: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class PipelineBase(BaseModel):
    tema: str
    formato: str
    modo_funil: bool = False
    status: str
    etapa_atual: Optional[str] = None
```

```python
# dtos/pipeline/criar_pipeline/request.py
from pydantic import BaseModel, field_validator
from typing import Optional


class CriarPipelineRequest(BaseModel):
    tema: str
    formato: str                                           # carrossel, post_unico, thumbnail_youtube
    modo_funil: bool = False
    modo_entrada: str = "texto"                            # texto, disciplina
    disciplina: Optional[str] = None
    tecnologia: Optional[str] = None
    foto_criador: Optional[str] = None

    @field_validator("tema")
    @classmethod
    def tema_minimo(cls, v: str) -> str:
        if len(v.strip()) < 20:
            raise ValueError("Tema deve ter no minimo 20 caracteres")
        return v.strip()

    @field_validator("formato")
    @classmethod
    def formato_valido(cls, v: str) -> str:
        validos = ["carrossel", "post_unico", "thumbnail_youtube"]
        if v not in validos:
            raise ValueError(f"Formato deve ser um de: {validos}")
        return v
```

```python
# dtos/pipeline/criar_pipeline/response.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

from dtos.pipeline.base import EtapaBase


class CriarPipelineResponse(BaseModel):
    id: UUID
    tema: str
    formato: str
    modo_funil: bool
    status: str
    etapa_atual: Optional[str]
    etapas: list[EtapaBase]
    created_at: datetime
```

```python
# dtos/pipeline/buscar_pipeline/response.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

from dtos.pipeline.base import EtapaBase


class BuscarEtapaDetalhe(EtapaBase):
    id: UUID
    entrada_resumo: Optional[str] = None
    saida_resumo: Optional[str] = None
    aprovado_por: Optional[str] = None
    approved_at: Optional[datetime] = None


class BuscarPipelineResponse(BaseModel):
    id: UUID
    tema: str
    formato: str
    modo_funil: bool
    status: str
    etapa_atual: Optional[str]
    modo_entrada: Optional[str]
    disciplina: Optional[str]
    tecnologia: Optional[str]
    etapas: list[BuscarEtapaDetalhe]
    created_at: datetime
    updated_at: Optional[datetime]
```

```python
# dtos/pipeline/listar_pipelines/request.py
from pydantic import BaseModel
from typing import Optional


class ListarPipelinesFiltros(BaseModel):
    formato: Optional[str] = None
    status: Optional[str] = None
    limit: int = 50
    offset: int = 0
```

```python
# dtos/pipeline/listar_pipelines/response.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class PipelineResumo(BaseModel):
    id: UUID
    tema: str
    formato: str
    status: str
    etapa_atual: Optional[str]
    final_score: Optional[float] = None
    created_at: datetime


class ListarPipelinesResponse(BaseModel):
    items: list[PipelineResumo]
    total: int
```

```python
# dtos/pipeline/aprovar_etapa/request.py
from pydantic import BaseModel
from typing import Optional


class AprovarEtapaRequest(BaseModel):
    dados_editados: Optional[dict] = None                  # Conteudo editado pelo usuario (briefing, copy, prompts, selecao)
    hook_selecionado: Optional[str] = None                 # A, B ou C (AP-2)
    variacoes_selecionadas: Optional[dict[str, int]] = None  # slide_index -> variacao (AP-4)
```

```python
# dtos/pipeline/aprovar_etapa/response.py
from pydantic import BaseModel


class AprovarEtapaResponse(BaseModel):
    sucesso: bool
    proxima_etapa: str | None = None
    mensagem: str
```

```python
# dtos/pipeline/rejeitar_etapa/request.py
from pydantic import BaseModel
from typing import Optional


class RejeitarEtapaRequest(BaseModel):
    feedback: Optional[str] = None                         # Feedback do usuario para re-execucao
```

```python
# dtos/pipeline/rejeitar_etapa/response.py
from pydantic import BaseModel


class RejeitarEtapaResponse(BaseModel):
    sucesso: bool
    etapa_reexecutada: str
    mensagem: str
```

```python
# dtos/pipeline/buscar_etapa/response.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, Any


class BuscarEtapaResponse(BaseModel):
    id: UUID
    agente: str
    ordem: int
    status: str
    entrada: Optional[Any] = None                          # JSON deserializado
    saida: Optional[Any] = None                            # JSON deserializado
    erro_mensagem: Optional[str] = None
    aprovado_por: Optional[str] = None
    approved_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
```

### 6.2 Agente

```python
# dtos/agente/base.py
from pydantic import BaseModel
from typing import Optional


class AgenteBase(BaseModel):
    slug: str
    nome: str
    descricao: str
    tipo: str                                              # "llm" ou "skill"
```

```python
# dtos/agente/listar_agentes/response.py
from pydantic import BaseModel

from dtos.agente.base import AgenteBase


class AgenteItem(AgenteBase):
    ordem_pipeline: int | None = None


class ListarAgentesResponse(BaseModel):
    agentes_llm: list[AgenteItem]
    skills_deterministicas: list[AgenteItem]
```

```python
# dtos/agente/buscar_agente/response.py
from pydantic import BaseModel
from typing import Optional

from dtos.agente.base import AgenteBase


class BuscarAgenteResponse(AgenteBase):
    conteudo: str                                          # system prompt ou descricao da skill
    ordem_pipeline: Optional[int] = None
    entrada_esperada: Optional[str] = None                 # Descricao do formato de entrada
    saida_esperada: Optional[str] = None                   # Descricao do formato de saida
```

```python
# dtos/agente/executar_agente/request.py
from pydantic import BaseModel
from typing import Any


class ExecutarAgenteRequest(BaseModel):
    entrada: dict[str, Any]                                # Dados de entrada no formato esperado pelo agente
```

```python
# dtos/agente/executar_agente/response.py
from pydantic import BaseModel
from typing import Any


class ExecutarAgenteResponse(BaseModel):
    agente: str
    saida: Any                                             # Saida no formato do agente
    tempo_execucao_ms: int
```

### 6.3 Score

```python
# dtos/score/base.py
from pydantic import BaseModel


class ScoreBase(BaseModel):
    clarity: float
    impact: float
    originality: float
    scroll_stop: float
    cta_strength: float
    final_score: float
    decision: str                                          # approved, needs_revision
    best_variation: str | None = None
```

```python
# dtos/score/buscar_score/response.py
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

from dtos.score.base import ScoreBase


class BuscarScoreResponse(ScoreBase):
    id: UUID
    conteudo_id: UUID
    feedback: Optional[str] = None
```

### 6.4 Config (novos casos de uso)

```python
# dtos/config/salvar_brand_palette/request.py
from pydantic import BaseModel


class CoresRequest(BaseModel):
    fundo_principal: str                                   # hex #XXXXXX
    destaque_primario: str
    destaque_secundario: str
    texto_principal: str
    texto_secundario: str


class SalvarBrandPaletteRequest(BaseModel):
    cores: CoresRequest
    fonte: str
    elementos_obrigatorios: list[str]
    estilo: str
```

```python
# dtos/config/salvar_brand_palette/response.py
from pydantic import BaseModel


class SalvarBrandPaletteResponse(BaseModel):
    sucesso: bool
    mensagem: str
```

```python
# dtos/config/buscar_brand_palette/response.py
from pydantic import BaseModel
from typing import Optional


class CoresResponse(BaseModel):
    fundo_principal: str
    destaque_primario: str
    destaque_secundario: str
    texto_principal: str
    texto_secundario: str


class BuscarBrandPaletteResponse(BaseModel):
    cores: CoresResponse
    fonte: str
    elementos_obrigatorios: list[str]
    estilo: str
```

```python
# dtos/config/salvar_creator_registry/request.py
from pydantic import BaseModel
from typing import Optional


class CriadorRequest(BaseModel):
    nome: str
    funcao: str                                            # TECH_SOURCE, EXPLAINER, VIRAL_ENGINE, THOUGHT_LEADER, DINAMICAS
    plataforma: str                                        # YouTube, Twitter, Blog, dev.to, HN
    url: Optional[str] = None
    ativo: bool = True


class SalvarCreatorRegistryRequest(BaseModel):
    criadores: list[CriadorRequest]
```

```python
# dtos/config/salvar_creator_registry/response.py
from pydantic import BaseModel


class SalvarCreatorRegistryResponse(BaseModel):
    sucesso: bool
    total_criadores: int
    mensagem: str
```

```python
# dtos/config/buscar_creator_registry/response.py
from pydantic import BaseModel
from typing import Optional


class CriadorResponse(BaseModel):
    nome: str
    funcao: str
    plataforma: str
    url: Optional[str] = None
    ativo: bool


class BuscarCreatorRegistryResponse(BaseModel):
    criadores: list[CriadorResponse]
```

```python
# dtos/config/salvar_platform_rules/request.py
from pydantic import BaseModel
from typing import Optional


class PlataformaRuleRequest(BaseModel):
    nome: str
    max_caracteres: int
    hashtags_max: Optional[int] = None
    specs: Optional[str] = None


class SalvarPlatformRulesRequest(BaseModel):
    plataformas: list[PlataformaRuleRequest]
```

```python
# dtos/config/salvar_platform_rules/response.py
from pydantic import BaseModel


class SalvarPlatformRulesResponse(BaseModel):
    sucesso: bool
    mensagem: str
```

```python
# dtos/config/buscar_platform_rules/response.py
from pydantic import BaseModel
from typing import Optional


class PlataformaRuleResponse(BaseModel):
    nome: str
    max_caracteres: int
    hashtags_max: Optional[int] = None
    specs: Optional[str] = None


class BuscarPlatformRulesResponse(BaseModel):
    plataformas: list[PlataformaRuleResponse]
```

### 6.5 Historico (refatorado)

```python
# dtos/historico/base.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HistoricoItemBase(BaseModel):
    titulo: str
    formato: Optional[str] = None
    status: Optional[str] = None
    disciplina: Optional[str] = None
    tecnologia_principal: Optional[str] = None
    total_slides: Optional[int] = None
    final_score: Optional[float] = None
    google_drive_link: Optional[str] = None
    created_at: Optional[datetime] = None
```

```python
# dtos/historico/listar_historico/request.py
from pydantic import BaseModel
from typing import Optional
from datetime import date


class ListarHistoricoFiltros(BaseModel):
    texto: Optional[str] = None
    formato: Optional[str] = None
    status: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    limit: int = 50
    offset: int = 0
```

```python
# dtos/historico/listar_historico/response.py
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime


class HistoricoItem(BaseModel):
    id: UUID
    titulo: str
    formato: Optional[str] = None
    status: Optional[str] = None
    disciplina: Optional[str] = None
    tecnologia_principal: Optional[str] = None
    tipo_carrossel: Optional[str] = None
    total_slides: Optional[int] = None
    final_score: Optional[float] = None
    google_drive_link: Optional[str] = None
    google_drive_folder_name: Optional[str] = None
    pipeline_id: Optional[str] = None
    created_at: Optional[datetime] = None


class ListarHistoricoResponse(BaseModel):
    items: list[HistoricoItem]
    total: int
```

```python
# dtos/historico/buscar_historico/response.py
from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime


class BuscarHistoricoResponse(BaseModel):
    id: UUID
    titulo: str
    formato: Optional[str] = None
    status: Optional[str] = None
    disciplina: Optional[str] = None
    tecnologia_principal: Optional[str] = None
    tipo_carrossel: Optional[str] = None
    total_slides: Optional[int] = None
    final_score: Optional[float] = None
    legenda_linkedin: Optional[str] = None
    google_drive_link: Optional[str] = None
    google_drive_folder_name: Optional[str] = None
    pipeline_id: Optional[str] = None
    created_at: Optional[datetime] = None
```

### 6.6 VisualPreference

```python
# dtos/visual_preference/base.py
from pydantic import BaseModel
from typing import Optional


class VisualPreferenceBase(BaseModel):
    estilo: str
    aprovado: bool
    contexto: Optional[dict] = None
```

```python
# dtos/visual_preference/salvar_preferencia/request.py
from pydantic import BaseModel
from typing import Optional


class SalvarPreferenciaRequest(BaseModel):
    estilo: str
    aprovado: bool
    contexto: Optional[dict] = None                        # formato, tema, etc.
```

```python
# dtos/visual_preference/salvar_preferencia/response.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class SalvarPreferenciaResponse(BaseModel):
    id: UUID
    estilo: str
    aprovado: bool
    created_at: datetime
```

```python
# dtos/visual_preference/listar_preferencias/response.py
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class PreferenciaItem(BaseModel):
    id: UUID
    estilo: str
    aprovado: bool
    contexto: Optional[dict] = None
    created_at: datetime


class ListarPreferenciasResponse(BaseModel):
    items: list[PreferenciaItem]
```

### 6.7 Drive (novo caso de uso)

```python
# dtos/drive/salvar_conteudo_drive/request.py
from pydantic import BaseModel
from typing import Optional


class SalvarConteudoDriveRequest(BaseModel):
    pipeline_id: str
    titulo: str
    formato: str
    pdf_base64: Optional[str] = None
    images_base64: list[str | None]
```

```python
# dtos/drive/salvar_conteudo_drive/response.py
from pydantic import BaseModel


class SalvarConteudoDriveResponse(BaseModel):
    subfolder_name: str
    web_view_link: str
    total_arquivos: int
```

---

## 7. Factories -- Codigo Completo

### 7.1 PipelineFactory

```python
# factories/pipeline_factory.py
import uuid
from datetime import datetime, timezone

from models.pipeline import PipelineModel, PipelineStepModel
from dtos.pipeline.criar_pipeline.request import CriarPipelineRequest


# Ordem fixa das etapas do pipeline
ETAPAS_PIPELINE = [
    ("strategist", 1),
    ("copywriter", 2),
    ("hook_specialist", 3),
    ("art_director", 4),
    ("image_generator", 5),
    ("brand_gate", 6),
    ("content_critic", 7),
]

# Etapas que exigem aprovacao humana
ETAPAS_APROVACAO = {
    "strategist": "AP-1",       # Aprovar briefing
    "hook_specialist": "AP-2",  # Escolher hook + aprovar copy
    "art_director": "AP-3",     # Aprovar prompt visual
    "brand_gate": "AP-4",       # Escolher variacao de imagem
}

FORMATOS_VALIDOS = ["carrossel", "post_unico", "thumbnail_youtube"]


class PipelineFactory:

    @staticmethod
    def to_model(dto: CriarPipelineRequest, tenant_id: str) -> PipelineModel:
        if dto.formato not in FORMATOS_VALIDOS:
            raise ValueError(f"Formato invalido: {dto.formato}. Validos: {FORMATOS_VALIDOS}")

        if len(dto.tema.strip()) < 20:
            raise ValueError("Tema deve ter no minimo 20 caracteres")

        if dto.modo_entrada == "disciplina" and not dto.disciplina:
            raise ValueError("Disciplina obrigatoria quando modo_entrada = disciplina")

        pipeline_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        pipeline = PipelineModel(
            id=pipeline_id,
            tenant_id=tenant_id,
            tema=dto.tema.strip(),
            formato=dto.formato,
            modo_funil=dto.modo_funil,
            status="pendente",
            etapa_atual="strategist",
            modo_entrada=dto.modo_entrada,
            disciplina=dto.disciplina,
            tecnologia=dto.tecnologia,
            foto_criador=dto.foto_criador,
            created_at=now,
        )

        # Cria todas as etapas do pipeline
        pipeline.etapas = []
        for agente, ordem in ETAPAS_PIPELINE:
            step = PipelineStepModel(
                id=uuid.uuid4(),
                pipeline_id=pipeline_id,
                agente=agente,
                ordem=ordem,
                status="pendente",
                created_at=now,
            )
            pipeline.etapas.append(step)

        return pipeline

    @staticmethod
    def etapa_requer_aprovacao(agente: str) -> bool:
        return agente in ETAPAS_APROVACAO

    @staticmethod
    def proxima_etapa(etapa_atual: str) -> str | None:
        for agente, ordem in ETAPAS_PIPELINE:
            if agente == etapa_atual:
                for next_agente, next_ordem in ETAPAS_PIPELINE:
                    if next_ordem == ordem + 1:
                        return next_agente
                return None
        return None
```

### 7.2 AgenteFactory

```python
# factories/agente_factory.py
from pathlib import Path
from typing import Optional

_BASE = Path(__file__).parent.parent
AGENTS_PATH = _BASE / "agents"
if not AGENTS_PATH.exists():
    AGENTS_PATH = _BASE.parent / "agents"

# Metadados dos 6 agentes LLM
AGENTES_LLM = [
    {
        "slug": "strategist",
        "nome": "Strategist",
        "descricao": "Gera briefing estruturado com funil (1 tema -> 5-7 pecas). Usa tendencias do trend_scanner.",
        "tipo": "llm",
        "ordem_pipeline": 1,
        "arquivo": "strategist.md",
    },
    {
        "slug": "copywriter",
        "nome": "Copywriter",
        "descricao": "Gera headline, narrativa, CTA e sequencia de slides/campos a partir do briefing aprovado.",
        "tipo": "llm",
        "ordem_pipeline": 2,
        "arquivo": "copywriter.md",
    },
    {
        "slug": "hook_specialist",
        "nome": "Hook Specialist",
        "descricao": "Gera 3 ganchos A/B/C com abordagens diferentes a partir da copy completa.",
        "tipo": "llm",
        "ordem_pipeline": 3,
        "arquivo": "hook_specialist.md",
    },
    {
        "slug": "art_director",
        "nome": "Art Director",
        "descricao": "Gera prompt de imagem detalhado por slide, adaptado ao formato e brand palette.",
        "tipo": "llm",
        "ordem_pipeline": 4,
        "arquivo": "art_director.md",
    },
    {
        "slug": "image_generator",
        "nome": "Image Generator",
        "descricao": "Gera 3 variacoes de imagem por slide via Gemini API (Pro/Flash).",
        "tipo": "llm",
        "ordem_pipeline": 5,
        "arquivo": None,
    },
    {
        "slug": "content_critic",
        "nome": "Content Critic",
        "descricao": "Avalia conteudo final com score em 6 dimensoes: clarity, impact, originality, scroll_stop, cta_strength, final_score.",
        "tipo": "llm",
        "ordem_pipeline": 7,
        "arquivo": "content_critic.md",
    },
]

# Metadados das 6 skills deterministicas
SKILLS = [
    {
        "slug": "brand_overlay",
        "nome": "Brand Overlay",
        "descricao": "Pillow: aplica foto redonda do criador + logo IT Valley em posicao fixa.",
        "tipo": "skill",
        "ordem_pipeline": None,
    },
    {
        "slug": "brand_validator",
        "nome": "Brand Validator",
        "descricao": "Pillow: valida cores, aspect ratio, elementos obrigatorios da marca.",
        "tipo": "skill",
        "ordem_pipeline": None,
    },
    {
        "slug": "visual_memory",
        "nome": "Visual Memory",
        "descricao": "Persiste preferencias visuais do usuario (estilos aprovados/rejeitados).",
        "tipo": "skill",
        "ordem_pipeline": None,
    },
    {
        "slug": "variation_engine",
        "nome": "Variation Engine",
        "descricao": "Gera 3 variacoes de prompt via manipulacao de string (sem LLM).",
        "tipo": "skill",
        "ordem_pipeline": None,
    },
    {
        "slug": "tone_guide",
        "nome": "Tone Guide",
        "descricao": "Valida vocabulario IT Valley (termos proibidos, tom de voz, jargoes).",
        "tipo": "skill",
        "ordem_pipeline": None,
    },
    {
        "slug": "trend_scanner",
        "nome": "Trend Scanner",
        "descricao": "Busca conteudo dos criadores do registry (dev.to + HN + YouTube RSS), cache 1h.",
        "tipo": "skill",
        "ordem_pipeline": None,
    },
]


class AgenteFactory:

    @staticmethod
    def listar_todos() -> tuple[list[dict], list[dict]]:
        return AGENTES_LLM, SKILLS

    @staticmethod
    def buscar_por_slug(slug: str) -> Optional[dict]:
        for agente in AGENTES_LLM + SKILLS:
            if agente["slug"] == slug:
                return agente
        return None

    @staticmethod
    def carregar_system_prompt(agente: dict) -> str:
        arquivo = agente.get("arquivo")
        if not arquivo:
            return agente["descricao"]
        path = AGENTS_PATH / arquivo
        if path.exists():
            return path.read_text(encoding="utf-8")
        return f"Arquivo nao encontrado: {arquivo}"
```

### 7.3 HistoricoFactory

```python
# factories/historico_factory.py
import uuid
from datetime import datetime, timezone

from models.historico import HistoricoModel


class HistoricoFactory:

    @staticmethod
    def to_model(
        titulo: str,
        tenant_id: str,
        formato: str = "carrossel",
        status: str = "completo",
        disciplina: str | None = None,
        tecnologia_principal: str | None = None,
        tipo_carrossel: str | None = None,
        total_slides: int | None = None,
        final_score: float | None = None,
        legenda_linkedin: str | None = None,
        google_drive_link: str | None = None,
        google_drive_folder_name: str | None = None,
        pipeline_id: str | None = None,
    ) -> HistoricoModel:
        if not titulo or not titulo.strip():
            raise ValueError("Titulo obrigatorio")

        return HistoricoModel(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            titulo=titulo.strip(),
            formato=formato,
            status=status,
            disciplina=disciplina,
            tecnologia_principal=tecnologia_principal,
            tipo_carrossel=tipo_carrossel,
            total_slides=total_slides,
            final_score=final_score,
            legenda_linkedin=legenda_linkedin,
            google_drive_link=google_drive_link,
            google_drive_folder_name=google_drive_folder_name,
            pipeline_id=pipeline_id,
            created_at=datetime.now(timezone.utc),
        )
```

### 7.4 VisualPreferenceFactory

```python
# factories/visual_preference_factory.py
import json
import uuid
from datetime import datetime, timezone

from models.visual_preference import VisualPreferenceModel
from dtos.visual_preference.salvar_preferencia.request import SalvarPreferenciaRequest


class VisualPreferenceFactory:

    @staticmethod
    def to_model(dto: SalvarPreferenciaRequest, tenant_id: str) -> VisualPreferenceModel:
        if not dto.estilo or not dto.estilo.strip():
            raise ValueError("Estilo obrigatorio")

        return VisualPreferenceModel(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            estilo=dto.estilo.strip(),
            aprovado=dto.aprovado,
            contexto=json.dumps(dto.contexto) if dto.contexto else None,
            created_at=datetime.now(timezone.utc),
        )
```

---

## 8. Mappers -- Codigo Completo

### 8.1 PipelineMapper

```python
# mappers/pipeline_mapper.py
import json

from models.pipeline import PipelineModel, PipelineStepModel
from dtos.pipeline.criar_pipeline.response import CriarPipelineResponse
from dtos.pipeline.buscar_pipeline.response import BuscarPipelineResponse, BuscarEtapaDetalhe
from dtos.pipeline.listar_pipelines.response import PipelineResumo
from dtos.pipeline.buscar_etapa.response import BuscarEtapaResponse
from dtos.pipeline.base import EtapaBase


class PipelineMapper:

    @staticmethod
    def to_criar_response(model: PipelineModel) -> CriarPipelineResponse:
        etapas = [
            EtapaBase(
                agente=e.agente,
                ordem=e.ordem,
                status=e.status,
            )
            for e in sorted(model.etapas, key=lambda e: e.ordem)
        ]
        return CriarPipelineResponse(
            id=model.id,
            tema=model.tema,
            formato=model.formato,
            modo_funil=model.modo_funil,
            status=model.status,
            etapa_atual=model.etapa_atual,
            etapas=etapas,
            created_at=model.created_at,
        )

    @staticmethod
    def to_buscar_response(model: PipelineModel) -> BuscarPipelineResponse:
        etapas = [
            BuscarEtapaDetalhe(
                id=e.id,
                agente=e.agente,
                ordem=e.ordem,
                status=e.status,
                erro_mensagem=e.erro_mensagem,
                started_at=e.started_at,
                finished_at=e.finished_at,
                entrada_resumo=PipelineMapper._resumir_json(e.entrada),
                saida_resumo=PipelineMapper._resumir_json(e.saida),
                aprovado_por=e.aprovado_por,
                approved_at=e.approved_at,
            )
            for e in sorted(model.etapas, key=lambda e: e.ordem)
        ]
        return BuscarPipelineResponse(
            id=model.id,
            tema=model.tema,
            formato=model.formato,
            modo_funil=model.modo_funil,
            status=model.status,
            etapa_atual=model.etapa_atual,
            modo_entrada=model.modo_entrada,
            disciplina=model.disciplina,
            tecnologia=model.tecnologia,
            etapas=etapas,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_resumo(model: PipelineModel) -> PipelineResumo:
        return PipelineResumo(
            id=model.id,
            tema=model.tema,
            formato=model.formato,
            status=model.status,
            etapa_atual=model.etapa_atual,
            created_at=model.created_at,
        )

    @staticmethod
    def to_list_resumo(models: list[PipelineModel]) -> list[PipelineResumo]:
        return [PipelineMapper.to_resumo(m) for m in models]

    @staticmethod
    def to_etapa_response(step: PipelineStepModel) -> BuscarEtapaResponse:
        return BuscarEtapaResponse(
            id=step.id,
            agente=step.agente,
            ordem=step.ordem,
            status=step.status,
            entrada=json.loads(step.entrada) if step.entrada else None,
            saida=json.loads(step.saida) if step.saida else None,
            erro_mensagem=step.erro_mensagem,
            aprovado_por=step.aprovado_por,
            approved_at=step.approved_at,
            started_at=step.started_at,
            finished_at=step.finished_at,
        )

    @staticmethod
    def _resumir_json(text: str | None) -> str | None:
        if not text:
            return None
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                keys = list(data.keys())[:5]
                return f"{{ {', '.join(keys)}... }}"
            return str(data)[:200]
        except (json.JSONDecodeError, TypeError):
            return text[:200] if text else None
```

### 8.2 AgenteMapper

```python
# mappers/agente_mapper.py
from dtos.agente.listar_agentes.response import ListarAgentesResponse, AgenteItem
from dtos.agente.buscar_agente.response import BuscarAgenteResponse


class AgenteMapper:

    @staticmethod
    def to_listar_response(agentes_llm: list[dict], skills: list[dict]) -> ListarAgentesResponse:
        return ListarAgentesResponse(
            agentes_llm=[
                AgenteItem(
                    slug=a["slug"],
                    nome=a["nome"],
                    descricao=a["descricao"],
                    tipo=a["tipo"],
                    ordem_pipeline=a.get("ordem_pipeline"),
                )
                for a in agentes_llm
            ],
            skills_deterministicas=[
                AgenteItem(
                    slug=s["slug"],
                    nome=s["nome"],
                    descricao=s["descricao"],
                    tipo=s["tipo"],
                    ordem_pipeline=s.get("ordem_pipeline"),
                )
                for s in skills
            ],
        )

    @staticmethod
    def to_buscar_response(agente: dict, conteudo: str) -> BuscarAgenteResponse:
        return BuscarAgenteResponse(
            slug=agente["slug"],
            nome=agente["nome"],
            descricao=agente["descricao"],
            tipo=agente["tipo"],
            conteudo=conteudo,
            ordem_pipeline=agente.get("ordem_pipeline"),
        )
```

### 8.3 ScoreMapper

```python
# mappers/score_mapper.py
from models.score import ScoreModel
from dtos.score.buscar_score.response import BuscarScoreResponse


class ScoreMapper:

    @staticmethod
    def to_response(model: ScoreModel) -> BuscarScoreResponse:
        return BuscarScoreResponse(
            id=model.id,
            conteudo_id=model.conteudo_id,
            clarity=model.clarity,
            impact=model.impact,
            originality=model.originality,
            scroll_stop=model.scroll_stop,
            cta_strength=model.cta_strength,
            final_score=model.final_score,
            decision=model.decision,
            best_variation=model.best_variation,
            feedback=model.feedback,
        )
```

### 8.4 ConfigMapper

```python
# mappers/config_mapper.py
import json

from dtos.config.buscar_brand_palette.response import BuscarBrandPaletteResponse, CoresResponse
from dtos.config.buscar_creator_registry.response import BuscarCreatorRegistryResponse, CriadorResponse
from dtos.config.buscar_platform_rules.response import BuscarPlatformRulesResponse, PlataformaRuleResponse


class ConfigMapper:

    @staticmethod
    def dict_to_brand_palette(data: dict) -> BuscarBrandPaletteResponse:
        cores = data.get("cores", {})
        return BuscarBrandPaletteResponse(
            cores=CoresResponse(
                fundo_principal=cores.get("fundo_principal", "#0A0A0F"),
                destaque_primario=cores.get("destaque_primario", "#A78BFA"),
                destaque_secundario=cores.get("destaque_secundario", "#6D28D9"),
                texto_principal=cores.get("texto_principal", "#FFFFFF"),
                texto_secundario=cores.get("texto_secundario", "#94A3B8"),
            ),
            fonte=data.get("fonte", "Outfit"),
            elementos_obrigatorios=data.get("elementos_obrigatorios", []),
            estilo=data.get("estilo", "dark_mode_premium"),
        )

    @staticmethod
    def dict_to_creator_registry(data: dict) -> BuscarCreatorRegistryResponse:
        criadores = data.get("criadores", [])
        return BuscarCreatorRegistryResponse(
            criadores=[
                CriadorResponse(
                    nome=c.get("nome", ""),
                    funcao=c.get("funcao", ""),
                    plataforma=c.get("plataforma", ""),
                    url=c.get("url"),
                    ativo=c.get("ativo", True),
                )
                for c in criadores
            ]
        )

    @staticmethod
    def dict_to_platform_rules(data: dict) -> BuscarPlatformRulesResponse:
        plataformas = data.get("plataformas", [])
        return BuscarPlatformRulesResponse(
            plataformas=[
                PlataformaRuleResponse(
                    nome=p.get("nome", ""),
                    max_caracteres=p.get("max_caracteres", 0),
                    hashtags_max=p.get("hashtags_max"),
                    specs=p.get("specs"),
                )
                for p in plataformas
            ]
        )
```

### 8.5 HistoricoMapper

```python
# mappers/historico_mapper.py
from models.historico import HistoricoModel
from dtos.historico.listar_historico.response import HistoricoItem
from dtos.historico.buscar_historico.response import BuscarHistoricoResponse


class HistoricoMapper:

    @staticmethod
    def to_item(model: HistoricoModel) -> HistoricoItem:
        return HistoricoItem(
            id=model.id,
            titulo=model.titulo,
            formato=model.formato,
            status=model.status,
            disciplina=model.disciplina,
            tecnologia_principal=model.tecnologia_principal,
            tipo_carrossel=model.tipo_carrossel,
            total_slides=model.total_slides,
            final_score=model.final_score,
            google_drive_link=model.google_drive_link,
            google_drive_folder_name=model.google_drive_folder_name,
            pipeline_id=model.pipeline_id,
            created_at=model.created_at,
        )

    @staticmethod
    def to_list(models: list[HistoricoModel]) -> list[HistoricoItem]:
        return [HistoricoMapper.to_item(m) for m in models]

    @staticmethod
    def to_buscar_response(model: HistoricoModel) -> BuscarHistoricoResponse:
        return BuscarHistoricoResponse(
            id=model.id,
            titulo=model.titulo,
            formato=model.formato,
            status=model.status,
            disciplina=model.disciplina,
            tecnologia_principal=model.tecnologia_principal,
            tipo_carrossel=model.tipo_carrossel,
            total_slides=model.total_slides,
            final_score=model.final_score,
            legenda_linkedin=model.legenda_linkedin,
            google_drive_link=model.google_drive_link,
            google_drive_folder_name=model.google_drive_folder_name,
            pipeline_id=model.pipeline_id,
            created_at=model.created_at,
        )
```

### 8.6 VisualPreferenceMapper

```python
# mappers/visual_preference_mapper.py
import json

from models.visual_preference import VisualPreferenceModel
from dtos.visual_preference.salvar_preferencia.response import SalvarPreferenciaResponse
from dtos.visual_preference.listar_preferencias.response import PreferenciaItem


class VisualPreferenceMapper:

    @staticmethod
    def to_salvar_response(model: VisualPreferenceModel) -> SalvarPreferenciaResponse:
        return SalvarPreferenciaResponse(
            id=model.id,
            estilo=model.estilo,
            aprovado=model.aprovado,
            created_at=model.created_at,
        )

    @staticmethod
    def to_item(model: VisualPreferenceModel) -> PreferenciaItem:
        contexto = None
        if model.contexto:
            try:
                contexto = json.loads(model.contexto)
            except (json.JSONDecodeError, TypeError):
                contexto = None
        return PreferenciaItem(
            id=model.id,
            estilo=model.estilo,
            aprovado=model.aprovado,
            contexto=contexto,
            created_at=model.created_at,
        )

    @staticmethod
    def to_list(models: list[VisualPreferenceModel]) -> list[PreferenciaItem]:
        return [VisualPreferenceMapper.to_item(m) for m in models]
```

---

## 9. Services -- Codigo Completo

### 9.1 PipelineService

```python
# services/pipeline_service.py
from factories.pipeline_factory import PipelineFactory
from mappers.pipeline_mapper import PipelineMapper
from data.interfaces.base_repository import BaseRepository


class PipelineService:

    def __init__(self, repo: BaseRepository):
        self._repo = repo

    async def criar(self, dto, tenant_id: str):
        model = PipelineFactory.to_model(dto, tenant_id)
        saved = await self._repo.create(model)
        return PipelineMapper.to_criar_response(saved)

    async def buscar(self, pipeline_id: str, tenant_id: str):
        model = await self._repo.get_by_id(pipeline_id, tenant_id)
        if not model:
            return None
        return PipelineMapper.to_buscar_response(model)

    async def listar(self, tenant_id: str, filters: dict = {}):
        models = await self._repo.list(tenant_id, filters)
        return PipelineMapper.to_list_resumo(models)

    async def aprovar_etapa(self, pipeline_id: str, etapa: str, dto, tenant_id: str):
        # Busca pipeline e delega para factory/mapper
        # Service NAO conhece campos -- so orquestra
        model = await self._repo.get_by_id(pipeline_id, tenant_id)
        if not model:
            raise ValueError("Pipeline nao encontrado")
        # Logica de aprovacao delegada ao pipeline_repository (query especifica)
        return await self._repo.aprovar_etapa(pipeline_id, etapa, dto, tenant_id)

    async def rejeitar_etapa(self, pipeline_id: str, etapa: str, dto, tenant_id: str):
        model = await self._repo.get_by_id(pipeline_id, tenant_id)
        if not model:
            raise ValueError("Pipeline nao encontrado")
        return await self._repo.rejeitar_etapa(pipeline_id, etapa, dto, tenant_id)

    async def retomar(self, pipeline_id: str, tenant_id: str):
        model = await self._repo.get_by_id(pipeline_id, tenant_id)
        if not model:
            raise ValueError("Pipeline nao encontrado")
        return await self._repo.retomar(pipeline_id, tenant_id)

    async def cancelar(self, pipeline_id: str, tenant_id: str):
        model = await self._repo.get_by_id(pipeline_id, tenant_id)
        if not model:
            raise ValueError("Pipeline nao encontrado")
        return await self._repo.cancelar(pipeline_id, tenant_id)

    async def buscar_etapa(self, pipeline_id: str, etapa: str, tenant_id: str):
        step = await self._repo.buscar_etapa(pipeline_id, etapa, tenant_id)
        if not step:
            return None
        return PipelineMapper.to_etapa_response(step)
```

### 9.2 AgenteService

```python
# services/agente_service.py
from factories.agente_factory import AgenteFactory
from mappers.agente_mapper import AgenteMapper


class AgenteService:

    async def listar(self):
        agentes_llm, skills = AgenteFactory.listar_todos()
        return AgenteMapper.to_listar_response(agentes_llm, skills)

    async def buscar(self, slug: str):
        agente = AgenteFactory.buscar_por_slug(slug)
        if not agente:
            return None
        conteudo = AgenteFactory.carregar_system_prompt(agente)
        return AgenteMapper.to_buscar_response(agente, conteudo)
```

### 9.3 ConfigService

```python
# services/config_service.py
import json
from pathlib import Path

from mappers.config_mapper import ConfigMapper

CONFIGS_PATH = Path(__file__).parent.parent / "configs"


class ConfigService:

    async def buscar_brand_palette(self):
        data = ConfigService._ler_json("brand_palette.json")
        return ConfigMapper.dict_to_brand_palette(data)

    async def salvar_brand_palette(self, dto):
        data = dto.model_dump()
        ConfigService._salvar_json("brand_palette.json", data)
        return {"sucesso": True, "mensagem": "Brand palette salva"}

    async def buscar_creator_registry(self):
        data = ConfigService._ler_json("creator_registry.json")
        return ConfigMapper.dict_to_creator_registry(data)

    async def salvar_creator_registry(self, dto):
        data = dto.model_dump()
        ConfigService._salvar_json("creator_registry.json", data)
        total = len(dto.criadores)
        return {"sucesso": True, "total_criadores": total, "mensagem": f"{total} criadores salvos"}

    async def buscar_platform_rules(self):
        data = ConfigService._ler_json("platform_rules.json")
        return ConfigMapper.dict_to_platform_rules(data)

    async def salvar_platform_rules(self, dto):
        data = dto.model_dump()
        ConfigService._salvar_json("platform_rules.json", data)
        return {"sucesso": True, "mensagem": "Platform rules salvas"}

    @staticmethod
    def _ler_json(filename: str) -> dict:
        path = CONFIGS_PATH / filename
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _salvar_json(filename: str, data: dict):
        CONFIGS_PATH.mkdir(exist_ok=True)
        path = CONFIGS_PATH / filename
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
```

### 9.4 HistoricoService

```python
# services/historico_service.py
from factories.historico_factory import HistoricoFactory
from mappers.historico_mapper import HistoricoMapper
from data.interfaces.base_repository import BaseRepository


class HistoricoService:

    def __init__(self, repo: BaseRepository):
        self._repo = repo

    async def listar(self, tenant_id: str, filters: dict = {}):
        models = await self._repo.list(tenant_id, filters)
        items = HistoricoMapper.to_list(models)
        total = len(items)
        return {"items": items, "total": total}

    async def buscar(self, item_id: str, tenant_id: str):
        model = await self._repo.get_by_id(item_id, tenant_id)
        if not model:
            return None
        return HistoricoMapper.to_buscar_response(model)

    async def deletar(self, item_id: str, tenant_id: str):
        return await self._repo.soft_delete(item_id, tenant_id)
```

### 9.5 VisualPreferenceService

```python
# services/visual_preference_service.py
from factories.visual_preference_factory import VisualPreferenceFactory
from mappers.visual_preference_mapper import VisualPreferenceMapper
from data.interfaces.base_repository import BaseRepository


class VisualPreferenceService:

    def __init__(self, repo: BaseRepository):
        self._repo = repo

    async def salvar(self, dto, tenant_id: str):
        model = VisualPreferenceFactory.to_model(dto, tenant_id)
        saved = await self._repo.create(model)
        return VisualPreferenceMapper.to_salvar_response(saved)

    async def listar(self, tenant_id: str):
        models = await self._repo.list(tenant_id)
        items = VisualPreferenceMapper.to_list(models)
        return {"items": items}
```

---

## 10. Routers -- Codigo Completo

### 10.1 PipelineRouter

```python
# routers/pipeline.py
from fastapi import APIRouter, HTTPException, Depends

from dtos.pipeline.criar_pipeline.request import CriarPipelineRequest
from dtos.pipeline.criar_pipeline.response import CriarPipelineResponse
from dtos.pipeline.buscar_pipeline.response import BuscarPipelineResponse
from dtos.pipeline.listar_pipelines.response import ListarPipelinesResponse
from dtos.pipeline.aprovar_etapa.request import AprovarEtapaRequest
from dtos.pipeline.aprovar_etapa.response import AprovarEtapaResponse
from dtos.pipeline.rejeitar_etapa.request import RejeitarEtapaRequest
from dtos.pipeline.rejeitar_etapa.response import RejeitarEtapaResponse
from dtos.pipeline.buscar_etapa.response import BuscarEtapaResponse
from services.pipeline_service import PipelineService
from data.connections.database import get_sql_session
from data.repositories.sql.pipeline_repository import PipelineRepository

TENANT_ID = "itvalley"  # Fixo ate multitenancia real

router = APIRouter(prefix="/pipelines", tags=["Pipeline"])


def _get_service(session=Depends(get_sql_session)):
    repo = PipelineRepository(session)
    return PipelineService(repo)


@router.post("/", response_model=CriarPipelineResponse, status_code=201)
async def criar_pipeline(
    dto: CriarPipelineRequest,
    service: PipelineService = Depends(_get_service),
):
    try:
        return await service.criar(dto, tenant_id=TENANT_ID)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{pipeline_id}", response_model=BuscarPipelineResponse)
async def buscar_pipeline(
    pipeline_id: str,
    service: PipelineService = Depends(_get_service),
):
    result = await service.buscar(pipeline_id, tenant_id=TENANT_ID)
    if not result:
        raise HTTPException(status_code=404, detail="Pipeline nao encontrado")
    return result


@router.get("/", response_model=ListarPipelinesResponse)
async def listar_pipelines(
    formato: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    service: PipelineService = Depends(_get_service),
):
    filters = {}
    if formato:
        filters["formato"] = formato
    if status:
        filters["status"] = status
    items = await service.listar(tenant_id=TENANT_ID, filters=filters)
    return ListarPipelinesResponse(items=items, total=len(items))


@router.post("/{pipeline_id}/etapas/{etapa}/aprovar", response_model=AprovarEtapaResponse)
async def aprovar_etapa(
    pipeline_id: str,
    etapa: str,
    dto: AprovarEtapaRequest,
    service: PipelineService = Depends(_get_service),
):
    try:
        return await service.aprovar_etapa(pipeline_id, etapa, dto, tenant_id=TENANT_ID)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{pipeline_id}/etapas/{etapa}/rejeitar", response_model=RejeitarEtapaResponse)
async def rejeitar_etapa(
    pipeline_id: str,
    etapa: str,
    dto: RejeitarEtapaRequest,
    service: PipelineService = Depends(_get_service),
):
    try:
        return await service.rejeitar_etapa(pipeline_id, etapa, dto, tenant_id=TENANT_ID)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{pipeline_id}/etapas/{etapa}", response_model=BuscarEtapaResponse)
async def buscar_etapa(
    pipeline_id: str,
    etapa: str,
    service: PipelineService = Depends(_get_service),
):
    result = await service.buscar_etapa(pipeline_id, etapa, tenant_id=TENANT_ID)
    if not result:
        raise HTTPException(status_code=404, detail="Etapa nao encontrada")
    return result


@router.post("/{pipeline_id}/retomar")
async def retomar_pipeline(
    pipeline_id: str,
    service: PipelineService = Depends(_get_service),
):
    try:
        return await service.retomar(pipeline_id, tenant_id=TENANT_ID)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{pipeline_id}/cancelar")
async def cancelar_pipeline(
    pipeline_id: str,
    service: PipelineService = Depends(_get_service),
):
    try:
        return await service.cancelar(pipeline_id, tenant_id=TENANT_ID)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{pipeline_id}/executar")
async def executar_proxima_etapa(
    pipeline_id: str,
    service: PipelineService = Depends(_get_service),
):
    # Executa a proxima etapa pendente do pipeline
    # Sera implementado pelo Dev Backend (Agente 10)
    raise HTTPException(status_code=501, detail="Execucao de etapa sera implementada pelo Dev Backend")
```

### 10.2 AgenteRouter (refatorado)

```python
# routers/agente.py
from fastapi import APIRouter, HTTPException

from dtos.agente.listar_agentes.response import ListarAgentesResponse
from dtos.agente.buscar_agente.response import BuscarAgenteResponse
from services.agente_service import AgenteService

router = APIRouter(tags=["Agentes"])

_service = AgenteService()


@router.get("/agentes", response_model=ListarAgentesResponse)
async def listar_agentes():
    return await _service.listar()


@router.get("/agentes/{slug}", response_model=BuscarAgenteResponse)
async def buscar_agente(slug: str):
    result = await _service.buscar(slug)
    if not result:
        raise HTTPException(status_code=404, detail="Agente nao encontrado")
    return result
```

### 10.3 ConfigRouter (refatorado)

```python
# routers/config.py
import os

from fastapi import APIRouter, HTTPException

from dtos.config.request import SaveConfigRequest
from dtos.config.response import ConfigStatusResponse
from dtos.config.salvar_brand_palette.request import SalvarBrandPaletteRequest
from dtos.config.salvar_brand_palette.response import SalvarBrandPaletteResponse
from dtos.config.buscar_brand_palette.response import BuscarBrandPaletteResponse
from dtos.config.salvar_creator_registry.request import SalvarCreatorRegistryRequest
from dtos.config.salvar_creator_registry.response import SalvarCreatorRegistryResponse
from dtos.config.buscar_creator_registry.response import BuscarCreatorRegistryResponse
from dtos.config.salvar_platform_rules.request import SalvarPlatformRulesRequest
from dtos.config.salvar_platform_rules.response import SalvarPlatformRulesResponse
from dtos.config.buscar_platform_rules.response import BuscarPlatformRulesResponse
from factories.config_factory import read_env, write_env, update_key
from services.config_service import ConfigService

router = APIRouter(tags=["Configuracoes"])

_config_service = ConfigService()


# --- API Keys (existente) ---

@router.post("/config")
async def salvar_config(req: SaveConfigRequest) -> dict:
    env = read_env()
    update_key(env, "CLAUDE_API_KEY", req.claude_api_key)
    update_key(env, "OPENAI_API_KEY", req.openai_api_key)
    update_key(env, "GEMINI_API_KEY", req.gemini_api_key)
    update_key(env, "GOOGLE_DRIVE_CREDENTIALS", req.google_drive_credentials)
    update_key(env, "GOOGLE_DRIVE_FOLDER_ID", req.google_drive_folder_id)
    write_env(env)
    return {"ok": True}


@router.get("/config", response_model=ConfigStatusResponse)
async def status_config() -> ConfigStatusResponse:
    return ConfigStatusResponse(
        claude_api_key_set=bool(os.getenv("CLAUDE_API_KEY")),
        openai_api_key_set=bool(os.getenv("OPENAI_API_KEY")),
        gemini_api_key_set=bool(os.getenv("GEMINI_API_KEY")),
        google_drive_credentials_set=bool(os.getenv("GOOGLE_DRIVE_CREDENTIALS")),
        google_drive_folder_id=os.getenv("GOOGLE_DRIVE_FOLDER_ID", ""),
    )


# --- Brand Palette (novo) ---

@router.get("/config/brand-palette", response_model=BuscarBrandPaletteResponse)
async def buscar_brand_palette():
    return await _config_service.buscar_brand_palette()


@router.put("/config/brand-palette", response_model=SalvarBrandPaletteResponse)
async def salvar_brand_palette(dto: SalvarBrandPaletteRequest):
    return await _config_service.salvar_brand_palette(dto)


# --- Creator Registry (novo) ---

@router.get("/config/creator-registry", response_model=BuscarCreatorRegistryResponse)
async def buscar_creator_registry():
    return await _config_service.buscar_creator_registry()


@router.put("/config/creator-registry", response_model=SalvarCreatorRegistryResponse)
async def salvar_creator_registry(dto: SalvarCreatorRegistryRequest):
    return await _config_service.salvar_creator_registry(dto)


# --- Platform Rules (novo) ---

@router.get("/config/platform-rules", response_model=BuscarPlatformRulesResponse)
async def buscar_platform_rules():
    return await _config_service.buscar_platform_rules()


@router.put("/config/platform-rules", response_model=SalvarPlatformRulesResponse)
async def salvar_platform_rules(dto: SalvarPlatformRulesRequest):
    return await _config_service.salvar_platform_rules(dto)
```

### 10.4 HistoricoRouter (refatorado)

```python
# routers/historico.py
from fastapi import APIRouter, HTTPException, Depends

from dtos.historico.listar_historico.response import ListarHistoricoResponse
from dtos.historico.buscar_historico.response import BuscarHistoricoResponse
from services.historico_service import HistoricoService
from data.connections.database import get_sql_session
from data.repositories.sql.historico_repository import HistoricoRepository

TENANT_ID = "itvalley"

router = APIRouter(tags=["Historico"])


def _get_service(session=Depends(get_sql_session)):
    repo = HistoricoRepository(session)
    return HistoricoService(repo)


@router.get("/historico", response_model=ListarHistoricoResponse)
async def listar_historico(
    texto: str | None = None,
    formato: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
    service: HistoricoService = Depends(_get_service),
):
    filters = {}
    if texto:
        filters["texto"] = texto
    if formato:
        filters["formato"] = formato
    if status:
        filters["status"] = status
    return await service.listar(tenant_id=TENANT_ID, filters=filters)


@router.get("/historico/{item_id}", response_model=BuscarHistoricoResponse)
async def buscar_historico(
    item_id: str,
    service: HistoricoService = Depends(_get_service),
):
    result = await service.buscar(item_id, tenant_id=TENANT_ID)
    if not result:
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    return result


@router.delete("/historico/{item_id}")
async def deletar_historico(
    item_id: str,
    service: HistoricoService = Depends(_get_service),
):
    ok = await service.deletar(item_id, tenant_id=TENANT_ID)
    if not ok:
        raise HTTPException(status_code=404, detail="Item nao encontrado")
    return {"ok": True}
```

### 10.5 VisualPreferenceRouter

```python
# routers/visual_preference.py
from fastapi import APIRouter, HTTPException, Depends

from dtos.visual_preference.salvar_preferencia.request import SalvarPreferenciaRequest
from dtos.visual_preference.salvar_preferencia.response import SalvarPreferenciaResponse
from dtos.visual_preference.listar_preferencias.response import ListarPreferenciasResponse
from services.visual_preference_service import VisualPreferenceService
from data.connections.database import get_sql_session
from data.repositories.sql.visual_preference_repository import VisualPreferenceRepository

TENANT_ID = "itvalley"

router = APIRouter(prefix="/visual-preferences", tags=["Visual Preferences"])


def _get_service(session=Depends(get_sql_session)):
    repo = VisualPreferenceRepository(session)
    return VisualPreferenceService(repo)


@router.post("/", response_model=SalvarPreferenciaResponse, status_code=201)
async def salvar_preferencia(
    dto: SalvarPreferenciaRequest,
    service: VisualPreferenceService = Depends(_get_service),
):
    try:
        return await service.salvar(dto, tenant_id=TENANT_ID)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=ListarPreferenciasResponse)
async def listar_preferencias(
    service: VisualPreferenceService = Depends(_get_service),
):
    return await service.listar(tenant_id=TENANT_ID)
```

---

## 11. Camada Data -- Codigo Completo

### 11.1 Interface Base

```python
# data/interfaces/base_repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):

    @abstractmethod
    async def get_by_id(self, id: str, tenant_id: str) -> Optional[T]:
        ...

    @abstractmethod
    async def list(self, tenant_id: str, filters: dict = {}) -> List[T]:
        ...

    @abstractmethod
    async def create(self, entity: T) -> T:
        ...

    @abstractmethod
    async def update(self, id: str, entity: T, tenant_id: str) -> T:
        ...

    @abstractmethod
    async def soft_delete(self, id: str, tenant_id: str) -> bool:
        ...
```

### 11.2 Base SQL Repository

```python
# data/repositories/sql/base_sql_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from data.interfaces.base_repository import BaseRepository, T


class BaseSQLRepository(BaseRepository[T]):

    def __init__(self, session: AsyncSession, model_class: type):
        self._session = session
        self._model = model_class

    async def get_by_id(self, id: str, tenant_id: str):
        result = await self._session.execute(
            select(self._model).where(
                self._model.id == id,
                self._model.tenant_id == tenant_id,
                self._model.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(self, tenant_id: str, filters: dict = {}):
        stmt = select(self._model).where(
            self._model.tenant_id == tenant_id,
            self._model.deleted_at.is_(None),
        )
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def create(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def update(self, id: str, entity: T, tenant_id: str) -> T:
        entity.updated_at = datetime.now(timezone.utc)
        await self._session.flush()
        return entity

    async def soft_delete(self, id: str, tenant_id: str) -> bool:
        obj = await self.get_by_id(id, tenant_id)
        if not obj:
            return False
        obj.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()
        return True
```

### 11.3 Pipeline Repository

```python
# data/repositories/sql/pipeline_repository.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from data.repositories.sql.base_sql_repository import BaseSQLRepository
from models.pipeline import PipelineModel, PipelineStepModel


class PipelineRepository(BaseSQLRepository[PipelineModel]):

    def __init__(self, session):
        super().__init__(session, PipelineModel)

    async def get_by_id(self, id: str, tenant_id: str):
        result = await self._session.execute(
            select(PipelineModel)
            .options(selectinload(PipelineModel.etapas))
            .where(
                PipelineModel.id == id,
                PipelineModel.tenant_id == tenant_id,
                PipelineModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(self, tenant_id: str, filters: dict = {}):
        stmt = select(PipelineModel).where(
            PipelineModel.tenant_id == tenant_id,
            PipelineModel.deleted_at.is_(None),
        ).order_by(PipelineModel.created_at.desc())

        if "formato" in filters:
            stmt = stmt.where(PipelineModel.formato == filters["formato"])
        if "status" in filters:
            stmt = stmt.where(PipelineModel.status == filters["status"])

        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def buscar_etapa(self, pipeline_id: str, agente: str, tenant_id: str):
        # Primeiro verifica que o pipeline pertence ao tenant
        pipeline = await self.get_by_id(pipeline_id, tenant_id)
        if not pipeline:
            return None
        result = await self._session.execute(
            select(PipelineStepModel).where(
                PipelineStepModel.pipeline_id == pipeline_id,
                PipelineStepModel.agente == agente,
            )
        )
        return result.scalar_one_or_none()
```

### 11.4 Historico Repository

```python
# data/repositories/sql/historico_repository.py
from sqlalchemy import select

from data.repositories.sql.base_sql_repository import BaseSQLRepository
from models.historico import HistoricoModel


class HistoricoRepository(BaseSQLRepository[HistoricoModel]):

    def __init__(self, session):
        super().__init__(session, HistoricoModel)

    async def list(self, tenant_id: str, filters: dict = {}):
        stmt = select(HistoricoModel).where(
            HistoricoModel.tenant_id == tenant_id,
            HistoricoModel.deleted_at.is_(None),
        ).order_by(HistoricoModel.created_at.desc())

        if "formato" in filters:
            stmt = stmt.where(HistoricoModel.formato == filters["formato"])
        if "status" in filters:
            stmt = stmt.where(HistoricoModel.status == filters["status"])
        if "texto" in filters:
            stmt = stmt.where(HistoricoModel.titulo.contains(filters["texto"]))

        result = await self._session.execute(stmt)
        return result.scalars().all()
```

### 11.5 Visual Preference Repository

```python
# data/repositories/sql/visual_preference_repository.py
from data.repositories.sql.base_sql_repository import BaseSQLRepository
from models.visual_preference import VisualPreferenceModel


class VisualPreferenceRepository(BaseSQLRepository[VisualPreferenceModel]):

    def __init__(self, session):
        super().__init__(session, VisualPreferenceModel)
```

### 11.6 Score Repository

```python
# data/repositories/sql/score_repository.py
from sqlalchemy import select

from data.repositories.sql.base_sql_repository import BaseSQLRepository
from models.score import ScoreModel


class ScoreRepository(BaseSQLRepository[ScoreModel]):

    def __init__(self, session):
        super().__init__(session, ScoreModel)

    async def buscar_por_conteudo(self, conteudo_id: str, tenant_id: str):
        result = await self._session.execute(
            select(ScoreModel).where(
                ScoreModel.conteudo_id == conteudo_id,
                ScoreModel.tenant_id == tenant_id,
                ScoreModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()
```

### 11.7 Conexoes

```python
# data/connections/sql_connection.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import settings

engine = create_async_engine(settings.MSSQL_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

```python
# data/connections/database.py
from data.connections.sql_connection import AsyncSessionLocal


async def get_sql_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### 11.8 Config (Settings)

```python
# config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MSSQL_URL: str = ""
    CLAUDE_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    GOOGLE_DRIVE_CREDENTIALS: str = ""
    GOOGLE_DRIVE_FOLDER_ID: str = ""
    TENANT_ID: str = "itvalley"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```

---

## 12. main.py (refatorado)

```python
# main.py
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from routers import conteudo, imagem, drive, config, agente, historico, pipeline, visual_preference

app = FastAPI(title="Content Factory v3 API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers novos (v3)
app.include_router(pipeline.router, prefix="/api")
app.include_router(visual_preference.router, prefix="/api")

# Routers refatorados
app.include_router(agente.router, prefix="/api")
app.include_router(config.router, prefix="/api")
app.include_router(historico.router, prefix="/api")

# Routers legados (manter)
app.include_router(conteudo.router, prefix="/api")
app.include_router(imagem.router, prefix="/api")
app.include_router(drive.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "3.0.0"}
```

---

## 13. Skills -- Estrutura de Codigo

As skills sao funcoes puras (sem LLM) na pasta `skills/`. Cada skill e um modulo Python com interface simples.

### 13.1 brand_validator

```python
# skills/brand_validator.py
from PIL import Image
import io
import base64
import json
from pathlib import Path


CONFIGS_PATH = Path(__file__).parent.parent / "configs"


def validar(image_base64: str, formato: str) -> dict:
    """Valida imagem contra brand_palette.json.

    Retorna:
        {"valido": bool, "erros": list[str]}
    """
    palette = _carregar_palette()
    erros = []

    # Decodificar imagem
    img_data = image_base64.split(",")[1] if "," in image_base64 else image_base64
    img = Image.open(io.BytesIO(base64.b64decode(img_data)))

    # Validar aspect ratio
    dims = _carregar_dimensions()
    esperado = dims.get(formato, {})
    if esperado:
        w_esperado, h_esperado = esperado["width"], esperado["height"]
        ratio_esperado = w_esperado / h_esperado
        ratio_atual = img.width / img.height
        if abs(ratio_atual - ratio_esperado) > 0.05:
            erros.append(f"Aspect ratio incorreto: esperado {ratio_esperado:.2f}, atual {ratio_atual:.2f}")

    # Validar dimensoes
    if esperado and (img.width != w_esperado or img.height != h_esperado):
        erros.append(f"Dimensoes incorretas: esperado {w_esperado}x{h_esperado}, atual {img.width}x{img.height}")

    return {"valido": len(erros) == 0, "erros": erros}


def _carregar_palette() -> dict:
    path = CONFIGS_PATH / "brand_palette.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _carregar_dimensions() -> dict:
    path = CONFIGS_PATH / "dimensions.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
```

### 13.2 brand_overlay

```python
# skills/brand_overlay.py
from PIL import Image, ImageDraw
import io
import base64


def aplicar(image_base64: str, foto_criador_base64: str | None = None, logo_base64: str | None = None) -> str:
    """Aplica foto redonda do criador + logo IT Valley sobre a imagem.

    Retorna: image_base64 com overlay aplicado.
    """
    img_data = image_base64.split(",")[1] if "," in image_base64 else image_base64
    img = Image.open(io.BytesIO(base64.b64decode(img_data))).convert("RGBA")

    if foto_criador_base64:
        foto_data = foto_criador_base64.split(",")[1] if "," in foto_criador_base64 else foto_criador_base64
        foto = Image.open(io.BytesIO(base64.b64decode(foto_data))).convert("RGBA")
        foto = _make_circle(foto, size=80)
        # Posicao: canto inferior esquerdo com margem
        pos = (20, img.height - 100)
        img.paste(foto, pos, foto)

    if logo_base64:
        logo_data = logo_base64.split(",")[1] if "," in logo_base64 else logo_base64
        logo = Image.open(io.BytesIO(base64.b64decode(logo_data))).convert("RGBA")
        logo.thumbnail((120, 40))
        # Posicao: canto inferior direito com margem
        pos = (img.width - logo.width - 20, img.height - 60)
        img.paste(logo, pos, logo)

    # Converter de volta para base64
    buffer = io.BytesIO()
    img_rgb = img.convert("RGB")
    img_rgb.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def _make_circle(img: Image.Image, size: int) -> Image.Image:
    img = img.resize((size, size))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output.paste(img, (0, 0), mask)
    return output
```

### 13.3 variation_engine

```python
# skills/variation_engine.py
import re


def gerar_variacoes(prompt: str) -> list[str]:
    """Gera 3 variacoes de prompt via manipulacao de string (sem LLM).

    Estrategia:
    - Variacao 1: prompt original
    - Variacao 2: estilo mais minimalista
    - Variacao 3: estilo mais dramatico

    Retorna: lista de 3 prompts.
    """
    v1 = prompt
    v2 = _variacao_minimalista(prompt)
    v3 = _variacao_dramatica(prompt)
    return [v1, v2, v3]


def _variacao_minimalista(prompt: str) -> str:
    prefix = "Minimalist style. Clean, simple composition with generous whitespace. "
    return prefix + prompt


def _variacao_dramatica(prompt: str) -> str:
    prefix = "Dramatic, high-contrast style. Bold shadows, vibrant accent colors, cinematic lighting. "
    return prefix + prompt
```

### 13.4 tone_guide

```python
# skills/tone_guide.py

# Termos proibidos no vocabulario IT Valley
TERMOS_PROIBIDOS = [
    "guru", "hack", "truque", "milagre", "facil", "rapido",
    "garantido", "infalivel", "segredo", "revelar",
]

# Substituicoes sugeridas
SUBSTITUICOES = {
    "guru": "especialista",
    "hack": "tecnica",
    "truque": "abordagem",
    "milagre": "resultado",
    "facil": "acessivel",
    "rapido": "eficiente",
    "garantido": "comprovado",
    "segredo": "insight",
}


def validar(texto: str) -> dict:
    """Valida vocabulario IT Valley.

    Retorna:
        {
            "valido": bool,
            "correcoes": [{"original": str, "sugestao": str}],
            "texto_corrigido": str
        }
    """
    correcoes = []
    texto_lower = texto.lower()
    texto_corrigido = texto

    for termo in TERMOS_PROIBIDOS:
        if termo in texto_lower:
            sugestao = SUBSTITUICOES.get(termo, f"[substituir '{termo}']")
            correcoes.append({"original": termo, "sugestao": sugestao})

    return {
        "valido": len(correcoes) == 0,
        "correcoes": correcoes,
        "texto_corrigido": texto_corrigido,
    }
```

### 13.5 trend_scanner

```python
# skills/trend_scanner.py
import time
import json
from pathlib import Path

import httpx

CONFIGS_PATH = Path(__file__).parent.parent / "configs"
CACHE_PATH = Path(__file__).parent.parent / ".cache"
CACHE_TTL = 3600  # 1 hora


async def buscar_tendencias() -> list[dict]:
    """Busca tendencias dos criadores registrados.
    Cache de 1 hora.

    Retorna: lista de tendencias [{titulo, fonte, url, data}]
    """
    cached = _ler_cache()
    if cached:
        return cached

    tendencias = []

    # Dev.to
    try:
        tendencias.extend(await _buscar_devto())
    except Exception:
        pass

    # Hacker News
    try:
        tendencias.extend(await _buscar_hackernews())
    except Exception:
        pass

    _salvar_cache(tendencias)
    return tendencias


async def _buscar_devto() -> list[dict]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get("https://dev.to/api/articles?tag=ai&top=7&per_page=5")
        res.raise_for_status()
        return [
            {
                "titulo": a["title"],
                "fonte": "dev.to",
                "url": a["url"],
                "data": a["published_at"],
            }
            for a in res.json()
        ]


async def _buscar_hackernews() -> list[dict]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        res = await client.get("https://hacker-news.firebaseio.com/v0/topstories.json")
        res.raise_for_status()
        ids = res.json()[:5]
        items = []
        for id in ids:
            r = await client.get(f"https://hacker-news.firebaseio.com/v0/item/{id}.json")
            item = r.json()
            if item:
                items.append({
                    "titulo": item.get("title", ""),
                    "fonte": "hackernews",
                    "url": item.get("url", f"https://news.ycombinator.com/item?id={id}"),
                    "data": None,
                })
        return items


def _ler_cache() -> list[dict] | None:
    path = CACHE_PATH / "tendencias.json"
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if time.time() - data.get("timestamp", 0) > CACHE_TTL:
        return None
    return data.get("items", [])


def _salvar_cache(items: list[dict]):
    CACHE_PATH.mkdir(exist_ok=True)
    path = CACHE_PATH / "tendencias.json"
    data = {"timestamp": time.time(), "items": items}
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
```

### 13.6 visual_memory

```python
# skills/visual_memory.py
# Nota: visual_memory persiste via VisualPreferenceService + VisualPreferenceRepository.
# Esta skill e apenas um wrapper que formata os dados para o Art Director.


def formatar_para_art_director(preferencias: list[dict]) -> str:
    """Formata preferencias visuais do usuario como contexto para o Art Director.

    Entrada: lista de preferencias [{estilo, aprovado, contexto}]
    Saida: texto formatado para incluir no system prompt do Art Director
    """
    if not preferencias:
        return "Nenhuma preferencia visual registrada."

    aprovados = [p for p in preferencias if p.get("aprovado")]
    rejeitados = [p for p in preferencias if not p.get("aprovado")]

    partes = []
    if aprovados:
        partes.append("ESTILOS APROVADOS pelo usuario:")
        for p in aprovados[-5:]:  # Ultimas 5
            partes.append(f"  - {p['estilo']}")

    if rejeitados:
        partes.append("ESTILOS REJEITADOS pelo usuario (EVITAR):")
        for p in rejeitados[-5:]:
            partes.append(f"  - {p['estilo']}")

    return "\n".join(partes)
```

---

## 14. Agents -- Estrutura de Codigo

Cada agente LLM e um modulo Python que encapsula system prompt + chamada a API.

```python
# agents/strategist.py
import json
from pathlib import Path

import anthropic

PROMPT_PATH = Path(__file__).parent / "strategist.md"
if not PROMPT_PATH.exists():
    PROMPT_PATH = Path(__file__).parent.parent / "agents" / "strategist.md"


async def executar(
    tema: str,
    formato: str,
    modo_funil: bool,
    tendencias: list[dict] | None = None,
    claude_api_key: str = "",
) -> dict:
    """Executa o Strategist: gera briefing estruturado.

    Retorna: dict com briefing, funil, etc.
    """
    system_prompt = PROMPT_PATH.read_text(encoding="utf-8") if PROMPT_PATH.exists() else ""

    user_prompt = f"Tema: {tema}\nFormato: {formato}\n"
    if modo_funil:
        user_prompt += "Modo funil ativo: gere 5-7 pecas conectadas (topo/meio/fundo).\n"
    if tendencias:
        user_prompt += "\nTendencias atuais:\n"
        for t in tendencias[:5]:
            user_prompt += f"- {t['titulo']} ({t['fonte']})\n"

    client = anthropic.AsyncAnthropic(api_key=claude_api_key)
    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    # Parse JSON da resposta
    text = message.content[0].text
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > 0:
        return json.loads(text[start:end])
    return {"briefing": text}
```

Os demais agentes (copywriter, hook_specialist, art_director, content_critic) seguem a mesma estrutura: system prompt + chamada Claude API + parse JSON.

O image_generator encapsula a logica existente de `imagem_service.py` + `imagem_factory.py` com adicao de 3 variacoes via `variation_engine`.

---

## 15. Tabela de Endpoints Completa

### Pipeline

| Metodo | Rota | Auth | Descricao |
|--------|------|------|-----------|
| POST | `/api/pipelines` | tenant_id fixo | Cria pipeline com tema + formato |
| GET | `/api/pipelines` | tenant_id fixo | Lista pipelines com filtros |
| GET | `/api/pipelines/{id}` | tenant_id fixo | Busca pipeline com etapas |
| POST | `/api/pipelines/{id}/etapas/{etapa}/aprovar` | tenant_id fixo | Aprova etapa (AP-1 a AP-4) |
| POST | `/api/pipelines/{id}/etapas/{etapa}/rejeitar` | tenant_id fixo | Rejeita etapa com feedback |
| GET | `/api/pipelines/{id}/etapas/{etapa}` | tenant_id fixo | Busca detalhes de etapa |
| POST | `/api/pipelines/{id}/retomar` | tenant_id fixo | Retoma de etapa com erro |
| POST | `/api/pipelines/{id}/cancelar` | tenant_id fixo | Cancela pipeline |
| POST | `/api/pipelines/{id}/executar` | tenant_id fixo | Executa proxima etapa |

### Agentes

| Metodo | Rota | Auth | Descricao |
|--------|------|------|-----------|
| GET | `/api/agentes` | - | Lista 6 agentes + 6 skills |
| GET | `/api/agentes/{slug}` | - | Busca agente com system prompt |

### Configuracoes

| Metodo | Rota | Auth | Descricao |
|--------|------|------|-----------|
| POST | `/api/config` | - | Salva API keys |
| GET | `/api/config` | - | Status das API keys |
| GET | `/api/config/brand-palette` | - | Busca brand palette |
| PUT | `/api/config/brand-palette` | - | Salva brand palette |
| GET | `/api/config/creator-registry` | - | Busca creator registry |
| PUT | `/api/config/creator-registry` | - | Salva creator registry |
| GET | `/api/config/platform-rules` | - | Busca platform rules |
| PUT | `/api/config/platform-rules` | - | Salva platform rules |

### Historico

| Metodo | Rota | Auth | Descricao |
|--------|------|------|-----------|
| GET | `/api/historico` | tenant_id fixo | Lista com filtros |
| GET | `/api/historico/{id}` | tenant_id fixo | Busca individual |
| DELETE | `/api/historico/{id}` | tenant_id fixo | Soft delete |

### Visual Preferences

| Metodo | Rota | Auth | Descricao |
|--------|------|------|-----------|
| POST | `/api/visual-preferences` | tenant_id fixo | Salva preferencia |
| GET | `/api/visual-preferences` | tenant_id fixo | Lista preferencias |

### Score

| Metodo | Rota | Auth | Descricao |
|--------|------|------|-----------|
| GET | `/api/pipelines/{pipeline_id}/score` | tenant_id fixo | Score do Content Critic |

### Conteudo (legado)

| Metodo | Rota | Auth | Descricao |
|--------|------|------|-----------|
| POST | `/api/gerar-conteudo` | - | Gera via Claude API |
| POST | `/api/gerar-conteudo-cli` | - | Gera via Claude Code CLI |

### Imagem (legado)

| Metodo | Rota | Auth | Descricao |
|--------|------|------|-----------|
| POST | `/api/gerar-imagem` | - | Gera todos os slides |
| POST | `/api/gerar-imagem-slide` | - | Gera 1 slide |

### Drive

| Metodo | Rota | Auth | Descricao |
|--------|------|------|-----------|
| POST | `/api/google-drive/carrossel` | - | Salva carrossel (legado) |
| POST | `/api/google-drive/conteudo` | - | Salva conteudo v3 |
| GET | `/api/drive/pastas` | - | Lista pastas |
| GET | `/api/drive/design-systems` | - | Lista design systems |
| POST | `/api/drive/design-systems` | - | Upload design system |
| GET | `/api/drive/design-systems/{file_id}` | - | Busca conteudo |
| DELETE | `/api/drive/design-systems/{file_id}` | - | Deleta |

### Health

| Metodo | Rota | Auth | Descricao |
|--------|------|------|-----------|
| GET | `/health` | - | Health check |

**Total: 33 endpoints** (9 pipeline + 2 agentes + 8 config + 3 historico + 2 visual + 1 score + 2 conteudo legado + 2 imagem legado + 3 drive + 1 health)

---

## 16. Nota sobre Autenticacao

O PRD define single-user com tenant_id padrao ("itvalley"). A estrutura esta preparada para multitenancia:

- `tenant_id` em toda tabela e toda query (RN-010)
- Constante `TENANT_ID = "itvalley"` nos routers
- Quando JWT for implementado, substituir a constante por `Depends(get_current_user)` e extrair `tenant_id` do token
- A camada Service/Repository ja recebe `tenant_id` como parametro -- nao muda

---

## 17. Dependencias Novas (requirements.txt)

```text
# Existentes
fastapi==0.115.6
python-dotenv==1.0.1
uvicorn[standard]==0.34.0
anthropic==0.42.0
httpx==0.28.1
python-multipart==0.0.20
pydantic==2.10.4
jinja2==3.1.5
google-auth==2.37.0
google-api-python-client==2.159.0
gunicorn==23.0.0
openai>=1.40.0
pymssql>=2.3.0
Pillow>=10.0.0

# Novos para v3
pydantic-settings>=2.0.0
sqlalchemy[asyncio]>=2.0.0
aioodbc>=0.5.0
```

---

## 18. Plano de Migracao

A refatoracao deve ser feita de forma incremental, sem quebrar o sistema existente.

### Fase 1 -- Infraestrutura (nao quebra nada)
1. Criar `config.py` (Settings)
2. Criar `models/base.py`
3. Criar `data/interfaces/base_repository.py`
4. Criar `data/repositories/sql/base_sql_repository.py`
5. Criar `data/connections/sql_connection.py` + `database.py`
6. Criar pasta `configs/` com JSONs iniciais
7. Criar pasta `skills/` com as 6 skills

### Fase 2 -- Novos dominios (adiciona sem alterar)
1. Pipeline: model + dtos + factory + mapper + service + router + repository
2. VisualPreference: model + dtos + factory + mapper + service + router + repository
3. Score: model + dtos + mapper + repository
4. Agents: pasta com os 6 agentes

### Fase 3 -- Refatoracao dos existentes (altera sem quebrar)
1. Agentes router: de `agentes.py` para `agente.py` (manter rota `/agentes` retrocompativel)
2. Config router: adicionar rotas de brand/creator/platform
3. Historico: migrar db_service para repository + model
4. Registrar novos routers no main.py

### Fase 4 -- Integrar pipeline com agentes e skills
1. Implementar `executar_proxima_etapa` no PipelineService
2. Conectar agentes LLM ao pipeline
3. Conectar skills ao pipeline (brand_gate, tone_guide, etc.)

---

## 19. Duvidas Tecnicas Finais

| ID | Duvida | Impacto |
|----|--------|---------|
| DA-BACK-001 | O MSSQL_URL atual usa pymssql sincrono. A migracao para SQLAlchemy async requer driver `aioodbc`. O servidor MSSQL suporta? | Conexao, performance |
| DA-BACK-002 | O pipeline executa agentes sequencialmente ou pode ter execucoes paralelas (ex: Copywriter + tone_guide)? | Pipeline, performance |
| DA-BACK-003 | O pipeline usa polling (frontend faz GET periodico) ou SSE (Server-Sent Events) para notificar progresso? DT-001 do TELAS.md depende disso. | Pipeline router, UX |
| DA-BACK-004 | O Brand Gate (image_generator + brand_validator + brand_overlay) executa como parte da etapa 5 (image_generator) ou como etapa separada (6)? Na estrutura atual, brand_gate e etapa 6. | Pipeline, factory |
| DA-BACK-005 | Os system prompts dos agentes LLM ja existem nos .md? Hoje so existem `anti-bel-pesce.md` e `nano-banana-carrossel.md`. Os 6 novos precisam ser criados. | Agentes, conteudo |
| DA-BACK-006 | O db_service.py legado (pymssql sincrono) sera mantido durante a transicao ou migrado de uma vez para SQLAlchemy async? | Historico, data layer |
| DA-BACK-007 | O Content Critic recebe a arte final (imagem + texto) ou so o texto? Se recebe imagem, precisa de modelo multimodal (Claude Vision). | Agentes, custo |

---

*Documento gerado pelo Agente 03 (Arquiteto IT Valley Backend) da esteira IT Valley.*
*Proximo: Agente 07 (Arquiteto SQL + MongoDB) -- depende deste documento para criar tabelas.*
