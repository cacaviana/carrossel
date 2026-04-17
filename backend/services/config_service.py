import json
from pathlib import Path

from mappers.config_mapper import ConfigMapper

CONFIGS_PATH = Path(__file__).parent.parent / "configs"

# Tenant default usado quando nenhum tenant_id for passado (back-compat) e tambem
# como destino da migracao de arquivos globais preexistentes.
DEFAULT_TENANT_ID = "itvalley"


class ConfigService:
    """Persistencia de configuracoes por tenant.

    INT-04 fix — cada tenant tem seu proprio namespace de arquivos:
        configs/
          brand_palette.json          (legado global — migrado para itvalley/ na primeira leitura)
          creator_registry.json       (legado global — idem)
          platform_rules.json         (legado global — idem)
          {tenant_id}/
            brand_palette.json
            creator_registry.json
            platform_rules.json
            plataformas.json
    """

    async def buscar_brand_palette(self, tenant_id: str | None = None):
        data = ConfigService._ler_json("brand_palette.json", tenant_id)
        return ConfigMapper.dict_to_brand_palette(data)

    async def salvar_brand_palette(self, dto, tenant_id: str | None = None):
        data = dto.model_dump()
        ConfigService._salvar_json("brand_palette.json", data, tenant_id)
        return {"sucesso": True, "mensagem": "Brand palette salva"}

    async def buscar_creator_registry(self, tenant_id: str | None = None):
        data = ConfigService._ler_json("creator_registry.json", tenant_id)
        return ConfigMapper.dict_to_creator_registry(data)

    async def salvar_creator_registry(self, dto, tenant_id: str | None = None):
        data = dto.model_dump()
        ConfigService._salvar_json("creator_registry.json", data, tenant_id)
        total = len(dto.criadores)
        return {"sucesso": True, "total_criadores": total, "mensagem": f"{total} criadores salvos"}

    async def buscar_platform_rules(self, tenant_id: str | None = None):
        data = ConfigService._ler_json("platform_rules.json", tenant_id)
        return ConfigMapper.dict_to_platform_rules(data)

    async def salvar_platform_rules(self, dto, tenant_id: str | None = None):
        data = dto.model_dump()
        ConfigService._salvar_json("platform_rules.json", data, tenant_id)
        return {"sucesso": True, "mensagem": "Platform rules salvas"}

    async def buscar_plataformas(self, tenant_id: str | None = None):
        data = ConfigService._ler_json("plataformas.json", tenant_id)
        return data if data else {"plataformas": []}

    async def salvar_plataformas(self, dto, tenant_id: str | None = None):
        data = dto.model_dump()
        ConfigService._salvar_json("plataformas.json", data, tenant_id)
        return {"sucesso": True, "mensagem": f"{len(dto.plataformas)} plataformas salvas"}

    # -----------------------------------------------------------------
    # Helpers privados de IO por tenant
    # -----------------------------------------------------------------
    @staticmethod
    def _tenant_dir(tenant_id: str | None) -> Path:
        """Pasta do tenant dentro de CONFIGS_PATH. Usa DEFAULT_TENANT_ID se None."""
        tid = tenant_id or DEFAULT_TENANT_ID
        return CONFIGS_PATH / tid

    @staticmethod
    def _path(filename: str, tenant_id: str | None) -> Path:
        return ConfigService._tenant_dir(tenant_id) / filename

    @staticmethod
    def _migrar_arquivo_global(filename: str, tenant_id: str | None) -> None:
        """Se existir um arquivo no nivel de CONFIGS_PATH (legado global) e nao
        existir copia para o tenant, copia para tenant_dir antes de ler/escrever.

        Nunca sobrescreve arquivo ja existente no tenant.
        So aplica a migracao para o tenant default (evita propagar dados globais
        pra tenants novos).
        """
        tid = tenant_id or DEFAULT_TENANT_ID
        if tid != DEFAULT_TENANT_ID:
            return
        legacy = CONFIGS_PATH / filename
        target = ConfigService._path(filename, tid)
        if legacy.exists() and not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(legacy.read_text(encoding="utf-8"), encoding="utf-8")

    @staticmethod
    def _ler_json(filename: str, tenant_id: str | None = None) -> dict:
        ConfigService._migrar_arquivo_global(filename, tenant_id)
        path = ConfigService._path(filename, tenant_id)
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _salvar_json(filename: str, data: dict, tenant_id: str | None = None):
        ConfigService._migrar_arquivo_global(filename, tenant_id)
        path = ConfigService._path(filename, tenant_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
