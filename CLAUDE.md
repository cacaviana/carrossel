# Sistema de Carrosséis IT Valley

## O que é
App web que cria carrosséis LinkedIn pra IT Valley School.
Pipeline: escolhe tema → gera conteúdo (Claude Code CLI ou API) → edita slides → gera imagens (Gemini) → exporta PDF → salva Google Drive.

## Skills na pasta agents/
- anti-bel-pesce.md = system prompt do Agente 1 (conteúdo) — 3, 7 ou 10 slides
- nano-banana-carrossel.md = lógica do Agente 2 (imagens) — dark mode premium
- design-system.html = referência visual dark mode Carlos Viana / IT Valley School

## Stack
- Frontend: SvelteKit + Tailwind CSS v4 + dark mode premium + fonte Outfit + jsPDF
- Backend: Python FastAPI (estrutura IT Valley — tudo na raiz de backend/)

## Estrutura
```
carrossel-system/
  agents/             # Skills dos agentes
  frontend/           # SvelteKit app
    src/
      routes/         # /, /carrossel, /historico, /agentes, /configuracoes
      lib/
        stores/       # config.ts (backendUrl, fotoCriador), carrossel.ts
        data/         # disciplinas.ts
  backend/
    main.py
    routers/          # conteudo, imagem, drive, config, agentes
    services/         # conteudo_service, conteudo_cli_service, imagem_service, drive_service
    dtos/             # Pydantic request/response
    .env              # NUNCA commitar — chaves salvas aqui
```

## API routes
POST /api/gerar-conteudo      → Claude API (pago)
POST /api/gerar-conteudo-cli  → Claude Code CLI (grátis, usa sessão local)
POST /api/gerar-imagem        → Gemini (todos os slides)
POST /api/gerar-imagem-slide  → Gemini (slide individual)
POST /api/google-drive/carrossel → cria subpasta + salva PDF + PNGs
GET  /api/drive/pastas        → lista pastas compartilhadas com service account
POST /api/config              → salva chaves no .env
GET  /api/config              → retorna status das chaves (sem expor valor)
GET  /api/agentes             → retorna conteúdo das skills

## Modelos Gemini — estratégia de custo
Suporta 3, 7 e 10 slides. Pro nos slides de alto impacto, Flash grátis no resto.

| Formato | Slides Pro | Slides Flash | Custo total |
|---------|-----------|-------------|-------------|
| 10 slides | 1 (capa), 6 (código), 10 (CTA) | 2-5, 7-9 | ~R$2,25 |
| 7 slides | 1 (capa), 6, 7 (CTA) | 2-5 | ~R$2,25 |
| 3 slides | 1 (capa), 2 (código), 3 (CTA) | — | ~R$2,25 |

Config em: backend/services/imagem_service.py → _select_model()
Templates em: backend/services/prompt_templates.py (dark mode premium)
Payload correto: { "responseModalities": ["IMAGE", "TEXT"] } — SEM imageMimeType

## Geração de conteúdo — dois modos
- Claude Code CLI: spawna `claude --dangerously-skip-permissions --system-prompt ... --output-format json --tools "" -p ...`
  - Requer: unset CLAUDECODE no env do subprocess (evita sessão aninhada)
  - Timeout: 180s
- Claude API: usa anthropic SDK com model claude-sonnet-4-20250514

## Google Drive
- Service account: itvalley-cloud-services@infinite-rider-442118-q1.iam.gserviceaccount.com
- Pasta raiz: Posts LinkendIN (1FRsxT62esou3hXMHkoIxNY1eh1yiMFst)
- Subpastas criadas automaticamente: "{título} - {YYYY-MM-DD}"
- Conteúdo: PDF + slide-01.png ... slide-NN.png (N = total de slides)
- Scope necessário: https://www.googleapis.com/auth/drive

## Chaves (.env no backend/)
- CLAUDE_API_KEY
- GEMINI_API_KEY
- GOOGLE_DRIVE_CREDENTIALS (JSON da service account)
- GOOGLE_DRIVE_FOLDER_ID

## Como rodar (nuvem — VM Azure 20.151.96.44)
```bash
# Backend (exposto na rede)
cd backend && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (exposto na rede)
cd frontend && npm run dev -- --port 5173 --host 0.0.0.0
```
Portas 5173 e 8000 precisam estar abertas no NSG da Azure.

## Disciplinas
D1 Linguagens (YOLO, OpenCV), D2 ETL, D3 ML (XGBoost, SVM), D4 Preditiva (Feature Eng),
D5 Deep Learning (Transfer Learning), D6 NLP (Whisper), D7 IA Gen (RAG, Agentes, LangChain),
D8 Cloud (AWS Serverless), D9 MLOps (Data Drift)
