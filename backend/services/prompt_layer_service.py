from factories.prompt_composer import PromptComposer
from mappers.prompt_layer_mapper import PromptLayerMapper
from dtos.prompt_layer.compor_prompt.request import ComporPromptRequest
from dtos.prompt_layer.compor_prompt.response import ComporPromptResponse
from dtos.prompt_layer.preview_prompt.request import PreviewPromptRequest
from dtos.prompt_layer.preview_prompt.response import PreviewPromptResponse


class PromptLayerService:

    @staticmethod
    def compor(request: ComporPromptRequest) -> ComporPromptResponse:
        if request.tipo == "imagem":
            prompt = PromptComposer.compor_prompt_imagem(
                slide=request.slide,
                position=request.position,
                total=request.total,
                brand_slug=request.brand_slug,
                formato=request.formato,
            )
            modelo = PromptComposer.selecionar_modelo(
                slide=request.slide,
                position=request.position,
                total=request.total,
                formato=request.formato,
            )
            camadas = ["seguranca", "plataforma", "marca", "post"]
        else:
            prompt = PromptComposer.compor_prompt_texto(
                brand_slug=request.brand_slug,
                agente=request.agente or "copywriter",
            )
            modelo = None
            camadas = ["seguranca", "marca"]

        return PromptLayerMapper.to_compor_response(prompt, camadas, modelo)

    @staticmethod
    def preview(request: PreviewPromptRequest) -> PreviewPromptResponse:
        preview_dict = PromptComposer.preview(
            tipo=request.tipo,
            brand_slug=request.brand_slug,
            formato=request.formato,
            slide_type=request.slide_type,
            position=request.position,
            total=request.total,
        )
        return PromptLayerMapper.to_preview_response(preview_dict)
