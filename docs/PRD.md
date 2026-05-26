# PRD -- Content Factory v3

## 1. Visao Geral

**Problema:** A IT Valley School precisa produzir conteudo visual para multiplas redes sociais (LinkedIn, Instagram, YouTube, Meta Ads) mas depende de uma designer que leva 1 semana por arte. O sistema de carrossel existente gera conteudo generico, com aparencia de "feito por IA", que nao engaja. Carlos Viana precisa de volume com qualidade visual premium e identidade de marca consistente.

**Solucao:** O Content Factory v3 transforma o gerador de carrosseis atual em uma fabrica de conteudo visual multi-formato com pipeline de 6 agentes LLM especializados, 6 skills deterministicas (sem LLM), aprovacao humana em pontos intermediarios e um Brand Gate que garante consistencia visual. O pipeline e 80% compartilhado entre formatos -- o que muda sao dimensoes, templates e regras de plataforma (20%).

**Usuarios-alvo:** Equipe de marketing da IT Valley School.

**Multitenante:** Nao no momento. Single-user com tenant_id padrao. Estrutura preparada para multitenancia futura (tenant_id em toda tabela e toda query).

---

## 2. Perfis de Usuario (ACL)

| Perfil | Descricao | Permissoes Principais |
|--------|-----------|----------------------|
| Marketing | Equipe de marketing da IT Valley. Opera o pipeline, aprova etapas intermediarias, escolhe variacoes. | Criar conteudo, aprovar/rejeitar etapas, escolher entre variacoes, exportar, salvar no Drive, ver historico, configurar preferencias visuais |
| Admin | Carlos Viana ou responsavel tecnico | Tudo do Marketing + configurar chaves de API, gerenciar agentes, gerenciar creator registry, configurar brand palette |

---

## 3. Pipeline de Agentes

O pipeline e a espinha dorsal do sistema. Ele e **identico para todos os formatos** -- o que muda por formato sao configs (dimensoes, template de campos, regras de plataforma).

### 3.1 Fluxo Completo

```
[Usuario informa tema + formato(s)]
         |
         v
   1. STRATEGIST (LLM)
         |  briefing com funil (1 tema -> 5-7 pecas)
         v
   *** APROVACAO HUMANA: usuario aprova/edita briefing ***
         |
         v
   2. COPYWRITER (LLM)
         |  headline, narrativa, CTA, sequencia
         v
   3. HOOK SPECIALIST (LLM)
         |  3 ganchos A/B/C
         v
   *** APROVACAO HUMANA: usuario escolhe hook + aprova copy ***
         |
         v
   4. ART DIRECTOR (LLM)
         |  prompt de imagem detalhado
         v
   *** APROVACAO HUMANA: usuario aprova/edita prompt visual ***
         |
         v
   5. IMAGE GENERATOR (Gemini API -- nao e LLM)
         |  3 variacoes de imagem
         v
   6. BRAND GATE (deterministico -- nao e LLM)
         |  brand_validator checa -> valido -> brand_overlay aplica
         |  invalido -> retry (max 2x) -> volta para Image Generator
         v
   *** APROVACAO HUMANA: usuario escolhe melhor variacao ***
         |
         v
   7. CONTENT CRITIC (LLM)
         |  score final {clarity, impact, originality, scroll_stop,
         |               cta_strength, final_score, decision, best_variation}
         v
   [Conteudo final -> Export PDF / Save Drive]
```

### 3.2 Pontos de Aprovacao Humana

O pipeline NAO e autonomo. Existem 4 pontos de aprovacao obrigatorios:

| Ponto | Apos Agente | O que o usuario faz |
|-------|-------------|---------------------|
| AP-1 | Strategist | Aprova ou edita o briefing gerado |
| AP-2 | Hook Specialist | Escolhe entre 3 hooks (A/B/C) e aprova a copy completa |
| AP-3 | Art Director | Aprova ou edita o prompt visual antes da geracao de imagem |
| AP-4 | Brand Gate | Escolhe entre variacoes de imagem validadas pela marca |

### 3.3 Agentes LLM (6)

