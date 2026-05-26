"""Testes unitarios — Rotas /brands/* (routers/config.py).

Cobre as rotas de todos os 17 casos de uso do dominio Marca:

CRUD Marca:
- GET  /api/brands                  Listar Marcas
- GET  /api/brands/{slug}           Obter Marca
- POST /api/brands                  Criar Marca
- PUT  /api/brands/{slug}           Atualizar Marca
- DELETE /api/brands/{slug}         Excluir Marca
- POST /api/brands/{slug}/clonar    Clonar Marca

Assets:
- GET    /api/brands/{slug}/foto    (Enviar Logo Marca)
- POST   /api/brands/{slug}/foto
- PUT    /api/brands/{slug}/foto
- GET    /api/brands/{slug}/assets  (Listar Assets)
- POST   /api/brands/{slug}/assets  (Enviar Ref Com/Sem Avatar)
- DELETE /api/brands/{slug}/assets/{nome} (Remover Ref)
- PUT    /api/brands/{slug}/referencia

IA:
- POST /api/analisar-referencias    (Analisar Padrao Visual Pool)
- POST /api/brands/{slug}/dna/regenerate (Regerar DNA)
- POST /api/descrever-referencia

Config:
- GET  /api/config/brand-palette    (Atualizar Paleta Cores/Fontes/Voz)
- PUT  /api/config/brand-palette

Camada opaca: router so delega pro service — testamos status codes + payload.
"""

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from routers.config import router


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router, prefix="/api")
    # slowapi precisa de state.limiter
    from middleware.rate_limiter import limiter
    app.state.limiter = limiter
    # Override get_current_user para os testes do router (JWT obrigatorio em prod)
    from tests.conftest import install_auth_override_on_app
    install_auth_override_on_app(app)
    return TestClient(app)


# ===================================================================
# Listar / Obter / Criar / Atualizar / Excluir Marca
# ===================================================================
class TestListarBrands:
    def test_retorna_lista_do_service(self, client):
        with patch("routers.config._listar_brands", return_value=[{"slug": "x", "nome": "X", "cor_principal": "#A78BFA", "cor_fundo": "#000"}]):
            resp = client.get("/api/brands")
        assert resp.status_code == 200
        assert resp.json()[0]["slug"] == "x"


class TestObterMarca:
    def test_404_quando_nao_existe(self, client):
        with patch("routers.config._buscar_brand", return_value=None):
            resp = client.get("/api/brands/nope")
        assert resp.status_code == 404

    def test_200_quando_existe(self, client):
        with patch("routers.config._buscar_brand", return_value={"slug": "x", "nome": "X"}):
            resp = client.get("/api/brands/x")
        assert resp.status_code == 200
        assert resp.json()["slug"] == "x"


class TestCriarMarca:
    def test_400_quando_slug_vazio(self, client):
        resp = client.post("/api/brands", json={"nome": "Sem slug"})
        assert resp.status_code == 400

    def test_201_quando_cria(self, client):
        with patch("routers.config._criar_brand", return_value={"slug": "novo", "nome": "N"}):
            resp = client.post("/api/brands", json={"slug": "novo", "nome": "N"})
        assert resp.status_code == 201
        assert resp.json()["slug"] == "novo"

    def test_409_quando_ja_existe(self, client):
        with patch("routers.config._criar_brand", side_effect=FileExistsError):
            resp = client.post("/api/brands", json={"slug": "existe"})
        assert resp.status_code == 409


class TestAtualizarMarca:
    def test_404_quando_service_retorna_none(self, client):
        with patch("routers.config._atualizar_brand", return_value=None):
            resp = client.put("/api/brands/nope", json={"nome": "X"})
        assert resp.status_code == 404

    def test_200_quando_atualiza(self, client):
        with patch("routers.config._atualizar_brand", return_value={"slug": "x", "nome": "novo"}):
            resp = client.put("/api/brands/x", json={"nome": "novo"})
        assert resp.status_code == 200


class TestExcluirMarca:
    def test_204_quando_deletou(self, client):
        with patch("routers.config._deletar_brand", return_value=True):
            resp = client.delete("/api/brands/x")
        assert resp.status_code == 204

    def test_404_quando_nao_existia(self, client):
        with patch("routers.config._deletar_brand", return_value=False):
            resp = client.delete("/api/brands/nope")
        assert resp.status_code == 404


