"""Factory do dominio Anuncio (pos-pivot 2026-04-23).

Anuncio = 1 formato 1080x1350 com copy de venda. Sem multiplas dimensoes.

Responsabilidades:
- Criar AnuncioModel (RN-010)
- Validar copy -- headline<=40, descricao<=125, cta<=30 (RN-017)
- Aplicar regras de CTA por modo_entrada (RN-023)
- Soft delete (RN-013)
- Registrar resultado final do pipeline no model
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from dtos.anuncio.criar_anuncio.request import CriarAnuncioRequest
from dtos.anuncio.editar_anuncio.request import EditarAnuncioRequest
from models.anuncio import AnuncioModel


STATUS_VALIDOS = {"rascunho", "gerando", "completo", "erro", "cancelado"}
ETAPAS_VALIDAS = {"topo", "meio", "fundo", "avulso"}

LIMITE_HEADLINE = 40    # RN-017
LIMITE_DESCRICAO = 125  # RN-017
LIMITE_CTA = 30         # RN-017


class AnuncioFactory:

    # ---------------- CRIACAO ----------------
    @staticmethod
    def criar(
        dto: CriarAnuncioRequest,
        tenant_id: str,
        criado_por: str,
        pipeline_id: Optional[str] = None,
        cta_default_marca: Optional[str] = None,
    ) -> AnuncioModel:
        """Cria AnuncioModel novo.

        Status inicial: 'rascunho'. Copy opcional no create (pipeline pode preencher depois).
        Se o usuario passou copy explicita, validamos aqui.
        Se nao passou CTA e o modo=texto_pronto, cai no default da marca (cta_anuncio).
        """
        etapa = AnuncioFactory._validar_etapa_funil(dto.etapa_funil)

        # CTA com fallback pra brand.cta_anuncio (RN-023, RN-024)
        cta_final = dto.cta
        if not cta_final and cta_default_marca:
            cta_final = cta_default_marca[:LIMITE_CTA]

        # Validar copy SE veio (modo texto_pronto)
        if dto.headline:
            AnuncioFactory._validar_limite(dto.headline, LIMITE_HEADLINE, "Headline")
        if dto.descricao:
            AnuncioFactory._validar_limite(dto.descricao, LIMITE_DESCRICAO, "Descricao")
        if cta_final:
            AnuncioFactory._validar_limite(cta_final, LIMITE_CTA, "CTA")

        # Regra CTA obrigatorio em modo texto_pronto (RN-023)
        modo = (dto.modo_entrada or "texto").strip()
        if modo in ("texto_pronto",):
            if not cta_final:
                raise ValueError(
                    "CTA obrigatorio no modo texto_pronto (configure CTA padrao na marca ou informe no request)"
                )

        anuncio = AnuncioModel(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            pipeline_id=pipeline_id,
            pipeline_funil_id=dto.pipeline_funil_id,
            titulo=dto.titulo.strip(),
            etapa_funil=etapa,
            tema_ou_briefing=dto.tema_ou_briefing or None,
            modo_entrada=modo,
            disciplina=dto.disciplina,
            tecnologia=dto.tecnologia,
            foto_criador_id=dto.foto_criador_id,
            criado_por=criado_por,
            headline=dto.headline,
            descricao=dto.descricao,
            cta=cta_final,
            status="rascunho",
            tentativas=0,
            created_at=datetime.now(timezone.utc),
        )
        return anuncio

    # ---------------- EDICAO ----------------
    @staticmethod
    def aplicar_edicao(anuncio: AnuncioModel, dto: EditarAnuncioRequest) -> AnuncioModel:
        """Aplica campos nao-None do dto. Valida limites se veio copy."""
        if dto.titulo is not None:
            anuncio.titulo = dto.titulo.strip()
        if dto.headline is not None:
            AnuncioFactory._validar_limite(dto.headline, LIMITE_HEADLINE, "Headline")
            anuncio.headline = dto.headline
        if dto.descricao is not None:
            AnuncioFactory._validar_limite(dto.descricao, LIMITE_DESCRICAO, "Descricao")
            anuncio.descricao = dto.descricao
        if dto.cta is not None:
            AnuncioFactory._validar_limite(dto.cta, LIMITE_CTA, "CTA")
            anuncio.cta = dto.cta
        if dto.etapa_funil is not None:
            anuncio.etapa_funil = AnuncioFactory._validar_etapa_funil(dto.etapa_funil)
        anuncio.updated_at = datetime.now(timezone.utc)
        return anuncio

    # ---------------- COPY ----------------
    @staticmethod
    def validar_copy(headline: str, descricao: str, cta: str) -> None:
        """Validacao completa ao fechar pipeline (headline + descricao + cta obrigatorios)."""
        if not headline or not headline.strip():
            raise ValueError("Headline obrigatoria")
        if not descricao or not descricao.strip():
            raise ValueError("Descricao obrigatoria")
        if not cta or not cta.strip():
            raise ValueError("CTA obrigatorio")
        AnuncioFactory._validar_limite(headline, LIMITE_HEADLINE, "Headline")
        AnuncioFactory._validar_limite(descricao, LIMITE_DESCRICAO, "Descricao")
        AnuncioFactory._validar_limite(cta, LIMITE_CTA, "CTA")

    @staticmethod
    def aplicar_copy_do_pipeline(
        anuncio: AnuncioModel, headline: str, descricao: str, cta: str,
    ) -> None:
        AnuncioFactory.validar_copy(headline, descricao, cta)
        anuncio.headline = headline
        anuncio.descricao = descricao
        anuncio.cta = cta
        anuncio.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def validar_cta_obrigatorio(
        cta: Optional[str], brand_cta_default: Optional[str], modo_entrada: str,
    ) -> str:
        """RN-023: modo=texto_pronto -> CTA obrigatorio. modo=ideia -> permite vazio."""
        cta_final = cta or brand_cta_default or ""
        if modo_entrada == "texto_pronto" and not cta_final.strip():
            raise ValueError("CTA obrigatorio no modo texto_pronto")
        if cta_final:
            AnuncioFactory._validar_limite(cta_final, LIMITE_CTA, "CTA")
        return cta_final

    # ---------------- REGISTRO DE PIPELINE ----------------
    @staticmethod
    def registrar_pipeline_concluido(
        anuncio: AnuncioModel,
        image_url: str,
        headline: Optional[str] = None,
        descricao: Optional[str] = None,
        cta: Optional[str] = None,
        brand_gate_score: Optional[float] = None,
        tentativas: Optional[int] = None,
    ) -> None:
        """Hook chamado pelo AnuncioPipelineService no fim do pipeline."""
        anuncio.image_url = image_url
        if headline is not None:
            anuncio.headline = headline
        if descricao is not None:
            anuncio.descricao = descricao
        if cta is not None:
            anuncio.cta = cta
        if brand_gate_score is not None:
            anuncio.brand_gate_score = float(brand_gate_score)
        if tentativas is not None:
            anuncio.tentativas = int(tentativas)
        anuncio.brand_gate_feedback = None
        anuncio.status = "completo"
        anuncio.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def registrar_pipeline_erro(
        anuncio: AnuncioModel,
        feedback: str,
        tentativas: Optional[int] = None,
    ) -> None:
        anuncio.status = "erro"
        anuncio.brand_gate_feedback = (feedback or "Pipeline falhou")[:3000]
        if tentativas is not None:
            anuncio.tentativas = int(tentativas)
        anuncio.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def marcar_gerando(anuncio: AnuncioModel) -> None:
        anuncio.status = "gerando"
        anuncio.updated_at = datetime.now(timezone.utc)

    # ---------------- EXCLUSAO ----------------
    @staticmethod
    def preparar_soft_delete(anuncio: AnuncioModel) -> None:
        anuncio.deleted_at = datetime.now(timezone.utc)
        anuncio.status = "cancelado"
        anuncio.updated_at = datetime.now(timezone.utc)

    # ---------------- VALIDADORES ----------------
    @staticmethod
    def _validar_etapa_funil(etapa: Optional[str]) -> str:
        if etapa is None or etapa == "":
            return "avulso"
        if etapa not in ETAPAS_VALIDAS:
            raise ValueError(f"Etapa funil invalida: {etapa}")
        return etapa

    @staticmethod
    def _validar_limite(texto: str, limite: int, rotulo: str) -> None:
        if len(texto) > limite:
            raise ValueError(f"{rotulo} excede {limite} caracteres")
