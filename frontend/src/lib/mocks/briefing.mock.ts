export const briefingMock = {
  pipeline_id: 'pip-001',
  briefing_completo: `## Briefing: RAG (Retrieval-Augmented Generation) com LangChain

### Contexto
LLMs como GPT e Claude sofrem de "alucinacao" — inventam informacoes que parecem verdadeiras mas nao sao. RAG resolve isso conectando o modelo a uma base de conhecimento real antes de responder.

### Angulo Editorial
Mostrar o problema (alucinacao) de forma visceral, depois revelar a arquitetura RAG como solucao elegante. Usar analogia: "e como dar um livro-texto para o aluno antes da prova, em vez de pedir que invente a resposta."

### Estrutura Sugerida (10 slides)
1. **Capa** — Hook com dado impactante sobre alucinacao
2. **O Problema** — Exemplos reais de alucinacao em producao
3. **Por que LLMs alucinam** — Explicacao tecnica acessivel
4. **O que e RAG** — Definicao com diagrama conceitual
5. **Arquitetura RAG** — Fluxo: Embed -> VectorDB -> Retrieve -> Augment -> Generate
6. **Codigo** — Implementacao minima com LangChain + ChromaDB
7. **Resultados** — Metricas antes/depois: faithfulness, relevance
8. **Quando NAO usar RAG** — Casos onde fine-tuning e melhor
9. **Stack recomendada** — LangChain + ChromaDB + FastAPI + Svelte
10. **CTA** — "Qual embedding model voce usa?"

### Tom de Voz
Tecnico mas acessivel. Sem jargoes desnecessarios. Direto ao ponto. Estilo IT Valley: pratico, com codigo real, sem enrolacao.

### Publico-Alvo
Desenvolvedores Python e engenheiros de ML que estao implementando LLMs em producao e enfrentam problemas de qualidade de resposta.

### Tendencias Detectadas
- Artigo no dev.to: "RAG is not dead" com 2.4k reactions (03/2026)
- Video do Fireship: "RAG in 100 seconds" com 890k views
- Hacker News: discussao sobre RAG vs fine-tuning com 340 comments`,

  tema_original: 'Como RAG resolve o problema de alucinacao em LLMs — arquitetura completa com LangChain e ChromaDB',
  formato_alvo: 'carrossel',
  funil_etapa: null,
  pecas_funil: [],
  tendencias_usadas: [
    'RAG is not dead — dev.to (2.4k reactions)',
    'Fireship: RAG in 100 seconds (890k views)',
    'HN: RAG vs fine-tuning (340 comments)'
  ]
};

export const briefingFunilMock = {
  pipeline_id: 'pip-funil-001',
  briefing_completo: 'Funil completo sobre RAG: da conscientizacao a implementacao pratica.',
  tema_original: 'RAG na pratica',
  formato_alvo: 'carrossel',
  funil_etapa: 'topo',
  pecas_funil: [
    { titulo: 'Por que seu chatbot inventa respostas?', etapa_funil: 'topo' as const, formato: 'carrossel' },
    { titulo: 'RAG explicado em 3 minutos', etapa_funil: 'topo' as const, formato: 'post_unico' },
    { titulo: 'Arquitetura RAG: passo a passo', etapa_funil: 'meio' as const, formato: 'carrossel' },
    { titulo: 'RAG vs Fine-tuning: quando usar cada um', etapa_funil: 'meio' as const, formato: 'thumbnail_youtube' },
    { titulo: 'Implementando RAG com LangChain + ChromaDB', etapa_funil: 'fundo' as const, formato: 'carrossel' },
    { titulo: 'RAG em producao: monitoramento e metricas', etapa_funil: 'fundo' as const, formato: 'post_unico' }
  ],
  tendencias_usadas: ['RAG is not dead — dev.to']
};
