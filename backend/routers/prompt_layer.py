from fastapi import APIRouter

from dtos.prompt_layer.compor_prompt.request import ComporPromptRequest
from dtos.prompt_layer.compor_prompt.response import ComporPromptResponse
from dtos.prompt_layer.preview_prompt.request import PreviewPromptRequest
from dtos.prompt_layer.preview_prompt.response import PreviewPromptResponse
from services.prompt_layer_service import PromptLayerService

router = APIRouter(tags=["Prompt Layer"])


@router.post("/prompt-layers/compor", response_model=ComporPromptResponse)
def compor_prompt(request: ComporPromptRequest):
    return PromptLayerService.compor(request)


@router.post("/prompt-layers/preview", response_model=PreviewPromptResponse)
def preview_prompt(request: PreviewPromptRequest):
    return PromptLayerService.preview(request)
