"""Testes unitarios — Mappers do dominio Brand (Marca).

Cobre VisualPreferenceMapper (mappers/visual_preference_mapper.py):
- to_salvar_response: Model -> SalvarPreferenciaResponse
- to_item: Model -> PreferenciaItem (faz parse do contexto JSON)
- to_list: Model[] -> PreferenciaItem[]

Filosofia IT Valley: Mapper so converte, nunca valida.
"""

import os
import sys
import uuid
import json
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mappers.visual_preference_mapper import VisualPreferenceMapper
from models.visual_preference import VisualPreferenceModel
from dtos.visual_preference.salvar_preferencia.response import SalvarPreferenciaResponse
from dtos.visual_preference.listar_preferencias.response import PreferenciaItem


def _make_model(
    estilo: str = "dark_premium",
    aprovado: bool = True,
    contexto: str | None = None,
):
    """Cria um VisualPreferenceModel fake — sem ORM, so dados."""
    m = VisualPreferenceModel()
    m.id = uuid.uuid4()
    m.tenant_id = "t1"
    m.estilo = estilo
    m.aprovado = aprovado
    m.contexto = contexto
    m.created_at = datetime.now(timezone.utc)
    return m


class TestToSalvarResponse:
    def test_converte_model_em_salvar_response(self):
        model = _make_model(estilo="premium_dark", aprovado=True)
        resp = VisualPreferenceMapper.to_salvar_response(model)
        assert isinstance(resp, SalvarPreferenciaResponse)
        assert resp.id == model.id
        assert resp.estilo == "premium_dark"
        assert resp.aprovado is True
        assert resp.created_at == model.created_at

    def test_nao_inclui_tenant_id_na_response(self):
        """Response publica NAO expoe tenant_id."""
        model = _make_model()
        resp = VisualPreferenceMapper.to_salvar_response(model)
        assert not hasattr(resp, "tenant_id")


class TestToItem:
    def test_converte_model_em_item(self):
        model = _make_model(estilo="flat", aprovado=False)
        item = VisualPreferenceMapper.to_item(model)
        assert isinstance(item, PreferenciaItem)
        assert item.estilo == "flat"
        assert item.aprovado is False
        assert item.contexto is None

    def test_parse_contexto_json_valido(self):
        """Contexto em JSON string -> dict no PreferenciaItem."""
        ctx_json = json.dumps({"motivo": "neon demais", "nota": 3})
        model = _make_model(contexto=ctx_json)
        item = VisualPreferenceMapper.to_item(model)
        assert item.contexto == {"motivo": "neon demais", "nota": 3}

    def test_contexto_invalido_vira_none(self):
        """JSON malformado: mapper deve retornar None sem crashar."""
        model = _make_model(contexto="{isso nao eh json}")
        item = VisualPreferenceMapper.to_item(model)
        assert item.contexto is None

    def test_contexto_vazio_vira_none(self):
        model = _make_model(contexto=None)
        item = VisualPreferenceMapper.to_item(model)
        assert item.contexto is None

    def test_contexto_string_vazia_vira_none(self):
        """contexto '' eh falsy — mapper nao tenta parse."""
        model = _make_model(contexto="")
        item = VisualPreferenceMapper.to_item(model)
        assert item.contexto is None


class TestToList:
    def test_lista_vazia(self):
        assert VisualPreferenceMapper.to_list([]) == []

    def test_converte_lista_de_models(self):
        models = [
            _make_model(estilo="dark"),
            _make_model(estilo="flat"),
            _make_model(estilo="minimalista"),
        ]
        items = VisualPreferenceMapper.to_list(models)
        assert len(items) == 3
        assert [i.estilo for i in items] == ["dark", "flat", "minimalista"]
        assert all(isinstance(i, PreferenciaItem) for i in items)
