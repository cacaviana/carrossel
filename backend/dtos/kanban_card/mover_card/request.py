from pydantic import BaseModel


class MoverCardRequest(BaseModel):
    column_id: str
