import os
import re
import json
import base64
from datetime import datetime, timezone
from pathlib import Path

from services.pipeline_db_service import (
    buscar_proxima_etapa,
    buscar_etapas_anteriores,
    atualizar_etapa,
    atualizar_pipeline,
)
from services.config_service import ConfigService
from factories.prompt_composer import PromptComposer

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
    context["_pipeline_id"] = pipeline_id
    context["_tema"] = tema

    # Se esta etapa foi rejeitada, incluir o feedback + saída anterior no context
    feedback_rejeicao = step.get("erro_mensagem", "")
    print(f"[pipeline] Etapa {agente}: status={step.get('status')}, feedback='{feedback_rejeicao}', tem_saida={bool(step.get('saida'))}")
    if feedback_rejeicao and feedback_rejeicao != "Rejeitado pelo usuario":
        context["_feedback_rejeicao"] = feedback_rejeicao
        print(f"[pipeline] Feedback setado: {feedback_rejeicao[:100]}")
    # Incluir saída anterior da PRÓPRIA etapa (pra ajustes incrementais)
    saida_anterior_raw = step.get("saida")
    if saida_anterior_raw and feedback_rejeicao:
        try:
            parsed = json.loads(saida_anterior_raw) if isinstance(saida_anterior_raw, str) else saida_anterior_raw
            context[agente] = parsed
            print(f"[pipeline] Saida anterior do {agente} carregada: {list(parsed.keys()) if isinstance(parsed, dict) else 'nao-dict'}")
        except (json.JSONDecodeError, TypeError) as e:
            print(f"[pipeline] Erro ao parsear saida anterior: {e}")

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
    if agente == "art_director":
        return {"copy_from": "copywriter"}
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
        # Hook removido — auto-completar pra pipelines legados que ainda tem essa etapa
        copy = context.get("copywriter", {})
        return {"hooks": [{"letra": "A", "texto": copy.get("headline", tema), "abordagem": "Auto"}]}

    if agente == "art_director":
        return await _exec_art_director(context, formato, claude_api_key, brand_slug=brand_slug, avatar_mode=avatar_mode)

    if agente == "image_generator":
        return await _exec_image_generator(context, formato, gemini_api_key, step_id, brand_slug=brand_slug, avatar_mode=avatar_mode)

    if agente == "brand_gate":
        return await _exec_brand_gate(context, formato, brand_slug=brand_slug)

    if agente == "content_critic":
        return await _exec_content_critic(context, formato, claude_api_key)

    raise ValueError(f"Agente desconhecido: {agente}")


