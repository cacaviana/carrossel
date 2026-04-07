# TELAS -- Content Factory v3

Documento de telas gerado pelo Agente 02 (Analista de Tela).
Base: PRD Content Factory v3 + analise das telas existentes no frontend SvelteKit 5.

---

## Sumario de Telas

| # | Tela | Rota | Status | Observacao |
|---|------|------|--------|------------|
| 1 | Home / Criar Conteudo | `/` | Refatorar | Hoje so cria carrossel. Precisa suportar multi-formato + iniciar pipeline v3 |
| 2 | Pipeline (Wizard de Etapas) | `/pipeline/[id]` | Nova | Tela principal da v3: acompanha pipeline com aprovacoes humanas |
| 3 | Aprovacao de Briefing (AP-1) | `/pipeline/[id]/briefing` | Nova | Sub-tela do pipeline: aprovar/editar briefing do Strategist |
| 4 | Aprovacao de Copy + Hook (AP-2) | `/pipeline/[id]/copy` | Nova | Sub-tela do pipeline: escolher hook A/B/C + aprovar copy |
| 5 | Aprovacao de Prompt Visual (AP-3) | `/pipeline/[id]/visual` | Nova | Sub-tela do pipeline: aprovar/editar prompt do Art Director |
| 6 | Aprovacao de Imagem (AP-4) | `/pipeline/[id]/imagem` | Nova | Sub-tela do pipeline: escolher entre variacoes de imagem |
| 7 | Preview e Export | `/pipeline/[id]/export` | Nova | Score do Content Critic + export PDF + salvar Drive |
| 8 | Editor de Conteudo (legado) | `/carrossel` | Manter | Preview/edicao do carrossel legado. Sera deprecado apos pipeline v3 |
| 9 | Historico | `/historico` | Refatorar | Adicionar filtro por formato, status do pipeline, scores |
| 10 | Agentes | `/agentes` | Refatorar | Mostrar 6 agentes LLM + 6 skills deterministicas + status do pipeline |
| 11 | Configuracoes | `/configuracoes` | Refatorar | Adicionar brand_palette, creator_registry, platform_rules |

---

## Navegacao Global

O layout atual (`+layout.svelte`) usa header com navegacao horizontal. O PRD menciona sidebar (menu lateral). A decisao de layout visual e do Designer (Agente 05), mas os itens de navegacao sao:

| Item | Rota | Perfis |
|------|------|--------|
| Home | `/` | Marketing, Admin |
| Pipeline | `/pipeline/[id]` | Marketing, Admin |
| Historico | `/historico` | Marketing, Admin |
| Agentes | `/agentes` | Marketing, Admin |
| Config | `/configuracoes` | Admin |

---

## Telas Detalhadas

---

### TELA: Home / Criar Conteudo

**Rota:** `/`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Ponto de entrada do sistema. O usuario informa o tema e seleciona o(s) formato(s) de saida para iniciar o pipeline. Substitui a tela atual que so cria carrosseis.

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| tema | text (textarea) | S | Minimo 20 caracteres | formulario |
| formato | select (multi-check) | S | Pelo menos 1 formato selecionado. Opcoes MVP: Carrossel, Post Unico, Thumbnail YouTube | formulario |
| modo_funil | toggle | N | Se ativo, Strategist gera 5-7 pecas conectadas | formulario |
| modo_entrada | select (tabs) | S | "texto" ou "disciplina" (manter legado) | formulario |
| disciplina | select (cards) | S (se modo=disciplina) | Deve estar na lista de disciplinas | formulario (store disciplinas) |
| tecnologia | select (chips) | S (se modo=disciplina) | Deve pertencer a disciplina selecionada | formulario (derivado de disciplina) |
| tema_custom | text | N | Opcional, complementa disciplina+tech | formulario |
| foto_criador | select (galeria) | N | Foto previamente carregada em Config | store (fotos) |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Selecionar formato(s) | clique nos cards de formato | Atualiza lista de formatos selecionados |
| Ativar modo funil | toggle change | Habilita geracao de 5-7 pecas por tema |
| Alternar modo entrada | clique na tab texto/disciplina | Mostra textarea ou selecao de disciplina |
| Selecionar disciplina | clique no card | Exibe lista de tecnologias da disciplina |
| Selecionar tecnologia | clique no chip | Marca tecnologia como selecionada |
| Selecionar foto | clique na miniatura | Define foto do criador para o pipeline |
| Iniciar Pipeline | clique no botao "Criar Conteudo" (submit) | Cria pipeline no backend, redireciona para `/pipeline/[id]` |

#### Estados da Tela

- **Loading:** Enquanto cria pipeline no backend. Botao mostra spinner + "Iniciando pipeline..."
- **Vazio:** Estado inicial. Todos os campos vazios, botao desabilitado ate preencher tema + formato.
- **Erro:** Validacao falhou (tema curto, nenhum formato selecionado) ou backend indisponivel. Mostra mensagem em banner vermelho.
- **Sucesso:** Pipeline criado. Redireciona automaticamente para `/pipeline/[id]`.