| # | Agente | Entrada | Saida | LLM |
|---|--------|---------|-------|-----|
| 1 | Strategist | tema + formato(s) alvo | briefing estruturado com funil (topo/meio/fundo), 1 tema -> 5-7 pecas conectadas | Claude API |
| 2 | Copywriter | briefing aprovado | headline, narrativa, CTA, sequencia de slides/campos | Claude API |
| 3 | Hook Specialist | copy completa | 3 ganchos A/B/C com variacao de abordagem | Claude API |
| 4 | Art Director | copy + hook escolhido + brand_palette + platform_rules | prompt de imagem detalhado por slide/campo, adaptado ao formato | Claude API |
| 5 | Image Generator | prompt de imagem | 3 variacoes de imagem | Gemini API (Pro/Flash) |
| 6 | Content Critic | arte final pos-Brand Gate | score {clarity, impact, originality, scroll_stop, cta_strength, final_score, decision, best_variation} | Claude API |

### 3.4 Skills Deterministicas (6 -- zero LLM)

| # | Skill | O que faz | Quando e chamada |
|---|-------|-----------|------------------|
| 1 | brand_overlay | Pillow: aplica foto redonda do Carlos + logo IT Valley em posicao fixa | Dentro do Brand Gate, apos validacao |
| 2 | brand_validator | Pillow: valida cores, aspect ratio, elementos obrigatorios da marca | Dentro do Brand Gate, antes do overlay |
| 3 | visual_memory | Persiste preferencias visuais do usuario em JSON (estilos aprovados/rejeitados) | Apos aprovacao humana de imagem (AP-4) |
| 4 | variation_engine | Gera 3 variacoes de prompt via manipulacao de string (sem LLM) | Antes do Image Generator, a partir do prompt do Art Director |
| 5 | tone_guide | Valida vocabulario IT Valley (termos proibidos, tom de voz, jargoes) | Apos Copywriter, antes de passar adiante |
| 6 | trend_scanner | Busca conteudo dos criadores do registry (dev.to + HN + YouTube RSS), cache 1h | Alimenta o Strategist com tendencias atuais |

### 3.5 Brand Gate

O Brand Gate e um checkpoint **deterministico** (sem LLM) entre o Image Generator e o Content Critic:

1. `brand_validator` analisa a imagem gerada:
   - Cores dentro da paleta? (tolerancia definida em brand_palette.json)
   - Aspect ratio correto para o formato?
   - Elementos obrigatorios presentes?
2. Se **valido**: `brand_overlay` aplica foto do Carlos + logo -> segue para Content Critic
3. Se **invalido**: retry automatico (max 2 tentativas) -> volta para Image Generator com prompt ajustado
4. Se falhar apos 2 retries: marca como "revisao manual necessaria"

---

## 4. Formatos de Saida

### 4.1 Arquitetura 80/20

O pipeline e 80% compartilhado. O que diferencia cada formato (20%) esta encapsulado em configs JSON:

| Config | O que define |
|--------|-------------|
| dimensions.json | Largura x Altura por formato |
| templates.json | Estrutura de campos por formato (quais campos existem, ordem) |
| brand_palette.json | Cores, fonte, elementos obrigatorios (compartilhado) |
| platform_rules.json | Limites de caracteres, hashtags, specs por plataforma |
| creator_registry.json | Lista curada de criadores por funcao (compartilhado) |

### 4.2 Formatos Suportados

| Formato | Dimensoes | Plataformas | MVP |
|---------|-----------|-------------|-----|
| Carrossel | 1080x1350 | LinkedIn, Instagram | Sim |
| Post imagem unica | 1080x1080 | Feed Instagram, Facebook, LinkedIn | Sim |
| Thumbnail YouTube | 1280x720 | YouTube | Sim |
| Capa de Reels | 1080x1920 | Instagram Reels | Nao |
| Anuncio | 1080x1080 | Meta Ads, Google Ads | Nao |

### 4.3 Modo Funil

O Strategist pode gerar um **funil de conteudo** a partir de 1 unico tema:

- 1 briefing = 5 a 7 pecas conectadas
- Distribuicao por etapa do funil: topo (awareness), meio (consideracao), fundo (conversao)
- Cada peca pode ser de formato diferente (ex: 1 carrossel topo + 1 post meio + 1 thumbnail fundo)
- O usuario aprova o plano do funil antes da execucao

---

## 5. Configs (JSON puro)

### 5.1 dimensions.json

```json
{
  "carrossel": { "width": 1080, "height": 1350 },
  "post_unico": { "width": 1080, "height": 1080 },
  "capa_reels": { "width": 1080, "height": 1920 },
  "thumbnail_youtube": { "width": 1280, "height": 720 },
  "anuncio": { "width": 1080, "height": 1080 }
}
```

