import asyncio, os, base64, json, time
from dotenv import load_dotenv
load_dotenv("/home/carlosviana/projectsdev/carrossel-system/backend/.env")

import sys
sys.path.insert(0, "/home/carlosviana/projectsdev/carrossel-system/backend")

from services.imagem_service import gerar_imagem_slide

# Load photo
with open('/home/carlosviana/projectsdev/carrossel-system/backend/foto-carlos-viana.b64', 'r') as f:
    foto_b64 = f.read()

gemini_key = os.getenv('GEMINI_API_KEY')

slides = [
    {
        "type": "cover",
        "headline": 'Spotify anunciou: "95% do código novo é gerado por agentes IA." Os devs não codam mais. Eles revisam.',
        "subline": "Carlos Viana"
    },
    {
        "type": "content",
        "etapa": "CONTEXTO",
        "title": "O que o Spotify fez de verdade",
        "bullets": [
            "Março 2025: Spotify revela que agentes IA geram a maioria do código novo em produção",
            "Devs viraram revisores — definem regras, validam output, aprovam merges",
            "O framework por trás: agentes com tipagem forte e validação estruturada",
            "Não é autocomplete de IDE. É agente autônomo que recebe task, planeja e executa",
            "A pergunta real: como você garante que agente não gera lixo?"
        ]
    },
    {
        "type": "content",
        "etapa": "STAKES",
        "title": "O problema que ninguém fala",
        "bullets": [
            "LLM retorna string. Sempre. Mesmo quando você pede JSON.",
            "Campo 'preço' vem como string '42.50' em vez de float",
            "Agente decide chamar função que não existe",
            "Output muda de estrutura entre chamadas idênticas",
            "Sem validação tipada = agente quebra em produção em < 48h",
            "Quanto maior a autonomia do agente, maior o risco de output malformado"
        ]
    },
    {
        "type": "content",
        "etapa": "FLUXO",
        "title": "Como PydanticAI resolve isso",
        "bullets": [
            "1. Você define o Agent com um result_type (modelo Pydantic)",
            "2. Registra tools com @agent.tool — tipagem validada na entrada E na saída",
            "3. Agent recebe prompt do usuário + dependencies (contexto injetado)",
            "4. LLM gera resposta → PydanticAI valida contra o schema → se formatação falha → erro explicado pro modelo",
            "5. Output final: objeto Python tipado. Não string. Não 'maybe JSON'."
        ]
    },
    {
        "type": "content",
        "etapa": "ANATOMIA",
        "title": "Anatomia de um Agent PydanticAI",
        "bullets": [
            "Agent(model, result_type, system_prompt) — o cérebro",
            "result_type = classe Pydantic — contrato do que o agente DEVE retornar",
            "@agent.tool → função Python que o agente pode chamar (com tipagem)",
            "RunContext(Dependencies) → injeta dados sem poluir o prompt",
            "agent.run_sync() → executa RunResult com .data tipado",
            "Retries embutidos: se o LLM erra o schema, PydanticAI corrige sozinho"
        ]
    },
    {
        "type": "code",
        "code": "from pydantic import BaseModel\nfrom pydantic_ai import Agent\n\nclass CodeReview(BaseModel):\n    aprovado: bool\n    problemas: list[str]\n    score_seguranca: float  # 0.0 a 1.0\n    sugestao_refactor: str | None\n\nagent = Agent(\n    'anthropic:claude-sonnet-4-20250514',\n    result_type=CodeReview,\n    system_prompt=(\n        'Você é um code reviewer sênior. '\n        'Analise o diff e retorne sua avaliação.'\n    ),\n)\n\nresult = agent.run_sync(\n    'def login(u,p): return db.query(f\"SELECT * FROM users WHERE user=\\'{u}\\' AND pass=\\'{p}\\'\")'  \n)\n\nprint(result.data.aprovado)           # False\nprint(result.data.score_seguranca)    # 0.1\nprint(result.data.problemas[0])       # 'SQL injection vulnerável'",
        "caption": "Output é CodeReview tipado. Não string. Não JSON pra parsear. Objeto Python."
    },
    {
        "type": "comparison",
        "left_label": "LangChain (chain tradicional)",
        "right_label": "PydanticAI",
        "left_items": [
            "Output: string → json.loads() → reza",
            "Tools: dicts com schema manual",
            "Validação: você implementa",
            "Retry: você implementa",
            "Tipagem: zero no output",
            "Debug: print no meio da chain"
        ],
        "right_items": [
            "Output: objeto Pydantic tipado",
            "Tools: funções Python com type hints",
            "Validação: automática pelo schema",
            "Retry: automático com feedback pro LLM",
            "Tipagem: end-to-end com mypy",
            "Debug: Logfire integrado nativamente"
        ]
    },
    {
        "type": "content",
        "etapa": "LIÇÕES",
        "title": "O que aprendi construindo agentes com PydanticAI",
        "bullets": [
            "result_type pequeno > result_type ambicioso. Agente com 3 campos acerta mais que com 15",
            "system_prompt curto e direto > prompt longo com 'você é especialista em...'",
            "Tools simples que fazem UMA coisa! > tool genérica é tool inútil",
            "Dependency injection via RunContext é o que diferencia toy project de produção",
            "model_retry com max_retries=3 salva 90% dos erros de schema",
            "PydanticAI foi criado pelo mesmo time do Pydantic. Não é wrapper. É extensão natural."
        ]
    },
    {
        "type": "content",
        "etapa": "ESPELHO",
        "title": "Se você já passou por isso...",
        "bullets": [
            "Já fez json.loads() no output do LLM e tomou KeyError em produção",
            "Já escreveu 'responda APENAS em JSON' no prompt e recebeu markdown",
            "Já criou regex pra extrair dados de resposta de modelo",
            "Já perdeu 2 dias debugando chain do LangChain sem entender onde quebrou",
            "Já sentiu que construir agente confiável é impossível sem framework tipado",
            "O Spotify resolveu isso. Você também pode."
        ]
    },
    {
        "type": "cta",
        "headline": "Qual foi o output mais bizarro que um LLM já te retornou em produção? Comenta aí — todo dev tem uma história de horror com JSON malformado.",
        "subline": "Se você quer aprender PydanticAI, RAG e Agentes autônomos na prática, a gente ensina na Disciplina D7 — IA Generativa da nossa pós de IA e ML. Diferença entre agente que quebra em produção toda segunda-feira e agente tipado que roda sozinho enquanto você revisa o PR tomando café.",
        "tags": ["#CódigoOuNãoAconteceu", "#NúmerosOuÉMentira", "#DevPraDevNãoGuruPraSeguidor", "#SemAutoajudaVazia", "#CarlosViana", "#ITValleySchool"]
    }
]

total = len(slides)
os.makedirs('/tmp/carrossel-novo', exist_ok=True)

async def generate_all():
    for i, slide in enumerate(slides):
        position = i + 1
        print(f"\n--- Gerando slide {position}/{total} (type={slide.get('type')}) ---", flush=True)
        start = time.time()
        try:
            result = await gerar_imagem_slide(
                slide=slide,
                slide_index=i,
                total_slides=total,
                gemini_api_key=gemini_key,
                foto_criador=foto_b64,
            )
            if result:
                img_data = result.split(',', 1)[1] if ',' in result else result
                fname = f'/tmp/carrossel-novo/slide-{position:02d}.png'
                with open(fname, 'wb') as f:
                    f.write(base64.b64decode(img_data))
                elapsed = time.time() - start
                print(f"  OK! ({elapsed:.1f}s) -> {fname}", flush=True)
            else:
                print(f"  FALHOU: sem imagem retornada", flush=True)
        except Exception as e:
            print(f"  ERRO: {e}", flush=True)

        # Delay between requests to avoid rate limiting
        if i < total - 1:
            await asyncio.sleep(3)

asyncio.run(generate_all())
print("\n=== DONE ===", flush=True)
