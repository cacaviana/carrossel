from dtos.prompt_layer.compor_prompt.response import ComporPromptResponse
from dtos.prompt_layer.preview_prompt.response import CamadaPreview, PreviewPromptResponse


class PromptLayerMapper:

    @staticmethod
    def to_compor_response(prompt_final: str, camadas_usadas: list[str], modelo: str | None) -> ComporPromptResponse:
        return ComporPromptResponse(
            prompt_final=prompt_final,
            camadas_usadas=camadas_usadas,
            modelo_sugerido=modelo,
            total_caracteres=len(prompt_final),
        )

    @staticmethod
    def to_preview_response(preview_dict: dict) -> PreviewPromptResponse:
        """Converte o dict retornado por PromptComposer.preview() em PreviewPromptResponse.

        O PromptComposer retorna chaves como camada_seguranca, camada_plataforma, etc.
        Este mapper extrai cada camada presente e monta a lista de CamadaPreview.
        """
        camada_keys = [
            ("seguranca", "camada_seguranca"),
            ("plataforma", "camada_plataforma"),
            ("marca", "camada_marca"),
            ("post", "camada_post"),
        ]
        camadas = []
        for nome, key in camada_keys:
            conteudo = preview_dict.get(key, "")
            if conteudo:
                camadas.append(CamadaPreview(nome=nome, conteudo=conteudo, chars=len(conteudo)))

        return PreviewPromptResponse(
            prompt_final=preview_dict["prompt_final"],
            camadas=camadas,
            total_caracteres=preview_dict["total_caracteres"],
            modelo_selecionado=preview_dict.get("modelo_selecionado"),
        )