### 5.2 brand_palette.json

```json
{
  "cores": {
    "fundo_principal": "#0A0A0F",
    "destaque_primario": "#A78BFA",
    "destaque_secundario": "#6D28D9",
    "texto_principal": "#FFFFFF",
    "texto_secundario": "#94A3B8"
  },
  "fonte": "Outfit",
  "elementos_obrigatorios": ["foto_carlos_redonda", "logo_itvalley"],
  "estilo": "dark_mode_premium"
}
```

### 5.3 creator_registry.json

Lista curada de criadores por funcao para alimentar o trend_scanner:

| Funcao | Descricao | Quantidade |
|--------|-----------|------------|
| TECH_SOURCE | Fontes tecnicas (blogs, repositorios) | 5-8 fixas |
| EXPLAINER | Criadores que explicam conceitos | 5-8 fixas |
| VIRAL_ENGINE | Criadores com alto engajamento | 5-8 fixas |
| THOUGHT_LEADER | Lideres de opiniao em tech | 5-8 fixas |
| DINAMICAS | Criadores adicionados pelo usuario | ate 10 |

Total: 20-30 fixas + ate 10 dinamicas.

**Criadores confirmados (lista inicial):**

| Criador | Funcao | Plataforma |
|---------|--------|------------|
| Fireship | EXPLAINER | YouTube |
| Andrej Karpathy | THOUGHT_LEADER | YouTube/Twitter |
| Yannic Kilcher | TECH_SOURCE | YouTube |
| Two Minute Papers | EXPLAINER | YouTube |
| Sentdex | TECH_SOURCE | YouTube |
| Lucas Montano | TECH_SOURCE | YouTube |
| Filipe Deschamps | EXPLAINER | YouTube |
| Fabio Akita | THOUGHT_LEADER | YouTube |
| Augusto Galego | TECH_SOURCE | YouTube |
| Tecnologia e Classe (Teclas) | EXPLAINER | YouTube |
| Matheus IA Coding | TECH_SOURCE | YouTube |

Fontes de dados: dev.to API, Hacker News API, YouTube RSS feeds.

---

## 6. Modulos do Sistema

### Modulo Pipeline

- **Descricao:** Orquestra a execucao do pipeline de agentes, gerencia estado entre etapas, persiste progresso, permite retomar de qualquer ponto.
- **Perfis com acesso:** Marketing, Admin
- **Funcionalidades:**
  - Iniciar pipeline com tema + formato(s) alvo
  - Pausar em pontos de aprovacao humana
  - Retomar apos aprovacao/edicao
  - Retry automatico no Brand Gate (max 2x)
  - Rastrear status de cada etapa (pendente, em_execucao, aguardando_aprovacao, aprovado, rejeitado, erro)
  - Modo funil: gerar multiplas pecas a partir de 1 tema

### Modulo Agentes

- **Descricao:** Gerencia os 6 agentes LLM. Cada agente tem seu system prompt, recebe entrada estruturada e produz saida estruturada.
- **Perfis com acesso:** Marketing, Admin
- **Funcionalidades:**
  - Executar agente individual com entrada tipada
  - Visualizar system prompt de cada agente
  - Historico de execucoes por agente

### Modulo Skills

- **Descricao:** Executa as 6 skills deterministicas. Nenhuma usa LLM.
- **Perfis com acesso:** Marketing, Admin (execucao automatica pelo pipeline)
- **Funcionalidades:**
  - brand_overlay: aplica foto + logo via Pillow
  - brand_validator: valida conformidade visual
  - visual_memory: persiste preferencias
  - variation_engine: gera 3 variacoes de prompt
  - tone_guide: valida vocabulario
  - trend_scanner: busca tendencias com cache 1h

### Modulo Conteudo (existente -- sera refatorado)

- **Descricao:** Geracao de conteudo textual. Hoje usa Claude API / CLI direto. Sera absorvido pelo pipeline (Copywriter + Hook Specialist).
- **Perfis com acesso:** Marketing, Admin
- **Funcionalidades:**
  - Gerar conteudo via Claude API
  - Gerar conteudo via Claude Code CLI (modo gratis)

### Modulo Imagem (existente -- sera refatorado)

