"""Integracao Kanban Card Deadline + Calendario.

Casos de uso:
- PATCH /api/kanban/cards/{id}  com campo deadline   (ClickUp Atribuir Prazo Publicacao 86e0y9gm4)
- GET /api/kanban/cards/calendario?mes=YYYY-MM       (ClickUp Listar Historico Calendario 86e0y9gj7)

Criterios:
- Campo deadline aceito no DTO e persistido
- Calendario filtra cards com deadline dentro do mes
- Response contem card_id, title, deadline, column_id, priority, pipeline_id, pdf_url
"""

from datetime import datetime, timezone

import pytest
from bson import ObjectId


FIXED_USER = "507f1f77bcf86cd799439011"
FIXED_TENANT = "tenant-A"


def _card_doc(title="Card Teste", deadline=None, column_id="col-copy", priority="media"):
    now = datetime.now(timezone.utc)
    return {
        "tenant_id": FIXED_TENANT,
        "board_id": "board-1",
        "column_id": column_id,
        "title": title,
        "copy_text": None,
        "disciplina": None,
        "tecnologia": None,
        "priority": priority,
        "assigned_user_ids": [],
        "created_by": FIXED_USER,
        "pipeline_id": None,
        "drive_link": None,
        "drive_folder_name": None,
        "pdf_url": None,
        "image_urls": [],
        "order_in_column": 0,
        "deadline": deadline,
        "created_at": now,
        "updated_at": None,
        "archived_at": None,
    }


class TestAtualizarCardDeadline:
    """PATCH /api/kanban/cards/{id} aceita campo deadline."""

    def test_dto_aceita_deadline_como_iso_string(self):
        from dtos.kanban_card.atualizar_card.request import AtualizarCardRequest
        dto = AtualizarCardRequest(deadline="2026-05-15T10:00:00+00:00")
        assert dto.deadline is not None
        assert dto.deadline.year == 2026
        assert dto.deadline.month == 5
        assert dto.deadline.day == 15

    def test_dto_aceita_deadline_none(self):
        from dtos.kanban_card.atualizar_card.request import AtualizarCardRequest
        dto = AtualizarCardRequest(title="Novo titulo")
        assert dto.deadline is None

    def test_factory_inclui_deadline_em_update_fields(self):
        """KanbanCardFactory.to_update_fields deve incluir deadline quando presente."""
        from dtos.kanban_card.atualizar_card.request import AtualizarCardRequest
        from factories.kanban_card_factory import KanbanCardFactory

        dto = AtualizarCardRequest(deadline="2026-05-15T10:00:00+00:00")
        fields = KanbanCardFactory.to_update_fields(dto)
        assert "deadline" in fields
        assert fields["deadline"].year == 2026

    def test_factory_nao_inclui_deadline_quando_none(self):
        from dtos.kanban_card.atualizar_card.request import AtualizarCardRequest
        from factories.kanban_card_factory import KanbanCardFactory

        dto = AtualizarCardRequest(title="Novo titulo")
        fields = KanbanCardFactory.to_update_fields(dto)
        assert "deadline" not in fields

    def test_response_serializa_deadline(self, mock_mongo):
        """CardResponse expoe deadline no body."""
        from mappers.kanban_card_mapper import KanbanCardMapper
        dt = datetime(2026, 5, 15, 10, 0, tzinfo=timezone.utc)
        doc = _card_doc(deadline=dt)
        doc["_id"] = ObjectId()
        resp = KanbanCardMapper.to_response(doc)
        assert resp.deadline is not None
        assert resp.deadline.year == 2026
        assert resp.deadline.day == 15