#### Fluxos de Navegacao

- Selecionar formato + preencher tema -> clicar "Criar Conteudo" -> `/pipeline/[id]`
- Clicar "Adicionar fotos" (se nenhuma foto) -> `/configuracoes`
- Nav: qualquer item do menu global

---

### TELA: Pipeline (Wizard de Etapas)

**Rota:** `/pipeline/[id]`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Tela central da v3. Mostra o progresso do pipeline como um wizard vertical/horizontal com 7 etapas. Cada etapa tem um status (pendente, em_execucao, aguardando_aprovacao, aprovado, rejeitado, erro). Os 4 pontos de aprovacao humana (AP-1 a AP-4) redirecionam para sub-telas especificas.

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| pipeline_id | text (readonly) | S | UUID valido | URL (param [id]) |
| tema | text (readonly) | S | - | API (pipeline) |
| formato | text (readonly) | S | - | API (pipeline) |
| etapa_atual | text (readonly) | S | Uma das 7 etapas | API (pipeline) |
| status_etapa[] | text (readonly) | S | pendente / em_execucao / aguardando_aprovacao / aprovado / rejeitado / erro | API (pipeline steps) |
| modo_funil | text (readonly) | N | - | API (pipeline) |
| pecas_funil[] | list (readonly) | N | Se modo funil ativo, lista de pecas com status individual | API (pipeline) |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Ver detalhes da etapa | clique na etapa do wizard | Expande detalhes inline (entrada, saida, tempo, status) |
| Aprovar briefing (AP-1) | clique em "Revisar Briefing" | Navega para `/pipeline/[id]/briefing` |
| Aprovar copy + hook (AP-2) | clique em "Revisar Copy" | Navega para `/pipeline/[id]/copy` |
| Aprovar prompt visual (AP-3) | clique em "Revisar Visual" | Navega para `/pipeline/[id]/visual` |
| Aprovar imagem (AP-4) | clique em "Revisar Imagem" | Navega para `/pipeline/[id]/imagem` |
| Ver resultado final | clique em "Ver Resultado" | Navega para `/pipeline/[id]/export` |
| Cancelar pipeline | clique em "Cancelar" | Confirma via modal, cancela pipeline no backend |
| Retomar pipeline | clique em "Retomar" (se etapa com erro) | Re-executa etapa que falhou |

#### Estados da Tela

- **Loading:** Carregando dados do pipeline. Skeleton do wizard com 7 etapas em cinza.
- **Vazio:** Pipeline nao encontrado (ID invalido). Mensagem "Pipeline nao encontrado" + link para Home.
- **Erro:** Etapa do pipeline com status "erro". A etapa com erro e destacada em vermelho. Botao "Retomar" aparece.
- **Sucesso:** Todas as etapas concluidas (status "aprovado"). Botao "Ver Resultado" destacado.
- **Aguardando aprovacao:** Etapa atual piscando/destacada com badge "Aguardando sua aprovacao". Botao de aprovacao proeminente.
- **Em execucao:** Etapa atual com spinner. Mensagem "Agente [nome] trabalhando..." com tempo estimado.

#### Fluxos de Navegacao

- Etapa AP-1 aguardando -> `/pipeline/[id]/briefing`
- Etapa AP-2 aguardando -> `/pipeline/[id]/copy`
- Etapa AP-3 aguardando -> `/pipeline/[id]/visual`
- Etapa AP-4 aguardando -> `/pipeline/[id]/imagem`
- Pipeline completo -> `/pipeline/[id]/export`
- Cancelar -> `/historico`
- Nav: qualquer item do menu global

---

### TELA: Aprovacao de Briefing (AP-1)

**Rota:** `/pipeline/[id]/briefing`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Apos o Strategist gerar o briefing, o usuario revisa, edita se necessario, e aprova para o pipeline continuar. Se modo funil ativo, mostra o plano de 5-7 pecas com distribuicao por etapa do funil (topo/meio/fundo).

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| briefing_completo | text (textarea, editavel) | S | Nao pode estar vazio | API (saida do Strategist) |
| tema_original | text (readonly) | S | - | API (pipeline) |
| formato_alvo | text (readonly) | S | - | API (pipeline) |
| funil_etapa | select (readonly) | N | topo / meio / fundo (se modo funil) | API (saida do Strategist) |
| pecas_funil[] | list (editavel) | N | Cada peca deve ter titulo + etapa_funil + formato | API (saida do Strategist) |
| tendencias_usadas | list (readonly) | N | Tendencias do trend_scanner que influenciaram o briefing | API (saida do Strategist) |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Editar briefing | clique no texto do briefing | Ativa modo edicao inline (textarea) |
| Editar peca do funil | clique na peca | Ativa edicao de titulo/etapa/formato da peca |
| Aprovar briefing | clique em "Aprovar e Continuar" (submit) | Envia briefing (editado ou nao) ao backend, pipeline avanca para Copywriter |
| Rejeitar briefing | clique em "Rejeitar e Regerar" | Re-executa Strategist com feedback do usuario |
| Voltar ao pipeline | clique em "Voltar" | Navega para `/pipeline/[id]` |

