"""Testes unitarios — Services do dominio Brand (Marca).

Cobre services/brand_service.py — 17 casos de uso do dominio Marca:
1. Criar Marca            -> criar_brand
2. Listar Marcas          -> listar_brands
3. Obter Marca            -> buscar_brand
4. Atualizar Marca        -> atualizar_brand
5. Excluir Marca          -> deletar_brand_service
6. Clonar Marca           -> clonar_brand
7. Enviar Logo Marca      -> salvar_foto_brand / buscar_foto_brand
8. Listar Assets          -> listar_assets
9. Enviar Ref Com/Sem Avatar -> upload_asset (pool=com_avatar|sem_avatar)
10. Remover Ref           -> deletar_asset
11. Definir Referencia    -> definir_referencia
12. Buscar foto bytes     -> buscar_foto_brand_bytes
13. Detectar pool         -> detectar_pool

Mongo e brand_prompt_builder sao mockados — testamos apenas a logica de negocio.
"""

import os
import sys
import base64
import io
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import services.brand_service as brand_service
from services.brand_service import (
    POOL_COM_AVATAR,
    POOL_SEM_AVATAR,
    VALID_LAYOUT_TAGS,
    detectar_pool,
    _aplicar_prefixo_pool,
    _comprimir_imagem,
)


def _png_b64(size=(100, 100), color=(120, 180, 240)) -> str:
    """Gera um PNG em base64 data URI pra usar nos testes."""
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{raw}"


# ===================================================================
# detectar_pool — logica de prefixo de nome de asset
# ===================================================================
class TestDetectarPool:
    def test_prefixo_ref_ca_eh_com_avatar(self):
        assert detectar_pool("ref_ca_image1") == POOL_COM_AVATAR

    def test_prefixo_ref_sa_eh_sem_avatar(self):
        assert detectar_pool("ref_sa_image1") == POOL_SEM_AVATAR

    def test_ref_legado_cai_em_com_avatar(self):
        """ref_* (sem ca/sa) migra invisivel para com_avatar."""
        assert detectar_pool("ref_legado_123") == POOL_COM_AVATAR

    def test_nome_sem_prefixo_ref_retorna_none(self):
        """Avatares e fotos nao pertencem a pool nenhum."""
        assert detectar_pool("avatar1") is None
        assert detectar_pool("__foto__") is None
        assert detectar_pool("") is None


class TestAplicarPrefixoPool:
    def test_aplica_ref_ca(self):
        assert _aplicar_prefixo_pool("img1", POOL_COM_AVATAR) == "ref_ca_img1"

    def test_aplica_ref_sa(self):
        assert _aplicar_prefixo_pool("img1", POOL_SEM_AVATAR) == "ref_sa_img1"

    def test_remove_prefixo_anterior_antes_de_aplicar(self):
        """Se ja tem ref_ca_, troca pra ref_sa_."""
        assert _aplicar_prefixo_pool("ref_ca_img1", POOL_SEM_AVATAR) == "ref_sa_img1"
        assert _aplicar_prefixo_pool("ref_sa_img1", POOL_COM_AVATAR) == "ref_ca_img1"

    def test_ref_legado_vira_ref_ca_ou_ref_sa(self):
        assert _aplicar_prefixo_pool("ref_old", POOL_COM_AVATAR) == "ref_ca_old"
        assert _aplicar_prefixo_pool("ref_old", POOL_SEM_AVATAR) == "ref_sa_old"


