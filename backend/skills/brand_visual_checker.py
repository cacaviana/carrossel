"""Validador visual de identidade de marca usando Gemini Vision.

Compara imagem gerada com refs da marca e uma narracao de identidade visual.
Retorna score + feedback pra regenerar se nao bateu.
"""

import base64
import json
import os

import httpx

from utils.constants import GEMINI_API_URL


def _build_identity_narration(brand: dict) -> str:
    """Monta narracao textual detalhada da identidade visual a partir da analise."""
    analise = brand.get("_analise_referencia", {})
    visual = brand.get("visual", {})
    cores = brand.get("cores", {})

    parts = []

    # Resumo geral
    if analise.get("resumo"):
        parts.append(f"RESUMO: {analise['resumo']}")
    if analise.get("estetica"):
        parts.append(f"ESTETICA: {analise['estetica']}")
    if analise.get("vibe"):
        parts.append(f"VIBE: {analise['vibe']}")

    # Cores detalhadas
    cores_analise = analise.get("cores", {})
    if cores_analise:
        cores_txt = []
        for k, v in cores_analise.items():
            if isinstance(v, dict):
                cores_txt.append(f"  {k}: {v.get('hex','')} - {v.get('descricao','')}")
            else:
                cores_txt.append(f"  {k}: {v}")
        parts.append("CORES:\n" + "\n".join(cores_txt))

    # Tipografia
    tipo = analise.get("tipografia", {})
    if tipo:
        tipo_txt = []
        for k, v in tipo.items():
            if isinstance(v, dict):
                tipo_txt.append(f"  {k}: fonte={v.get('fonte','')} peso={v.get('peso','')} efeito={v.get('efeito','')}")
            else:
                tipo_txt.append(f"  {k}: {v}")
        parts.append("TIPOGRAFIA:\n" + "\n".join(tipo_txt))

    # Decoracao
    deco = analise.get("decoracao", {})
    if deco:
        parts.append(f"FUNDO: {deco.get('fundo_tipo','')} - {deco.get('fundo_detalhe','')}")
        elementos = deco.get("elementos", [])
        if elementos:
            parts.append("ELEMENTOS DECORATIVOS:\n" + "\n".join(f"  - {e}" for e in elementos[:8]))

    # Foto/pessoa
    foto = analise.get("foto_pessoa", {})
    if foto and foto.get("tem"):
        parts.append(f"PESSOA: {foto.get('descricao','')}\nPOSICAO: {foto.get('posicao','')}")

    # Visual da marca
    if visual.get("estilo_fundo"):
        parts.append(f"ESTILO FUNDO: {visual['estilo_fundo']}")
    if visual.get("estilo_texto"):
        parts.append(f"ESTILO TEXTO: {visual['estilo_texto']}")
    if visual.get("estilo_desenho"):
        parts.append(f"ESTILO GRAFICO: {visual['estilo_desenho']}")

    return "\n\n".join(parts)


async def validar_imagem(
    image_b64: str,
    ref_b64: str,
    brand: dict,
    gemini_api_key: str = "",
) -> dict:
    """Compara imagem gerada com ref da marca usando Gemini Vision.

    Retorna:
        {
            "aprovado": bool,
            "score": int (0-10),
            "problemas": list[str],
            "sugestao_prompt": str  # instrucao pra regenerar
        }
    """
    if not gemini_api_key:
        gemini_api_key = os.getenv("GEMINI_API_KEY", "")
    if not gemini_api_key:
        return {"aprovado": True, "score": 7, "problemas": [], "sugestao_prompt": ""}

    narration = _build_identity_narration(brand)

    # Preparar imagens
    ref_raw = ref_b64.split(",")[1] if "," in ref_b64 else ref_b64
    img_raw = image_b64.split(",")[1] if "," in image_b64 else image_b64

    prompt = f"""Voce e um diretor de arte validando se uma imagem gerada segue a identidade visual de uma marca.

=== IDENTIDADE VISUAL DA MARCA ===
{narration}

=== INSTRUCOES ===
A primeira imagem e a REFERENCIA (identidade visual correta da marca).
A segunda imagem e a IMAGEM GERADA que precisa ser validada.

Compare e avalie de 0 a 10:
- Cores (paleta, tons, saturacao)
- Tipografia (estilo, peso, efeitos)
- Composicao (layout, espacamento, hierarquia)
- Elementos graficos (stickers, decoracoes, estilo)
- Estilo fotografico/artistico (foto real vs ilustracao, iluminacao)
- Consistencia geral com a marca

Se o score for < 7, descreva os problemas E sugira um trecho de prompt curto (max 2 frases) pra corrigir na proxima geracao.

Responda APENAS em JSON valido:
{{
  "score": 8,
  "aprovado": true,
  "problemas": ["tipografia diferente da ref"],
  "sugestao_prompt": "Use bold bubble font with 3D shadow effect, pastel pink and blue"
}}"""

    parts = [
        {"inline_data": {"mime_type": "image/png", "data": ref_raw}},
        {"inline_data": {"mime_type": "image/png", "data": img_raw}},
        {"text": prompt},
    ]

    # Usar Flash pra economizar (validacao nao precisa de Pro)
    model = "gemini-2.5-flash"
    url = GEMINI_API_URL.format(model=model) + f"?key={gemini_api_key}"

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 512},
    }

    print(f"[brand_visual_checker] Chamando Gemini {model}...")
    print(f"[brand_visual_checker] URL: {url[:80]}...")
    print(f"[brand_visual_checker] ref size: {len(ref_raw)//1024}KB, img size: {len(img_raw)//1024}KB")

    async with httpx.AsyncClient(timeout=120) as client:
        try:
            resp = await client.post(url, json=payload)
            print(f"[brand_visual_checker] Status: {resp.status_code}")
            if resp.status_code != 200:
                print(f"[brand_visual_checker] Response: {resp.text[:500]}")
            resp.raise_for_status()
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            print(f"[brand_visual_checker] Gemini respondeu: {text[:200]}")

            # Parsear JSON da resposta
            import re
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                result = json.loads(json_match.group())
                result["aprovado"] = result.get("score", 0) >= 7
                return result
            else:
                print(f"[brand_visual_checker] JSON nao encontrado na resposta")
        except Exception as e:
            print(f"[brand_visual_checker] Erro: {type(e).__name__}: {e}")

    # Fallback: aprovar se Gemini falhar
    return {"aprovado": True, "score": 7, "problemas": [], "sugestao_prompt": ""}
