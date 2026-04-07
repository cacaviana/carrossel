export const scoreMock = {
  pipeline_id: 'pip-001',
  clarity: 8.5,
  impact: 9.0,
  originality: 7.8,
  scroll_stop: 8.7,
  cta_strength: 7.5,
  final_score: 8.3,
  decision: 'approved' as const,
  best_variation: 'Variacao B apresentou melhor composicao visual e maior contraste nos elementos de destaque.'
};

export const scoreBaixoMock = {
  pipeline_id: 'pip-004',
  clarity: 6.2,
  impact: 5.8,
  originality: 7.0,
  scroll_stop: 5.5,
  cta_strength: 4.8,
  final_score: 5.9,
  decision: 'needs_revision' as const,
  best_variation: 'Nenhuma variacao atingiu o limiar minimo de qualidade. Recomenda-se ajustar o contraste e reforcar o CTA.'
};

export const legendaLinkedinMock = `Seu chatbot inventa respostas? RAG resolve isso com 20 linhas de codigo.

87% dos chatbots corporativos sofrem com alucinacao — inventam dados, citam papers inexistentes e criam estatisticas falsas com total confianca.

RAG (Retrieval-Augmented Generation) e a solucao mais adotada pela industria:
1. Recebe a pergunta
2. Busca documentos relevantes no vector store
3. Envia docs + pergunta para o LLM
4. Resposta fundamentada em dados reais

Resultado: reducao de 91% nas alucinacoes.

Qual embedding model voce usa nos seus projetos RAG?

#RAG #LangChain #ChromaDB #IA #MachineLearning #ITValleySchool

---
Carlos Viana | IT Valley School
Pos-graduacao em IA & Machine Learning`;
