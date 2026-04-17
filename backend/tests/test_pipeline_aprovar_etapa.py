"""Testes unitarios — Aprovar Etapa (INT-02)

Cobre:
- AprovarEtapaRequest aceita tanto saida_editada (legado) quanto dados_editados + etapa (novo)
- PipelineService.aprovar_etapa serializa dados_editados dict para JSON string antes de salvar
- Comportamento legado com saida_editada string continua funcionando
- Quando ambos vem, dados_editados tem prioridade
"""

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services.pipeline_service import PipelineService
from dtos.pipeline.aprovar_etapa.request import AprovarEtapaRequest


def _run(coro):
    return asyncio.run(coro)


# ===================================================================
# DTO — AprovarEtapaRequest (INT-02)
# ===================================================================
class TestAprovarEtapaRequest:
    def test_legado_saida_editada_funciona(self):
        dto = AprovarEtapaRequest(saida_editada='{"x":1}')
        assert dto.saida_editada == '{"x":1}'
        assert dto.dados_editados is None
        assert dto.etapa is None

    def test_novo_formato_dados_editados_dict(self):
        dto = AprovarEtapaRequest(
            dados_editados={"prompts": [{"p": 1}]},
            etapa="art_director",
        )
        assert dto.dados_editados == {"prompts": [{"p": 1}]}
        assert dto.etapa == "art_director"
        assert dto.saida_editada is None

    def test_payload_vazio_aceito(self):
        """Aprovar sem body e valido (aprova saida original)."""
        dto = AprovarEtapaRequest()
        assert dto.saida_editada is None
        assert dto.dados_editados is None
        assert dto.etapa is None

    def test_ambos_formatos_simultaneos(self):
        """Pydantic aceita ambos; service decide qual usar."""
        dto = AprovarEtapaRequest(
            saida_editada='"legado"',
            dados_editados={"novo": "dados"},
            etapa="strategist",
        )
        assert dto.saida_editada is not None
        assert dto.dados_editados is not None

    def test_dados_editados_pode_ser_list(self):
        """Frontend pode mandar lista diretamente (ex: {prompts})."""
        dto = AprovarEtapaRequest(dados_editados=[{"a": 1}, {"b": 2}])
        assert dto.dados_editados == [{"a": 1}, {"b": 2}]


