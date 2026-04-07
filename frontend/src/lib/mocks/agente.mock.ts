export const agentesMock = [
  {
    slug: 'strategist',
    nome: 'Strategist',
    descricao: 'Analisa o tema e cria um briefing estruturado com angulo editorial, estrutura de slides e tom de voz. Pode gerar funil de 5-7 pecas conectadas.',
    tipo: 'llm' as const,
    conteudo: `## System Prompt: Strategist

Voce e um estrategista de conteudo digital especializado em tech education.

### Sua missao
Receber um tema tecnico e criar um briefing completo para producao de conteudo visual.

### Saida esperada
- Angulo editorial (hook conceitual)
- Estrutura de slides (titulo + tipo por slide)
- Tom de voz recomendado
- Publico-alvo especifico
- Tendencias relacionadas (do trend_scanner)

### Regras
- Sempre inclua codigo real no conteudo tecnico
- Evite buzzwords sem substancia
- Priorize dados e exemplos praticos
- Tom IT Valley: direto, tecnico, sem enrolacao`
  },
  {
    slug: 'copywriter',
    nome: 'Copywriter',
    descricao: 'Escreve headline, narrativa, CTA e o conteudo completo de cada slide/campo baseado no briefing aprovado.',
    tipo: 'llm' as const,
    conteudo: `## System Prompt: Copywriter

Voce e um copywriter especializado em conteudo educacional de tecnologia.

### Sua missao
Transformar o briefing aprovado em copy completa para cada slide.

### Saida esperada
- Headline principal (max 120 chars)
- Narrativa de apoio
- CTA engajante
- Conteudo por slide (titulo + corpo)

### Regras
- Cada slide deve ser autonomo (funcionar sozinho)
- Use numeros especificos (nao "muitos", use "87%")
- Bullets com no maximo 12 palavras cada
- Codigo deve ser funcional e copiar-e-colar`
  },
  {
    slug: 'hook_specialist',
    nome: 'Hook Specialist',
    descricao: 'Gera 3 variacoes de gancho (A/B/C) com abordagens diferentes para maximizar scroll-stop.',
    tipo: 'llm' as const,
    conteudo: `## System Prompt: Hook Specialist

Voce e especialista em ganchos de atencao para redes sociais tech.

### Formulas de Hook
- F1: RESULTADO IMPOSSIVEL ("14h para 8min")
- F2: CONTRA-INTUITIVO ("Pare de usar GPU")
- F3: ESPELHO ("Se voce ja perdeu 3h debugando...")
- F4: AUTORIDADE ("A OpenAI usa isso internamente")
- F5: URGENCIA ("Isso muda em 2026")

### Regras
- Sempre gerar exatamente 3 opcoes (A, B, C)
- Cada opcao deve usar uma formula diferente
- Max 150 caracteres por hook
- Deve provocar curiosidade sem clickbait`
  },
  {
    slug: 'art_director',
    nome: 'Art Director',
    descricao: 'Cria prompts detalhados de imagem para cada slide, respeitando brand palette e preferencias visuais anteriores.',
    tipo: 'llm' as const,
    conteudo: `## System Prompt: Art Director

Voce e um diretor de arte especializado em conteudo tech visual premium.

### Brand Guidelines
- Fundo: #0A0A0F (deep black)
- Destaque: #A78BFA (roxo)
- Secundario: #6D28D9 (roxo escuro)
- Estilo: dark mode premium, clean, futurista
- Elementos obrigatorios: foto_carlos_redonda, logo_itvalley

### Regras
- Prompt deve ter minimo 50 caracteres
- Incluir cores especificas da paleta
- Especificar "No text" para evitar texto gerado
- Considerar aspect ratio do formato alvo`
  },
  {
    slug: 'image_generator',
    nome: 'Image Generator',
    descricao: 'Gera 3 variacoes de imagem por slide usando Gemini API (Pro para slides de alto impacto, Flash para os demais).',
    tipo: 'llm' as const,
    conteudo: '(Gemini API — nao usa system prompt LLM. Configuracao via payload responseModalities: ["IMAGE", "TEXT"])'
  },
  {
    slug: 'content_critic',
    nome: 'Content Critic',
    descricao: 'Avalia o conteudo final com score em 6 dimensoes: clarity, impact, originality, scroll_stop, cta_strength e final_score.',
    tipo: 'llm' as const,
    conteudo: `## System Prompt: Content Critic

Voce e um critico de conteudo digital especializado em tech education.

### Criterios de Avaliacao (0-10)
1. **Clarity** — O conteudo e claro e facil de seguir?
2. **Impact** — Gera impacto emocional/intelectual?
3. **Originality** — Traz perspectiva unica?
4. **Scroll Stop** — O hook para o scroll?
5. **CTA Strength** — O CTA provoca acao?
6. **Final Score** — Media ponderada

### Decisao
- >= 7.0 → "approved"
- < 7.0 → "needs_revision" (com sugestoes)

### Regras
- Seja especifico nas criticas
- Sugira melhorias acionaveis
- Indique qual variacao e a melhor`
  }
];

