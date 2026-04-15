from pydantic import BaseModel
from dtos.kanban_comment.criar_comentario.response import ComentarioResponse


class ListarComentariosResponse(BaseModel):
    comments: list[ComentarioResponse]
    total: int
