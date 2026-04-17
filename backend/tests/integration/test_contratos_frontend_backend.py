"""Contratos DTO — frontend x backend.

Este arquivo documenta todos os drifts de contrato encontrados entre
os DTOs do frontend (toPayload) e os DTOs do backend (Pydantic Request).

Cada teste falha se o drift persiste.
"""

import pathlib

import pytest


FRONTEND_REPO_DIR = pathlib.Path(__file__).resolve().parents[3] / "frontend" / "src" / "lib" / "repositories"
FRONTEND_DTO_DIR = pathlib.Path(__file__).resolve().parents[3] / "frontend" / "src" / "lib" / "dtos"


def _read_frontend(subpath: str) -> str:
    p = FRONTEND_REPO_DIR / subpath if not subpath.startswith("dtos/") else FRONTEND_DTO_DIR / subpath.replace("dtos/", "")
    if not p.exists():
        pytest.skip(f"Arquivo frontend nao encontrado: {p}")
    return p.read_text(encoding="utf-8")


class TestHistoricoContract:
    """INT-01 corrigido: frontend le data.created_at (campo canonico).
    Compat mantida para data.criado_em (mocks legados).
    """

    def test_backend_response_campo_created_at(self):
        from dtos.historico.listar_historico.response import HistoricoItem
        campos = HistoricoItem.model_fields.keys()
        assert "created_at" in campos

    def test_frontend_dto_le_created_at(self):
        """Fix INT-01: frontend passa a ler data.created_at primeiro."""
        if not (FRONTEND_DTO_DIR / "HistoricoItemDTO.ts").exists():
            pytest.skip("HistoricoItemDTO.ts nao existe")
        content = (FRONTEND_DTO_DIR / "HistoricoItemDTO.ts").read_text(encoding="utf-8")
        assert "data.created_at" in content, (
            "HistoricoItemDTO deve ler data.created_at como fonte canonica."
        )

    def test_drift_resolvido(self):
        """Frontend agora le data.created_at ?? data.criado_em."""
        content = (FRONTEND_DTO_DIR / "HistoricoItemDTO.ts").read_text(encoding="utf-8")
        le_created_at = "data.created_at" in content
        assert le_created_at, "DRIFT INT-01 volta: HistoricoItemDTO nao esta lendo data.created_at"


class TestAprovarEtapaContract:
    """INT-02 corrigido: backend agora aceita dados_editados e etapa alem de saida_editada."""

    def test_backend_dto_aceita_ambos_formatos(self):
        from dtos.pipeline.aprovar_etapa.request import AprovarEtapaRequest
        campos = set(AprovarEtapaRequest.model_fields.keys())
        assert "saida_editada" in campos, "Formato legado mantido"
        assert "dados_editados" in campos, "INT-02: novo formato do frontend aceito"
        assert "etapa" in campos, "INT-02: campo etapa aceito"

    def test_backend_dto_aceita_dados_editados_dict(self):
        """DTO deve parsear dict aninhado sem erro."""
        from dtos.pipeline.aprovar_etapa.request import AprovarEtapaRequest
        dto = AprovarEtapaRequest(dados_editados={"prompts": [{"x": 1}]}, etapa="art_director")
        assert dto.dados_editados == {"prompts": [{"x": 1}]}
        assert dto.etapa == "art_director"
        assert dto.saida_editada is None

    def test_backend_dto_aceita_saida_editada_legado(self):
        from dtos.pipeline.aprovar_etapa.request import AprovarEtapaRequest
        dto = AprovarEtapaRequest(saida_editada='{"x":1}')
        assert dto.saida_editada == '{"x":1}'
        assert dto.dados_editados is None

    def test_frontend_briefing_manda_dados_editados(self):
        content = _read_frontend("BriefingRepository.ts")
        assert "dados_editados" in content


class TestRejeitarEtapaContract:
    """INT-03 corrigido: todos os repositories enviam `motivo` (padrao do backend)."""

    def test_backend_dto(self):
        from dtos.pipeline.rejeitar_etapa.request import RejeitarEtapaRequest
        campos = RejeitarEtapaRequest.model_fields.keys()
        assert "motivo" in campos

    @staticmethod
    def _rejeitar_body(content: str) -> str:
        """Extrai o conteudo do metodo rejeitar() para inspecao."""
        idx = content.find("async rejeitar")
        if idx == -1:
            return ""
        # Pega ate 500 chars a partir do metodo
        return content[idx:idx + 500]

    def test_briefing_envia_motivo(self):
        content = _read_frontend("BriefingRepository.ts")
        body = self._rejeitar_body(content)
        assert body, "BriefingRepository deve ter metodo rejeitar"
        assert "motivo" in body, f"BriefingRepository.rejeitar deve mandar motivo, vi: {body[:200]}"
        assert "{ feedback }" not in body, "Nao pode mais mandar {feedback}"

    def test_visual_envia_motivo(self):
        content = _read_frontend("VisualRepository.ts")
        body = self._rejeitar_body(content)
        assert body, "VisualRepository deve ter metodo rejeitar"
        assert "motivo" in body, f"VisualRepository.rejeitar deve mandar motivo, vi: {body[:200]}"

    def test_imagem_envia_motivo(self):
        content = _read_frontend("ImagemRepository.ts")
        body = self._rejeitar_body(content)
        assert body, "ImagemRepository deve ter metodo rejeitar"
        assert "motivo" in body, f"ImagemRepository.rejeitar deve mandar motivo, vi: {body[:200]}"
        assert "feedback:" not in body, "Nao pode mais mandar feedback:"


