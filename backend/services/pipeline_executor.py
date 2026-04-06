import os
import json
from datetime import datetime, timezone

from services.pipeline_db_service import (
    buscar_proxima_etapa,
    buscar_etapas_anteriores,
    atualizar_etapa,
    atualizar_pipeline,
)
from services.config_service import ConfigService

from agents.strategist import executar as executar_strategist
from agents.copywriter import executar as executar_copywriter
from agents.hook_specialist import executar as executar_hook_specialist
from agents.art_director import executar as executar_art_director
from services.imagem_service import gerar_imagens as gerar_imagens_v9
from agents.content_critic import executar as executar_content_critic
from skills.brand_validator import validar as brand_validar
from skills.brand_overlay import aplicar as brand_overlay_aplicar


async def executar_proxima_etapa(pipeline_id: str, tenant_id: str = "") -> dict:
    if not tenant_id:
        from config import settings
        tenant_id = settings.TENANT_ID
    """Executa a proxima etapa pendente do pipeline.

    Retorna dict com informacoes da etapa executada.
    Raises ValueError se nao ha etapa pendente.
    """
    pipeline, step = await buscar_proxima_etapa(pipeline_id, tenant_id)

    if not pipeline:
        raise ValueError("Pipeline nao encontrado")

    if not step:
        raise ValueError("Nenhuma etapa pendente para executar")

    agente = step["agente"]
    step_id = str(step["id"])
    ordem = step["ordem"]
    formato = pipeline["formato"]
    tema = pipeline["tema"]
    modo_funil = bool(pipeline["modo_funil"])
    brand_slug = pipeline.get("brand_slug")
    avatar_mode = pipeline.get("avatar_mode", "livre")

    # Marcar etapa como em execucao
    now = datetime.now(timezone.utc)
    await atualizar_etapa(step_id, {
        "status": "executando",
        "started_at": now,
    })
    await atualizar_pipeline(pipeline_id, {
        "status": "executando",
        "etapa_atual": agente,
    })

    # Buscar saidas anteriores
    etapas_anteriores = await buscar_etapas_anteriores(pipeline_id, ordem)
    context = _build_context(etapas_anteriores)

    # Se esta etapa foi rejeitada, incluir o feedback no context
    feedback_rejeicao = step.get("erro_mensagem", "")
    if feedback_rejeicao and feedback_rejeicao != "Rejeitado pelo usuario":
        context["_feedback_rejeicao"] = feedback_rejeicao

    try:
        saida = await _executar_agente(
            agente=agente,
            tema=tema,
            formato=formato,
            modo_funil=modo_funil,
            context=context,
            pipeline=pipeline,
            step_id=step_id,
            brand_slug=brand_slug,
            avatar_mode=avatar_mode,
        )

        saida_json = json.dumps(saida, ensure_ascii=False)
        entrada_json = json.dumps(
            _build_entrada(agente, tema, context), ensure_ascii=False
        )

        # Determinar status final
        status_final = "aguardando_aprovacao"
        if agente == "content_critic":
            status_final = "completo"

        finished_at = datetime.now(timezone.utc)
        await atualizar_etapa(step_id, {
            "status": status_final,
            "entrada": entrada_json,
            "saida": saida_json,
            "finished_at": finished_at,
        })

        # Se content_critic, pipeline completo
        if agente == "content_critic":
            await atualizar_pipeline(pipeline_id, {"status": "completo"})
        else:
            await atualizar_pipeline(pipeline_id, {"status": "aguardando_aprovacao"})

        return {
            "pipeline_id": pipeline_id,
            "etapa": agente,
            "ordem": ordem,
            "status": status_final,
            "saida": saida,
        }

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[EXECUTOR ERROR] {agente}: {tb}")
        finished_at = datetime.now(timezone.utc)
        await atualizar_etapa(step_id, {
            "status": "erro",
            "erro_mensagem": f"{type(e).__name__}: {str(e) or tb[-200:]}",
            "finished_at": finished_at,
        })
        await atualizar_pipeline(pipeline_id, {"status": "erro"})
        raise