async def _exec_strategist(tema, formato, modo_funil, api_key, feedback="", brand_slug=None):
    brand_ctx = _get_brand_context(brand_slug)
    tema_com_marca = tema
    if brand_ctx:
        tema_com_marca = (
            f"{tema}\n\n"
            f"=== CONTEXTO DA MARCA (APENAS TOM E ESTILO — NAO E O TEMA!) ===\n"
            f"{brand_ctx}\n"
            f"INSTRUCAO: Use APENAS o tom, linguagem e estilo visual desta marca.\n"
            f"O TEMA do carrossel e EXCLUSIVAMENTE o que esta acima: '{tema}'.\n"
            f"NAO mude o assunto. NAO fale sobre hobbies, produtos ou interesses da persona.\n"
            f"A persona da marca so define COMO falar, nunca SOBRE O QUE falar.\n"
            f"=== FIM ==="
        )
    try:
        return await executar_strategist(
            tema=tema_com_marca,
            formato=formato,
            modo_funil=modo_funil,
            feedback=feedback,
            claude_api_key=api_key,
        )
    except Exception as e:
        print(f"[executor] strategist falhou: {e}. Tentando fallback OpenAI...")
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if not openai_key:
            raise RuntimeError("Claude sem creditos e OpenAI nao configurada")
        import openai
        from utils.json_parser import parse_llm_json
        from pathlib import Path
        prompt_path = Path(__file__).parent.parent / "agents" / "strategist.md"
        system_prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""
        user_prompt = (
            f"TEMA OBRIGATORIO (nao mude, nao substitua, nao invente outro): {tema_com_marca}\n"
            f"Formato: {formato}\n"
            f"REGRA CRITICA: O briefing DEVE ser sobre o tema acima. "
            f"Use EXATAMENTE esse assunto como tema_principal. "
            f"NAO gere conteudo sobre outro assunto.\n"
        )
        if feedback:
            user_prompt += f"\nFEEDBACK DO USUARIO: {feedback}\n"
        user_prompt += "\nResposta OBRIGATORIAMENTE em JSON valido. Sem comentarios, sem trailing commas."
        client = openai.AsyncOpenAI(api_key=openai_key)
        response = await client.chat.completions.create(
            model="gpt-4o",
            max_tokens=4096,
            temperature=0.9,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        result = parse_llm_json(response.choices[0].message.content or "")
        result["_provider"] = "openai"
        result["_fallback"] = True
        if "raw_text" in result:
            return {"briefing": result["raw_text"], "raw": True}
        return result


def _get_brand_context(brand_slug: str | None) -> str:
    """Monta contexto da marca pra injetar nos agentes LLM.

    Delega para PromptComposer.compor_prompt_texto() que junta
    camada de seguranca + camada de marca (persona, tom, hooks, etc).
    Fallback manual caso PromptComposer falhe.
    """
    if not brand_slug:
        return ""
    try:
        resultado = PromptComposer.compor_prompt_texto(brand_slug=brand_slug)
        if resultado:
            return resultado
    except Exception as e:
        print(f"[WARN] PromptComposer falhou, usando fallback: {e}")

    # Fallback: codigo original inline caso PromptComposer falhe
    from services.brand_prompt_builder import carregar_brand
    brand = carregar_brand(brand_slug)
    if not brand:
        return ""
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
    # Extrair max_slides do tema (formato: "tema [MAX N SLIDES]")
    # Priorizar context._tema (tema raw da pipeline com o sufixo MAX intacto) —
    # strategist limpa o sufixo de tema_principal, entao nunca achava o MAX.
    tema_str = context.get("_tema", "") or briefing.get("briefing", {}).get("tema_principal", "")
    m = re.search(r'\[MAX\s+(\d+)\s+SLIDES?\]', tema_str, re.IGNORECASE)
    if m:
        briefing["_max_slides"] = int(m.group(1))
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


async def _exec_art_director(context, formato, api_key, brand_slug=None, avatar_mode="livre"):
    copy = context.get("copywriter", {})
    feedback = context.get("_feedback_rejeicao", "")

    # Se tem feedback + saida anterior, usar Claude pra AJUSTAR a cena (não recriar)
    prev_art = context.get("art_director", {})
    if feedback and prev_art.get("prompts"):
        from utils.json_parser import parse_llm_json
        prev_prompts = prev_art["prompts"]
        adjust_prompt = (
            f"Aqui esta a descricao de cena anterior de cada slide:\n"
            f"{json.dumps(prev_prompts, ensure_ascii=False, indent=2)}\n\n"
            f"O usuario pediu este ajuste: {feedback}\n\n"
            f"Aplique APENAS o ajuste pedido. Mantenha TODO o resto identico.\n"
            f"Retorne o JSON atualizado no mesmo formato: {{\"prompts\": [...]}}\n"
            f"Responda APENAS JSON valido."
        )
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=api_key)
            msg = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[{"role": "user", "content": adjust_prompt}],
            )
            return parse_llm_json(msg.content[0].text)
        except Exception as e:
            print(f"[art_director adjust] Claude falhou: {e}. Tentando OpenAI...")
            import openai
            openai_key = os.getenv("OPENAI_API_KEY", "")
            if not openai_key:
                raise RuntimeError("Claude sem creditos e OpenAI nao configurada")
            oai_client = openai.AsyncOpenAI(api_key=openai_key)
            response = await oai_client.chat.completions.create(
                model="gpt-4o",
                max_tokens=2048,
                messages=[{"role": "user", "content": adjust_prompt}],
            )
            result = parse_llm_json(response.choices[0].message.content or "")
            result["_provider"] = "openai"
            result["_fallback"] = True
            return result

    # Montar palette compacta (sem campos pesados como _raw_content)
    brand_palette_dict = None
    if brand_slug:
        from services.brand_prompt_builder import carregar_brand
        brand = carregar_brand(brand_slug)
        if brand:
            # Extrair prompt_perfeito da analise de referencia (o mais importante)
            analise = brand.get("_analise_referencia", {})
            prompt_ref = analise.get("prompt_perfeito") or analise.get("prompt_replicar", "")
            regras = brand.get("regras_feed") or analise.get("regras_feed", {})

            brand_palette_dict = {
                "nome": brand.get("nome"),
                "cores": brand.get("cores"),
                "fontes": brand.get("fontes"),
                "visual": brand.get("visual"),
                "elementos": brand.get("elementos"),
                "comunicacao": {k: v for k, v in brand.get("comunicacao", {}).items() if k != "exemplos_frase"},
                "prompt_referencia": prompt_ref,
                "regras_feed": regras,
                "padrao_visual": brand.get("padrao_visual"),
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
        hook="",
        formato=formato,
        brand_palette=brand_palette_dict,
        claude_api_key=api_key,
        avatar_mode=avatar_mode,
    )