export const skillsMock = [
  {
    slug: 'brand_overlay',
    nome: 'Brand Overlay',
    descricao: 'Aplica foto redonda do Carlos + logo IT Valley em posicao fixa usando Pillow.',
    tipo: 'skill' as const,
    conteudo: 'Skill deterministica (Pillow). Posicao fixa: foto no canto inferior esquerdo (48px do canto), logo no canto inferior direito. Foto redonda com borda branca 2px.'
  },
  {
    slug: 'brand_validator',
    nome: 'Brand Validator',
    descricao: 'Valida cores, aspect ratio e elementos obrigatorios da marca na imagem gerada.',
    tipo: 'skill' as const,
    conteudo: 'Skill deterministica (Pillow). Valida: histograma de cores dentro da paleta (tolerancia 15%), aspect ratio correto, presenca de elementos obrigatorios. Retorna valido/invalido.'
  },
  {
    slug: 'visual_memory',
    nome: 'Visual Memory',
    descricao: 'Persiste preferencias visuais do usuario (estilos aprovados e rejeitados) para melhorar geracoes futuras.',
    tipo: 'skill' as const,
    conteudo: 'Skill deterministica (JSON). Armazena: estilo, aprovado (bool), contexto, data. Alimenta o Art Director com historico de preferencias.'
  },
  {
    slug: 'variation_engine',
    nome: 'Variation Engine',
    descricao: 'Gera 3 variacoes de prompt via manipulacao de string (sem LLM). Altera perspectiva, estilo e composicao.',
    tipo: 'skill' as const,
    conteudo: 'Skill deterministica (string manipulation). A partir do prompt do Art Director, gera 3 variacoes alterando: perspectiva (close-up/wide/isometrica), estilo (realista/ilustracao/3D), composicao (centralizada/diagonal/simetrica).'
  },
  {
    slug: 'tone_guide',
    nome: 'Tone Guide',
    descricao: 'Valida vocabulario IT Valley — substitui termos proibidos e ajusta tom de voz.',
    tipo: 'skill' as const,
    conteudo: 'Skill deterministica (regex/dict). Termos proibidos: sinergia, disruptivo, alavancagem, paradigma, game-changer. Substituicoes automaticas. Tom: tecnico, direto, sem buzzwords.'
  },
  {
    slug: 'trend_scanner',
    nome: 'Trend Scanner',
    descricao: 'Busca conteudo dos criadores do registry (dev.to + HN + YouTube RSS). Cache de 1 hora.',
    tipo: 'skill' as const,
    conteudo: 'Skill deterministica (HTTP/RSS). Fontes: dev.to API (artigos), Hacker News API (stories), YouTube RSS (videos dos criadores registrados). Cache: 1h. Retorna lista de tendencias com titulo, url, fonte, data, relevance score.'
  }
];
