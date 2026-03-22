"""Mapper de Drive — dict ↔ DTOs."""

from dtos.drive.salvar_drive.response import SaveCarrosselDriveResponse, PastaResponse


def dict_to_save_response(data: dict) -> SaveCarrosselDriveResponse:
    return SaveCarrosselDriveResponse(
        subfolder_name=data.get("subfolder_name", ""),
        web_view_link=data.get("web_view_link", ""),
    )


def dicts_to_pasta_list(data: list[dict]) -> list[PastaResponse]:
    return [PastaResponse(id=d["id"], name=d["name"]) for d in data]
