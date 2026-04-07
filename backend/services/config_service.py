import json
from pathlib import Path

from mappers.config_mapper import ConfigMapper

CONFIGS_PATH = Path(__file__).parent.parent / "configs"


class ConfigService:

    async def buscar_brand_palette(self):
        data = ConfigService._ler_json("brand_palette.json")
        return ConfigMapper.dict_to_brand_palette(data)

    async def salvar_brand_palette(self, dto):
        data = dto.model_dump()
        ConfigService._salvar_json("brand_palette.json", data)
        return {"sucesso": True, "mensagem": "Brand palette salva"}

    async def buscar_creator_registry(self):
        data = ConfigService._ler_json("creator_registry.json")
        return ConfigMapper.dict_to_creator_registry(data)

    async def salvar_creator_registry(self, dto):
        data = dto.model_dump()
        ConfigService._salvar_json("creator_registry.json", data)
        total = len(dto.criadores)
        return {"sucesso": True, "total_criadores": total, "mensagem": f"{total} criadores salvos"}

    async def buscar_platform_rules(self):
        data = ConfigService._ler_json("platform_rules.json")
        return ConfigMapper.dict_to_platform_rules(data)

    async def salvar_platform_rules(self, dto):
        data = dto.model_dump()
        ConfigService._salvar_json("platform_rules.json", data)
        return {"sucesso": True, "mensagem": "Platform rules salvas"}

    async def buscar_plataformas(self):
        data = ConfigService._ler_json("plataformas.json")
        return data if data else {"plataformas": []}

    async def salvar_plataformas(self, dto):
        data = dto.model_dump()
        ConfigService._salvar_json("plataformas.json", data)
        return {"sucesso": True, "mensagem": f"{len(dto.plataformas)} plataformas salvas"}

    @staticmethod
    def _ler_json(filename: str) -> dict:
        path = CONFIGS_PATH / filename
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _salvar_json(filename: str, data: dict):
        CONFIGS_PATH.mkdir(exist_ok=True)
        path = CONFIGS_PATH / filename
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