def _build_context(etapas_anteriores: list[dict]) -> dict:
    """Monta dicionario com saidas de etapas anteriores, indexado por agente."""
    context = {}
    for step in etapas_anteriores:
        agente = step["agente"]
        saida_raw = step.get("saida")
        if saida_raw:
            try:
                context[agente] = json.loads(saida_raw)
            except (json.JSONDecodeError, TypeError):
                context[agente] = saida_raw
    return context


def _build_entrada(agente: str, tema: str, context: dict) -> dict:
    """Monta resumo da entrada para salvar no banco."""
    if agente == "strategist":
        return {"tema": tema}
    if agente == "copywriter":
        return {"briefing_from": "strategist"}
    if agente == "hook_specialist":
        return {"copy_from": "copywriter"}
    if agente == "art_director":
        return {"copy_from": "copywriter", "hook_from": "hook_specialist"}
    if agente == "image_generator":
        return {"prompts_from": "art_director"}
    if agente == "brand_gate":
        return {"images_from": "image_generator"}
    if agente == "content_critic":
        return {"all_from": list(context.keys())}
    return {}


async def _executar_agente(
    agente: str,
    tema: str,
    formato: str,
    modo_funil: bool,
    context: dict,
    pipeline: dict,
    step_id: str = "",
    brand_slug: str | None = None,
    avatar_mode: str = "livre",
) -> dict:
    """Despacha execucao para o agente correto."""
    claude_api_key = os.getenv("CLAUDE_API_KEY", "")
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    if agente == "strategist":
        feedback = context.get("_feedback_rejeicao", "")
        return await _exec_strategist(tema, formato, modo_funil, claude_api_key, feedback, brand_slug=brand_slug)

    if agente == "copywriter":
        return await _exec_copywriter(context, formato, claude_api_key, brand_slug=brand_slug)

    if agente == "hook_specialist":
        return await _exec_hook_specialist(context, formato, claude_api_key, brand_slug=brand_slug)

    if agente == "art_director":
        return await _exec_art_director(context, formato, claude_api_key, brand_slug=brand_slug)

    if agente == "image_generator":
        return await _exec_image_generator(context, formato, gemini_api_key, step_id, brand_slug=brand_slug, avatar_mode=avatar_mode)

    if agente == "brand_gate":
        return await _exec_brand_gate(context, formato)

    if agente == "content_critic":
        return await _exec_content_critic(context, formato, claude_api_key)

    raise ValueError(f"Agente desconhecido: {agente}")


async def _exec_strategist(tema, formato, modo_funil, api_key, feedback="", brand_slug=None):
    brand_ctx = _get_brand_context(brand_slug)
    tema_com_marca = tema
    if brand_ctx:
        tema_com_marca = f"{tema}\n\n=== CONTEXTO DA MARCA ===\n{brand_ctx}\nCrie o briefing para ESTA marca, usando o tom e linguagem dela. NAO use IT Valley ou Carlos Viana se a marca for outra.\n=== FIM ==="
    return await executar_strategist(
        tema=tema_com_marca,
        formato=formato,
        modo_funil=modo_funil,
        feedback=feedback,
        claude_api_key=api_key,
    )


def _get_brand_context(brand_slug: str | None) -> str:
    """Monta contexto da marca pra injetar nos agentes LLM."""
    if not brand_slug:
        return ""
    from services.brand_prompt_builder import carregar_brand
    brand = carregar_brand(brand_slug)
    if not brand:
        return ""
    import json
    partes = []
    partes.append(f"MARCA: {brand.get('nome', brand_slug)}")
    com = brand.get("comunicacao", {})
    if com.get("persona"):
        partes.append(f"PERSONA: {com['persona']}")
    if com.get("tom"):
        partes.append(f"TOM: {com['tom']}")
    if com.get("linguagem"):
        partes.append(f"LINGUAGEM: {com['linguagem']}")
    if com.get("publico"):
        partes.append(f"PUBLICO: {com['publico']}")
    if com.get("palavras_proibidas"):
        partes.append(f"PALAVRAS PROIBIDAS: {', '.join(com['palavras_proibidas'])}")
    vis = brand.get("visual", {})
    if vis.get("estilo_fundo"):
        partes.append(f"VISUAL FUNDO: {vis['estilo_fundo']}")
    if vis.get("estilo_desenho"):
        partes.append(f"VISUAL DESENHO: {vis['estilo_desenho']}")
    if vis.get("estilo_card"):
        partes.append(f"VISUAL CARD: {vis['estilo_card']}")
    cores = brand.get("cores", {})
    if cores:
        partes.append(f"CORES: principal={cores.get('acento_principal','')}, fundo={cores.get('fundo','')}, texto={cores.get('texto_principal','')}")
    return "\n".join(partes)