- **Descricao:** Geracao de imagens via Gemini API. Sera absorvido pelo pipeline (Image Generator + Brand Gate).
- **Perfis com acesso:** Marketing, Admin
- **Funcionalidades:**
  - Gerar imagem por slide/campo
  - Gerar 3 variacoes
  - Estrategia Pro/Flash por relevancia do slide

### Modulo Export

- **Descricao:** Exportacao do conteudo final em PDF e imagens PNG.
- **Perfis com acesso:** Marketing, Admin
- **Funcionalidades:**
  - Export PDF (jsPDF no frontend)
  - Download de imagens individuais (PNG)
  - Salvar no Google Drive (subpasta automatica)

### Modulo Historico (existente)

- **Descricao:** Registro de todos os conteudos gerados com metadados.
- **Perfis com acesso:** Marketing, Admin
- **Funcionalidades:**
  - Listar historico com filtros (formato, data, status)
  - Visualizar conteudo gerado
  - Reabrir pipeline de um conteudo anterior

### Modulo Configuracoes (existente)

- **Descricao:** Gerenciamento de chaves de API e configuracoes do sistema.
- **Perfis com acesso:** Admin
- **Funcionalidades:**
  - Configurar chaves (Claude, Gemini, Google Drive)
  - Gerenciar brand_palette.json
  - Gerenciar creator_registry.json
  - Gerenciar platform_rules.json

---

## 7. Regras de Negocio

| ID | Regra | Modulo |
|----|-------|--------|
| RN-001 | O pipeline NAO e autonomo. Existem 4 pontos de aprovacao humana obrigatorios (AP-1 a AP-4). O conteudo so avanca quando o usuario aprova. | Pipeline |
| RN-002 | O Brand Gate permite no maximo 2 retries automaticos. Apos isso, marca como "revisao manual necessaria". | Pipeline / Skills |
| RN-003 | O Strategist pode gerar um funil de 5-7 pecas conectadas a partir de 1 tema. Cada peca passa pelo pipeline completo. | Pipeline / Agentes |
| RN-004 | O trend_scanner faz cache de 1 hora. Nao busca dados novos antes de expirar o cache. | Skills |
| RN-005 | O variation_engine sempre gera exatamente 3 variacoes de prompt (sem LLM, manipulacao de string). | Skills |
| RN-006 | O tone_guide valida vocabulario IT Valley antes do conteudo seguir no pipeline. Se reprovar, o Copywriter e re-executado com feedback. | Skills / Agentes |
| RN-007 | O visual_memory persiste preferencias do usuario (estilos aprovados/rejeitados) e alimenta o Art Director em execucoes futuras. | Skills / Agentes |
| RN-008 | Modelo Gemini Pro e usado para slides de alto impacto (capa, codigo, CTA). Flash para o restante. Custo alvo: ~R$2,25 por conteudo de 10 slides. | Imagem |
| RN-009 | O Content Critic gera score com 6 dimensoes: clarity, impact, originality, scroll_stop, cta_strength, final_score. Se final_score < 7, recomenda ajustes. | Agentes |
| RN-010 | tenant_id presente em toda tabela e toda query, mesmo em modo single-user. | Todos |
| RN-011 | O Hook Specialist sempre gera exatamente 3 opcoes (A, B, C) com abordagens diferentes. | Agentes |
| RN-012 | O pipeline pode ser retomado de qualquer ponto. O estado e persistido a cada etapa. | Pipeline |
| RN-013 | O usuario pode editar a saida de qualquer agente antes de aprovar (nao apenas aceitar/rejeitar). | Pipeline |
| RN-014 | Configs (dimensions, templates, brand_palette, platform_rules, creator_registry) sao JSON puro, sem logica de negocio. | Configuracoes |

---

## 8. Integracoes Externas

| Sistema | Tipo | Finalidade |
|---------|------|-----------|
| Claude API (Anthropic) | API REST | LLM para os 5 agentes textuais (Strategist, Copywriter, Hook Specialist, Art Director, Content Critic) |
| Claude Code CLI | Subprocess local | Modo gratuito de geracao de conteudo (usa sessao local do Claude Code) |
| Gemini API (Google) | API REST | Geracao de imagens (Image Generator). Modelos Pro e Flash. |
| Google Drive API | API REST (OAuth2 service account) | Salvar PDF + PNGs em subpastas automaticas |
| MSSQL | Conexao direta (pyodbc/SQLAlchemy) | Persistencia de historico, estado do pipeline, visual_memory |
| dev.to API | API REST | trend_scanner: buscar artigos tecnicos recentes |
| Hacker News API | API REST | trend_scanner: buscar noticias tech em alta |
| YouTube RSS | HTTP/RSS | trend_scanner: buscar videos recentes dos criadores registrados |