class TestCalendario:
    """GET /api/kanban/cards/calendario?mes=YYYY-MM."""

    def test_mes_invalido_retorna_422(self, client, admin_headers):
        resp = client.get("/api/kanban/cards/calendario?mes=2026-13", headers=admin_headers)
        assert resp.status_code == 422

    def test_mes_sem_formato_retorna_422(self, client, admin_headers):
        resp = client.get("/api/kanban/cards/calendario?mes=abril", headers=admin_headers)
        assert resp.status_code == 422

    def test_retorna_vazio_quando_sem_cards(self, client, admin_headers, mock_mongo):
        resp = client.get("/api/kanban/cards/calendario?mes=2026-05", headers=admin_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["mes"] == "2026-05"
        assert body["total"] == 0
        assert body["items"] == []

    def test_retorna_cards_com_deadline_no_mes(self, client, admin_headers, mock_mongo):
        mock_mongo.kanban_cards.insert_many([
            _card_doc(title="Card Maio 10", deadline=datetime(2026, 5, 10, 12, 0, tzinfo=timezone.utc)),
            _card_doc(title="Card Maio 28", deadline=datetime(2026, 5, 28, 18, 0, tzinfo=timezone.utc)),
            _card_doc(title="Card Abril", deadline=datetime(2026, 4, 15, 10, 0, tzinfo=timezone.utc)),
            _card_doc(title="Card sem deadline", deadline=None),
        ])

        resp = client.get("/api/kanban/cards/calendario?mes=2026-05", headers=admin_headers)
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["total"] == 2
        titles = [i["title"] for i in body["items"]]
        assert "Card Maio 10" in titles
        assert "Card Maio 28" in titles
        # Card Abril e sem_deadline nao devem aparecer
        assert "Card Abril" not in titles
        assert "Card sem deadline" not in titles

    def test_items_ordenados_por_deadline_ascendente(self, client, admin_headers, mock_mongo):
        mock_mongo.kanban_cards.insert_many([
            _card_doc(title="Dia 28", deadline=datetime(2026, 5, 28, 12, 0, tzinfo=timezone.utc)),
            _card_doc(title="Dia 05", deadline=datetime(2026, 5, 5, 9, 0, tzinfo=timezone.utc)),
            _card_doc(title="Dia 15", deadline=datetime(2026, 5, 15, 15, 0, tzinfo=timezone.utc)),
        ])
        resp = client.get("/api/kanban/cards/calendario?mes=2026-05", headers=admin_headers)
        assert resp.status_code == 200
        titles = [i["title"] for i in resp.json()["items"]]
        assert titles == ["Dia 05", "Dia 15", "Dia 28"]

    def test_response_inclui_campos_obrigatorios(self, client, admin_headers, mock_mongo):
        mock_mongo.kanban_cards.insert_one(_card_doc(
            title="Teste",
            deadline=datetime(2026, 5, 10, tzinfo=timezone.utc),
            column_id="col-design",
            priority="alta",
        ))
        body = client.get("/api/kanban/cards/calendario?mes=2026-05", headers=admin_headers).json()
        assert body["total"] == 1
        item = body["items"][0]
        for campo in ("card_id", "title", "deadline", "column_id", "priority", "pipeline_id", "pdf_url"):
            assert campo in item
        assert item["priority"] == "alta"
        assert item["column_id"] == "col-design"

    def test_isolamento_tenant(self, client, admin_headers, mock_mongo):
        """Card de outro tenant nao aparece no calendario."""
        doc = _card_doc(title="Alheio", deadline=datetime(2026, 5, 10, tzinfo=timezone.utc))
        doc["tenant_id"] = "tenant-outro"
        mock_mongo.kanban_cards.insert_one(doc)
        body = client.get("/api/kanban/cards/calendario?mes=2026-05", headers=admin_headers).json()
        assert body["total"] == 0

    def test_archivados_nao_aparecem(self, client, admin_headers, mock_mongo):
        doc = _card_doc(title="Archivado", deadline=datetime(2026, 5, 10, tzinfo=timezone.utc))
        doc["archived_at"] = datetime.now(timezone.utc)
        mock_mongo.kanban_cards.insert_one(doc)
        body = client.get("/api/kanban/cards/calendario?mes=2026-05", headers=admin_headers).json()
        assert body["total"] == 0


class TestContratoCalendario:
    def test_rota_registrada(self, client):
        paths = client.get("/openapi.json").json()["paths"]
        assert "/api/kanban/cards/calendario" in paths
        assert "get" in paths["/api/kanban/cards/calendario"]

    def test_response_schema(self, client):
        schemas = client.get("/openapi.json").json()["components"]["schemas"]
        s = schemas["ListarCalendarioResponse"]
        props = set(s["properties"].keys())
        assert {"mes", "total", "items"}.issubset(props)