class TestClonarMarca:
    def test_400_quando_falta_campos(self, client):
        resp = client.post("/api/brands/x/clonar", json={})
        assert resp.status_code == 400

    def test_404_quando_origem_nao_existe(self, client):
        with patch("routers.config._clonar_brand", side_effect=ValueError("'x' nao encontrada")):
            resp = client.post(
                "/api/brands/x/clonar",
                json={"slug_destino": "novo", "nome_destino": "Novo"},
            )
        assert resp.status_code == 404

    def test_409_quando_destino_existe(self, client):
        with patch(
            "routers.config._clonar_brand",
            side_effect=FileExistsError("'novo' ja existe"),
        ):
            resp = client.post(
                "/api/brands/x/clonar",
                json={"slug_destino": "novo", "nome_destino": "Novo"},
            )
        assert resp.status_code == 409

    def test_201_quando_clona(self, client):
        with patch(
            "routers.config._clonar_brand",
            return_value={"slug": "novo", "nome": "Novo", "mensagem": "ok"},
        ):
            resp = client.post(
                "/api/brands/x/clonar",
                json={"slug_destino": "novo", "nome_destino": "Novo"},
            )
        assert resp.status_code == 201


# ===================================================================
# Upload/Buscar Foto Marca (Enviar Logo Marca)
# ===================================================================
class TestFotoMarca:
    def test_post_foto_400_sem_body(self, client):
        resp = client.post("/api/brands/x/foto", json={})
        assert resp.status_code == 400

    def test_post_foto_ok(self, client):
        with patch(
            "routers.config._salvar_foto_brand",
            return_value={"slug": "x", "foto": "data:..."},
        ):
            resp = client.post("/api/brands/x/foto", json={"foto": "data:image/png;base64,ABC"})
        assert resp.status_code == 200

    def test_put_foto_400_sem_body(self, client):
        resp = client.put("/api/brands/x/foto", json={})
        assert resp.status_code == 400

    def test_put_foto_ok(self, client):
        with patch(
            "routers.config._salvar_foto_brand",
            return_value={"slug": "x", "foto": "data:..."},
        ):
            resp = client.put("/api/brands/x/foto", json={"foto": "data:..."})
        assert resp.status_code == 200

    def test_get_foto_ok(self, client):
        with patch(
            "routers.config._buscar_foto_brand",
            return_value={"foto": "data:image/png;base64,X"},
        ):
            resp = client.get("/api/brands/x/foto")
        assert resp.status_code == 200
        assert resp.json()["foto"].startswith("data:")

    def test_get_foto_file_404(self, client):
        with patch("services.brand_service.buscar_foto_brand_bytes", return_value=None):
            resp = client.get("/api/brands/x/foto/file")
        assert resp.status_code == 404

    def test_get_foto_file_serve_bytes(self, client):
        with patch(
            "services.brand_service.buscar_foto_brand_bytes",
            return_value=(b"\x89PNG\r\n", "image/png"),
        ):
            resp = client.get("/api/brands/x/foto/file")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/png"


# ===================================================================
# Assets da Marca (Listar, Upload, Deletar, Referencia)
# ===================================================================
class TestAssetsMarca:
    def test_listar_assets(self, client):
        with patch(
            "routers.config._listar_assets",
            return_value={"assets": [{"nome": "ref_ca_1"}], "total": 1},
        ):
            resp = client.get("/api/brands/x/assets")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_upload_asset_400_sem_imagem(self, client):
        resp = client.post("/api/brands/x/assets", json={"nome": "a"})
        assert resp.status_code == 400

    def test_upload_asset_ok(self, client):
        with patch(
            "routers.config._upload_asset",
            return_value={"nome": "ref_ca_1", "arquivo": "ref_ca_1.jpg", "pool": "com_avatar", "layout_tag": None},
        ):
            resp = client.post(
                "/api/brands/x/assets",
                json={"nome": "1", "imagem": "data:image/png;base64,ABC", "pool": "com_avatar"},
            )
        assert resp.status_code == 200
        assert resp.json()["pool"] == "com_avatar"

    def test_upload_asset_400_se_service_erra_valor(self, client):
        with patch("routers.config._upload_asset", side_effect=ValueError("pool invalido")):
            resp = client.post(
                "/api/brands/x/assets",
                json={"nome": "1", "imagem": "data:x", "pool": "nope"},
            )
        assert resp.status_code == 400

    def test_deletar_asset_ok(self, client):
        with patch("routers.config._deletar_asset", return_value={"deletado": "a"}):
            resp = client.delete("/api/brands/x/assets/a")
        assert resp.status_code == 200

    def test_deletar_asset_404(self, client):
        with patch("routers.config._deletar_asset", return_value=None):
            resp = client.delete("/api/brands/x/assets/nope")
        assert resp.status_code == 404

    def test_definir_referencia_ok(self, client):
        with patch(
            "routers.config._definir_referencia",
            return_value={"slug": "x", "referencia_imagem": "ref_1"},
        ):
            resp = client.put("/api/brands/x/referencia", json={"nome": "ref_1"})
        assert resp.status_code == 200

    def test_definir_referencia_404(self, client):
        with patch("routers.config._definir_referencia", return_value=None):
            resp = client.put("/api/brands/x/referencia", json={"nome": "nope"})
        assert resp.status_code == 404