async def _exec_image_generator(context, formato, gemini_api_key, step_id="", brand_slug=None, avatar_mode="livre"):
    from services.step_progress import atualizar as progress_update

    # Pegar slides da copy e converter pro formato que imagem_service espera
    copy_output = context.get("copywriter", {})
    slides_raw = copy_output.get("slides", copy_output.get("sequencia_slides", []))

    # Fallback: LLM pode retornar slides dentro de um objeto (ex: carrossel.slides)
    if not slides_raw:
        for key in copy_output:
            val = copy_output[key]
            if isinstance(val, dict) and isinstance(val.get("slides"), list):
                slides_raw = val["slides"]
                break
            if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict) and val[0].get("titulo"):
                slides_raw = val
                break

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

        # Preservar tipo_layout se o LLM/usuario mandou; senao, inferir
        if s.get("tipo_layout"):
            slide["tipo_layout"] = s["tipo_layout"]
        elif "tipo_layout" not in slide:
            from factories.pipeline_factory import inferir_tipo_layout
            slide["tipo_layout"] = inferir_tipo_layout(slide)

        slides.append(slide)

    # Injetar direção de cena do Art Director nos slides (illustration_description)
    art_output = context.get("art_director", {})
    art_prompts = art_output.get("prompts", [])
    for ap in art_prompts:
        idx = ap.get("slide_index", 0) - 1
        scene = ap.get("illustration_description", "")
        if 0 <= idx < len(slides) and scene:
            slides[idx]["illustration_description"] = scene

    # Se avatar_mode pede pessoa mas slide nao tem illustration_description,
    # injetar cena com pessoa pra que o PromptComposer use o path de illustration
    if avatar_mode in ("sim", "capa"):
        from factories.imagem_factory import _load_avatars
        has_avatars = len(_load_avatars(brand_slug)) > 0 if brand_slug else False
        if has_avatars:
            for i, slide in enumerate(slides):
                if slide.get("illustration_description"):
                    continue  # Art Director ja definiu cena
                if avatar_mode == "capa" and i > 0:
                    continue  # so capa
                titulo = slide.get("headline") or slide.get("title", "")
                slide["illustration_description"] = (
                    f"The brand's person/creator featured prominently, "
                    f"in a natural confident pose related to: {titulo}"
                )

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
        pipeline_id=context.get("_pipeline_id"),
    )

    # PASS 2: Correcao automatica de avatar nos slides com pessoa.
    # Pass 1 gera a cena (estilo+layout+pessoa generica seguindo o art director).
    # Pass 2 pega essa imagem + 3 fotos do avatar real e troca APENAS o rosto
    # mantendo pose/cena/iluminacao. Resolve o problema de Gemini alucinar a
    # face no pass unico (ex: Carlos virando outra pessoa).
    print(f"[pass2] iniciando — brand={brand_slug} avatar_mode={avatar_mode} total_imgs={len(images)}")
    if brand_slug and avatar_mode != "sem":
        from factories.imagem_factory import _load_avatars
        avatars_count = len(_load_avatars(brand_slug))
        brand_has_avatar = avatars_count > 0
        print(f"[pass2] brand_has_avatar={brand_has_avatar} avatars={avatars_count}")

        if brand_has_avatar:
            from services.avatar_fixer import corrigir_avatar

            total_slides = len(slides)
            for i, img in enumerate(images):
                position = i + 1
                if not img:
                    print(f"[pass2] slide {position}: sem imagem do pass1, skip")
                    continue
                is_capa_ou_cta = (position == 1 or position == total_slides)
                should_fix = (
                    avatar_mode == "sim" or
                    (avatar_mode in ("livre", "capa") and is_capa_ou_cta)
                )
                # capa mode: so slide 1
                if avatar_mode == "capa" and position != 1:
                    should_fix = False
                if not should_fix:
                    print(f"[pass2] slide {position}: nao precisa corrigir (mode={avatar_mode}, capa/cta={is_capa_ou_cta})")
                    continue

                try:
                    print(f"[pass2] slide {position}: corrigindo avatar... (img len={len(img) if isinstance(img, str) else 'nao-str'})")
                    result = await corrigir_avatar(img, brand_slug, gemini_api_key)
                    if result and len(result) > 100:
                        images[i] = result
                        print(f"[pass2] slide {position}: OK (nova img len={len(result)})")
                    else:
                        print(f"[pass2] slide {position}: corrigir_avatar retornou vazio, mantendo pass1")
                except Exception as e:
                    import traceback
                    print(f"[pass2] slide {position} FALHOU: {type(e).__name__}: {e}")
                    print(f"[pass2] traceback:\n{traceback.format_exc()}")
                    # mantem a imagem do pass 1 em caso de erro
    else:
        print(f"[pass2] skipped — brand_slug={brand_slug} avatar_mode={avatar_mode}")

    # Salvar imagens no disco ao inves de base64 no banco
    from utils.pipeline_images import salvar_imagem
    imagens_result = []
    for i, img in enumerate(images):
        if img:
            path_rel = salvar_imagem(context.get("_pipeline_id", "temp"), i + 1, img, formato=formato)
        else:
            path_rel = None
        imagens_result.append({
            "slide_index": i + 1,
            "variacao": 1,
            "image_path": path_rel,
            "modelo": "v9",
        })

    return {
        "imagens": imagens_result,
        "total_slides": len(slides),
    }


