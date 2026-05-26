"""Extrai titulo e corpo de um slide, independente da estrutura que o LLM retornou."""


def _str(val) -> str:
    """Extrai string de texto de qualquer estrutura (string, dict, list de dicts)."""
    if isinstance(val, str):
        return val
    if not val:
        return ""
    if isinstance(val, list):
        parts = []
        for item in val:
            if isinstance(item, dict):
                parts.append(_str(item.get("texto", item.get("conteudo", ""))))
            elif isinstance(item, str):
                parts.append(item)
        return " ".join(p for p in parts if p)
    if not isinstance(val, dict):
        return ""
    if isinstance(val.get("texto"), str):
        return val["texto"]
    if isinstance(val.get("conteudo"), str):
        return val["conteudo"]
    if isinstance(val.get("titulo"), str):
        return val["titulo"]
    if isinstance(val.get("conteudo"), list):
        return _str(val["conteudo"])
    for k in val:
        v = val[k]
        if isinstance(v, str) and len(v) > 3:
            return v
    return ""


def extrair_texto_slide(slide: dict) -> tuple[str, str]:
    """Retorna (titulo, corpo) de um slide em qualquer formato LLM."""
    # 1. Campos diretos
    titulo = _str(slide.get("headline")) or _str(slide.get("title")) or _str(slide.get("titulo")) or ""
    corpo = ""
    bullets = slide.get("bullets", [])
    if bullets and isinstance(bullets, list):
        corpo = "\n".join(b if isinstance(b, str) else str(b) for b in bullets)
    if not corpo:
        corpo = _str(slide.get("subline")) or _str(slide.get("corpo")) or _str(slide.get("conteudo")) or _str(slide.get("texto")) or _str(slide.get("code")) or ""

    # 2. Fallback: buscar em elementos[]
    if (not titulo or not corpo) and isinstance(slide.get("elementos"), list):
        for el in slide["elementos"]:
            if not isinstance(el, dict):
                continue
            t = el.get("tipo", "")
            val = _str(el.get("texto")) or _str(el.get("conteudo")) or _str(el)
            if not titulo and ("titulo" in t or t == "headline"):
                titulo = val
            if not corpo and ("card" in t or t in ("corpo", "subtitulo", "call_to_action", "descricao")):
                corpo = val

    # 3. Fallback: se titulo vazio mas corpo tem texto, usar corpo como titulo
    if not titulo and corpo:
        titulo = corpo

    return titulo, corpo