#### Estados da Tela

- **Loading:** Carregando saida do Strategist. Skeleton com bloco de texto.
- **Vazio:** Strategist ainda nao executou. Mensagem "Aguardando geracao do briefing...".
- **Erro:** Strategist falhou. Mensagem de erro + botao "Tentar novamente".
- **Sucesso:** Briefing aprovado. Redireciona para `/pipeline/[id]` com etapa 2 em execucao.

#### Fluxos de Navegacao

- Aprovar -> `/pipeline/[id]` (etapa Copywriter inicia automaticamente)
- Rejeitar -> permanece na tela, Strategist re-executa
- Voltar -> `/pipeline/[id]`

---

### TELA: Aprovacao de Copy + Hook (AP-2)

**Rota:** `/pipeline/[id]/copy`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Apos Copywriter + Hook Specialist executarem, o usuario ve a copy completa e escolhe entre 3 hooks (A/B/C). Pode editar a copy antes de aprovar. O tone_guide ja validou o vocabulario -- se houve correcoes, elas sao mostradas.

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| headline | text (editavel) | S | Nao pode estar vazio | API (saida do Copywriter) |
| narrativa | text (textarea, editavel) | S | Nao pode estar vazio | API (saida do Copywriter) |
| cta | text (editavel) | S | Nao pode estar vazio | API (saida do Copywriter) |
| sequencia_slides[] | list (editavel) | S | Pelo menos 1 slide/campo | API (saida do Copywriter) |
| hook_a | text (readonly) | S | - | API (saida do Hook Specialist) |
| hook_b | text (readonly) | S | - | API (saida do Hook Specialist) |
| hook_c | text (readonly) | S | - | API (saida do Hook Specialist) |
| hook_selecionado | select (radio) | S | Deve ser A, B ou C | formulario |
| correcoes_tone_guide | list (readonly) | N | Termos corrigidos pelo tone_guide | API (saida do tone_guide) |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Selecionar hook | clique no card A, B ou C | Marca hook como selecionado (radio) |
| Editar headline | clique no campo headline | Ativa edicao inline |
| Editar narrativa | clique na narrativa | Ativa edicao inline (textarea) |
| Editar CTA | clique no campo CTA | Ativa edicao inline |
| Editar slide/campo | clique no item da sequencia | Ativa edicao inline |
| Adicionar slide/campo | clique em "+ Adicionar" | Insere novo item na sequencia |
| Remover slide/campo | clique em "X" no item | Remove item da sequencia |
| Reordenar slides | drag-and-drop | Altera ordem dos slides |
| Aprovar copy + hook | clique em "Aprovar e Continuar" (submit) | Envia copy editada + hook escolhido, pipeline avanca para Art Director |
| Rejeitar copy | clique em "Rejeitar e Regerar" | Re-executa Copywriter + Hook Specialist |
| Voltar ao pipeline | clique em "Voltar" | Navega para `/pipeline/[id]` |

#### Estados da Tela

- **Loading:** Carregando saida do Copywriter/Hook Specialist. Skeleton com 3 cards de hook + bloco de copy.
- **Vazio:** Copywriter ainda nao executou. Mensagem "Aguardando geracao da copy...".
- **Erro:** Copywriter ou Hook Specialist falhou. Mensagem de erro + botao "Tentar novamente".
- **Sucesso:** Copy + hook aprovados. Redireciona para `/pipeline/[id]`.

#### Fluxos de Navegacao

- Aprovar -> `/pipeline/[id]` (etapa Art Director inicia automaticamente)
- Rejeitar -> permanece na tela, Copywriter re-executa
- Voltar -> `/pipeline/[id]`

---

### TELA: Aprovacao de Prompt Visual (AP-3)

**Rota:** `/pipeline/[id]/visual`
**Perfis com acesso:** Marketing, Admin
**Descricao:** O Art Director gerou prompts de imagem detalhados por slide/campo. O usuario revisa e edita os prompts antes de enviar para o Image Generator. O visual_memory mostra preferencias anteriores como referencia.

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| prompts_por_slide[] | list (editavel) | S | Cada slide deve ter prompt nao vazio | API (saida do Art Director) |
| prompt_slide.titulo | text (readonly) | S | - | API (saida do Art Director) |
| prompt_slide.prompt_imagem | text (textarea, editavel) | S | Minimo 50 caracteres | API (saida do Art Director) |
| prompt_slide.modelo_sugerido | text (readonly) | S | "pro" ou "flash" | API (saida do Art Director) |
| preferencias_visuais[] | list (readonly) | N | Estilos aprovados/rejeitados anteriormente | API (visual_memory) |
| brand_palette | object (readonly) | S | Cores, fonte, estilo | API (brand_palette.json) |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Editar prompt de slide | clique no textarea do prompt | Ativa edicao do prompt de imagem |
| Ver preferencias visuais | clique em "Ver historico visual" | Expande lista de estilos aprovados/rejeitados |
| Ver brand palette | clique em "Ver paleta" | Expande painel com cores e elementos obrigatorios |
| Aprovar prompts | clique em "Aprovar e Gerar Imagens" (submit) | Envia prompts ao backend, pipeline avanca para Image Generator |
| Rejeitar prompts | clique em "Rejeitar e Regerar" | Re-executa Art Director com feedback |
| Voltar ao pipeline | clique em "Voltar" | Navega para `/pipeline/[id]` |

