export const promptVisualMock = {
  pipeline_id: 'pip-001',
  prompts: [
    {
      slide_index: 0,
      titulo: 'Capa',
      prompt_imagem: 'Dark premium tech slide background. Abstract neural network visualization with glowing purple nodes (#A78BFA) connected by thin light lines against deep black (#0A0A0F) background. Central holographic brain shape with data streams flowing into it. Subtle grid pattern in the background. Style: futuristic, clean, minimal. No text. 1080x1350 portrait.',
      modelo_sugerido: 'pro' as const
    },
    {
      slide_index: 1,
      titulo: 'O Problema',
      prompt_imagem: 'Dark premium tech illustration showing a broken chatbot interface with red warning signals. Glitchy holographic text bubbles with wrong information highlighted in red (#F87171). Background deep black (#0A0A0F) with subtle purple (#A78BFA) accent lighting. Style: dark mode premium, tech illustration. No text. 1080x1350.',
      modelo_sugerido: 'flash' as const
    },
    {
      slide_index: 2,
      titulo: 'Por que LLMs alucinam',
      prompt_imagem: 'Dark premium abstract visualization of probability distributions as floating 3D graphs with purple (#A78BFA) glowing edges. Dice and random number generators in the background suggest randomness. Deep black (#0A0A0F) background. Clean and minimal style. No text. 1080x1350.',
      modelo_sugerido: 'flash' as const
    },
    {
      slide_index: 3,
      titulo: 'O que e RAG',
      prompt_imagem: 'Dark premium tech diagram showing a pipeline flow: document icon -> embedding arrow -> database cylinder -> search magnifying glass -> brain/AI icon -> response bubble. All elements in purple (#A78BFA) and white against deep black (#0A0A0F). Clean vector style with subtle glow effects. No text. 1080x1350.',
      modelo_sugerido: 'flash' as const
    },
    {
      slide_index: 4,
      titulo: 'Arquitetura RAG',
      prompt_imagem: 'Dark premium technical architecture diagram. Horizontal flow showing: User query box -> Embedding processor -> Vector Database (ChromaDB cylinder shape) -> Retrieved Documents stack -> Augmented Prompt -> LLM brain -> Generated Response. All in purple (#A78BFA) neon glow style on black (#0A0A0F). Arrows connecting each step. No text. 1080x1350.',
      modelo_sugerido: 'flash' as const
    },
    {
      slide_index: 5,
      titulo: 'Codigo',
      prompt_imagem: 'Dark premium code editor screenshot aesthetic. Floating code blocks with syntax highlighting in purple (#A78BFA), green (#34D399), and white on deep black (#0A0A0F) background. Python code symbols and brackets artistically arranged. Terminal window frame with minimal chrome. Holographic effect on key lines. No actual readable text. 1080x1350.',
      modelo_sugerido: 'pro' as const
    },
    {
      slide_index: 6,
      titulo: 'Resultados',
      prompt_imagem: 'Dark premium data visualization. Split comparison: left side shows declining red (#F87171) metrics bars, right side shows ascending green (#34D399) metrics bars. Central dividing line in purple (#A78BFA). Background deep black (#0A0A0F) with subtle grid. Clean infographic style. No text. 1080x1350.',
      modelo_sugerido: 'flash' as const
    },
    {
      slide_index: 7,
      titulo: 'Quando NAO usar',
      prompt_imagem: 'Dark premium warning/caution illustration. Red (#F87171) crossed-out icons representing wrong use cases, contrasted with green (#34D399) checkmarks for right use cases. Amber (#FBBF24) warning triangle in center. Deep black (#0A0A0F) background with subtle purple (#A78BFA) accents. No text. 1080x1350.',
      modelo_sugerido: 'flash' as const
    },
    {
      slide_index: 8,
      titulo: 'Stack Recomendada',
      prompt_imagem: 'Dark premium tech stack visualization. Floating 3D icons representing: Python snake, database cylinder, brain/AI, server rack, web browser. All connected by glowing purple (#A78BFA) lines forming a constellation pattern. Deep black (#0A0A0F) background. Futuristic holographic style. No text. 1080x1350.',
      modelo_sugerido: 'flash' as const
    },
    {
      slide_index: 9,
      titulo: 'CTA',
      prompt_imagem: 'Dark premium call-to-action slide background. Central glowing purple (#A78BFA) conversation bubble icon with question mark. Radiating light rays in purple gradient from center. Deep black (#0A0A0F) background. Particles and sparkles around the bubble. Inviting, engaging feel. No text. 1080x1350.',
      modelo_sugerido: 'pro' as const
    }
  ]
};

export const preferenciasVisuaisMock = [
  { estilo: 'Neon glow em elementos tecnicos', aprovado: true, contexto: 'Carrossel sobre Docker' },
  { estilo: 'Gradiente roxo para destaque', aprovado: true, contexto: 'Post sobre MLOps' },
  { estilo: 'Ilustracao cartoon', aprovado: false, contexto: 'Carrossel sobre Python — rejeitado por parecer infantil' },
  { estilo: 'Foto stock de pessoas', aprovado: false, contexto: 'Post sobre IA — rejeitado por ser generico' }
];

export const brandPaletteMock = {
  cores: {
    fundo_principal: '#0A0A0F',
    destaque_primario: '#A78BFA',
    destaque_secundario: '#6D28D9',
    texto_principal: '#FFFFFF',
    texto_secundario: '#94A3B8'
  },
  fonte: 'Outfit',
  elementos_obrigatorios: ['foto_carlos_redonda', 'logo_itvalley'],
  estilo: 'dark_mode_premium'
};
