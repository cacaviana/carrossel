export const copyMock = {
  pipeline_id: 'pip-001',
  headline: 'Seu chatbot inventa respostas? RAG resolve isso com 20 linhas de codigo.',
  narrativa: 'LLMs sao incriveis para gerar texto, mas tem um problema serio: alucinacao. Eles inventam dados, citam papers que nao existem e criam estatisticas falsas com total confianca. RAG (Retrieval-Augmented Generation) e a solucao mais adotada pela industria. Em vez de confiar apenas na memoria do modelo, RAG busca informacao real em uma base de dados vetorial antes de responder. Neste carrossel, vamos implementar RAG do zero com LangChain e ChromaDB.',
  cta: 'Qual embedding model voce usa nos seus projetos RAG? Comenta aqui.',
  sequencia_slides: [
    { titulo: 'Capa', conteudo: 'Seu chatbot inventa respostas?\nRAG resolve em 20 linhas.\nA arquitetura que a OpenAI usa.', tipo: 'cover', ordem: 0 },
    { titulo: 'O Problema', conteudo: '87% dos chatbots corporativos sofrem com alucinacao.\n- Inventam dados financeiros\n- Citam papers inexistentes\n- Criam estatisticas falsas', tipo: 'content', ordem: 1 },
    { titulo: 'Por que LLMs alucinam', conteudo: 'LLMs geram texto baseado em probabilidade, nao em verdade.\nEles nao "sabem" nada — apenas preveem o proximo token.\nSem acesso a dados reais, inventam com confianca.', tipo: 'content', ordem: 2 },
    { titulo: 'O que e RAG', conteudo: 'Retrieval-Augmented Generation:\n1. Recebe a pergunta do usuario\n2. Busca documentos relevantes\n3. Envia docs + pergunta para o LLM\n4. LLM responde baseado nos docs reais', tipo: 'content', ordem: 3 },
    { titulo: 'Arquitetura RAG', conteudo: 'Usuario -> Embedding -> VectorDB (ChromaDB)\n-> Top-K documentos -> Prompt Aumentado -> LLM -> Resposta fundamentada', tipo: 'diagram', ordem: 4 },
    { titulo: 'Codigo: RAG em 20 linhas', conteudo: 'from langchain.vectorstores import Chroma\nfrom langchain.embeddings import OpenAIEmbeddings\nfrom langchain.chains import RetrievalQA\nfrom langchain.llms import ChatAnthropic\n\ndb = Chroma.from_documents(docs, OpenAIEmbeddings())\nretriever = db.as_retriever(k=4)\nchain = RetrievalQA.from_chain_type(\n    llm=ChatAnthropic(model="claude-sonnet"),\n    retriever=retriever\n)\nresult = chain.invoke("Qual a politica de reembolso?")', tipo: 'code', ordem: 5 },
    { titulo: 'Resultados', conteudo: 'Antes do RAG:\n- Faithfulness: 43%\n- Relevance: 51%\n\nDepois do RAG:\n- Faithfulness: 94%\n- Relevance: 89%\n\nReducao de 91% nas alucinacoes.', tipo: 'comparison', ordem: 6 },
    { titulo: 'Quando NAO usar RAG', conteudo: '- Dados mudam a cada segundo (use API direta)\n- Base de conhecimento < 10 docs (nao precisa)\n- Tarefa criativa (fine-tuning melhor)\n- Budget muito apertado (embeddings custam)', tipo: 'content', ordem: 7 },
    { titulo: 'Stack Recomendada', conteudo: 'LangChain — orquestracao\nChromaDB — vector store local\nOpenAI Embeddings — text-embedding-3-small\nClaude Sonnet — LLM principal\nFastAPI — backend\nSvelteKit — frontend', tipo: 'content', ordem: 8 },
    { titulo: 'CTA', conteudo: 'Qual embedding model voce usa?\n\nDisciplina D7 da Pos IA & ML\n#RAG #LangChain #ITValleySchool', tipo: 'cta', ordem: 9 }
  ]
};

export const hooksMock = {
  pipeline_id: 'pip-001',
  hook_a: 'Seu chatbot inventou que a empresa tem 50 anos de mercado. Ela foi fundada em 2019. RAG teria evitado isso.',
  hook_b: '87% dos chatbots corporativos alucinam. O seu provavelmente tambem. A solucao cabe em 20 linhas de Python.',
  hook_c: 'A OpenAI, a Anthropic e o Google usam RAG internamente. Voce deveria usar tambem. Aqui esta o codigo.',
  hook_selecionado: null
};

export const correcoesToneGuideMock = [
  { original: 'sinergia entre modelos', corrigido: 'integracao entre modelos' },
  { original: 'solucao disruptiva', corrigido: 'solucao inovadora' }
];
