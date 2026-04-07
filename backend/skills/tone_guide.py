# Termos proibidos no vocabulario IT Valley
TERMOS_PROIBIDOS = [
    "guru", "hack", "truque", "milagre", "facil", "rapido",
    "garantido", "infalivel", "segredo", "revelar",
]

# Substituicoes sugeridas
SUBSTITUICOES = {
    "guru": "especialista",
    "hack": "tecnica",
    "truque": "abordagem",
    "milagre": "resultado",
    "facil": "acessivel",
    "rapido": "eficiente",
    "garantido": "comprovado",
    "segredo": "insight",
}


def validar(texto: str) -> dict:
    """Valida vocabulario IT Valley.

    Retorna:
        {
            "valido": bool,
            "correcoes": [{"original": str, "sugestao": str}],
            "texto_corrigido": str
        }
    """
    correcoes = []
    texto_lower = texto.lower()
    texto_corrigido = texto

    for termo in TERMOS_PROIBIDOS:
        if termo in texto_lower:
            sugestao = SUBSTITUICOES.get(termo, f"[substituir '{termo}']")
            correcoes.append({"original": termo, "sugestao": sugestao})

    return {
        "valido": len(correcoes) == 0,
        "correcoes": correcoes,
        "texto_corrigido": texto_corrigido,
    }
