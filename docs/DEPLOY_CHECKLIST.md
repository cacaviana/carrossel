# Checklist de Deploy — Content Factory

## VM Azure (20.151.96.44)

### 1. Pull do codigo

```bash
cd /home/azureuser/carrossel   # ou onde estiver o projeto
git fetch origin
git checkout feat/refactor-dry-pipeline
git pull origin feat/refactor-dry-pipeline
```

### 2. Backend — instalar dependencias

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Dependencia nova:** `slowapi` (rate limiting). Se o pip falhar, instale manualmente:
```bash
pip install slowapi==0.1.9
```

### 3. Backend — configurar .env

Adicionar esta linha no `.env` do backend (OBRIGATORIO, senao CORS bloqueia tudo):

```env
ALLOWED_ORIGINS=https://app-carrossel-frontend.azurewebsites.net,http://20.151.96.44:5173,http://localhost:5173
```

**Se usar Azure App Service** com dominio customizado, adicionar o dominio tambem:
```env
ALLOWED_ORIGINS=https://seudominio.com,https://app-carrossel-frontend.azurewebsites.net,http://localhost:5173
```

Verificar que as chaves existentes continuam la:
```env
CLAUDE_API_KEY=sk-ant-...
GEMINI_API_KEY=AI...
GOOGLE_DRIVE_CREDENTIALS={"type":"service_account",...}
GOOGLE_DRIVE_FOLDER_ID=1FRsxT62...
MSSQL_URL=mssql+aioodbc://...   (se usar banco)
```

### 4. Backend — limpar cache Python

```bash
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
```

### 5. Backend — reiniciar

```bash
# Se usa systemd:
sudo systemctl restart carrossel-backend

# Se roda direto:
pkill -f "uvicorn main:app"
cd backend && source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
```

### 6. Backend — verificar

```bash
# Health check
curl http://localhost:8000/health
# Esperado: {"status":"ok"}

# Agentes (deve retornar 15)
curl -s http://localhost:8000/api/agentes | python3 -c "import sys,json; print(len(json.load(sys.stdin)))"
# Esperado: 15

# Rate limit (deve retornar headers X-RateLimit)
curl -v http://localhost:8000/api/agentes 2>&1 | grep -i ratelimit
```

### 7. Frontend — instalar e buildar

```bash
cd frontend
npm install
npm run build
```

### 8. Frontend — iniciar

```bash
# Se usa PM2:
pm2 restart carrossel-frontend

# Se roda direto:
npm run dev -- --port 5173 --host 0.0.0.0 &

# Se usa adapter-node em producao:
node build/index.js &
```

### 9. Frontend — verificar

Abrir no browser:
- `http://20.151.96.44:5173` (ou o dominio Azure)
- Clicar em "Agentes" no menu — deve mostrar "9 agentes LLM + 6 skills"
- Criar um pipeline de teste
- No editor, ultimo slide deve ter "Baixar PDF" e "Salvar no Drive"

### 10. Testar fluxo completo

1. Home → escolher "Carrossel" → "Ideia livre" → digitar tema → "Criar Carrossel"
2. Pipeline: acompanhar 7 etapas (Strategist → Content Critic)
3. Aprovar briefing (AP-1)
4. Escolher hook + aprovar copy (AP-2)
5. Aprovar visuais (AP-3)
6. Aguardar imagens (~1-2min)
7. Clicar "Ver Imagens" → Editor
8. Posicionar logo, testar "Corrigir texto" em um slide
9. Ultimo slide: "Baixar PDF" e "Salvar no Drive"
10. Verificar PDF baixado e link do Drive

---

## O que mudou neste deploy

### Novos arquivos criticos
- `backend/middleware/rate_limiter.py` — rate limiting
- `backend/utils/json_parser.py` — parse centralizado
- `backend/utils/constants.py` — GEMINI_API_URL centralizada
- `backend/utils/image_text_fixer.py` — correcao de texto DRY
- `backend/services/brand_service.py` — logica de brands
- `backend/services/editor_service.py` — logica do editor (PDF, correcao)
- `backend/services/pipeline_service.py` — logica de aprovacao/rejeicao
- `frontend/src/lib/api.ts` — API_BASE centralizado
- `frontend/src/lib/components/ui/SlideDotsNav.svelte` — componente extraido
- `frontend/src/lib/components/pipeline/ApprovalBar.svelte` — componente extraido
- `frontend/playwright.config.ts` + `frontend/e2e/` — testes E2E

### Mudancas de comportamento
- **CORS**: era `["*"]`, agora precisa de `ALLOWED_ORIGINS` no .env
- **Rate limiting**: endpoints de geracao limitados a 5/min por IP
- **Imagens**: geracao paralela (3 simultaneas) em vez de sequencial
- **Texto errado**: retry preserva visual original (antes regenerava do zero)
- **Agentes**: endpoint retorna 15 (9 LLM + 6 skills) em vez de 2

### Nada que quebre o fluxo existente
- Todos os endpoints mantêm mesmos paths e response formats
- O fluxo legado (/carrossel) continua funcionando
- Nenhum dado do banco foi alterado
