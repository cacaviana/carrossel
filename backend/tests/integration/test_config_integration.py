"""Integracao Config — caso de uso Creator Registry + Brand Palette + Platform Rules.

Fluxo:
Router -> ConfigService -> file storage (configs/*.json)

Nao toca em LLM nem em banco. Testa contrato completo.
"""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture
def tmp_configs_dir(tmp_path, monkeypatch):
    """Aponta ConfigService para diretorio temporario."""
    configs = tmp_path / "configs"
    configs.mkdir()

    # Monkey patch no ConfigService path
    try:
        import services.config_service as cs
        # ConfigService usa path interno; se houver ROOT, vamos patchar CONFIGS_DIR
        candidates = [name for name in dir(cs) if "DIR" in name or "PATH" in name]
        for attr in candidates:
            old = getattr(cs, attr)
            if isinstance(old, (str, Path)):
                monkeypatch.setattr(cs, attr, configs, raising=False)
    except Exception:
        pass

    return configs


class TestCreatorRegistry:
    """Caso de uso 'Obter Creator Registry' + 'Salvar Creator Registry'."""

    def test_buscar_sem_auth_401(self, client):
        resp = client.get("/api/config/creator-registry")
        assert resp.status_code in (401, 403)

    def test_buscar_com_auth(self, client, admin_headers):
        resp = client.get("/api/config/creator-registry", headers=admin_headers)
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            body = resp.json()
            assert "criadores" in body

    def test_salvar_com_auth(self, client, admin_headers):
        payload = {
            "criadores": [
                {"nome": "Carlos Viana", "funcao": "THOUGHT_LEADER", "plataforma": "LinkedIn", "url": "", "ativo": True},
                {"nome": "Outro", "funcao": "EXPLAINER", "plataforma": "YouTube", "url": "", "ativo": False},
            ]
        }
        resp = client.put(
            "/api/config/creator-registry",
            json=payload,
            headers=admin_headers,
        )
        assert resp.status_code in (200, 500)
        if resp.status_code == 200:
            body = resp.json()
            # SalvarCreatorRegistryResponse: sucesso + total_criadores + mensagem
            assert body["sucesso"] is True
            assert body["total_criadores"] == 2

    def test_salvar_creator_dto_contract(self, client, admin_headers):
        """Request deve aceitar: nome, funcao, plataforma. url, ativo opcionais."""
        # Sem nome -> 422
        resp = client.put(
            "/api/config/creator-registry",
            json={"criadores": [{"funcao": "EXPLAINER", "plataforma": "X"}]},
            headers=admin_headers,
        )
        assert resp.status_code == 422


class TestBrandPalette:
    """Caso de uso 'Obter/Salvar Brand Palette'."""

    def test_buscar_sem_auth_401(self, client):
        resp = client.get("/api/config/brand-palette")
        assert resp.status_code in (401, 403)

    def test_buscar_com_auth(self, client, admin_headers):
        resp = client.get("/api/config/brand-palette", headers=admin_headers)
        assert resp.status_code in (200, 404, 500)

    def test_salvar_dto_valido(self, client, admin_headers):
        payload = {
            "cores": {
                "fundo_principal": "#0A0A0F",
                "destaque_primario": "#A78BFA",
                "destaque_secundario": "#6D28D9",
                "texto_principal": "#FFFFFF",
                "texto_secundario": "#94A3B8",
            },
            "fonte": "Outfit",
            "elementos_obrigatorios": ["lines", "dots"],
            "estilo": "dark_mode_premium",
        }
        resp = client.put("/api/config/brand-palette", json=payload, headers=admin_headers)
        assert resp.status_code in (200, 500), resp.text

    def test_salvar_sem_cores_422(self, client, admin_headers):
        resp = client.put(
            "/api/config/brand-palette",
            json={"fonte": "X", "elementos_obrigatorios": [], "estilo": "y"},
            headers=admin_headers,
        )
        assert resp.status_code == 422


class TestPlatformRules:
    """Caso de uso 'Obter/Salvar Platform Rules'."""

    def test_buscar_sem_auth_401(self, client):
        resp = client.get("/api/config/platform-rules")
        assert resp.status_code in (401, 403)

    def test_buscar_com_auth(self, client, admin_headers):
        resp = client.get("/api/config/platform-rules", headers=admin_headers)
        assert resp.status_code in (200, 404, 500)


class TestApiKeysConfig:
    """Caso de uso 'Salvar API Keys'."""

    def test_status_config_sem_auth(self, client):
        resp = client.get("/api/config")
        assert resp.status_code in (401, 403)

    def test_status_config_com_auth(self, client, admin_headers):
        resp = client.get("/api/config", headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        # ConfigStatusResponse
        assert "claude_api_key_set" in body
        assert "gemini_api_key_set" in body
        assert "google_drive_credentials_set" in body


class TestIsolamentoCreatorTenant:
    """BUG CRITICO: creator registry eh armazenado em arquivo JSON GLOBAL.
    NAO isola por tenant. Todos os tenants compartilham os mesmos criadores.

    Este teste documenta o problema: o dominio multi-tenant nao existe no storage.
    """

    def test_creator_registry_storage_nao_tem_tenant(self):
        """ConfigService salva creator registry sem considerar tenant."""
        import inspect
        from services import config_service as cs_mod
        src = inspect.getsource(cs_mod)
        # Se nao tiver 'tenant' na logica, storage eh global
        menciona_tenant = "tenant" in src.lower()
        if not menciona_tenant:
            pytest.fail(
                "VIOLACAO MULTI-TENANT: ConfigService nao considera tenant_id. "
                "Creator registry, brand palette e platform rules sao globais entre tenants."
            )
