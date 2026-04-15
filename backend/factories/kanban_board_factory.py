from datetime import datetime, timezone


COLUNAS_MVP = [
    {"id": "col-copy",      "name": "Copy",       "order": 0, "color": "#3B82F6"},
    {"id": "col-design",    "name": "Design",      "order": 1, "color": "#8B5CF6"},
    {"id": "col-revisao",   "name": "Revisao",     "order": 2, "color": "#EAB308"},
    {"id": "col-aprovado",  "name": "Aprovado",    "order": 3, "color": "#22C55E"},
    {"id": "col-publicado", "name": "Publicado",   "order": 4, "color": "#15803D"},
    {"id": "col-cancelado", "name": "Cancelado",   "order": 5, "color": "#6B7280"},
]

COLUNAS_TERMINAIS = {"col-publicado", "col-cancelado"}
COLUNA_COPY = "col-copy"
COLUNA_DESIGN = "col-design"
COLUNA_REVISAO = "col-revisao"
COLUNA_APROVADO = "col-aprovado"
COLUNA_PUBLICADO = "col-publicado"
COLUNA_CANCELADO = "col-cancelado"


class KanbanBoardFactory:

    @staticmethod
    def criar_board_padrao(tenant_id: str) -> dict:
        return {
            "tenant_id": tenant_id,
            "name": "Pipeline de Carrosseis",
            "columns": [col.copy() for col in COLUNAS_MVP],
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
        }

    @staticmethod
    def validar_coluna_destino(column_id: str, column_origem_id: str):
        if column_origem_id in COLUNAS_TERMINAIS:
            raise ValueError("Card em coluna terminal nao pode ser movido")
        if column_id != COLUNA_CANCELADO:
            raise ValueError(
                "Movimentacao manual so e permitida para a coluna Cancelado. "
                "Demais movimentacoes sao automaticas via pipeline."
            )

    @staticmethod
    def validar_movimentacao_pipeline(column_destino: str):
        colunas_validas = {c["id"] for c in COLUNAS_MVP}
        if column_destino not in colunas_validas:
            raise ValueError(f"Coluna destino invalida: {column_destino}")
