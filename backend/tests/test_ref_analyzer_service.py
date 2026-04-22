"""ref_analyzer_service: analyze-once, use-forever.

Testa:
- cache hit: doc ja tem analise_visual → retorna sem chamar Claude
- cache miss: chama Claude Vision, salva no Mongo, retorna
- doc inexistente → None (sem crash)
- Mongo indisponivel → None
- Claude falha → None (nao salva lixo)
- invalidar_cache: remove campo analise_visual
- _parse_json_seguro: tolerancia a texto envolvente
"""

import asyncio
import json

import pytest

from services import ref_analyzer_service as svc


def _run(coro):
    return asyncio.run(coro)


class _FakeCollection:
    """Mock minimal de pymongo Collection pros testes."""
    def __init__(self, docs: list[dict]):
        self.docs = docs
        self.updates: list[tuple[dict, dict]] = []

    def find_one(self, query: dict):
        for d in self.docs:
            if all(d.get(k) == v for k, v in query.items()):
                return d
        return None

    def update_one(self, query: dict, update: dict):
        class _R: modified_count = 0
        r = _R()
        for d in self.docs:
            if all(d.get(k) == v for k, v in query.items()):
                self.updates.append((query, update))
                if "$set" in update:
                    d.update(update["$set"])
                if "$unset" in update:
                    for k in update["$unset"]:
                        d.pop(k, None)
                r.modified_count = 1
                return r
        return r


class _FakeDB:
    def __init__(self, brand_assets_docs):
        self.brand_assets = _FakeCollection(brand_assets_docs)


@pytest.fixture
def mock_db(monkeypatch):
    """Retorna o FakeDB populado com uma ref; monkeypatch get_mongo_db."""
    docs = [{
        "_id": "doc1",
        "slug": "linkedin",
        "nome": "ref_sa_POST__07",
        "is_referencia": True,
        "data_uri": "data:image/jpeg;base64,FAKE_B64_DATA",
    }]
    db = _FakeDB(docs)
    monkeypatch.setattr(svc, "get_mongo_db", lambda: db)
    return db


class TestObterOuAnalisar:

    def test_cache_hit_retorna_sem_chamar_claude(self, mock_db, monkeypatch):
        """Se doc ja tem analise_visual, nao chama Claude."""
        mock_db.brand_assets.docs[0]["analise_visual"] = {"composicao": "cached"}

        async def deveria_falhar(*a, **kw):
            raise AssertionError("Claude nao deveria ter sido chamado — tinha cache")
        monkeypatch.setattr(svc, "_analisar_com_claude", deveria_falhar)

        result = _run(svc.obter_ou_analisar("linkedin", "ref_sa_POST__07", "api-key"))
        assert result == {"composicao": "cached"}

    def test_cache_miss_chama_claude_salva_e_retorna(self, mock_db, monkeypatch):
        """Sem cache: chama Claude, salva no doc, retorna."""
        analise_fake = {
            "composicao": "fundo branco + card",
            "paleta": {"fundo": "#FFFFFF"},
            "blocos_conteudo": 1,
        }

        async def fake_claude(b64, mime, key):
            assert b64 == "FAKE_B64_DATA"
            assert mime == "image/jpeg"
            assert key == "api-key"
            return analise_fake

        monkeypatch.setattr(svc, "_analisar_com_claude", fake_claude)

        result = _run(svc.obter_ou_analisar("linkedin", "ref_sa_POST__07", "api-key"))
        assert result == analise_fake
        # Persistido
        assert mock_db.brand_assets.docs[0]["analise_visual"] == analise_fake
        assert len(mock_db.brand_assets.updates) == 1

    def test_doc_inexistente_retorna_none(self, mock_db):
        result = _run(svc.obter_ou_analisar("linkedin", "nao-existe", "api-key"))
        assert result is None

    def test_mongo_indisponivel_retorna_none(self, monkeypatch):
        monkeypatch.setattr(svc, "get_mongo_db", lambda: None)
        result = _run(svc.obter_ou_analisar("x", "y", "k"))
        assert result is None

    def test_claude_falha_nao_salva(self, mock_db, monkeypatch):
        async def falhar(*a, **kw):
            return None
        monkeypatch.setattr(svc, "_analisar_com_claude", falhar)

        result = _run(svc.obter_ou_analisar("linkedin", "ref_sa_POST__07", "api-key"))
        assert result is None
        # Nao salvou lixo no doc
        assert "analise_visual" not in mock_db.brand_assets.docs[0]

    def test_doc_sem_data_uri_retorna_none(self, mock_db, monkeypatch):
        mock_db.brand_assets.docs[0]["data_uri"] = ""

        async def deveria_falhar(*a, **kw):
            raise AssertionError("sem data_uri, nao deveria chamar Claude")
        monkeypatch.setattr(svc, "_analisar_com_claude", deveria_falhar)

        result = _run(svc.obter_ou_analisar("linkedin", "ref_sa_POST__07", "api-key"))
        assert result is None

    def test_media_type_detectado_do_data_uri(self, mock_db, monkeypatch):
        """PNG e WebP sao detectados corretamente."""
        mock_db.brand_assets.docs[0]["data_uri"] = "data:image/png;base64,XXX"

        captured = {}
        async def cap(b64, mime, key):
            captured["mime"] = mime
            return {"composicao": "x"}
        monkeypatch.setattr(svc, "_analisar_com_claude", cap)

        _run(svc.obter_ou_analisar("linkedin", "ref_sa_POST__07", "k"))
        assert captured["mime"] == "image/png"


class TestInvalidarCache:

    def test_remove_analise_do_doc(self, mock_db):
        mock_db.brand_assets.docs[0]["analise_visual"] = {"composicao": "old"}

        ok = svc.invalidar_cache_analise("linkedin", "ref_sa_POST__07")
        assert ok is True
        assert "analise_visual" not in mock_db.brand_assets.docs[0]

    def test_ref_inexistente_retorna_false(self, mock_db):
        assert svc.invalidar_cache_analise("linkedin", "nao-existe") is False

    def test_mongo_indisponivel_retorna_false(self, monkeypatch):
        monkeypatch.setattr(svc, "get_mongo_db", lambda: None)
        assert svc.invalidar_cache_analise("x", "y") is False


class TestParseJson:

    def test_json_puro(self):
        assert svc._parse_json_seguro('{"a": 1}') == {"a": 1}

    def test_json_envolto_em_texto(self):
        """Claude as vezes retorna prefixo/sufixo — tolerar."""
        raw = 'Aqui esta o JSON:\n{"composicao": "teste"}\nEspero que ajude.'
        assert svc._parse_json_seguro(raw) == {"composicao": "teste"}

    def test_json_invalido_retorna_none(self):
        assert svc._parse_json_seguro("nao-eh-json") is None

    def test_string_vazia_retorna_none(self):
        assert svc._parse_json_seguro("") is None