#### Estados da Tela

- **Loading:** Carregando saida do Art Director. Skeleton com blocos de prompt por slide.
- **Vazio:** Art Director ainda nao executou. Mensagem "Aguardando geracao dos prompts visuais...".
- **Erro:** Art Director falhou. Mensagem de erro + botao "Tentar novamente".
- **Sucesso:** Prompts aprovados. Redireciona para `/pipeline/[id]` com etapa Image Generator em execucao.

#### Fluxos de Navegacao

- Aprovar -> `/pipeline/[id]` (etapa Image Generator + Brand Gate iniciam)
- Rejeitar -> permanece na tela, Art Director re-executa
- Voltar -> `/pipeline/[id]`

---

### TELA: Aprovacao de Imagem (AP-4)

**Rota:** `/pipeline/[id]/imagem`
**Perfis com acesso:** Marketing, Admin
**Descricao:** O Image Generator criou 3 variacoes de imagem por slide/campo. O Brand Gate ja validou conformidade visual e aplicou brand_overlay (foto + logo). O usuario escolhe a melhor variacao para cada slide. Se alguma imagem precisar de "revisao manual", ela e destacada.

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| slides[] | list (readonly) | S | - | API (pipeline) |
| slide.titulo | text (readonly) | S | - | API |
| slide.variacoes[] | list (imagens) | S | Exatamente 3 variacoes por slide | API (saida Image Generator + Brand Gate) |
| slide.variacao_selecionada | select (radio por imagem) | S | Deve selecionar 1 de 3 para cada slide | formulario |
| slide.brand_gate_status | text (readonly) | S | "valido" ou "revisao_manual" | API (saida Brand Gate) |
| slide.brand_gate_retries | number (readonly) | N | 0, 1 ou 2 | API |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Selecionar variacao | clique na imagem | Marca variacao como selecionada para aquele slide |
| Ampliar imagem | clique em icone de lupa ou duplo-clique | Abre imagem em modal fullscreen |
| Regerar variacao | clique em "Regerar" em uma variacao especifica | Re-executa Image Generator + Brand Gate para aquela variacao |
| Aprovar selecao | clique em "Aprovar e Finalizar" (submit) | Envia selecao, pipeline avanca para Content Critic |
| Rejeitar todas | clique em "Rejeitar Todas e Regerar" | Re-executa Image Generator para todos os slides |
| Voltar ao pipeline | clique em "Voltar" | Navega para `/pipeline/[id]` |

#### Estados da Tela

- **Loading:** Carregando imagens do Brand Gate. Skeleton com grid 3 colunas por slide.
- **Vazio:** Image Generator ainda nao executou. Mensagem "Aguardando geracao de imagens...".
- **Erro:** Brand Gate falhou apos 2 retries. Badge "revisao manual necessaria" no slide afetado. Usuario pode aprovar mesmo assim ou regerar.
- **Sucesso:** Todas as variacoes selecionadas. Redireciona para `/pipeline/[id]`.

#### Fluxos de Navegacao

- Aprovar -> `/pipeline/[id]` (Content Critic executa automaticamente) -> `/pipeline/[id]/export`
- Rejeitar -> permanece na tela, Image Generator re-executa
- Voltar -> `/pipeline/[id]`

---

### TELA: Preview e Export

