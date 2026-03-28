from pydantic import BaseModel


class PublicarRequest(BaseModel):
    images_base64: list[str]
    legenda_instagram: str
    texto_linkedin: str
    contas: list[str] = ["instagram_carlosviana", "instagram_itvalley", "linkedin_pessoal", "linkedin_organizacao"]
