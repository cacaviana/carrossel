"""Testes unitarios — DTOs do dominio Brand (Marca).

Cobre validacao Pydantic dos DTOs de:
- AnalisarReferencias (request/response)
- SalvarBrandPalette (request/response) e BuscarBrandPalette (response)
- AplicarFoto (foto_overlay — request/response)
- VisualPreference (salvar_preferencia / listar_preferencias)

Filosofia IT Valley: DTO valida campos obrigatorios, tipos, defaults.
"""

import os
import sys
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dtos.brand.analisar_referencias.request import AnalisarReferenciasRequest
from dtos.brand.analisar_referencias.response import (
    AnalisarReferenciasResponse,
    CoresExtraidas,
    VisualExtraido,
)
from dtos.config.salvar_brand_palette.request import (
    CoresRequest,
    SalvarBrandPaletteRequest,
)
from dtos.config.salvar_brand_palette.response import SalvarBrandPaletteResponse
from dtos.config.buscar_brand_palette.response import (
    BuscarBrandPaletteResponse,
    CoresResponse,
)
from dtos.foto_overlay.aplicar_foto.request import AplicarFotoRequest
from dtos.foto_overlay.aplicar_foto.response import AplicarFotoResponse
from dtos.visual_preference.base import VisualPreferenceBase
from dtos.visual_preference.salvar_preferencia.request import SalvarPreferenciaRequest
from dtos.visual_preference.salvar_preferencia.response import SalvarPreferenciaResponse
from dtos.visual_preference.listar_preferencias.response import (
    ListarPreferenciasResponse,
    PreferenciaItem,
)


# ===================================================================
# AnalisarReferenciasRequest (Enviar Referencia / Analisar Padrao Visual Pool)
# ===================================================================
class TestAnalisarReferenciasRequest:
    def test_cria_com_imagens_obrigatorias(self):
        req = AnalisarReferenciasRequest(imagens=["b64a", "b64b"])
        assert req.imagens == ["b64a", "b64b"]
        assert req.nome_marca == ""
        assert req.descricao == ""

    def test_aceita_nome_e_descricao_opcionais(self):
        req = AnalisarReferenciasRequest(
            imagens=["b64"],
            nome_marca="IT Valley",
            descricao="Escola de IA",
        )
        assert req.nome_marca == "IT Valley"
        assert req.descricao == "Escola de IA"

    def test_rejeita_sem_imagens(self):
        """Pydantic nao tem list obrigatoria vazia — mas imagens eh campo obrigatorio."""
        with pytest.raises(ValidationError):
            AnalisarReferenciasRequest()

    def test_aceita_lista_vazia_mas_regra_negocio_rejeita_depois(self):
        """DTO permite lista vazia, mas BrandAnalyzer.analisar rejeita (regra de negocio no factory)."""
        req = AnalisarReferenciasRequest(imagens=[])
        assert req.imagens == []


# ===================================================================
# AnalisarReferenciasResponse — estrutura rica com cores e visual
# ===================================================================
class TestCoresExtraidas:
    def _valid(self):
        return dict(
            fundo="#0A0A0F",
            gradiente_de="#1A1A2E",
            gradiente_ate="#16213E",
            card="#1E1E2E",
            card_borda="rgba(255,255,255,0.2)",
            acento_principal="#A78BFA",
            acento_secundario="#6D28D9",
            texto_secundario="#94A3B8",
        )

    def test_cria_com_campos_minimos(self):
        c = CoresExtraidas(**self._valid())
        assert c.acento_negativo == "#F87171"
        assert c.texto_principal == "#FFFFFF"
        assert c.acento_terciario is None

    def test_aceita_acento_terciario(self):
        data = self._valid()
        data["acento_terciario"] = "#F0F0F0"
        c = CoresExtraidas(**data)
        assert c.acento_terciario == "#F0F0F0"

    def test_rejeita_sem_campo_obrigatorio(self):
        with pytest.raises(ValidationError):
            CoresExtraidas(fundo="#000000")


class TestVisualExtraido:
    def test_cria_com_todos_os_campos(self):
        v = VisualExtraido(
            estilo_fundo="gradiente escuro",
            estilo_elemento={"tipo": "wireframe"},
            estilo_card="glass morphism",
            estilo_texto="bold outfit",
            estilo_desenho="aquarela",
            regras_extras="nada neon",
        )
        assert v.estilo_elemento["tipo"] == "wireframe"

    def test_rejeita_sem_campo_obrigatorio(self):
        with pytest.raises(ValidationError):
            VisualExtraido(estilo_fundo="x")


class TestAnalisarReferenciasResponse:
    def _cores(self):
        return CoresExtraidas(
            fundo="#0A0A0F",
            gradiente_de="#1A1A2E",
            gradiente_ate="#16213E",
            card="#1E1E2E",
            card_borda="rgba(255,255,255,0.2)",
            acento_principal="#A78BFA",
            acento_secundario="#6D28D9",
            texto_secundario="#94A3B8",
        )

    def _visual(self):
        return VisualExtraido(
            estilo_fundo="gradient",
            estilo_elemento={"tipo": "wireframe"},
            estilo_card="glass",
            estilo_texto="bold",
            estilo_desenho="line-art",
            regras_extras="nada",
        )

    def test_cria_response_completo(self):
        resp = AnalisarReferenciasResponse(
            cores=self._cores(),
            visual=self._visual(),
            atmosfera="premium dark mode",
            sugestao_nome="IT Valley",
        )
        assert resp.sugestao_nome == "IT Valley"
        assert resp.cores.acento_principal == "#A78BFA"

    def test_aceita_dict_direto_para_cores_visual(self):
        """Pydantic converte dict em modelo aninhado automaticamente."""
        resp = AnalisarReferenciasResponse(
            cores=self._cores().model_dump(),
            visual=self._visual().model_dump(),
            atmosfera="x",
            sugestao_nome="y",
        )
        assert isinstance(resp.cores, CoresExtraidas)