**Rota:** `/pipeline/[id]/export`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Tela final do pipeline. Mostra o conteudo pronto com o score do Content Critic (6 dimensoes). Permite exportar PDF, download de PNGs individuais e salvar no Google Drive. Se score < 7, mostra recomendacao de ajustes.

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| titulo | text (readonly) | S | - | API (conteudo) |
| formato | text (readonly) | S | - | API (conteudo) |
| slides_finais[] | list (imagens) | S | - | API (conteudo + imagens selecionadas) |
| legenda_linkedin | text (readonly, copiavel) | N | - | API (conteudo) |
| score.clarity | number (readonly) | S | 0-10 | API (Content Critic) |
| score.impact | number (readonly) | S | 0-10 | API (Content Critic) |
| score.originality | number (readonly) | S | 0-10 | API (Content Critic) |
| score.scroll_stop | number (readonly) | S | 0-10 | API (Content Critic) |
| score.cta_strength | number (readonly) | S | 0-10 | API (Content Critic) |
| score.final_score | number (readonly) | S | 0-10 | API (Content Critic) |
| score.decision | text (readonly) | S | "approved" ou "needs_revision" | API (Content Critic) |
| score.best_variation | text (readonly) | N | Indica qual variacao e a melhor | API (Content Critic) |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Navegar entre slides | clique nos dots / setas / swipe | Mostra slide anterior/proximo no preview |
| Copiar legenda | clique em "Copiar" | Copia legenda LinkedIn para clipboard |
| Exportar PDF | clique em "Exportar PDF" | Gera PDF com jsPDF e faz download |
| Download PNG individual | clique em "Download" no slide | Faz download da imagem PNG do slide |
| Salvar no Drive | clique em "Salvar no Drive" | Cria subpasta no Drive, salva PDF + PNGs |
| Voltar ao pipeline | clique em "Voltar" | Navega para `/pipeline/[id]` |
| Criar novo conteudo | clique em "Novo Conteudo" | Navega para `/` |

#### Estados da Tela

- **Loading:** Content Critic avaliando. Skeleton dos scores + preview dos slides.
- **Vazio:** Content Critic ainda nao executou. Mensagem "Avaliando qualidade do conteudo...".
- **Erro:** Content Critic falhou. Preview dos slides disponivel sem scores. Mensagem "Score indisponivel, mas voce pode exportar."
- **Sucesso:** Score exibido. Se final_score >= 7: badge verde "Aprovado". Se < 7: badge amarelo "Recomenda ajustes" com sugestoes.
- **Drive salvo:** Banner verde "Salvo no Drive!" com link para abrir pasta.

#### Fluxos de Navegacao

- Exportar PDF -> download do arquivo (permanece na tela)
- Salvar no Drive -> permanece na tela com confirmacao
- Novo Conteudo -> `/`
- Voltar -> `/pipeline/[id]`

---

### TELA: Editor de Conteudo (legado)

**Rota:** `/carrossel`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Tela legada de preview e edicao do carrossel gerado pelo fluxo antigo (Claude direto -> Gemini). Sera mantida durante a transicao para o pipeline v3 e deprecada depois. Nenhuma alteracao necessaria na v3.

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| titulo | text (readonly) | S | - | store (carrosselAtual) |
| disciplina | text (readonly) | N | - | store (carrosselAtual) |
| tecnologia_principal | text (readonly) | N | - | store (carrosselAtual) |
| slides[] | list (editavel) | S | - | store (carrosselAtual) |
| slide.headline | text (editavel) | N | - | store |
| slide.subline | text (editavel) | N | - | store |
| slide.title | text (editavel) | N | - | store |
| slide.bullets[] | text[] (editavel) | N | - | store |
| slide.code | text (textarea, editavel) | N | - | store |
| slide.caption | text (editavel) | N | - | store |
| slide.etapa | text (editavel) | N | - | store |
| slide.illustration_description | text (textarea, editavel) | N | - | store |
| slide.imageBase64 | image (readonly) | N | - | store (gerado pelo Gemini) |
| design_system | select | N | Deve existir no Drive | API (drive/design-systems) |
| foto_criador | select (galeria) | N | - | store (fotos) |
| legenda_linkedin | text (readonly, copiavel) | N | - | store (carrosselAtual) |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Alternar modo edicao/preview | clique em "Editar" / "Visualizar" | Alterna entre modo edicao (formularios) e preview (imagens) |
| Editar campo do slide | change em qualquer campo | Atualiza store carrosselAtual |
| Adicionar bullet | clique em "+ Adicionar bullet" | Insere bullet vazio no slide |
| Remover bullet | clique em "X" no bullet | Remove bullet do slide |
| Gerar imagem (slide individual) | clique em "Gerar imagem" no slide | POST /api/gerar-imagem-slide, atualiza imageBase64 |
| Gerar todas as imagens | clique em "Imagens" | POST /api/gerar-imagem, gera todas |
| Navegar slides (preview) | clique nas setas / dots / swipe | Mostra slide anterior/proximo |
| Selecionar design system | clique no chip da marca | Carrega conteudo do design system do Drive |
| Selecionar foto | clique na miniatura | Atualiza foto do criador |
| Copiar legenda | clique em "Copiar" | Copia legenda LinkedIn para clipboard |
| Exportar PDF | clique em "PDF" | Gera PDF com jsPDF e faz download |
| Salvar no Drive | clique em "Drive" | POST /api/google-drive/carrossel |

#### Estados da Tela

- **Loading:** Gerando imagens. Botao "Imagens" mostra spinner + "Gerando...". Slide individual mostra spinner no card.
- **Vazio:** Nenhum carrossel no store. Mensagem "Nenhum carrossel gerado ainda" + link para Home.
- **Erro:** Falha na geracao ou salvamento. Banner vermelho com mensagem.
- **Sucesso:** Imagens geradas. Checklist lateral mostra marcacoes verdes. Drive salvo mostra link.

