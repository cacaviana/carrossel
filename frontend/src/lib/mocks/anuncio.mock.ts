// src/lib/mocks/anuncio.mock.ts
//
// Pos-pivot (2026-04-23): 5 anuncios em estados relevantes.
// Formato unico 1080x1350 (mesmo post_unico) + copy de venda (headline / descricao / cta).
// Imagens usam picsum.photos?random=N pra thumbnails realistas.
//
// Estados cobertos:
// - anu-001: CONCLUIDO, com Drive salvo
// - anu-002: CONCLUIDO sem Drive ainda
// - anu-003: EM ANDAMENTO (pipeline rodando)
// - anu-004: ERRO (pipeline falhou, sem imagem)
// - anu-005: RASCUNHO (nem iniciou pipeline ainda)

const TENANT = 'tenant-itvalley';
const CRIADOR = 'Carlos Viana';

function imgUrl(seed: number): string {
  // picsum.photos com seed estavel — 1080x1350 (retrato).
  return `https://picsum.photos/seed/anuncio-${seed}/1080/1350`;
}

// Estado local mutavel (permite simular criar / editar / regerar / excluir em memoria)
export let anunciosMock: Record<string, any>[] = [
  // anu-001: CONCLUIDO com Drive
  {
    id: 'anu-001',
    tenant_id: TENANT,
    titulo: 'Matriculas IT Valley Maio 2026',
    copy: {
      headline: 'Aprenda IA em 90 dias com mentoria',
      descricao: 'Turma IT Valley School abre em maio com bolsas ate 50% para iniciantes. Vagas limitadas, garanta a sua.',
      cta: 'Matricule-se agora'
    },
    image_url: imgUrl(1),
    status: 'concluido',
    etapa_funil: 'fundo',
    pipeline_id: 'pipe-anu-001',
    pipeline_funil_id: 'funnel-001',
    drive_folder_link: 'https://drive.google.com/drive/folders/mock-folder-anu-001',
    criado_por: CRIADOR,
    created_at: '2026-04-20T14:00:00Z',
    updated_at: '2026-04-20T14:35:00Z',
    deleted_at: ''
  },
  // anu-002: CONCLUIDO sem Drive
  {
    id: 'anu-002',
    tenant_id: TENANT,
    titulo: 'Workshop RAG + Agentes LangChain',
    copy: {
      headline: 'Construa agentes de IA em 2h',
      descricao: 'Workshop ao vivo: crie aplicacoes RAG com LangChain do zero. 500 vagas gratuitas, sabado 10h.',
      cta: 'Inscreva-se gratis'
    },
    image_url: imgUrl(2),
    status: 'concluido',
    etapa_funil: 'topo',
    pipeline_id: 'pipe-anu-002',
    pipeline_funil_id: '',
    drive_folder_link: '',
    criado_por: CRIADOR,
    created_at: '2026-04-21T11:00:00Z',
    updated_at: '2026-04-21T11:42:00Z',
    deleted_at: ''
  },
  // anu-003: EM ANDAMENTO
  {
    id: 'anu-003',
    tenant_id: TENANT,
    titulo: 'Formacao Deep Learning - Turma Junho',
    copy: {
      headline: 'Deep Learning do zero ao projeto',
      descricao: 'Formacao completa em Deep Learning com PyTorch. Projeto real no final, certificado IT Valley.',
      cta: 'Garanta sua vaga'
    },
    image_url: '',
    status: 'em_andamento',
    etapa_funil: 'meio',
    pipeline_id: 'pipe-anu-003',
    pipeline_funil_id: 'funnel-001',
    drive_folder_link: '',
    criado_por: CRIADOR,
    created_at: '2026-04-23T08:00:00Z',
    updated_at: '2026-04-23T08:15:00Z',
    deleted_at: ''
  },
  // anu-004: ERRO
  {
    id: 'anu-004',
    tenant_id: TENANT,
    titulo: 'Bolsas Parciais MLOps',
    copy: {
      headline: 'MLOps com 50% de bolsa',
      descricao: 'Vagas limitadas para a formacao MLOps com 50% de desconto ate 25/04. Unica turma do ano.',
      cta: 'Saiba mais'
    },
    image_url: '',
    status: 'erro',
    etapa_funil: 'avulso',
    pipeline_id: 'pipe-anu-004',
    pipeline_funil_id: '',
    drive_folder_link: '',
    criado_por: CRIADOR,
    created_at: '2026-04-19T10:00:00Z',
    updated_at: '2026-04-19T10:08:00Z',
    deleted_at: ''
  },
  // anu-005: RASCUNHO
  {
    id: 'anu-005',
    tenant_id: TENANT,
    titulo: 'Webinar: Transicao de Carreira para IA',
    copy: {
      headline: 'Mude para IA em 2026',
      descricao: 'Webinar gratuito: como mudar de carreira para IA sem precisar comecar do zero. Ao vivo, 2h.',
      cta: 'Reserve seu lugar'
    },
    image_url: '',
    status: 'rascunho',
    etapa_funil: 'topo',
    pipeline_id: '',
    pipeline_funil_id: '',
    drive_folder_link: '',
    criado_por: CRIADOR,
    created_at: '2026-04-22T16:00:00Z',
    updated_at: '2026-04-22T16:00:00Z',
    deleted_at: ''
  }
];