async def _exec_copywriter(context, formato, api_key, brand_slug=None):
    briefing = context.get("strategist", {})
    feedback = context.get("_feedback_rejeicao", "")
    brand_ctx = _get_brand_context(brand_slug)
    if brand_ctx:
        briefing = {**briefing, "_brand_context": brand_ctx}
    return await executar_copywriter(
        briefing=briefing,
        formato=formato,
        feedback=feedback,
        claude_api_key=api_key,
    )


async def _exec_hook_specialist(context, formato, api_key, brand_slug=None):
    copy = context.get("copywriter", {})
    feedback = context.get("_feedback_rejeicao", "")
    brand_ctx = _get_brand_context(brand_slug)
    if brand_ctx:
        copy = {**copy, "_brand_context": brand_ctx}
    return await executar_hook_specialist(
        copy=copy,
        formato=formato,
        feedback=feedback,
        claude_api_key=api_key,
    )


async def _exec_art_director(context, formato, api_key, brand_slug=None):
    copy = context.get("copywriter", {})
    hooks_data = context.get("hook_specialist", {})

    hook_texto = ""
    hooks = hooks_data.get("hooks", [])
    if hooks:
        hook_texto = hooks[0].get("texto", "")

    # Montar palette compacta (sem campos pesados como _raw_content)
    brand_palette_dict = None
    if brand_slug:
        from services.brand_prompt_builder import carregar_brand
        brand = carregar_brand(brand_slug)
        if brand:
            brand_palette_dict = {
                "nome": brand.get("nome"),
                "cores": brand.get("cores"),
                "visual": brand.get("visual"),
                "elementos": brand.get("elementos"),
                "comunicacao": {k: v for k, v in brand.get("comunicacao", {}).items() if k != "exemplos_frase"},
            }
    else:
        config_service = ConfigService()
        try:
            brand_palette = await config_service.buscar_brand_palette()
            brand_palette_dict = brand_palette.model_dump() if hasattr(brand_palette, "model_dump") else brand_palette
        except Exception:
            pass

    return await executar_art_director(
        copy=copy,
        hook=hook_texto,
        formato=formato,
        brand_palette=brand_palette_dict,
        claude_api_key=api_key,
    )