#### Fluxos de Navegacao

- Nenhum carrossel -> clicar "Criar carrossel" -> `/`
- Exportar PDF -> download (permanece na tela)
- Salvar no Drive -> permanece na tela com link
- Nav: qualquer item do menu global

---

### TELA: Historico

**Rota:** `/historico`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Lista todos os conteudos gerados com metadados. Na v3, precisa suportar multi-formato, status do pipeline e scores do Content Critic. Hoje so mostra carrosseis salvos no Drive.

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| filtro_texto | text | N | - | formulario |
| filtro_formato | select | N | Todos / Carrossel / Post Unico / Thumbnail YouTube | formulario |
| filtro_status | select | N | Todos / Completo / Em andamento / Erro / Cancelado | formulario |
| filtro_data_inicio | date | N | Data valida | formulario |
| filtro_data_fim | date | N | Data valida, >= data_inicio | formulario |
| itens_historico[] | list (readonly) | - | - | API (/api/historico) |
| item.id | number (readonly) | S | - | API |
| item.titulo | text (readonly) | S | - | API |
| item.formato | text (readonly) | S | - | API |
| item.status | text (readonly) | S | - | API |
| item.disciplina | text (readonly) | N | - | API |
| item.tecnologia_principal | text (readonly) | N | - | API |
| item.tipo_carrossel | text (readonly) | N | - | API |
| item.total_slides | number (readonly) | N | - | API |
| item.final_score | number (readonly) | N | 0-10 | API |
| item.google_drive_link | text (readonly) | N | URL valida | API |
| item.criado_em | text (readonly) | N | - | API |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Filtrar por texto | change no campo de filtro | Filtra lista em tempo real |
| Filtrar por formato | change no select formato | Filtra lista |
| Filtrar por status | change no select status | Filtra lista |
| Filtrar por data | change nos campos de data | Filtra lista |
| Abrir no Drive | clique em "Abrir no Drive" | Abre link em nova aba |
| Reabrir pipeline | clique em "Reabrir" | Navega para `/pipeline/[id]` |
| Remover item | clique em "remover" | DELETE no backend, remove da lista |
| Ver detalhes | clique no card do item | Navega para `/pipeline/[id]/export` (se pipeline v3) ou expande detalhes inline (legado) |

#### Estados da Tela

- **Loading:** Carregando historico do backend. Spinner centralizado.
- **Vazio (sem filtro):** Nenhum conteudo salvo. Mensagem "Nenhum conteudo salvo ainda." + "Salve conteudos no Google Drive para ve-los aqui."
- **Vazio (com filtro):** Filtro sem resultados. Mensagem "Nenhum resultado encontrado."
- **Erro:** Backend indisponivel. Mensagem "Backend indisponivel".
- **Sucesso:** Grid de cards com conteudos. Cada card mostra titulo, formato, score, data.

#### Fluxos de Navegacao

- Reabrir pipeline -> `/pipeline/[id]`
- Ver resultado -> `/pipeline/[id]/export`
- Abrir no Drive -> nova aba (link externo)
- Nav: qualquer item do menu global

---

### TELA: Agentes

**Rota:** `/agentes`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Visualizacao dos 6 agentes LLM e 6 skills deterministicas do pipeline. Hoje mostra 2 skills legadas (anti-bel-pesce e nano-banana). Na v3, precisa listar todos os 12 componentes com system prompts, descricoes e status de execucao no pipeline ativo.

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| agentes_llm[] | list (readonly) | S | 6 agentes | API (/api/agentes) |
| skills_deterministicas[] | list (readonly) | S | 6 skills | API (/api/agentes) |
| agente.slug | text (readonly) | S | - | API |
| agente.nome | text (readonly) | S | - | API |
| agente.descricao | text (readonly) | S | - | API |
| agente.tipo | text (readonly) | S | "llm" ou "skill" | API |
| agente.conteudo | text (readonly) | S | System prompt ou descricao da skill | API |
| agente_selecionado | text | N | Slug valido | formulario (clique) |
| pipeline_visual | object (readonly) | N | Sequencia do pipeline com 7 etapas | API |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Selecionar agente/skill | clique no card | Exibe system prompt / descricao detalhada no painel direito |
| Alternar entre LLM e Skills | clique na tab "Agentes LLM" / "Skills" | Filtra lista para mostrar so LLM ou so Skills |

#### Estados da Tela

- **Loading:** Carregando agentes. Skeleton na lista e no painel de detalhes.
- **Vazio:** Nenhum agente cadastrado (improvavel). Mensagem "Nenhum agente encontrado."
- **Erro:** Backend indisponivel. Banner vermelho com mensagem.
- **Sucesso:** Lista de 12 componentes no painel esquerdo, detalhes do selecionado no painel direito, pipeline visual na parte inferior.

#### Fluxos de Navegacao

- Nav: qualquer item do menu global

---