# ===================================================================
# Analisar Padrao Visual Pool + DNA
# ===================================================================
class TestAnalisarReferencias:
    def test_400_quando_service_valida_erro(self, client):
        with patch(
            "routers.config.BrandAnalyzerService.analisar",
            new=AsyncMock(side_effect=ValueError("Envie ao menos 1 imagem")),
        ):
            resp = client.post(
                "/api/analisar-referencias",
                json={"imagens": [], "nome_marca": "", "descricao": ""},
            )
        assert resp.status_code == 400

    def test_500_quando_servico_explode(self, client):
        with patch(
            "routers.config.BrandAnalyzerService.analisar",
            new=AsyncMock(side_effect=RuntimeError("gemini off")),
        ):
            resp = client.post(
                "/api/analisar-referencias",
                json={"imagens": ["b64"], "nome_marca": "", "descricao": ""},
            )
        assert resp.status_code == 500


class TestRegenerarDnaEndpoint:
    def test_404_quando_marca_inexistente(self, client):
        with patch(
            "services.dna_generator.regenerar_dna",
            new=AsyncMock(side_effect=ValueError("nao encontrada")),
        ):
            resp = client.post("/api/brands/nope/dna/regenerate", json={})
        assert resp.status_code == 404

    def test_500_quando_gemini_key_ausente(self, client):
        with patch(
            "services.dna_generator.regenerar_dna",
            new=AsyncMock(side_effect=RuntimeError("GEMINI_API_KEY")),
        ):
            resp = client.post("/api/brands/x/dna/regenerate", json={})
        assert resp.status_code == 500

    def test_200_quando_gera(self, client):
        with patch(
            "services.dna_generator.regenerar_dna",
            new=AsyncMock(return_value={"slug": "x", "dna": {}, "refs_analisadas": {"com_avatar": 2}}),
        ):
            resp = client.post("/api/brands/x/dna/regenerate", json={})
        assert resp.status_code == 200


class TestDescreverReferencia:
    def test_400_sem_imagem(self, client):
        resp = client.post("/api/descrever-referencia", json={})
        assert resp.status_code == 400

    def test_500_quando_servico_explode(self, client):
        with patch(
            "routers.config.BrandAnalyzerService.descrever_estilo",
            new=AsyncMock(side_effect=Exception("boom")),
        ):
            resp = client.post("/api/descrever-referencia", json={"imagem": "b64"})
        assert resp.status_code == 500

    def test_200_retorna_descricao(self, client):
        with patch(
            "routers.config.BrandAnalyzerService.descrever_estilo",
            new=AsyncMock(return_value={"estilo": "dark"}),
        ):
            resp = client.post("/api/descrever-referencia", json={"imagem": "b64"})
        assert resp.status_code == 200
        assert resp.json()["estilo"] == "dark"


# ===================================================================
# Brand Palette (config) — Atualizar Paleta Cores + Fontes
# ===================================================================
class TestBrandPalette:
    def test_get_retorna_palette(self, client):
        async def fake(tenant_id=None):
            return {
                "cores": {
                    "fundo_principal": "#000",
                    "destaque_primario": "#A78BFA",
                    "destaque_secundario": "#6D28D9",
                    "texto_principal": "#FFF",
                    "texto_secundario": "#CCC",
                },
                "fonte": "Outfit",
                "elementos_obrigatorios": [],
                "estilo": "dark_mode_premium",
            }

        with patch("routers.config._config_service.buscar_brand_palette", new=fake):
            resp = client.get("/api/config/brand-palette")
        assert resp.status_code == 200
        assert resp.json()["fonte"] == "Outfit"

    def test_put_salva_palette(self, client):
        async def fake(dto, tenant_id=None):
            return {"sucesso": True, "mensagem": "salvo"}

        with patch("routers.config._config_service.salvar_brand_palette", new=fake):
            resp = client.put(
                "/api/config/brand-palette",
                json={
                    "cores": {
                        "fundo_principal": "#000",
                        "destaque_primario": "#A78BFA",
                        "destaque_secundario": "#6D28D9",
                        "texto_principal": "#FFF",
                        "texto_secundario": "#CCC",
                    },
                    "fonte": "Outfit",
                    "elementos_obrigatorios": ["foto"],
                    "estilo": "dark_mode_premium",
                },
            )
        assert resp.status_code == 200
        assert resp.json()["sucesso"] is True

    def test_put_rejeita_payload_invalido(self, client):
        """Pydantic valida antes de chamar o service (422)."""
        resp = client.put("/api/config/brand-palette", json={"fonte": "Outfit"})
        assert resp.status_code == 422