---

## 9. Requisitos Nao Funcionais

- **Performance:** Geracao de conteudo textual (agentes LLM) em menos de 30s por etapa. Geracao de imagem em menos de 60s por variacao. Skills deterministicas em menos de 2s.
- **Seguranca:** tenant_id em toda tabela e query. Chaves de API armazenadas em .env no servidor, nunca expostas ao frontend. JWT preparado para quando houver multitenancia.
- **Escalabilidade:** Sistema roda em Azure VM unica por enquanto. Arquitetura permite extrair agentes para microservicos no futuro.
- **Disponibilidade:** Sistema interno, nao e critico 24/7. Tolerancia a downtime para deploys.
- **Custo:** Alvo de ~R$2,25 por conteudo de 10 slides (estrategia Pro/Flash Gemini). Claude API usado com modelo claude-sonnet para balanco custo/qualidade.
- **Resiliencia:** Pipeline persiste estado a cada etapa. Em caso de falha, o usuario retoma de onde parou sem perder progresso.
- **Observabilidade:** Logs estruturados por execucao de pipeline. Historico de scores do Content Critic para acompanhar evolucao da qualidade.

---

## 10. MVP -- Escopo do Primeiro Lancamento

### Formatos
- Carrossel (LinkedIn, Instagram) -- refatoracao completa do existente
- Post imagem unica (Feed Instagram, Facebook, LinkedIn)
- Thumbnail YouTube

### Pipeline completo
- 6 agentes LLM operacionais (Strategist, Copywriter, Hook Specialist, Art Director, Image Generator, Content Critic)
- 6 skills deterministicas operacionais (brand_overlay, brand_validator, visual_memory, variation_engine, tone_guide, trend_scanner)
- Brand Gate com retry automatico (max 2x)
- 4 pontos de aprovacao humana (AP-1 a AP-4)

### Configs
- dimensions.json (3 formatos MVP)
- templates.json (3 formatos MVP)
- brand_palette.json
- platform_rules.json (LinkedIn, Instagram, YouTube)
- creator_registry.json (20-30 criadores fixos)

### Infraestrutura
- Persistencia de estado do pipeline (retomar de qualquer ponto)
- Historico de execucoes com scores
- Export PDF + PNG
- Save Google Drive
- Visual memory (preferencias visuais)

### Frontend
- Tela de criacao com selecao de formato
- Tela de pipeline com aprovacao em etapas
- Tela de escolha entre variacoes (hooks, imagens)
- Tela de historico (refatorada para multi-formato)
- Tela de configuracoes (chaves + brand palette + creator registry)

---

## 11. Roadmap -- Fora do MVP

| Item | Descricao | Prioridade |
|------|-----------|------------|
| Capa de Reels | Formato 1080x1920 para Instagram Reels | Alta |
| Anuncio | Formato 1080x1080 para Meta Ads e Google Ads | Alta |
| Multitenancia real | Multiplas empresas usando a mesma plataforma, isolamento por tenant_id | Media |
| Dashboard de performance | Metricas de engajamento por conteudo (integracao com APIs das redes) | Media |
| Agendamento de publicacao | Agendar posts diretamente nas plataformas | Media |
| A/B testing automatico | Publicar 2 variacoes e medir qual performa melhor | Baixa |
| Creator registry dinamico | Descoberta automatica de novos criadores relevantes | Baixa |
| Templates visuais customizados | Usuario cria templates alem dos padrao | Baixa |
| Modo batch | Gerar conteudo em massa para semana/mes inteiro | Media |
| Integracao WhatsApp | Alertas de conteudo pronto via microservico WhatsApp existente | Baixa |

---

## 12. Entidades Principais

