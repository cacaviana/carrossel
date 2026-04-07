from dtos.config.buscar_brand_palette.response import BuscarBrandPaletteResponse, CoresResponse
from dtos.config.buscar_creator_registry.response import BuscarCreatorRegistryResponse, CriadorResponse
from dtos.config.buscar_platform_rules.response import BuscarPlatformRulesResponse, PlataformaRuleResponse


class ConfigMapper:

    @staticmethod
    def dict_to_brand_palette(data: dict) -> BuscarBrandPaletteResponse:
        cores = data.get("cores", {})
        return BuscarBrandPaletteResponse(
            cores=CoresResponse(
                fundo_principal=cores.get("fundo_principal", "#0A0A0F"),
                destaque_primario=cores.get("destaque_primario", "#A78BFA"),
                destaque_secundario=cores.get("destaque_secundario", "#6D28D9"),
                texto_principal=cores.get("texto_principal", "#FFFFFF"),
                texto_secundario=cores.get("texto_secundario", "#94A3B8"),
            ),
            fonte=data.get("fonte", "Outfit"),
            elementos_obrigatorios=data.get("elementos_obrigatorios", []),
            estilo=data.get("estilo", "dark_mode_premium"),
        )

    @staticmethod
    def dict_to_creator_registry(data: dict) -> BuscarCreatorRegistryResponse:
        criadores = data.get("criadores", [])
        return BuscarCreatorRegistryResponse(
            criadores=[
                CriadorResponse(
                    nome=c.get("nome", ""),
                    funcao=c.get("funcao", ""),
                    plataforma=c.get("plataforma", ""),
                    url=c.get("url"),
                    ativo=c.get("ativo", True),
                )
                for c in criadores
            ]
        )

    @staticmethod
    def dict_to_platform_rules(data: dict) -> BuscarPlatformRulesResponse:
        plataformas = data.get("plataformas", [])
        return BuscarPlatformRulesResponse(
            plataformas=[
                PlataformaRuleResponse(
                    nome=p.get("nome", ""),
                    max_caracteres=p.get("max_caracteres", 0),
                    hashtags_max=p.get("hashtags_max"),
                    specs=p.get("specs"),
                )
                for p in plataformas
            ]
        )