# ===================================================================
# SalvarBrandPaletteRequest (Atualizar Paleta Cores + Fontes)
# ===================================================================
class TestCoresRequest:
    def test_cria_com_5_cores_obrigatorias(self):
        c = CoresRequest(
            fundo_principal="#000",
            destaque_primario="#A78BFA",
            destaque_secundario="#6D28D9",
            texto_principal="#FFF",
            texto_secundario="#94A3B8",
        )
        assert c.destaque_primario == "#A78BFA"

    def test_rejeita_cor_faltando(self):
        with pytest.raises(ValidationError):
            CoresRequest(fundo_principal="#000")


class TestSalvarBrandPaletteRequest:
    def _cores(self):
        return dict(
            fundo_principal="#0A0A0F",
            destaque_primario="#A78BFA",
            destaque_secundario="#6D28D9",
            texto_principal="#FFFFFF",
            texto_secundario="#94A3B8",
        )

    def test_cria_palette_valida(self):
        req = SalvarBrandPaletteRequest(
            cores=self._cores(),
            fonte="Outfit",
            elementos_obrigatorios=["foto", "logo"],
            estilo="dark_mode_premium",
        )
        assert req.fonte == "Outfit"
        assert "foto" in req.elementos_obrigatorios

    def test_rejeita_sem_fonte(self):
        with pytest.raises(ValidationError):
            SalvarBrandPaletteRequest(
                cores=self._cores(),
                elementos_obrigatorios=[],
                estilo="dark",
            )

    def test_rejeita_sem_cores(self):
        with pytest.raises(ValidationError):
            SalvarBrandPaletteRequest(
                fonte="Outfit",
                elementos_obrigatorios=[],
                estilo="dark",
            )


class TestSalvarBrandPaletteResponse:
    def test_cria_response_sucesso(self):
        r = SalvarBrandPaletteResponse(sucesso=True, mensagem="ok")
        assert r.sucesso is True
        assert r.mensagem == "ok"


class TestBuscarBrandPaletteResponse:
    def test_cria_com_palette_completa(self):
        r = BuscarBrandPaletteResponse(
            cores=CoresResponse(
                fundo_principal="#000",
                destaque_primario="#A78BFA",
                destaque_secundario="#6D28D9",
                texto_principal="#FFF",
                texto_secundario="#94A3B8",
            ),
            fonte="Outfit",
            elementos_obrigatorios=["foto"],
            estilo="dark_mode_premium",
        )
        assert r.fonte == "Outfit"


# ===================================================================
# AplicarFoto (Gerenciar Avatar Pessoa / Enviar Logo Marca — overlay)
# ===================================================================
class TestAplicarFotoRequest:
    def test_cria_com_slide_e_foto(self):
        req = AplicarFotoRequest(
            slide_image="data:image/png;base64,abc",
            foto_criador="data:image/jpeg;base64,xyz",
        )
        assert req.is_cta is False

    def test_aceita_is_cta_true(self):
        req = AplicarFotoRequest(
            slide_image="abc",
            foto_criador="xyz",
            is_cta=True,
        )
        assert req.is_cta is True

    def test_rejeita_sem_slide(self):
        with pytest.raises(ValidationError):
            AplicarFotoRequest(foto_criador="xyz")

    def test_rejeita_sem_foto_criador(self):
        with pytest.raises(ValidationError):
            AplicarFotoRequest(slide_image="abc")


class TestAplicarFotoResponse:
    def test_cria_com_image(self):
        r = AplicarFotoResponse(image="data:image/png;base64,OK")
        assert r.image.startswith("data:")


# ===================================================================
# VisualPreference (Remover/Enviar Referencia, feedback visual)
# ===================================================================
class TestVisualPreferenceBase:
    def test_cria_com_campos_obrigatorios(self):
        b = VisualPreferenceBase(estilo="premium_dark", aprovado=True)
        assert b.contexto is None

    def test_aceita_contexto_opcional(self):
        b = VisualPreferenceBase(
            estilo="flat",
            aprovado=False,
            contexto={"motivo": "muito neon"},
        )
        assert b.contexto["motivo"] == "muito neon"


class TestSalvarPreferenciaRequest:
    def test_cria_com_estilo_e_aprovado(self):
        req = SalvarPreferenciaRequest(estilo="dark_premium", aprovado=True)
        assert req.aprovado is True

    def test_rejeita_sem_estilo(self):
        with pytest.raises(ValidationError):
            SalvarPreferenciaRequest(aprovado=True)

    def test_rejeita_sem_aprovado(self):
        with pytest.raises(ValidationError):
            SalvarPreferenciaRequest(estilo="x")


class TestSalvarPreferenciaResponse:
    def test_cria_com_uuid_e_timestamp(self):
        r = SalvarPreferenciaResponse(
            id=uuid4(),
            estilo="dark",
            aprovado=True,
            created_at=datetime.now(timezone.utc),
        )
        assert r.aprovado is True


class TestListarPreferenciasResponse:
    def test_lista_vazia(self):
        r = ListarPreferenciasResponse(items=[])
        assert r.items == []

    def test_lista_com_items(self):
        r = ListarPreferenciasResponse(
            items=[
                PreferenciaItem(
                    id=uuid4(),
                    estilo="dark",
                    aprovado=True,
                    created_at=datetime.now(timezone.utc),
                )
            ]
        )
        assert len(r.items) == 1
        assert r.items[0].estilo == "dark"