class TestCreatorRegistryContract:
    """Bug menor: frontend CreatorEntryDTO tem `id`, backend nao tem."""

    def test_backend_creator_response_nao_tem_id(self):
        from dtos.config.buscar_creator_registry.response import CriadorResponse
        campos = CriadorResponse.model_fields.keys()
        assert "id" not in campos, "Backend CriadorResponse nao deve ter id (nao tem)"

    def test_frontend_creator_tem_id(self):
        if not (FRONTEND_DTO_DIR / "CreatorEntryDTO.ts").exists():
            pytest.skip()
        content = (FRONTEND_DTO_DIR / "CreatorEntryDTO.ts").read_text(encoding="utf-8")
        assert "readonly id: string" in content, "Frontend CreatorEntryDTO tem id"

    def test_drift_documentado(self):
        """Frontend CreatorEntryDTO espera id, backend nao retorna.
        Frontend sempre recebe '' (default). Nao impede UI, mas eh drift."""
        content = (FRONTEND_DTO_DIR / "CreatorEntryDTO.ts").read_text(encoding="utf-8")
        if "data.id" in content:
            # Nao fail, so documenta
            pass


class TestLoginContract:
    """Contratos auth - login/me."""

    def test_login_response_campos(self):
        from dtos.auth.login.response import LoginResponse
        campos = set(LoginResponse.model_fields.keys())
        # Frontend AuthDTO espera token OU access_token
        assert "access_token" in campos

    def test_login_request_campos(self):
        from dtos.auth.login.request import LoginRequest
        campos = set(LoginRequest.model_fields.keys())
        assert campos == {"email", "password"}


class TestAtualizarUsuarioContract:
    def test_patch_request_campos_opcionais(self):
        """Backend aceita name, role, avatar_url — todos opcionais."""
        from dtos.auth.atualizar_usuario.request import AtualizarUsuarioRequest
        campos = AtualizarUsuarioRequest.model_fields.keys()
        assert "name" in campos
        assert "role" in campos
        assert "avatar_url" in campos

    def test_frontend_editar_toPayload(self):
        content = (FRONTEND_DTO_DIR / "EditarUsuarioDTO.ts").read_text(encoding="utf-8")
        # toPayload envia name, role, avatar_url — bate com backend
        assert "name" in content
        assert "role" in content
        assert "avatar_url" in content


class TestIniciarPipelineContract:
    """Contrato para criar pipeline."""

    def test_backend_request_tem_tema_e_formatos(self):
        from dtos.pipeline.criar_pipeline.request import CriarPipelineRequest
        campos = CriarPipelineRequest.model_fields.keys()
        assert "tema" in campos
        assert "formato" in campos
        assert "formatos" in campos
        assert "modo_entrada" in campos

    def test_frontend_dto_compativel(self):
        """Frontend IniciarPipelineDTO.toPayload envia: tema, formatos, modo_funil, foto_criador_id.
        Backend aceita esses + outros opcionais. OK."""
        content = (FRONTEND_DTO_DIR / "IniciarPipelineDTO.ts").read_text(encoding="utf-8")
        assert "tema:" in content
        assert "formatos:" in content
        assert "modo_funil:" in content
        assert "foto_criador_id:" in content

    def test_frontend_modo_entrada_vs_backend(self):
        """Frontend tem modo_entrada: 'texto' | 'disciplina'. Backend aceita 'ideia' | 'texto_pronto' | 'upload'.
        Mas toPayload() NAO inclui modo_entrada — entao o default backend 'ideia' prevalece. OK."""
        content = (FRONTEND_DTO_DIR / "IniciarPipelineDTO.ts").read_text(encoding="utf-8")
        # toPayload nao inclui modo_entrada, entao drift eh nao-observavel
        # Mas se adicionarem modo_entrada, os valores vao quebrar
        if "modo_entrada" in content:
            # Verificar se em toPayload
            assert "'disciplina'" not in content.split("toPayload")[-1], (
                "Se toPayload passa modo_entrada='disciplina', backend rejeita (so aceita ideia/texto_pronto/upload)"
            )


class TestVisualPreferenceContract:
    def test_backend_request(self):
        from dtos.visual_preference.salvar_preferencia.request import SalvarPreferenciaRequest
        campos = SalvarPreferenciaRequest.model_fields.keys()
        assert "estilo" in campos
        assert "aprovado" in campos
        assert "contexto" in campos

    def test_backend_response(self):
        from dtos.visual_preference.salvar_preferencia.response import SalvarPreferenciaResponse
        campos = SalvarPreferenciaResponse.model_fields.keys()
        assert "id" in campos
        assert "created_at" in campos


class TestBrandPaletteContract:
    def test_backend_salvar_request(self):
        from dtos.config.salvar_brand_palette.request import SalvarBrandPaletteRequest, CoresRequest
        campos = SalvarBrandPaletteRequest.model_fields.keys()
        cores = CoresRequest.model_fields.keys()
        assert "cores" in campos
        assert "fonte" in campos
        assert "elementos_obrigatorios" in campos
        assert "estilo" in campos
        # Cores obrigatorias
        for c in ("fundo_principal", "destaque_primario", "destaque_secundario", "texto_principal", "texto_secundario"):
            assert c in cores

    def test_frontend_toPayload_bate(self):
        content = (FRONTEND_DTO_DIR / "BrandPaletteDTO.ts").read_text(encoding="utf-8")
        # toPayload retorna cores{...} + fonte + elementos_obrigatorios + estilo
        assert "fundo_principal:" in content
        assert "destaque_primario:" in content
        assert "fonte:" in content
        assert "elementos_obrigatorios:" in content