# ===================================================================
# Service — aprovar_etapa com dados_editados
# ===================================================================
class TestAprovarEtapaService:
    def _mock_step(self, status="aguardando_aprovacao"):
        return {"id": "step-1", "status": status, "agente": "strategist"}

    def test_dados_editados_dict_serializa_para_json_string(self):
        """Quando dados_editados e dict, service faz json.dumps antes de salvar."""
        step = self._mock_step()
        update_mock = AsyncMock()

        with patch("services.pipeline_service.buscar_etapa_por_agente", new=AsyncMock(return_value=step)), \
             patch("services.pipeline_service.atualizar_etapa", new=update_mock), \
             patch("services.pipeline_service.buscar_proxima_etapa", new=AsyncMock(return_value=(None, None))), \
             patch("services.pipeline_service.atualizar_pipeline", new=AsyncMock()):
            _run(PipelineService.aprovar_etapa(
                "pipe-1", "strategist",
                dados_editados={"briefing_completo": "Texto editado", "pecas_funil": []},
            ))

        # Verifica que atualizar_etapa foi chamado com saida=JSON string
        call_args = update_mock.call_args
        updates = call_args[0][1]
        assert "saida" in updates
        saida_salva = updates["saida"]
        assert isinstance(saida_salva, str)
        parsed = json.loads(saida_salva)
        assert parsed["briefing_completo"] == "Texto editado"

    def test_dados_editados_lista_serializa(self):
        step = self._mock_step()
        update_mock = AsyncMock()

        with patch("services.pipeline_service.buscar_etapa_por_agente", new=AsyncMock(return_value=step)), \
             patch("services.pipeline_service.atualizar_etapa", new=update_mock), \
             patch("services.pipeline_service.buscar_proxima_etapa", new=AsyncMock(return_value=(None, None))), \
             patch("services.pipeline_service.atualizar_pipeline", new=AsyncMock()):
            _run(PipelineService.aprovar_etapa(
                "pipe-1", "strategist",
                dados_editados=[{"prompt": "p1"}, {"prompt": "p2"}],
            ))

        updates = update_mock.call_args[0][1]
        parsed = json.loads(updates["saida"])
        assert isinstance(parsed, list)
        assert len(parsed) == 2

    def test_dados_editados_prioridade_sobre_saida_editada(self):
        """Se ambos vierem, dados_editados vence."""
        step = self._mock_step()
        update_mock = AsyncMock()

        with patch("services.pipeline_service.buscar_etapa_por_agente", new=AsyncMock(return_value=step)), \
             patch("services.pipeline_service.atualizar_etapa", new=update_mock), \
             patch("services.pipeline_service.buscar_proxima_etapa", new=AsyncMock(return_value=(None, None))), \
             patch("services.pipeline_service.atualizar_pipeline", new=AsyncMock()):
            _run(PipelineService.aprovar_etapa(
                "pipe-1", "strategist",
                saida_editada='"legado"',
                dados_editados={"novo": "valor"},
            ))

        updates = update_mock.call_args[0][1]
        parsed = json.loads(updates["saida"])
        assert parsed == {"novo": "valor"}

    def test_saida_editada_legada_ainda_funciona(self):
        """Quando so saida_editada vem, comportamento antigo preservado."""
        step = self._mock_step()
        update_mock = AsyncMock()

        with patch("services.pipeline_service.buscar_etapa_por_agente", new=AsyncMock(return_value=step)), \
             patch("services.pipeline_service.atualizar_etapa", new=update_mock), \
             patch("services.pipeline_service.buscar_proxima_etapa", new=AsyncMock(return_value=(None, None))), \
             patch("services.pipeline_service.atualizar_pipeline", new=AsyncMock()):
            _run(PipelineService.aprovar_etapa(
                "pipe-1", "strategist",
                saida_editada='{"legacy": true}',
            ))

        updates = update_mock.call_args[0][1]
        assert updates["saida"] == '{"legacy": true}'

    def test_sem_edicoes_nao_sobrescreve_saida(self):
        step = self._mock_step()
        update_mock = AsyncMock()

        with patch("services.pipeline_service.buscar_etapa_por_agente", new=AsyncMock(return_value=step)), \
             patch("services.pipeline_service.atualizar_etapa", new=update_mock), \
             patch("services.pipeline_service.buscar_proxima_etapa", new=AsyncMock(return_value=(None, None))), \
             patch("services.pipeline_service.atualizar_pipeline", new=AsyncMock()):
            _run(PipelineService.aprovar_etapa("pipe-1", "strategist"))

        updates = update_mock.call_args[0][1]
        # saida nao e tocada quando nenhuma edicao e enviada
        assert "saida" not in updates
        assert updates["status"] == "aprovado"

    def test_etapa_nao_aguardando_aprovacao_levanta(self):
        step = self._mock_step(status="pendente")
        with patch("services.pipeline_service.buscar_etapa_por_agente", new=AsyncMock(return_value=step)):
            with pytest.raises(ValueError, match="aguardando aprovacao"):
                _run(PipelineService.aprovar_etapa(
                    "pipe-1", "strategist",
                    dados_editados={"x": 1},
                ))

    def test_etapa_inexistente_retorna_none(self):
        with patch("services.pipeline_service.buscar_etapa_por_agente", new=AsyncMock(return_value=None)):
            result = _run(PipelineService.aprovar_etapa(
                "pipe-1", "strategist",
                dados_editados={"x": 1},
            ))
        assert result is None
