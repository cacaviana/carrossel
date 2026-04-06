from pydantic import BaseModel
from typing import Optional


class AprovarEtapaRequest(BaseModel):
    saida_editada: Optional[str] = None
