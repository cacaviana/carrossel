"""Progresso em tempo real por etapa (in-memory, sem DB)."""

_progress: dict[str, dict] = {}


def atualizar(step_id: str, atual: int, total: int, detalhe: str = ""):
    _progress[step_id] = {"atual": atual, "total": total, "detalhe": detalhe}


def buscar(step_id: str) -> dict | None:
    return _progress.get(step_id)


def limpar(step_id: str):
    _progress.pop(step_id, None)
