"""Testes unitarios — factories/historico_factory.py (Factory compartilhada).

Aplica-se aos 5 casos de uso x 3 formatos (PostUnico, Reels, Thumbnail) —
a Factory e polimorfica, recebe 'formato' como string.

Regras de negocio:
 - titulo obrigatorio (ValueError se vazio/espaço)
 - tenant_id sempre presente no model
 - defaults: formato='carrossel', status='completo'
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from factories.historico_factory import HistoricoFactory


class TestHistoricoFactoryValidacao:
    """Invariantes da Factory — regras de negocio isoladas do banco."""

    def test_rejeita_titulo_vazio(self):
        with pytest.raises(ValueError, match="Titulo obrigatorio"):
            HistoricoFactory.to_model(titulo="", tenant_id="t1")

    def test_rejeita_titulo_so_espacos(self):
        with pytest.raises(ValueError, match="Titulo obrigatorio"):
            HistoricoFactory.to_model(titulo="   ", tenant_id="t1")

    def test_titulo_e_trimado(self):
        m = HistoricoFactory.to_model(titulo="  YOLO  ", tenant_id="t1")
        assert m.titulo == "YOLO"

    def test_defaults_aplicados(self):
        m = HistoricoFactory.to_model(titulo="x", tenant_id="t1")
        assert m.formato == "carrossel"
        assert m.status == "completo"
        assert m.disciplina is None
        assert m.final_score is None

    def test_tenant_id_obrigatorio_no_model(self):
        m = HistoricoFactory.to_model(titulo="x", tenant_id="tenant-abc")
        assert m.tenant_id == "tenant-abc"

    def test_cria_id_e_created_at(self):
        m = HistoricoFactory.to_model(titulo="x", tenant_id="t1")
        assert m.id is not None
        assert m.created_at is not None


# =============================================================================
# Parametrizacao por formato (Criar PostUnico, CapaReels, Thumbnail)
# =============================================================================
@pytest.mark.parametrize("formato,total_slides", [
    ("post_unico", 1),
    ("capa_reels", 1),
    ("thumbnail_youtube", 1),
    ("carrossel", 10),
])
class TestHistoricoFactoryPorFormato:
    def test_cria_historico_para_formato(self, formato, total_slides):
        m = HistoricoFactory.to_model(
            titulo=f"Titulo {formato}",
            tenant_id="t1",
            formato=formato,
            total_slides=total_slides,
        )
        assert m.formato == formato
        assert m.total_slides == total_slides

    def test_cria_com_pipeline_id(self, formato, total_slides):
        m = HistoricoFactory.to_model(
            titulo=f"x-{formato}",
            tenant_id="t1",
            formato=formato,
            total_slides=total_slides,
            pipeline_id="pipe-uuid-123",
        )
        assert m.pipeline_id == "pipe-uuid-123"

    def test_cria_com_campos_de_drive(self, formato, total_slides):
        m = HistoricoFactory.to_model(
            titulo=f"x-{formato}",
            tenant_id="t1",
            formato=formato,
            total_slides=total_slides,
            google_drive_link="https://drive.google.com/drive/folders/abc",
            google_drive_folder_name=f"{formato} - 2025-04-17",
        )
        assert "drive.google.com" in m.google_drive_link
        assert formato in m.google_drive_folder_name


class TestHistoricoFactoryRegerar:
    """Regerar = recriar model com mesmos dados (factory nao tem logica extra).

    Funciona pros 3 formatos porque o campo formato e dado de entrada.
    """

    @pytest.mark.parametrize("formato", ["post_unico", "capa_reels", "thumbnail_youtube"])
    def test_regerar_preserva_formato_e_disciplina(self, formato):
        # "regerar" — chamar factory de novo com mesmo input
        m1 = HistoricoFactory.to_model(
            titulo="YOLO Tutorial",
            tenant_id="t1",
            formato=formato,
            disciplina="D1",
            tecnologia_principal="YOLO",
        )
        m2 = HistoricoFactory.to_model(
            titulo="YOLO Tutorial",
            tenant_id="t1",
            formato=formato,
            disciplina="D1",
            tecnologia_principal="YOLO",
        )
        assert m1.formato == m2.formato == formato
        assert m1.disciplina == m2.disciplina == "D1"
        # ids diferem (cada regeneracao e um novo registro)
        assert m1.id != m2.id
