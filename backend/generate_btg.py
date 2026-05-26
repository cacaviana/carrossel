import asyncio, os, base64, time, json
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
        "headline": "Domingo de manhã.\nHackers entraram no BTG Pactual\ne saíram com R$ 100 milhões.",
        "subline": "Carlos Viana"
    },
    {
        "type": "content",
        "etapa": "CONTEXTO",
        "title": "O que realmente aconteceu",
        "bullets": [
            "Não foi conta de cliente. Não foi dado vazado.",
            "Foi a conta que o BTG mantém direto no Banco Central — a engrenagem invisível por trás de cada Pix que você faz.",
            "O Banco Central emitiu alerta às 6 da manhã.",
            "O BTG não travou a tempo."
        ]
    },
    {
        "type": "content",
        "etapa": "O ROTEIRO",
        "title": "Arquitetura do ataque",
        "bullets": [
            "O movimento foi cirúrgico.",
            "Pix saindo pra sete bancos diferentes ao mesmo tempo — Inter, Bradesco, Caixa, Itaú, PicPay, Mercado Pago, Banco do Brasil.",
            "Depois de lá, tudo convertido em cripto.",
            "Isso não é amador. Isso é arquitetura de ataque."
        ]
    },
    {
        "type": "content",
        "etapa": "LEITURA DO SISTEMA",
        "title": "Aqui é onde a maioria para de pensar",
        "bullets": [
            "Mas o dev que lê o sistema enxerga outra coisa.",
            "Esse não é o primeiro. Em junho de 2025, a C&M Software perdeu R$ 813 milhões via Pix.",
            "Em setembro, a Sinqia perdeu R$ 710 milhões.",
            "Os hackers pararam de atacar o app do banco.",
            "Agora eles atacam a infraestrutura invisível — os intermediários tecnológicos que ninguém vê mas que movimentam bilhões por dia."
        ]
    },
    {
        "type": "content",
        "etapa": "REVELAÇÃO",
        "title": "O que isso revela",
        "bullets": [
            "As novas regras de cibersegurança do Banco Central entraram em vigor em 1º de março de 2026.",
            "O ataque foi no dia 22.",
            "Três semanas depois.",
            "Regra nova no papel não é sistema seguro na prática. Nunca foi."
        ]
    },
    {
        "type": "content",
        "etapa": "VIRADA",
        "title": "O que ninguém está falando",
        "bullets": [
            "Existe uma geração inteira de devs que vai construir a segurança dessa infraestrutura nos próximos cinco anos.",
            "Não os que ficam ajustando prompt.",
            "Os que entendem como o sistema funciona por baixo."
        ]
    },
    {
        "type": "cta",
        "headline": "Se você quer entender como sistemas reais funcionam — e como eles quebram — me segue.",
        "subline": "carlosviana.ca",
        "tags": ["#CódigoOuNãoAconteceu", "#NúmerosOuÉMentira", "#DevPraDevNãoGuruPraSeguidor", "#SemAutoajudaVazia", "#CarlosViana", "#ITValleySchool"]
    }
]

total = len(slides)
os.makedirs('/tmp/carrossel-btg', exist_ok=True)

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
                fname = f'/tmp/carrossel-btg/slide-{position:02d}.png'
                with open(fname, 'wb') as f:
                    f.write(base64.b64decode(img_data))
                elapsed = time.time() - start
                print(f"  OK! ({elapsed:.1f}s) -> {fname}", flush=True)
            else:
                print(f"  FALHOU: sem imagem retornada", flush=True)
        except Exception as e:
            print(f"  ERRO: {e}", flush=True)

        if i < total - 1:
            await asyncio.sleep(3)

asyncio.run(generate_all())
print("\n=== DONE ===", flush=True)
