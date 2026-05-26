"""Modulo [DNA] do prompt composavel.

4 linhas simples da marca: estilo, cores, tipografia, elementos.
Vem do brand profile (campo 'dna'). Se nao tiver, retorna string vazia.
"""


def dna_block(brand: dict | None) -> str:
    """Retorna o bloco [DNA] a partir do brand profile.

    Args:
        brand: dict do brand profile. Procura brand['dna'] com chaves
               'estilo', 'cores', 'tipografia', 'elementos'.

    Returns:
        String com o bloco, ou string vazia se nenhum campo preenchido.
    """
    dna = (brand or {}).get("dna") or {}

    estilo = (dna.get("estilo") or "").strip()
    cores = (dna.get("cores") or "").strip()
    tipografia = (dna.get("tipografia") or "").strip()
    elementos = (dna.get("elementos") or "").strip()

    if not any([estilo, cores, tipografia, elementos]):
        return ""

    return (
        "[DNA]\n\n"
        f"- Estilo: {estilo}\n"
        f"- Cores: {cores}\n"
        f"- Tipografia: {tipografia}\n"
        f"- Elementos: {elementos}"
    )
