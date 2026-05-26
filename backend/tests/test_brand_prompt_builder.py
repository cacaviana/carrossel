"""Testes unitarios — services/brand_prompt_builder.py.

Cobre a persistencia do Brand Profile (JSON disco + Mongo) e a montagem do
design system text para prompts.

Casos cobertos:
- carregar_brand: mescla Mongo + disco
- salvar_brand: filtra campos pesados (_assets, _fotoPreview)
- salvar_brand: rejeita duplicata sem overwrite
- deletar_brand: remove disco
- listar_brands: mescla Mongo + disco sem duplicar
- build_design_system_text: monta texto a partir do brand profile
"""

import os
import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services import brand_prompt_builder as bpb


@pytest.fixture
def tmp_ds_dir(tmp_path, monkeypatch):
    """Substitui DS_DIR por um tmp path pra nao tocar em disco real."""
    monkeypatch.setattr(bpb, "DS_DIR", tmp_path)
    return tmp_path


def _write_disk_brand(ds_dir: Path, slug: str, data: dict) -> None:
    (ds_dir / f"{slug}.json").write_text(json.dumps(data), encoding="utf-8")


class TestCarregarBrand:
    def test_retorna_none_se_nao_existe_em_lugar_nenhum(self, tmp_ds_dir):
        """Mongo indisponivel + arquivo nao existe -> None."""
        with patch("data.repositories.mongo.brand_repository.BrandRepository.buscar", return_value=None):
            assert bpb.carregar_brand("nope") is None

    def test_carrega_do_disco_quando_mongo_indisponivel(self, tmp_ds_dir):
        _write_disk_brand(tmp_ds_dir, "itvalley", {"slug": "itvalley", "nome": "IT"})
        with patch(
            "data.repositories.mongo.brand_repository.BrandRepository.buscar",
            return_value=None,
        ):
            result = bpb.carregar_brand("itvalley")
        assert result["slug"] == "itvalley"

    def test_carrega_do_mongo_quando_disco_vazio(self, tmp_ds_dir):
        with patch(
            "data.repositories.mongo.brand_repository.BrandRepository.buscar",
            return_value={"slug": "x", "nome": "X"},
        ):
            result = bpb.carregar_brand("x")
        assert result["slug"] == "x"

    def test_mescla_mongo_sobrescreve_disco(self, tmp_ds_dir):
        """Mongo ganha em cima do disco, mas dicts nested fazem deep merge."""
        _write_disk_brand(
            tmp_ds_dir,
            "x",
            {"slug": "x", "nome": "Disco", "cores": {"fundo": "#000", "card": "#111"}},
        )
        with patch(
            "data.repositories.mongo.brand_repository.BrandRepository.buscar",
            return_value={"slug": "x", "nome": "Mongo", "cores": {"card": "#999"}},
        ):
            result = bpb.carregar_brand("x")
        assert result["nome"] == "Mongo"
        # cores.fundo do disco preservado; cores.card sobrescrito pelo Mongo
        assert result["cores"]["fundo"] == "#000"
        assert result["cores"]["card"] == "#999"

    def test_tolera_mongo_lancando_excecao(self, tmp_ds_dir):
        """Se Mongo explode, fallback pro disco."""
        _write_disk_brand(tmp_ds_dir, "x", {"slug": "x", "nome": "X"})
        with patch(
            "data.repositories.mongo.brand_repository.BrandRepository.buscar",
            side_effect=Exception("mongo off"),
        ):
            result = bpb.carregar_brand("x")
        assert result["slug"] == "x"


class TestSalvarBrand:
    def test_rejeita_duplicata_sem_overwrite(self, tmp_ds_dir):
        _write_disk_brand(tmp_ds_dir, "x", {"slug": "x", "nome": "X"})
        with patch(
            "data.repositories.mongo.brand_repository.BrandRepository.buscar",
            return_value=None,
        ):
            with patch(
                "data.repositories.mongo.brand_repository.BrandRepository.salvar"
            ):
                with pytest.raises(FileExistsError, match="ja existe"):
                    bpb.salvar_brand("x", {"nome": "novo"})

    def test_aceita_overwrite_true(self, tmp_ds_dir):
        _write_disk_brand(tmp_ds_dir, "x", {"slug": "x", "nome": "X"})
        mock_save = MagicMock()
        with patch(
            "data.repositories.mongo.brand_repository.BrandRepository.buscar",
            return_value=None,
        ):
            with patch(
                "data.repositories.mongo.brand_repository.BrandRepository.salvar",
                mock_save,
            ):
                bpb.salvar_brand("x", {"nome": "novo"}, overwrite=True)
        # Confere que gravou no disco
        saved = json.loads((tmp_ds_dir / "x.json").read_text(encoding="utf-8"))
        assert saved["nome"] == "novo"
        assert saved["slug"] == "x"

    def test_filtra_campos_pesados_do_disco_e_mongo(self, tmp_ds_dir):
        mock_save = MagicMock()
        with patch(
            "data.repositories.mongo.brand_repository.BrandRepository.buscar",
            return_value=None,
        ):
            with patch(
                "data.repositories.mongo.brand_repository.BrandRepository.salvar",
                mock_save,
            ):
                bpb.salvar_brand(
                    "novo",
                    {
                        "nome": "N",
                        "_assets": ["heavy"],
                        "_fotoPreview": "data:...",
                        "_foto_base64": "base64pesado",
                        "cores": {"fundo": "#000"},
                    },
                )
        saved_mongo = mock_save.call_args.args[0]
        assert "_assets" not in saved_mongo
        assert "_fotoPreview" not in saved_mongo
        assert "_foto_base64" not in saved_mongo

        saved_disco = json.loads((tmp_ds_dir / "novo.json").read_text(encoding="utf-8"))
        assert "_assets" not in saved_disco
        assert "_fotoPreview" not in saved_disco

    def test_tolera_mongo_off_e_salva_so_no_disco(self, tmp_ds_dir):
        with patch(
            "data.repositories.mongo.brand_repository.BrandRepository.buscar",
            return_value=None,
        ):
            with patch(
                "data.repositories.mongo.brand_repository.BrandRepository.salvar",
                side_effect=Exception("mongo off"),
            ):
                # Nao deve crashar
                bpb.salvar_brand("x", {"nome": "X"})
        assert (tmp_ds_dir / "x.json").exists()