// ==============================
// Helpers usados pelo Repository
// ==============================

export function buscarAnuncioMockPorId(id: string): Record<string, any> | undefined {
  return anunciosMock.find(a => a.id === id);
}

export function filtrarAnunciosMock(filtro: Record<string, any>): Record<string, any>[] {
  let lista = [...anunciosMock];

  // incluir_excluidos: por default, oculta deleted_at preenchidos
  if (!filtro.incluir_excluidos) {
    lista = lista.filter(a => !a.deleted_at);
  }

  // busca: titulo + headline + cta
  const busca = (filtro.busca ?? '').toString().trim().toLowerCase();
  if (busca) {
    lista = lista.filter(a =>
      (a.titulo ?? '').toLowerCase().includes(busca)
      || (a.copy?.headline ?? '').toLowerCase().includes(busca)
      || (a.copy?.cta ?? '').toLowerCase().includes(busca)
    );
  }

  // status
  if (filtro.status && filtro.status !== 'todos') {
    lista = lista.filter(a => a.status === filtro.status);
  }

  // etapa_funil
  if (filtro.etapa_funil && filtro.etapa_funil !== 'todas') {
    lista = lista.filter(a => a.etapa_funil === filtro.etapa_funil);
  }

  // datas
  if (filtro.data_inicio) {
    lista = lista.filter(a => (a.created_at ?? '') >= filtro.data_inicio);
  }
  if (filtro.data_fim) {
    const limite = filtro.data_fim + 'T23:59:59Z';
    lista = lista.filter(a => (a.created_at ?? '') <= limite);
  }

  // ordena desc por created_at
  lista.sort((a, b) => (b.created_at ?? '').localeCompare(a.created_at ?? ''));
  return lista;
}

export function listarNaoExcluidosMock(): Record<string, any>[] {
  return anunciosMock.filter(a => !a.deleted_at);
}

// Mutacoes em memoria para simular backend
export function criarAnuncioMock(payload: Record<string, any>): Record<string, any> {
  const seed = Date.now() % 1000;
  const id = `anu-${String(anunciosMock.length + 1).padStart(3, '0')}-${Date.now().toString(36)}`;
  const novo = {
    id,
    tenant_id: TENANT,
    titulo: payload.titulo ?? 'Novo anuncio',
    copy: {
      headline: 'Headline gerada pelo Copywriter',
      descricao: 'Descricao persuasiva gerada pelo Copywriter. Sera substituida quando backend concluir.',
      cta: payload.cta ?? 'Saiba mais'
    },
    image_url: '',
    status: 'em_andamento',
    etapa_funil: payload.etapa_funil ?? 'avulso',
    pipeline_id: `pipe-${id}`,
    pipeline_funil_id: payload.pipeline_funil_id ?? '',
    drive_folder_link: '',
    criado_por: CRIADOR,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    deleted_at: ''
  };
  anunciosMock = [novo, ...anunciosMock];
  agendarConclusaoMock(id, seed);
  return novo;
}

