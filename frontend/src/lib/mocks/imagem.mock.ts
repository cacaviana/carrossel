// Gera SVG placeholder como base64 para simular imagens geradas
function gerarPlaceholderSvg(titulo: string, variacao: number, cor: string): string {
  const cores = ['#A78BFA', '#6D28D9', '#34D399'];
  const corAccent = cores[variacao - 1] || cor;
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="540" height="675" viewBox="0 0 540 675">
    <rect width="540" height="675" fill="#0A0A0F"/>
    <rect x="20" y="20" width="500" height="635" rx="16" fill="#12121A" stroke="${corAccent}" stroke-width="2" stroke-opacity="0.3"/>
    <circle cx="270" cy="280" r="80" fill="none" stroke="${corAccent}" stroke-width="2" stroke-opacity="0.5"/>
    <circle cx="270" cy="280" r="40" fill="${corAccent}" fill-opacity="0.15"/>
    <text x="270" y="290" text-anchor="middle" font-family="sans-serif" font-size="16" fill="${corAccent}">V${variacao}</text>
    <text x="270" y="420" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#9896A3">${titulo}</text>
    <text x="270" y="450" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#5A5A66">Imagem mockada — Content Factory v3</text>
    <rect x="200" y="580" width="140" height="32" rx="16" fill="${corAccent}" fill-opacity="0.1" stroke="${corAccent}" stroke-width="1" stroke-opacity="0.2"/>
    <text x="270" y="601" text-anchor="middle" font-family="sans-serif" font-size="11" fill="${corAccent}">IT Valley School</text>
  </svg>`;
  return `data:image/svg+xml;base64,${btoa(svg)}`;
}

export const imagemVariacoesMock = {
  pipeline_id: 'pip-001',
  slides: [
    {
      slide_index: 0,
      titulo: 'Capa',
      variacoes: [
        { variacao_id: 'v1-s0', url: '', base64: '' },
        { variacao_id: 'v2-s0', url: '', base64: '' },
        { variacao_id: 'v3-s0', url: '', base64: '' }
      ],
      variacao_selecionada: null,
      brand_gate_status: 'valido' as const,
      brand_gate_retries: 0
    },
    {
      slide_index: 1,
      titulo: 'O Problema',
      variacoes: [
        { variacao_id: 'v1-s1', url: '', base64: '' },
        { variacao_id: 'v2-s1', url: '', base64: '' },
        { variacao_id: 'v3-s1', url: '', base64: '' }
      ],
      variacao_selecionada: null,
      brand_gate_status: 'valido' as const,
      brand_gate_retries: 0
    },
    {
      slide_index: 2,
      titulo: 'Codigo RAG',
      variacoes: [
        { variacao_id: 'v1-s2', url: '', base64: '' },
        { variacao_id: 'v2-s2', url: '', base64: '' },
        { variacao_id: 'v3-s2', url: '', base64: '' }
      ],
      variacao_selecionada: null,
      brand_gate_status: 'valido' as const,
      brand_gate_retries: 1
    },
    {
      slide_index: 3,
      titulo: 'Resultados',
      variacoes: [
        { variacao_id: 'v1-s3', url: '', base64: '' },
        { variacao_id: 'v2-s3', url: '', base64: '' },
        { variacao_id: 'v3-s3', url: '', base64: '' }
      ],
      variacao_selecionada: null,
      brand_gate_status: 'revisao_manual' as const,
      brand_gate_retries: 2
    },
    {
      slide_index: 4,
      titulo: 'CTA',
      variacoes: [
        { variacao_id: 'v1-s4', url: '', base64: '' },
        { variacao_id: 'v2-s4', url: '', base64: '' },
        { variacao_id: 'v3-s4', url: '', base64: '' }
      ],
      variacao_selecionada: null,
      brand_gate_status: 'valido' as const,
      brand_gate_retries: 0
    }
  ]
};

// Preenche os base64 em runtime (evita JSON gigante no arquivo)
export function getImagemVariacoesComPlaceholders() {
  const data = JSON.parse(JSON.stringify(imagemVariacoesMock));
  for (const slide of data.slides) {
    slide.variacoes = slide.variacoes.map((v: any, i: number) => ({
      ...v,
      base64: gerarPlaceholderSvg(slide.titulo, i + 1, '#A78BFA')
    }));
  }
  return data;
}