# ===================================================================
# _comprimir_imagem — regra de negocio: caber em doc do Cosmos (2MB)
# ===================================================================
class TestComprimirImagem:
    def test_comprime_png_para_jpeg(self):
        img = Image.new("RGB", (500, 500), (255, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        raw = buf.getvalue()

        comprimido, mime = _comprimir_imagem(raw)
        assert mime == "image/jpeg"
        assert len(comprimido) > 0

    def test_resize_imagens_maiores_que_1600px(self):
        img = Image.new("RGB", (3200, 2400), (100, 100, 100))
        buf = io.BytesIO()
        img.save(buf, format="PNG")

        comprimido, _ = _comprimir_imagem(buf.getvalue())
        reaberta = Image.open(io.BytesIO(comprimido))
        assert max(reaberta.size) == 1600

    def test_mantem_imagens_menores_que_1600px(self):
        img = Image.new("RGB", (800, 600), (100, 100, 100))
        buf = io.BytesIO()
        img.save(buf, format="PNG")

        comprimido, _ = _comprimir_imagem(buf.getvalue())
        reaberta = Image.open(io.BytesIO(comprimido))
        assert reaberta.size == (800, 600)

    def test_rgba_vira_rgb_com_fundo_branco(self):
        """JPEG nao suporta alpha — converte pra RGB achatando."""
        img = Image.new("RGBA", (200, 200), (0, 0, 0, 128))
        buf = io.BytesIO()
        img.save(buf, format="PNG")

        comprimido, _ = _comprimir_imagem(buf.getvalue())
        reaberta = Image.open(io.BytesIO(comprimido))
        assert reaberta.mode == "RGB"


# ===================================================================
# criar_brand / atualizar_brand / buscar_brand / deletar_brand / listar
# (delegam para brand_prompt_builder — mockamos ele)
# ===================================================================
class TestCRUDBrand:
    def test_criar_brand_delega_pra_salvar_brand(self):
        with patch("services.brand_service._salvar_brand") as mock_salvar:
            mock_salvar.return_value = {"slug": "itvalley", "nome": "IT Valley"}
            result = brand_service.criar_brand("itvalley", {"nome": "IT Valley"})
        mock_salvar.assert_called_once_with("itvalley", {"nome": "IT Valley"})
        assert result["slug"] == "itvalley"

    def test_buscar_brand_delega_pra_carregar_brand(self):
        with patch("services.brand_service.carregar_brand") as mock_carregar:
            mock_carregar.return_value = {"slug": "x", "nome": "X"}
            result = brand_service.buscar_brand("x")
        assert result == {"slug": "x", "nome": "X"}

    def test_atualizar_brand_retorna_none_se_nao_existe(self):
        with patch("services.brand_service.carregar_brand", return_value=None):
            result = brand_service.atualizar_brand("nope", {"nome": "X"})
        assert result is None

    def test_atualizar_brand_salva_com_overwrite_true(self):
        with patch("services.brand_service.carregar_brand", return_value={"slug": "x"}):
            with patch("services.brand_service._salvar_brand") as mock_salvar:
                mock_salvar.return_value = {"slug": "x", "nome": "novo"}
                brand_service.atualizar_brand("x", {"nome": "novo"})
        args, kwargs = mock_salvar.call_args
        assert kwargs.get("overwrite") is True or (len(args) >= 3 and args[2] is True)

    def test_atualizar_brand_preserva_slug_no_data(self):
        with patch("services.brand_service.carregar_brand", return_value={"slug": "x"}):
            with patch("services.brand_service._salvar_brand") as mock_salvar:
                brand_service.atualizar_brand("x", {"nome": "novo"})
        data_passado = mock_salvar.call_args.args[1]
        assert data_passado["slug"] == "x"

    def test_deletar_brand_service(self):
        with patch("services.brand_service._deletar_brand", return_value=True) as mock_del:
            assert brand_service.deletar_brand_service("x") is True
        mock_del.assert_called_once_with("x")

    def test_listar_brands_enriquece_com_cores(self):
        with patch("services.brand_service._listar_brands") as mock_lista:
            with patch("services.brand_service.carregar_brand") as mock_carregar:
                mock_lista.return_value = [{"slug": "a", "nome": "A"}]
                mock_carregar.return_value = {
                    "cores": {"acento_principal": "#A78BFA", "fundo": "#0A0A0F"}
                }
                result = brand_service.listar_brands()
        assert result[0]["cor_principal"] == "#A78BFA"
        assert result[0]["cor_fundo"] == "#0A0A0F"

    def test_listar_brands_tolera_brand_sem_cores(self):
        with patch("services.brand_service._listar_brands") as mock_lista:
            with patch("services.brand_service.carregar_brand", return_value=None):
                mock_lista.return_value = [{"slug": "a", "nome": "A"}]
                result = brand_service.listar_brands()
        assert result[0]["cor_principal"] == ""


# ===================================================================
# clonar_brand — regras: sanitiza slug, rejeita colisao, copia assets
# ===================================================================
class TestClonarBrand:
    def test_rejeita_origem_inexistente(self):
        with patch("services.brand_service.carregar_brand", return_value=None):
            with pytest.raises(ValueError, match="nao encontrada"):
                brand_service.clonar_brand("inexistente", "novo", "Novo")

    def test_rejeita_destino_ja_existente(self):
        def carregar_side(slug):
            if slug == "origem":
                return {"slug": "origem", "nome": "O"}
            return {"slug": "destino"}
        with patch("services.brand_service.carregar_brand", side_effect=carregar_side):
            with pytest.raises(FileExistsError, match="ja existe"):
                brand_service.clonar_brand("origem", "destino", "Destino")

    def test_sanitiza_slug_destino(self):
        """Slug destino vira minusculo, sem espacos, so [a-z0-9-]."""
        def carregar_side(slug):
            if slug == "origem":
                return {"slug": "origem", "nome": "O"}
            return None
        with patch("services.brand_service.carregar_brand", side_effect=carregar_side):
            with patch("services.brand_service._salvar_brand"):
                with patch("services.brand_service._get_assets_col", return_value=None):
                    result = brand_service.clonar_brand("origem", "Novo Slug!@#", "N")
        assert result["slug"] == "novo-slug"

    def test_slug_destino_vazio_apos_sanitize_erra(self):
        def carregar_side(slug):
            if slug == "origem":
                return {"slug": "origem"}
            return None
        with patch("services.brand_service.carregar_brand", side_effect=carregar_side):
            with pytest.raises(ValueError, match="Slug invalido"):
                brand_service.clonar_brand("origem", "!!!", "N")

    def test_copia_assets_do_mongo(self):
        def carregar_side(slug):
            if slug == "origem":
                return {"slug": "origem", "nome": "O"}
            return None

        mock_col = MagicMock()
        mock_col.find.return_value = [
            {"slug": "origem", "nome": "logo", "data_uri": "data:..."},
            {"slug": "origem", "nome": "ref_ca_1", "data_uri": "data:..."},
        ]
        with patch("services.brand_service.carregar_brand", side_effect=carregar_side):
            with patch("services.brand_service._salvar_brand"):
                with patch("services.brand_service._get_assets_col", return_value=mock_col):
                    brand_service.clonar_brand("origem", "destino", "Destino")
        # 2 update_one (um por asset)
        assert mock_col.update_one.call_count == 2


# ===================================================================
# salvar_foto_brand / buscar_foto_brand (Enviar Logo Marca)
# ===================================================================
class TestFotoBrand:
    def test_salvar_foto_exige_mongo(self):
        foto = _png_b64()
        with patch("services.brand_service._get_assets_col", return_value=None):
            with pytest.raises(RuntimeError, match="MongoDB indisponivel"):
                brand_service.salvar_foto_brand("x", foto)

    def test_salvar_foto_faz_upsert_no_mongo(self):
        mock_col = MagicMock()
        foto = _png_b64()
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            result = brand_service.salvar_foto_brand("itvalley", foto)
        assert result["slug"] == "itvalley"
        assert result["foto"].startswith("data:image/jpeg;base64,")
        mock_col.update_one.assert_called_once()
        filtro, update = mock_col.update_one.call_args.args[:2]
        assert filtro == {"slug": "itvalley", "nome": "__foto__"}
        assert update["$set"]["is_referencia"] is False

    def test_salvar_foto_aceita_base64_sem_prefix_data_uri(self):
        mock_col = MagicMock()
        # Gera PNG puro sem prefixo
        img = Image.new("RGB", (10, 10), (0, 255, 0))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        raw_b64 = base64.b64encode(buf.getvalue()).decode()

        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            result = brand_service.salvar_foto_brand("x", raw_b64)
        assert result["foto"].startswith("data:image/jpeg;base64,")

    def test_buscar_foto_sem_mongo_retorna_none(self):
        with patch("services.brand_service._get_assets_col", return_value=None):
            assert brand_service.buscar_foto_brand("x") == {"foto": None}

    def test_buscar_foto_nao_encontrada(self):
        mock_col = MagicMock()
        mock_col.find_one.return_value = None
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            assert brand_service.buscar_foto_brand("x") == {"foto": None}

    def test_buscar_foto_encontrada(self):
        mock_col = MagicMock()
        mock_col.find_one.return_value = {
            "slug": "x",
            "nome": "__foto__",
            "data_uri": "data:image/jpeg;base64,ABC",
        }
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            assert brand_service.buscar_foto_brand("x")["foto"] == "data:image/jpeg;base64,ABC"

    def test_buscar_foto_bytes_retorna_tuple(self):
        mock_col = MagicMock()
        # data URI de um PNG 1x1 valido base64
        png_1x1 = base64.b64encode(
            io.BytesIO().getvalue() or b"\x89PNG\r\n\x1a\n"
        ).decode()
        mock_col.find_one.return_value = {
            "data_uri": f"data:image/jpeg;base64,{png_1x1}"
        }
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            result = brand_service.buscar_foto_brand_bytes("x")
        assert result is not None
        raw, mime = result
        assert mime == "image/jpeg"
        assert isinstance(raw, bytes)


# ===================================================================
# upload_asset (Enviar Ref Com/Sem Avatar, Gerenciar Avatar Pessoa)
# ===================================================================
class TestUploadAsset:
    def test_rejeita_pool_invalido(self):
        with patch("services.brand_service._get_assets_col", return_value=MagicMock()):
            with pytest.raises(ValueError, match="pool invalido"):
                brand_service.upload_asset("x", "a", _png_b64(), pool="hacker")

    def test_rejeita_layout_tag_invalido(self):
        with patch("services.brand_service._get_assets_col", return_value=MagicMock()):
            with pytest.raises(ValueError, match="layout_tag invalido"):
                brand_service.upload_asset(
                    "x", "a", _png_b64(), pool="com_avatar", layout_tag="inexistente"
                )

    def test_aceita_todos_layout_tags_validos(self):
        mock_col = MagicMock()
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            for tag in VALID_LAYOUT_TAGS:
                brand_service.upload_asset(
                    "x", f"img_{tag}", _png_b64(), pool="com_avatar", layout_tag=tag
                )

    def test_aplica_prefixo_ref_ca_quando_pool_com_avatar(self):
        mock_col = MagicMock()
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            result = brand_service.upload_asset(
                "x", "foto_jennie", _png_b64(), pool=POOL_COM_AVATAR
            )
        assert result["nome"] == "ref_ca_foto_jennie"
        assert result["pool"] == POOL_COM_AVATAR

    def test_aplica_prefixo_ref_sa_quando_pool_sem_avatar(self):
        mock_col = MagicMock()
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            result = brand_service.upload_asset(
                "x", "background", _png_b64(), pool=POOL_SEM_AVATAR
            )
        assert result["nome"] == "ref_sa_background"
        assert result["pool"] == POOL_SEM_AVATAR

    def test_sem_pool_nao_adiciona_prefixo(self):
        """Upload de avatar/foto (pool=None) preserva o nome original."""
        mock_col = MagicMock()
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            result = brand_service.upload_asset("x", "avatar_carlos", _png_b64())
        assert result["nome"] == "avatar_carlos"
        assert result["pool"] is None

    def test_exige_mongo(self):
        with patch("services.brand_service._get_assets_col", return_value=None):
            with pytest.raises(RuntimeError, match="MongoDB indisponivel"):
                brand_service.upload_asset("x", "a", _png_b64())

    def test_is_referencia_baseado_em_prefixo(self):
        mock_col = MagicMock()
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            brand_service.upload_asset("x", "img1", _png_b64(), pool=POOL_COM_AVATAR)
        doc = mock_col.update_one.call_args.args[1]["$set"]
        assert doc["is_referencia"] is True

    def test_layout_tag_salvo_no_doc_quando_passado(self):
        mock_col = MagicMock()
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            brand_service.upload_asset(
                "x", "img", _png_b64(), pool="com_avatar", layout_tag="dados"
            )
        doc = mock_col.update_one.call_args.args[1]["$set"]
        assert doc["layout_tag"] == "dados"


# ===================================================================
# deletar_asset (Remover Referencia)
# ===================================================================
class TestDeletarAsset:
    def test_sem_mongo_retorna_none(self):
        with patch("services.brand_service._get_assets_col", return_value=None):
            assert brand_service.deletar_asset("x", "a") is None

    def test_deletou_retorna_dict(self):
        mock_col = MagicMock()
        mock_col.delete_one.return_value = MagicMock(deleted_count=1)
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            assert brand_service.deletar_asset("x", "a") == {"deletado": "a"}

    def test_nao_achou_retorna_none(self):
        mock_col = MagicMock()
        mock_col.delete_one.return_value = MagicMock(deleted_count=0)
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            assert brand_service.deletar_asset("x", "nao-existe") is None


# ===================================================================
# listar_assets (Listar Assets)
# ===================================================================
class TestListarAssets:
    def test_sem_mongo_retorna_vazio(self):
        with patch("services.brand_service._get_assets_col", return_value=None):
            assert brand_service.listar_assets("x") == {"assets": [], "total": 0}

    def test_filtra_foto_da_listagem(self):
        """__foto__ nao aparece na lista de assets."""
        mock_col = MagicMock()
        mock_col.find.return_value = [
            {"slug": "x", "nome": "__foto__", "data_uri": "data:..."},
            {"slug": "x", "nome": "ref_ca_1", "data_uri": "data:..."},
        ]
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            result = brand_service.listar_assets("x")
        assert result["total"] == 1
        assert result["assets"][0]["nome"] == "ref_ca_1"

    def test_enriquece_com_pool_detectado(self):
        mock_col = MagicMock()
        mock_col.find.return_value = [
            {"slug": "x", "nome": "ref_ca_1", "data_uri": "d"},
            {"slug": "x", "nome": "ref_sa_2", "data_uri": "d"},
            {"slug": "x", "nome": "avatar", "data_uri": "d"},
        ]
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            result = brand_service.listar_assets("x")
        por_nome = {a["nome"]: a for a in result["assets"]}
        assert por_nome["ref_ca_1"]["pool"] == POOL_COM_AVATAR
        assert por_nome["ref_sa_2"]["pool"] == POOL_SEM_AVATAR
        assert por_nome["avatar"]["pool"] is None

    def test_inclui_is_referencia_default_baseado_em_prefixo(self):
        mock_col = MagicMock()
        mock_col.find.return_value = [
            {"slug": "x", "nome": "ref_ca_1", "data_uri": "d"},
            {"slug": "x", "nome": "avatar", "data_uri": "d"},
        ]
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            result = brand_service.listar_assets("x")
        por_nome = {a["nome"]: a for a in result["assets"]}
        assert por_nome["ref_ca_1"]["is_referencia"] is True
        assert por_nome["avatar"]["is_referencia"] is False


# ===================================================================
# definir_referencia
# ===================================================================
class TestDefinirReferencia:
    def test_brand_inexistente_retorna_none(self):
        with patch("services.brand_service.carregar_brand", return_value=None):
            assert brand_service.definir_referencia("x", "a") is None

    def test_atualiza_campo_referencia_imagem(self):
        with patch("services.brand_service.carregar_brand", return_value={"slug": "x"}):
            with patch("services.brand_service._salvar_brand") as mock_salvar:
                result = brand_service.definir_referencia("x", "ref_ca_1")
        assert result == {"slug": "x", "referencia_imagem": "ref_ca_1"}
        data_passada = mock_salvar.call_args.args[1]
        assert data_passada["referencia_imagem"] == "ref_ca_1"

    def test_remove_referencia_quando_nome_none(self):
        with patch("services.brand_service.carregar_brand", return_value={"slug": "x"}):
            with patch("services.brand_service._salvar_brand"):
                result = brand_service.definir_referencia("x", None)
        assert result["referencia_imagem"] is None


# ===================================================================
# buscar_asset_bytes
# ===================================================================
class TestBuscarAssetBytes:
    def test_sem_mongo_retorna_none(self):
        with patch("services.brand_service._get_assets_col", return_value=None):
            assert brand_service.buscar_asset_bytes("x", "a") is None

    def test_nao_achou_retorna_none(self):
        mock_col = MagicMock()
        mock_col.find_one.return_value = None
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            assert brand_service.buscar_asset_bytes("x", "a") is None

    def test_extrai_bytes_e_mime_do_data_uri(self):
        raw = b"\x89PNG\r\n\x1a\n"
        b64 = base64.b64encode(raw).decode()
        mock_col = MagicMock()
        mock_col.find_one.return_value = {"data_uri": f"data:image/png;base64,{b64}"}
        with patch("services.brand_service._get_assets_col", return_value=mock_col):
            result = brand_service.buscar_asset_bytes("x", "a")
        assert result is not None
        data, mime = result
        assert mime == "image/png"
        assert data == raw