async def _exec_image_generator(context, formato, gemini_api_key, step_id="", brand_slug=None, avatar_mode="livre"):
    from services.step_progress import atualizar as progress_update

    # Pegar slides da copy e converter pro formato que imagem_service espera
    copy_output = context.get("copywriter", {})
    slides_raw = copy_output.get("slides", copy_output.get("sequencia_slides", []))

    if not slides_raw:
        raise ValueError("Nenhum slide encontrado na saida do copywriter")

    # Converter formato copywriter -> formato Slide (que prompt_templates entende)
    # Cada tipo de slide usa seu template especifico do v9 (cover, content, code, cta)
    tipo_map = {"capa": "cover", "conteudo": "content", "codigo": "code", "dados": "infographic", "cta": "cta"}
    slides = []
    for s in slides_raw:
        tipo_raw = s.get("tipo", "conteudo")
        slide_type = tipo_map.get(tipo_raw, "content")
        titulo = s.get("titulo", "")
        corpo = s.get("corpo", "")

        if slide_type == "cover":
            slide = {"type": "cover", "headline": titulo, "subline": corpo}
        elif slide_type == "cta":
            slide = {"type": "cta", "headline": titulo, "subline": corpo, "tags": []}
        elif slide_type == "code":
            slide = {"type": "code", "code": corpo or titulo, "caption": titulo if corpo else ""}
        else:
            bullets = [line.strip() for line in corpo.split("\n") if line.strip()] if corpo else []
            slide = {"type": "content", "title": titulo, "bullets": bullets, "etapa": ""}
        slides.append(slide)

    design_system = None  # Usa o DESIGN_SYSTEM padrao do prompt_templates (v9)

    if step_id:
        progress_update(step_id, 0, len(slides), "Gerando imagens...")

    # Carregar foto da marca (ou fallback pra foto_criador padrao)
    import base64
    from pathlib import Path
    assets_dir = Path(__file__).parent.parent / "assets"
    foto_criador = None
    # Tentar foto da marca primeiro
    if brand_slug:
        for ext in ("jpg", "png", "jpeg"):
            foto_path = assets_dir / "fotos" / f"{brand_slug}.{ext}"
            if foto_path.exists():
                foto_b64 = base64.b64encode(foto_path.read_bytes()).decode()
                mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
                foto_criador = f"data:{mime};base64,{foto_b64}"
                break
    # Fallback pra foto padrao
    if not foto_criador:
        foto_path = assets_dir / "foto_criador.jpg"
        if foto_path.exists():
            foto_b64 = base64.b64encode(foto_path.read_bytes()).decode()
            foto_criador = f"data:image/jpeg;base64,{foto_b64}"

    # Usar o mesmo fluxo do v9 — 1 imagem por slide, sem variações
    from services.smart_image_service import gerar_imagens_smart
    images = await gerar_imagens_smart(
        slides=slides,
        gemini_api_key=gemini_api_key,
        brand_slug=brand_slug,
        avatar_mode=avatar_mode,
        formato=formato,
    )

    imagens_result = []
    for i, img in enumerate(images):
        imagens_result.append({
            "slide_index": i + 1,
            "variacao": 1,
            "image_base64": img,
            "modelo": "v9",
        })

    return {
        "imagens": imagens_result,
        "total_slides": len(slides),
    }


async def _exec_brand_gate(context, formato):
    """Executa brand_validator + brand_overlay sobre as imagens geradas.
    Deterministico, sem LLM.
    """
    image_gen_output = context.get("image_generator", {})
    imagens = image_gen_output.get("imagens", [])

    resultados = []
    for img_item in imagens:
        image_b64 = img_item.get("image_base64")
        if not image_b64:
            resultados.append({
                "slide_index": img_item.get("slide_index"),
                "variacao": img_item.get("variacao"),
                "validacao": {"valido": False, "erros": ["Imagem nao disponivel"]},
                "image_base64": None,
            })
            continue

        # Validar contra brand palette
        validacao = brand_validar(image_b64, formato)

        # Aplicar overlay (foto criador + logo) se validacao passou
        image_final = image_b64
        if validacao["valido"]:
            try:
                image_final = brand_overlay_aplicar(image_b64)
            except Exception:
                pass

        resultados.append({
            "slide_index": img_item.get("slide_index"),
            "variacao": img_item.get("variacao"),
            "validacao": validacao,
            "image_base64": image_final,
        })

    total = len(resultados)
    validos = sum(1 for r in resultados if r["validacao"]["valido"])

    return {
        "resultados": resultados,
        "total": total,
        "validos": validos,
        "aprovado": validos == total,
    }


async def _exec_content_critic(context, formato, api_key):
    # Montar conteudo completo para avaliacao
    conteudo = {
        "briefing": context.get("strategist", {}),
        "copy": context.get("copywriter", {}),
        "hooks": context.get("hook_specialist", {}),
        "art_direction": context.get("art_director", {}),
        "brand_gate": context.get("brand_gate", {}),
    }

    return await executar_content_critic(
        conteudo=conteudo,
        formato=formato,
        claude_api_key=api_key,
    )