// Agenda "conclusao" assincrona dos anuncios recem-criados
function agendarConclusaoMock(id: string, seed: number) {
  if (typeof window === 'undefined') return;
  setTimeout(() => {
    const idx = anunciosMock.findIndex(a => a.id === id);
    if (idx < 0) return;
    // 80% conclusao, 20% erro (pra mostrar ambos os fluxos)
    const alvo = Math.random() < 0.8 ? 'concluido' : 'erro';
    if (alvo === 'concluido') {
      anunciosMock[idx] = {
        ...anunciosMock[idx],
        status: 'concluido',
        image_url: imgUrl(seed),
        updated_at: new Date().toISOString()
      };
    } else {
      anunciosMock[idx] = {
        ...anunciosMock[idx],
        status: 'erro',
        image_url: '',
        updated_at: new Date().toISOString()
      };
    }
  }, 3500);
}

export function editarCopyMock(payload: Record<string, any>): Record<string, any> | undefined {
  const idx = anunciosMock.findIndex(a => a.id === payload.id);
  if (idx < 0) return undefined;
  anunciosMock[idx] = {
    ...anunciosMock[idx],
    titulo: payload.titulo ?? anunciosMock[idx].titulo,
    copy: {
      headline: payload.headline ?? anunciosMock[idx].copy?.headline ?? '',
      descricao: payload.descricao ?? anunciosMock[idx].copy?.descricao ?? '',
      cta: payload.cta ?? anunciosMock[idx].copy?.cta ?? ''
    },
    etapa_funil: payload.etapa_funil ?? anunciosMock[idx].etapa_funil,
    updated_at: new Date().toISOString()
  };
  return anunciosMock[idx];
}

export function excluirAnuncioMock(id: string): boolean {
  const idx = anunciosMock.findIndex(a => a.id === id);
  if (idx < 0) return false;
  anunciosMock[idx] = {
    ...anunciosMock[idx],
    deleted_at: new Date().toISOString(),
    status: 'cancelado'
  };
  return true;
}

// Regeneracao da imagem inteira (pos-pivot: sem mais dimensoes separadas)
export function regerarImagemMock(anuncioId: string): void {
  const idx = anunciosMock.findIndex(a => a.id === anuncioId);
  if (idx < 0) return;

  // Marca como em_andamento + limpa imagem
  anunciosMock[idx] = {
    ...anunciosMock[idx],
    status: 'em_andamento',
    image_url: '',
    updated_at: new Date().toISOString()
  };

  // Agenda conclusao da regeneracao
  if (typeof window === 'undefined') return;
  const seed = (Date.now() % 1000) + 500;
  setTimeout(() => {
    const idx2 = anunciosMock.findIndex(a => a.id === anuncioId);
    if (idx2 < 0) return;
    anunciosMock[idx2] = {
      ...anunciosMock[idx2],
      status: 'concluido',
      image_url: imgUrl(seed),
      updated_at: new Date().toISOString()
    };
  }, 2200);
}

export function salvarDriveMock(id: string): string | undefined {
  const idx = anunciosMock.findIndex(a => a.id === id);
  if (idx < 0) return undefined;
  const link = `https://drive.google.com/drive/folders/mock-folder-${id}-${Date.now().toString(36)}`;
  anunciosMock[idx] = {
    ...anunciosMock[idx],
    drive_folder_link: link,
    updated_at: new Date().toISOString()
  };
  return link;
}