async def _exec_brand_gate(context, formato, brand_slug=None):
    """Executa validacao visual de identidade de marca usando Gemini Vision.

    Compara cada imagem gerada com as refs da marca.
    Se score < 7, marca como reprovado com feedback pra regenerar.
    """
    image_gen_output = context.get("image_generator", {})
    imagens = image_gen_output.get("imagens", [])

    from utils.pipeline_images import carregar_imagem_b64, salvar_imagem
    from skills.brand_visual_checker import validar_imagem
    from factories.imagem_factory import _load_all_references

    gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    # Carregar brand e ref pra comparacao visual
    print(f"[brand_gate] brand_slug={brand_slug}, imagens={len(imagens)}")
    brand = None
    ref_b64 = None
    if brand_slug:
        from services.brand_prompt_builder import carregar_brand
        brand = carregar_brand(brand_slug)
        refs = _load_all_references(brand_slug)
        if refs:
            ref_b64 = refs[0]  # Usar primeira ref como referencia

    resultados = []
    for img_item in imagens:
        # Carregar imagem
        image_b64 = None
        if img_item.get("image_path"):
            image_b64 = carregar_imagem_b64(img_item["image_path"])
        if not image_b64:
            image_b64 = img_item.get("image_base64")
        if not image_b64:
            resultados.append({
                "slide_index": img_item.get("slide_index"),
                "variacao": img_item.get("variacao"),
                "validacao": {"valido": False, "erros": ["Imagem nao disponivel"]},
                "image_path": None,
            })
            continue

        # Validacao visual com Gemini (se tem brand + ref)
        visual_check = {"aprovado": True, "score": 7, "problemas": [], "sugestao_prompt": ""}
        if brand and ref_b64:
            try:
                visual_check = await validar_imagem(
                    image_b64=image_b64,
                    ref_b64=ref_b64,
                    brand=brand,
                    gemini_api_key=gemini_api_key,
                )
                slide_idx = img_item.get("slide_index", "?")
                print(f"[brand_gate] Slide {slide_idx}: score={visual_check.get('score',0)} aprovado={visual_check.get('aprovado',False)} problemas={visual_check.get('problemas',[])}")
            except Exception as e:
                print(f"[brand_gate] Validacao visual falhou: {e}")

        validacao = {
            "valido": visual_check.get("aprovado", True),
            "score": visual_check.get("score", 7),
            "erros": visual_check.get("problemas", []),
            "sugestao_prompt": visual_check.get("sugestao_prompt", ""),
        }

        # Aplicar overlay se aprovado
        image_final = image_b64
        if validacao["valido"]:
            try:
                image_final = brand_overlay_aplicar(image_b64)
            except Exception:
                pass

        # Salvar resultado no disco
        pipeline_id = context.get("_pipeline_id", "temp")
        slide_idx = img_item.get("slide_index", 1)
        path_rel = salvar_imagem(pipeline_id, slide_idx, image_final, formato=formato)

        resultados.append({
            "slide_index": slide_idx,
            "variacao": img_item.get("variacao"),
            "validacao": validacao,
            "image_path": path_rel,
        })

    total = len(resultados)
    validos = sum(1 for r in resultados if r["validacao"]["valido"])
    scores = [r["validacao"].get("score", 0) for r in resultados]
    avg_score = sum(scores) / len(scores) if scores else 0

    return {
        "resultados": resultados,
        "total": total,
        "validos": validos,
        "aprovado": validos == total,
        "score_medio": round(avg_score, 1),
    }


async def _exec_content_critic(context, formato, api_key):
    # Montar conteudo completo para avaliacao
    conteudo = {
        "briefing": context.get("strategist", {}),
        "copy": context.get("copywriter", {}),
        "art_direction": context.get("art_director", {}),
        "brand_gate": context.get("brand_gate", {}),
    }

    return await executar_content_critic(
        conteudo=conteudo,
        formato=formato,
        claude_api_key=api_key,
    )
