import { test, expect } from '@playwright/test';

const API_BASE = 'http://localhost:8000/api';

/**
 * Testes de API — Prompt Layers (backend)
 *
 * Estes testes usam request context do Playwright para chamar
 * a API de prompt layers diretamente, sem precisar de UI.
 * Requerem que o backend esteja rodando em localhost:8000.
 */
test.describe('Prompt Layers — API /preview', () => {
  test.beforeEach(async ({ request }) => {
    // Verifica se backend esta up
    try {
      const health = await request.get('http://localhost:8000/health');
      test.skip(!health.ok(), 'Backend nao esta rodando em localhost:8000');
    } catch {
      test.skip(true, 'Backend nao esta rodando em localhost:8000');
    }
  });

  test('preview tipo=imagem retorna 200 com 4 camadas e total_caracteres > 0', async ({ request }) => {
    const response = await request.post(`${API_BASE}/prompt-layers/preview`, {
      data: {
        tipo: 'imagem',
        brand_slug: 'itvalley',
        formato: 'carrossel',
        slide_type: 'content',
        position: 1,
        total: 7,
      },
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body.camadas).toBeDefined();
    expect(body.camadas.length).toBe(4);
    expect(body.total_caracteres).toBeGreaterThan(0);
    expect(body.prompt_final).toBeTruthy();
  });

  test('preview tipo=texto retorna 200 e contem hooks_padrao na marca', async ({ request }) => {
    const response = await request.post(`${API_BASE}/prompt-layers/preview`, {
      data: {
        tipo: 'texto',
        brand_slug: 'itvalley',
        formato: 'carrossel',
        slide_type: 'content',
        position: 1,
        total: 7,
      },
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body.camadas).toBeDefined();
    expect(body.total_caracteres).toBeGreaterThan(0);
    // Camada marca deve conter hooks_padrao no conteudo
    const camadaMarca = body.camadas.find((c: any) => c.nome.toLowerCase().includes('marca'));
    expect(camadaMarca).toBeTruthy();
    expect(camadaMarca.conteudo).toContain('hooks_padrao');
  });

  test('preview com formato post_unico retorna 200', async ({ request }) => {
    const response = await request.post(`${API_BASE}/prompt-layers/preview`, {
      data: {
        tipo: 'imagem',
        brand_slug: 'itvalley',
        formato: 'post_unico',
        slide_type: 'content',
        position: 1,
        total: 1,
      },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.total_caracteres).toBeGreaterThan(0);
  });

  test('preview com formato thumbnail_youtube retorna 200', async ({ request }) => {
    const response = await request.post(`${API_BASE}/prompt-layers/preview`, {
      data: {
        tipo: 'imagem',
        brand_slug: 'itvalley',
        formato: 'thumbnail_youtube',
        slide_type: 'content',
        position: 1,
        total: 1,
      },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.total_caracteres).toBeGreaterThan(0);
  });
});

test.describe('Prompt Layers — API /compor', () => {
  test.beforeEach(async ({ request }) => {
    try {
      const health = await request.get('http://localhost:8000/health');
      test.skip(!health.ok(), 'Backend nao esta rodando em localhost:8000');
    } catch {
      test.skip(true, 'Backend nao esta rodando em localhost:8000');
    }
  });

  test('compor slide cover (position=1) sugere modelo Pro', async ({ request }) => {
    const response = await request.post(`${API_BASE}/prompt-layers/compor`, {
      data: {
        tipo: 'imagem',
        brand_slug: 'itvalley',
        formato: 'carrossel',
        slide: {
          type: 'cover',
          headline: 'Titulo de teste',
          bullets: [],
        },
        position: 1,
        total: 7,
        avatar_mode: 'livre',
      },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.modelo_sugerido).toBeTruthy();
    // Capa (position 1) deve usar modelo Pro
    expect(body.modelo_sugerido!.toLowerCase()).toContain('pro');
    expect(body.prompt_final).toBeTruthy();
    expect(body.total_caracteres).toBeGreaterThan(0);
  });

  test('compor slide content (position=3) sugere modelo Flash', async ({ request }) => {
    const response = await request.post(`${API_BASE}/prompt-layers/compor`, {
      data: {
        tipo: 'imagem',
        brand_slug: 'itvalley',
        formato: 'carrossel',
        slide: {
          type: 'content',
          headline: 'Conteudo tecnico',
          bullets: ['Item 1', 'Item 2'],
        },
        position: 3,
        total: 7,
        avatar_mode: 'livre',
      },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.modelo_sugerido).toBeTruthy();
    // Slide de conteudo (position 3) deve usar modelo Flash
    expect(body.modelo_sugerido!.toLowerCase()).toContain('flash');
  });

  test('compor slide CTA (position=total, last) sugere modelo Pro', async ({ request }) => {
    const response = await request.post(`${API_BASE}/prompt-layers/compor`, {
      data: {
        tipo: 'imagem',
        brand_slug: 'itvalley',
        formato: 'carrossel',
        slide: {
          type: 'cta',
          headline: 'Siga para mais!',
          bullets: [],
        },
        position: 7,
        total: 7,
        avatar_mode: 'livre',
      },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.modelo_sugerido).toBeTruthy();
    // CTA (ultima posicao) deve usar modelo Pro
    expect(body.modelo_sugerido!.toLowerCase()).toContain('pro');
  });

  test('compor com formato=post_unico NAO contem "1/1" no prompt', async ({ request }) => {
    const response = await request.post(`${API_BASE}/prompt-layers/compor`, {
      data: {
        tipo: 'imagem',
        brand_slug: 'itvalley',
        formato: 'post_unico',
        slide: {
          type: 'cover',
          headline: 'Post unico de teste',
          bullets: [],
        },
        position: 1,
        total: 1,
        avatar_mode: 'sim',
      },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    // Post unico nao deve ter indicador de paginacao "1/1"
    expect(body.prompt_final).not.toContain('1/1');
  });

  test('compor tipo=texto retorna prompt com camadas de texto', async ({ request }) => {
    const response = await request.post(`${API_BASE}/prompt-layers/compor`, {
      data: {
        tipo: 'texto',
        brand_slug: 'itvalley',
        formato: 'carrossel',
        slide: {},
        position: 1,
        total: 7,
        avatar_mode: 'livre',
        agente: 'copywriter',
      },
    });

    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.prompt_final).toBeTruthy();
    expect(body.camadas_usadas).toBeDefined();
    expect(body.camadas_usadas.length).toBeGreaterThan(0);
    expect(body.total_caracteres).toBeGreaterThan(0);
  });

  test('compor com brand_slug invalido retorna 200 (fallback sem marca)', async ({ request }) => {
    const response = await request.post(`${API_BASE}/prompt-layers/compor`, {
      data: {
        tipo: 'imagem',
        brand_slug: 'marca_inexistente',
        formato: 'carrossel',
        slide: {
          type: 'content',
          headline: 'Teste fallback',
          bullets: [],
        },
        position: 2,
        total: 7,
        avatar_mode: 'livre',
      },
    });

    // Deve funcionar mesmo sem marca (fallback)
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.prompt_final).toBeTruthy();
  });
});
