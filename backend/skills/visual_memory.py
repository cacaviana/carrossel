# Nota: visual_memory persiste via VisualPreferenceService + VisualPreferenceRepository.
# Esta skill e apenas um wrapper que formata os dados para o Art Director.


def formatar_para_art_director(preferencias: list[dict]) -> str:
    """Formata preferencias visuais do usuario como contexto para o Art Director.

    Entrada: lista de preferencias [{estilo, aprovado, contexto}]
    Saida: texto formatado para incluir no system prompt do Art Director
    """
    if not preferencias:
        return "Nenhuma preferencia visual registrada."

    aprovados = [p for p in preferencias if p.get("aprovado")]
    rejeitados = [p for p in preferencias if not p.get("aprovado")]

    partes = []
    if aprovados:
        partes.append("ESTILOS APROVADOS pelo usuario:")
        for p in aprovados[-5:]:  # Ultimas 5
            partes.append(f"  - {p['estilo']}")

    if rejeitados:
        partes.append("ESTILOS REJEITADOS pelo usuario (EVITAR):")
        for p in rejeitados[-5:]:
            partes.append(f"  - {p['estilo']}")

    return "\n".join(partes)