### TELA: Configuracoes

**Rota:** `/configuracoes`
**Perfis com acesso:** Admin
**Descricao:** Gerenciamento de chaves de API, brand palette, creator registry, platform rules, design systems e fotos do criador. Na v3, precisa adicionar secoes para brand_palette.json, creator_registry.json e platform_rules.json.

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| **Secao: API Keys** | | | | |
| claude_api_key | text (password) | N (se ja configurada) | Formato sk-ant-* | formulario |
| gemini_api_key | text (password) | N (se ja configurada) | Formato AI* | formulario |
| google_drive_credentials | text (textarea) | N (se ja configurada) | JSON valido de service account | formulario |
| google_drive_folder_id | text | N | ID de pasta do Drive | formulario ou selecao |
| **Secao: Pasta Google Drive** | | | | |
| pastas_drive[] | list (readonly) | N | - | API (/api/drive/pastas) |
| pasta_selecionada | text | N | ID da pasta | formulario / API |
| folder_id_manual | text | N | - | formulario |
| **Secao: Brand Palette (NOVA)** | | | | |
| fundo_principal | text (color picker) | S | Formato hex (#XXXXXX) | API (brand_palette.json) |
| destaque_primario | text (color picker) | S | Formato hex | API (brand_palette.json) |
| destaque_secundario | text (color picker) | S | Formato hex | API (brand_palette.json) |
| texto_principal | text (color picker) | S | Formato hex | API (brand_palette.json) |
| texto_secundario | text (color picker) | S | Formato hex | API (brand_palette.json) |
| fonte | text | S | Nome da fonte valido | API (brand_palette.json) |
| elementos_obrigatorios[] | text[] (chips) | S | Lista de strings | API (brand_palette.json) |
| estilo | text | S | - | API (brand_palette.json) |
| **Secao: Creator Registry (NOVA)** | | | | |
| criadores[] | list (editavel) | S | - | API (creator_registry.json) |
| criador.nome | text (editavel) | S | Nao pode estar vazio | formulario |
| criador.funcao | select | S | TECH_SOURCE / EXPLAINER / VIRAL_ENGINE / THOUGHT_LEADER / DINAMICAS | formulario |
| criador.plataforma | select | S | YouTube / Twitter / Blog / dev.to / HN | formulario |
| criador.url | text (editavel) | N | URL valida | formulario |
| criador.ativo | toggle | S | - | formulario |
| **Secao: Platform Rules (NOVA)** | | | | |
| plataformas[] | list (readonly) | S | - | API (platform_rules.json) |
| plataforma.nome | text (readonly) | S | - | API |
| plataforma.max_caracteres | number (editavel) | S | > 0 | API / formulario |
| plataforma.hashtags_max | number (editavel) | N | >= 0 | API / formulario |
| plataforma.specs | text (readonly) | N | Detalhes tecnicos | API |
| **Secao: Design Systems (existente)** | | | | |
| design_systems[] | list (readonly) | N | - | API (drive/design-systems) |
| ds_upload | file | N | .md ou .html | formulario |
| **Secao: Backend** | | | | |
| backend_url | text (url) | S | URL valida | store (config) |
| **Secao: Fotos (existente)** | | | | |
| fotos[] | list (readonly) | N | - | store (fotos) |
| foto_upload | file (multiple) | N | Imagem (image/*) | formulario |
| foto_ativa | select (galeria) | N | - | formulario |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Salvar API keys | submit | POST /api/config com chaves preenchidas |
| Listar pastas do Drive | clique em "Listar pastas" | GET /api/drive/pastas, exibe lista |
| Selecionar pasta | clique na pasta | POST /api/config com folder_id |
| Salvar brand palette | submit na secao | PUT /api/config/brand-palette |
| Adicionar criador | clique em "Adicionar criador" | Insere formulario de novo criador |
| Remover criador | clique em "Remover" no criador | Remove criador da lista |
| Salvar creator registry | submit na secao | PUT /api/config/creator-registry |
| Editar regra de plataforma | change nos campos da plataforma | Edita valor localmente |
| Salvar platform rules | submit na secao | PUT /api/config/platform-rules |
| Upload design system | clique em "Upload" | POST /api/drive/design-systems |
| Preview design system | clique em "Ver" | GET /api/drive/design-systems/[id], mostra inline |
| Deletar design system | clique em "Remover" | DELETE /api/drive/design-systems/[id] |
| Upload foto | clique em "Adicionar fotos" | Abre file picker, salva no store local |
| Selecionar foto ativa | clique na miniatura | Marca como foto ativa |
| Remover foto | clique em "x" na foto | Remove do store local |
| Salvar tudo | clique em "Salvar configuracoes" | Persiste todas as alteracoes |
| Resetar | clique em "Resetar" | Volta ao estado padrao |

#### Estados da Tela

- **Loading:** Carregando status das chaves e configs do backend. Spinner no topo.
- **Vazio:** Todas as chaves nao configuradas. Labels indicam "nao configurada" em vermelho.
- **Erro:** Falha ao salvar. Banner vermelho com mensagem.
- **Sucesso:** Salvo com sucesso. Banner verde "Configuracoes salvas com sucesso!".

#### Fluxos de Navegacao

- Nav: qualquer item do menu global

---

## Mapa de Navegacao Completo

```
[Home /]
   |
   +--(iniciar pipeline)--> [Pipeline /pipeline/[id]]
   |                             |
   |                             +--(AP-1)--> [Briefing /pipeline/[id]/briefing]
   |                             |                  |
   |                             |                  +--(aprovar)--> volta para Pipeline
   |                             |
   |                             +--(AP-2)--> [Copy /pipeline/[id]/copy]
   |                             |                  |
   |                             |                  +--(aprovar)--> volta para Pipeline
   |                             |
   |                             +--(AP-3)--> [Visual /pipeline/[id]/visual]
   |                             |                  |
   |                             |                  +--(aprovar)--> volta para Pipeline
   |                             |
   |                             +--(AP-4)--> [Imagem /pipeline/[id]/imagem]
   |                             |                  |
   |                             |                  +--(aprovar)--> volta para Pipeline
   |                             |
   |                             +--(completo)--> [Export /pipeline/[id]/export]
   |                                                   |
   |                                                   +--(novo)--> volta para Home
   |
   +--(nav)--> [Historico /historico]
   |                  |
   |                  +--(reabrir)--> [Pipeline /pipeline/[id]]
   |
   +--(nav)--> [Agentes /agentes]
   |
   +--(nav)--> [Config /configuracoes]
   |
   +--(legado)--> [Carrossel /carrossel]
```

---

## Dvidas Tecnicas de Tela

| ID | Dvida | Impacto |
|----|-------|---------|
| DT-001 | O pipeline deve usar polling, SSE ou WebSocket para atualizar status em tempo real na tela Pipeline? | Afeta UX de todas as telas de pipeline. Polling e mais simples mas menos responsivo. SSE e ideal para atualizacoes unidirecionais. |
| DT-002 | As sub-telas de aprovacao (AP-1 a AP-4) devem ser rotas separadas ou modais/drawers sobre a tela Pipeline? | Rotas separadas facilitam deep-linking e retomada. Modais sao mais fluidos mas perdem URL. Recomendacao: rotas separadas. |
| DT-003 | O modo funil gera 5-7 pecas. Cada peca passa pelo pipeline completo. A tela Pipeline deve mostrar 1 peca por vez ou todas em paralelo? | Se paralelo, o wizard fica complexo. Recomendacao: 1 peca por vez com navegacao lateral entre pecas. |
| DT-004 | A tela de aprovacao de imagem (AP-4) mostra 3 variacoes por slide. Em um carrossel de 10 slides, sao 30 imagens. Como organizar visualmente? | Grid por slide (accordion? tabs? scroll vertical?). Recomendacao: accordion por slide, 3 colunas por slide aberto. |
| DT-005 | O layout global vai migrar de header horizontal para sidebar? O PRD menciona sidebar mas o existente usa header. | Impacta todas as telas. Decisao do Designer (Agente 05). |
| DT-006 | A tela de Configuracoes esta ficando muito longa com as novas secoes (brand palette, creator registry, platform rules). Dividir em sub-rotas? | `/configuracoes/api-keys`, `/configuracoes/brand`, `/configuracoes/criadores`, etc. Ou usar tabs/accordion. |
| DT-007 | A tela legada `/carrossel` sera acessivel por quanto tempo apos a v3? Deve ter link no menu ou so via URL direta? | Manter no menu durante transicao. Remover quando pipeline v3 estiver estavel. |

---

## Glossario

| Termo | Definicao |
|-------|-----------|
| Pipeline | Sequencia de 7 etapas (6 agentes + 1 checkpoint) que transforma tema em conteudo visual |
| AP (Approval Point) | Ponto de aprovacao humana. Existem 4: AP-1 (briefing), AP-2 (copy+hook), AP-3 (prompt visual), AP-4 (imagem) |
| Brand Gate | Checkpoint deterministico que valida conformidade visual da marca |
| Wizard | Componente de UI que mostra progresso por etapas com indicadores visuais |
| Score | Avaliacao do Content Critic com 6 dimensoes numericas (0-10) |
| Funil | Modo onde 1 tema gera 5-7 pecas distribuidas por etapa do funil de marketing |
| Variacao | Uma das 3 opcoes geradas pelo Image Generator ou Hook Specialist |
| Store | Estado reativo do frontend (Svelte writable/derived store) |
| Design System | Arquivo .md ou .html que define identidade visual de uma marca |

---

*Documento gerado pelo Agente 02 (Analista de Tela) da esteira IT Valley.*
*Proximo: Agentes 03 (Arquiteto Backend), 04 (Arquiteto Frontend), 05 (Arquiteto Designer) -- em paralelo.*