class TestDeletarBrand:
    def test_deleta_do_disco(self, tmp_ds_dir):
        _write_disk_brand(tmp_ds_dir, "x", {"slug": "x"})
        with patch(
            "data.repositories.mongo.brand_repository.BrandRepository.deletar",
            return_value=False,
        ):
            assert bpb.deletar_brand("x") is True
        assert not (tmp_ds_dir / "x.json").exists()

    def test_retorna_false_se_nao_existe(self, tmp_ds_dir):
        with patch(
            "data.repositories.mongo.brand_repository.BrandRepository.deletar",
            return_value=False,
        ):
            assert bpb.deletar_brand("nope") is False


class TestListarBrands:
    def test_lista_vazia(self, tmp_ds_dir):
        with patch(
            "data.repositories.mongo.brand_repository.BrandRepository.listar",
            return_value=[],
        ):
            assert bpb.listar_brands() == []

    def test_mescla_mongo_e_disco_sem_duplicar(self, tmp_ds_dir):
        _write_disk_brand(tmp_ds_dir, "itvalley", {"slug": "itvalley", "nome": "IT"})
        _write_disk_brand(tmp_ds_dir, "doceria", {"slug": "doceria", "nome": "Doceria"})
        with patch(
            "data.repositories.mongo.brand_repository.BrandRepository.listar",
            return_value=[{"slug": "itvalley", "nome": "IT-Mongo"}],
        ):
            result = bpb.listar_brands()
        slugs = [b["slug"] for b in result]
        assert sorted(slugs) == ["doceria", "itvalley"]
        # Mongo tem prioridade pro nome do itvalley
        it = next(b for b in result if b["slug"] == "itvalley")
        assert it["nome"] == "IT-Mongo"


class TestBuildDesignSystemText:
    def test_brand_completo_inclui_todos_partes(self):
        brand = {
            "cores": {
                "acento_principal": "#A78BFA",
                "acento_secundario": "#6D28D9",
                "acento_terciario": "#F0F0F0",
                "acento_negativo": "#F87171",
                "texto_principal": "#FFF",
                "texto_secundario": "#CCC",
                "card": "#1E1E2E",
                "card_borda": "rgba(0,0,0,0.2)",
            },
            "visual": {
                "estilo_fundo": "GRADIENT_FUNDO",
                "estilo_elemento": {
                    "tipo": "wireframe",
                    "linhas": "finas",
                    "complexidade": "media",
                    "profundidade": "2D",
                    "opacidade": "80%",
                    "tematico": "cientifico",
                },
                "estilo_card": "GLASS_CARD",
                "estilo_texto": "BOLD_TEXTO",
                "regras_extras": "NADA_NEON",
            },
        }
        text = bpb.build_design_system_text(brand)
        assert "GRADIENT_FUNDO" in text
        assert "GLASS_CARD" in text
        assert "BOLD_TEXTO" in text
        assert "NADA_NEON" in text
        assert "#A78BFA" in text
        assert "ELEMENTO DECORATIVO" in text
        assert "[seed:" in text

    def test_elemento_string_tambem_aceito(self):
        brand = {
            "cores": {},
            "visual": {"estilo_elemento": "elemento simples string"},
        }
        text = bpb.build_design_system_text(brand)
        assert "ELEMENTO DECORATIVO: elemento simples string" in text

    def test_brand_vazio_nao_crasha(self):
        text = bpb.build_design_system_text({})
        assert "REGRA CRITICA" in text
        assert "[seed:" in text

    def test_inclui_regra_critica_de_texto(self):
        text = bpb.build_design_system_text({})
        assert "DEVE ser renderizado" in text
        assert "NAO alterar, NAO traduzir" in text