| Entidade | Descricao | Campos-chave |
|----------|-----------|-------------|
| Pipeline | Execucao completa do pipeline para 1 conteudo | id, tenant_id, tema, formato, status, etapa_atual, created_at |
| PipelineStep | Estado de cada etapa do pipeline | id, pipeline_id, agente, entrada, saida, status, aprovado_por, approved_at |
| Conteudo | Conteudo final gerado (texto + metadados) | id, tenant_id, pipeline_id, formato, titulo, copy, hook, cta |
| Imagem | Imagem gerada por slide/campo | id, conteudo_id, variacao, url_drive, score, selecionada |
| Score | Score do Content Critic | id, conteudo_id, clarity, impact, originality, scroll_stop, cta_strength, final_score, decision |
| VisualPreference | Preferencia visual persistida | id, tenant_id, estilo, aprovado, contexto, created_at |
| CreatorEntry | Entrada no creator registry | id, nome, funcao, plataforma, url, ativo |

---

## 13. Dvidas em Aberto

| ID | Dvida | Impacto |
|----|-------|---------|
| DA-001 | Qual o limite de pecas por funil? O Strategist gera 5-7, mas o usuario pode pedir mais? | Strategist, Pipeline |
| DA-002 | O Content Critic com score < 7 recomenda ajustes, mas quem decide se refaz? O usuario ou e automatico? | Pipeline, Agentes |
| DA-003 | O Claude Code CLI (modo gratis) sera mantido na v3 ou so Claude API pago? | Agentes, Custo |
| DA-004 | O visual_memory influencia so o Art Director ou tambem o Image Generator (ex: parametros Gemini)? | Skills, Agentes |
| DA-005 | O tone_guide tem lista de termos proibidos definida? Quem mantem essa lista? | Skills, Configuracoes |
| DA-006 | A foto redonda do Carlos e fixa ou o usuario pode trocar por outra pessoa? | Skills (brand_overlay) |
| DA-007 | O trend_scanner deve rodar automaticamente antes de cada pipeline ou sob demanda? | Skills, Pipeline |
| DA-008 | Existe limite de budget diario/mensal para chamadas de API (Claude + Gemini)? | Pipeline, Configuracoes |

---

## 14. Glossario

| Termo | Definicao |
|-------|-----------|
| Pipeline | Sequencia completa de agentes e skills que transforma um tema em conteudo visual final |
| Agente LLM | Componente que usa modelo de linguagem (Claude/Gemini) para gerar conteudo |
| Skill deterministica | Componente que executa logica fixa sem usar LLM (Pillow, manipulacao de string, HTTP) |
| Brand Gate | Checkpoint deterministico que valida conformidade visual da marca antes do conteudo seguir |
| Ponto de aprovacao (AP) | Momento do pipeline onde o humano deve aprovar/editar/escolher antes de continuar |
| Funil | Conjunto de 5-7 pecas de conteudo conectadas (topo/meio/fundo) geradas a partir de 1 tema |
| Creator Registry | Lista curada de criadores de conteudo que alimentam o trend_scanner |
| Visual Memory | Persistencia de preferencias visuais do usuario para melhorar geracoes futuras |
| Brand Palette | Configuracao de cores, fonte e elementos visuais obrigatorios da marca |
| Variation Engine | Skill que gera 3 variacoes de prompt sem usar LLM |
| Content Critic | Agente LLM que avalia o conteudo final com score numerico em 6 dimensoes |
| Dark Mode Premium | Estilo visual padrao IT Valley: fundo escuro (#0A0A0F), acentos roxos, fonte Outfit |
| Camada opaca | Service e Router que nao conhecem campos do DTO -- so delegam |
| Factory | Camada que cria objetos e contem regras de negocio |
| DTO | Data Transfer Object -- define o que entra e sai de cada caso de uso |

---

## 15. Stack Tecnica (referencia para agentes seguintes)

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python FastAPI (tudo na raiz de backend/, sem pasta app/) |
| Frontend | SvelteKit 5 + Tailwind CSS v4 |
| LLM conteudo | Claude API (Anthropic) -- modelo claude-sonnet |
| LLM imagem | Gemini API (Google) -- Pro + Flash |
| Processamento imagem | Pillow (Python) |
| Banco de dados | MSSQL (SQLAlchemy) |
| Storage | Google Drive (service account) |
| Export | jsPDF (frontend) + PNG |
| Deploy | Azure VM (20.151.96.44) |
| Fonte | Outfit |

---

*Documento gerado pelo Agente 01 (PRD Analyst) da esteira IT Valley.*
*Proximo: Agente 02 (Analista de Tela).*
