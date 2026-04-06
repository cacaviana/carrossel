from pathlib import Path
from typing import Optional

_BASE = Path(__file__).resolve().parent.parent
# Os .md ficam em carrossel/agents/, nao em backend/agents/
AGENTS_PATH = _BASE.parent / "agents"
if not AGENTS_PATH.exists():
    AGENTS_PATH = _BASE / "agents"

# Metadados dos 6 agentes LLM
AGENTES_LLM = [
    {
        "slug": "strategist",
        "nome": "Strategist",
        "descricao": "Gera briefing estruturado com funil (1 tema -> 5-7 pecas). Usa tendencias do trend_scanner.",
        "tipo": "llm",
        "ordem_pipeline": 1,
        "arquivo": "strategist.md",
    },
    {
        "slug": "copywriter",
        "nome": "Copywriter",
        "descricao": "Roteador: carrega agente especializado por formato (carrossel, post unico, thumbnail).",
        "tipo": "llm",
        "ordem_pipeline": 2,
        "arquivo": "copywriter-carrossel.md",
    },
    {
        "slug": "copywriter-carrossel",
        "nome": "Copywriter Carrossel",
        "descricao": "Cria carrosseis de alto impacto: hook, identificacao, aprofundamento, prova, CTA. Anti-guru, anti-lista.",
        "tipo": "llm",
        "ordem_pipeline": None,
        "arquivo": "copywriter-carrossel.md",
    },
    {
        "slug": "copywriter-post-unico",
        "nome": "Copywriter Post Unico",
        "descricao": "Cria posts unicos (1080x1080): 1 ideia forte, texto grande, legenda rica no LinkedIn.",
        "tipo": "llm",
        "ordem_pipeline": None,
        "arquivo": "copywriter-post-unico.md",
    },
    {
        "slug": "copywriter-thumbnail",
        "nome": "Copywriter Thumbnail",
        "descricao": "Cria thumbnails YouTube (1280x720): maximo 4 palavras, alto CTR, conceito visual forte.",
        "tipo": "llm",
        "ordem_pipeline": None,
        "arquivo": "copywriter-thumbnail.md",
    },
    {
        "slug": "hook_specialist",
        "nome": "Hook Specialist",
        "descricao": "Gera 3 ganchos A/B/C com abordagens diferentes a partir da copy completa.",
        "tipo": "llm",
        "ordem_pipeline": 3,
        "arquivo": "hook-specialist.md",
    },
    {
        "slug": "art_director",
        "nome": "Art Director",
        "descricao": "Gera prompt de imagem detalhado por slide, adaptado ao formato e brand palette.",
        "tipo": "llm",
        "ordem_pipeline": 4,
        "arquivo": "art-director.md",
    },
    {
        "slug": "image_generator",
        "nome": "Image Generator",
        "descricao": "Gera 3 variacoes de imagem por slide via Gemini API (Pro/Flash).",
        "tipo": "llm",
        "ordem_pipeline": 5,
        "arquivo": None,
    },
    {
        "slug": "content_critic",
        "nome": "Content Critic",
        "descricao": "Avalia conteudo final com score em 6 dimensoes: clarity, impact, originality, scroll_stop, cta_strength, final_score.",
        "tipo": "llm",
        "ordem_pipeline": 7,
        "arquivo": "content-critic.md",
    },
]

# Metadados das 6 skills deterministicas
SKILLS = [
    {
        "slug": "brand_overlay",
        "nome": "Brand Overlay",
        "descricao": "Pillow: aplica foto redonda do criador + logo IT Valley em posicao fixa.",
        "tipo": "skill",
        "ordem_pipeline": None,
    },
    {
        "slug": "brand_validator",
        "nome": "Brand Validator",
        "descricao": "Pillow: valida cores, aspect ratio, elementos obrigatorios da marca.",
        "tipo": "skill",
        "ordem_pipeline": None,
    },
    {
        "slug": "visual_memory",
        "nome": "Visual Memory",
        "descricao": "Persiste preferencias visuais do usuario (estilos aprovados/rejeitados).",
        "tipo": "skill",
        "ordem_pipeline": None,
    },
    {
        "slug": "variation_engine",
        "nome": "Variation Engine",
        "descricao": "Gera 3 variacoes de prompt via manipulacao de string (sem LLM).",
        "tipo": "skill",
        "ordem_pipeline": None,
    },
    {
        "slug": "tone_guide",
        "nome": "Tone Guide",
        "descricao": "Valida vocabulario IT Valley (termos proibidos, tom de voz, jargoes).",
        "tipo": "skill",
        "ordem_pipeline": None,
    },
    {
        "slug": "trend_scanner",
        "nome": "Trend Scanner",
        "descricao": "Busca conteudo dos criadores do registry (dev.to + HN + YouTube RSS), cache 1h.",
        "tipo": "skill",
        "ordem_pipeline": None,
    },
]


class AgenteFactory:

    @staticmethod
    def listar_todos() -> tuple[list[dict], list[dict]]:
        return AGENTES_LLM, SKILLS

    @staticmethod
    def buscar_por_slug(slug: str) -> Optional[dict]:
        for agente in AGENTES_LLM + SKILLS:
            if agente["slug"] == slug:
                return agente
        return None

    @staticmethod
    def carregar_system_prompt(agente: dict) -> str:
        arquivo = agente.get("arquivo")
        if not arquivo:
            return agente["descricao"]
        path = AGENTS_PATH / arquivo
        if path.exists():
            return path.read_text(encoding="utf-8")
        return f"Arquivo nao encontrado: {arquivo}"
