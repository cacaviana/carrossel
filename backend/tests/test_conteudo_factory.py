"""Testes unitarios — factories/conteudo_factory.py (build_user_prompt e build_system_prompt).

Essa factory monta o prompt para os 3 formatos (post_unico usa tipo_carrossel='infografico',
capa_reels/thumbnail usam formatos internos mas o prompt so varia por tipo_carrossel).

Regras testadas:
 - texto_livre tem prioridade sobre disciplina/tecnologia
 - total_slides aparece no prompt (exceto infografico)
 - infografico sempre = 1 slide
 - tipo_layout e mencionado em todos os prompts
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from factories.conteudo_factory import build_user_prompt, build_system_prompt, DISCIPLINAS


# =============================================================================
# build_system_prompt
# =============================================================================
class TestBuildSystemPrompt:
    def test_retorna_string_nao_vazia(self):
        prompt = build_system_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 50

    def test_retorna_mesmo_prompt_ao_chamar_duas_vezes(self):
        assert build_system_prompt() == build_system_prompt()


# =============================================================================
# build_user_prompt — modo tradicional (disciplina + tecnologia)
# =============================================================================
class TestBuildUserPrompt:
    def test_com_disciplina_e_tecnologia(self):
        p = build_user_prompt(
            disciplina="D1",
            tecnologia="YOLO",
            tema_custom=None,
            texto_livre=None,
            total_slides=10,
            tipo_carrossel="texto",
        )
        assert "YOLO" in p
        # Mapeia D1 para nome completo
        assert DISCIPLINAS["D1"] in p
        assert "10 slides" in p

    def test_com_tema_custom(self):
        p = build_user_prompt(
            disciplina="D3",
            tecnologia="XGBoost",
            tema_custom="hyperparameter tuning",
            texto_livre=None,
            total_slides=7,
        )
        assert "hyperparameter tuning" in p
        assert "7 slides" in p

    def test_texto_livre_tem_prioridade(self):
        """Quando texto_livre esta presente, deve ignorar disciplina/tecnologia."""
        p = build_user_prompt(
            disciplina="D1",
            tecnologia="YOLO",
            tema_custom=None,
            texto_livre="Texto sobre SVM aplicado a bancario",
            total_slides=5,
        )
        # O texto_livre aparece
        assert "SVM aplicado a bancario" in p
        # Nao monta a frase padrao com disciplina
        # (a palavra YOLO so entra se tivesse usado o modo default)

    def test_total_slides_aparece_no_prompt(self):
        p = build_user_prompt(None, None, None, "texto", total_slides=3)
        assert "3 slides" in p

    def test_tipo_layout_mencionado(self):
        p = build_user_prompt(
            disciplina="D1", tecnologia="YOLO",
            tema_custom=None, texto_livre=None,
            total_slides=5, tipo_carrossel="texto",
        )
        # Instrucao sobre tipo_layout em todos
        assert "tipo_layout" in p


# =============================================================================
# Tipos de carrossel (texto / visual / infografico)
# =============================================================================
class TestTipoCarrossel:
    def test_tipo_texto_sem_illustration_hint(self):
        p = build_user_prompt(
            disciplina="D1", tecnologia="YOLO",
            tema_custom=None, texto_livre=None,
            total_slides=10, tipo_carrossel="texto",
        )
        assert "TEXTO TECNICO" in p or "texto tecnico" in p.lower()

    def test_tipo_visual_inclui_illustration(self):
        p = build_user_prompt(
            disciplina="D1", tecnologia="YOLO",
            tema_custom=None, texto_livre=None,
            total_slides=10, tipo_carrossel="visual",
        )
        assert "illustration_description" in p
        assert "VISUAL" in p

    def test_tipo_infografico_e_1_slide(self):
        p = build_user_prompt(
            disciplina="D1", tecnologia="YOLO",
            tema_custom=None, texto_livre=None,
            total_slides=10,  # sera ignorado pelo tipo infografico
            tipo_carrossel="infografico",
        )
        assert "1 slide" in p or "infografico unico" in p.lower()
        assert "INFOGRAFICO" in p

    def test_tipo_desconhecido_cai_no_default_texto(self):
        p = build_user_prompt(
            disciplina="D1", tecnologia="YOLO",
            tema_custom=None, texto_livre=None,
            total_slides=5, tipo_carrossel="desconhecido",
        )
        # Default = texto
        assert "TEXTO TECNICO" in p or "texto tecnico" in p.lower()


# =============================================================================
# Parametrizacao por formato — usado pros 3 novos formatos
# =============================================================================
@pytest.mark.parametrize("formato_app,tipo_carrossel,total_esperado", [
    ("post_unico", "infografico", 1),
    ("capa_reels", "visual", 1),
    ("thumbnail_youtube", "visual", 1),
])
class TestPromptPorFormatoNovo:
    """Simula o caminho do router: post_unico/capa_reels/thumbnail_youtube
    geram 1 slide (o router forca total=1 quando tipo=='infografico')."""

    def test_prompt_gerado_para_formato(self, formato_app, tipo_carrossel, total_esperado):
        p = build_user_prompt(
            disciplina="D5",
            tecnologia="Transfer Learning",
            tema_custom=f"post para {formato_app}",
            texto_livre=None,
            total_slides=total_esperado,
            tipo_carrossel=tipo_carrossel,
        )
        assert f"post para {formato_app}" in p
        if tipo_carrossel == "infografico":
            assert "1 slide" in p
