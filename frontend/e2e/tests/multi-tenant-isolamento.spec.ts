import { test, expect, request } from '@playwright/test';
import { backendHealthy } from '../helpers/backend-auth';
import { makeTokenForTenant } from '../helpers/jwt-maker';

/**
 * E2E: Isolamento multi-tenant (regression INT-04)
 *
 * Antes do fix, tenant_id vinha do body do request (forjavel).
 * Depois do fix, tenant_id vem do JWT (confiavel).
 *
 * Testa:
 * - Tenant A salva paleta
 * - Tenant B busca paleta — nao enxerga a de A
 * - Tenant A busca sua propria paleta — enxerga
 */

const BACKEND_URL = 'http://localhost:8000';

// Serial: teste de isolamento tenant A vs B — ordem das escritas importa
test.describe.configure({ mode: 'serial' });

test.describe('Isolamento multi-tenant (INT-04)', () => {
  const tenantA = 'tenant-e2e-A-' + Date.now();
  const tenantB = 'tenant-e2e-B-' + Date.now();
  let tokenA = '';
  let tokenB = '';

  test.beforeAll(async () => {
    const up = await backendHealthy();
    test.skip(!up, 'Backend nao esta UP');
    tokenA = makeTokenForTenant(tenantA);
    tokenB = makeTokenForTenant(tenantB);
  });

  test('tenant A salva brand-palette; tenant B ve paleta diferente', async () => {
    const ctxA = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${tokenA}` },
    });
    const ctxB = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${tokenB}` },
    });

    // Tenant A salva paleta com cor unica
    const corUnicaA = '#AABBCC';
    const saveA = await ctxA.put('/api/config/brand-palette', {
      data: {
        cores: {
          fundo_principal: corUnicaA,
          destaque_primario: '#123456',
          destaque_secundario: '#112233',
          texto_principal: '#FFFFFF',
          texto_secundario: '#AAAAAA',
        },
        fonte: 'Inter',
        elementos_obrigatorios: ['logo', 'assinatura'],
        estilo: 'tenant-A-unico',
      },
    });
    expect(saveA.status()).toBe(200);

    // Tenant B salva paleta propria com cor diferente
    const corUnicaB = '#DDEEFF';
    const saveB = await ctxB.put('/api/config/brand-palette', {
      data: {
        cores: {
          fundo_principal: corUnicaB,
          destaque_primario: '#654321',
          destaque_secundario: '#445566',
          texto_principal: '#FFFFFF',
          texto_secundario: '#BBBBBB',
        },
        fonte: 'Arial',
        elementos_obrigatorios: ['logo'],
        estilo: 'tenant-B-unico',
      },
    });
    expect(saveB.status()).toBe(200);

    // Tenant A busca sua paleta — deve retornar corUnicaA
    const getA = await ctxA.get('/api/config/brand-palette');
    expect(getA.status()).toBe(200);
    const dataA = await getA.json();
    const jsonA = JSON.stringify(dataA);
    expect(jsonA).toContain(corUnicaA);
    expect(jsonA).not.toContain(corUnicaB); // Nao pode vazar do tenant B

    // Tenant B busca sua paleta — deve retornar corUnicaB e NAO corUnicaA
    const getB = await ctxB.get('/api/config/brand-palette');
    expect(getB.status()).toBe(200);
    const dataB = await getB.json();
    const jsonB = JSON.stringify(dataB);
    expect(jsonB).toContain(corUnicaB);
    expect(jsonB).not.toContain(corUnicaA); // ISOLAMENTO: tenant B NAO ve paleta de A

    await ctxA.dispose();
    await ctxB.dispose();
  });

  test('tenant A salva creators; tenant B nao enxerga', async () => {
    const ctxA = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${tokenA}` },
    });
    const ctxB = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${tokenB}` },
    });

    const nomeUnicoA = `Creator-A-${Date.now()}`;
    await ctxA.put('/api/config/creator-registry', {
      data: {
        criadores: [
          { nome: nomeUnicoA, funcao: 'TECH_SOURCE', plataforma: 'YouTube', url: 'https://yt/a', ativo: true },
        ],
      },
    });

    const nomeUnicoB = `Creator-B-${Date.now()}`;
    await ctxB.put('/api/config/creator-registry', {
      data: {
        criadores: [
          { nome: nomeUnicoB, funcao: 'EXPLAINER', plataforma: 'Twitter', url: 'https://tw/b', ativo: true },
        ],
      },
    });

    const getA = await ctxA.get('/api/config/creator-registry');
    const dataA = await getA.json();
    const creatorsA = Array.isArray(dataA) ? dataA : (dataA.criadores ?? dataA.creators ?? []);
    const namesA = creatorsA.map((c: any) => c.nome);
    expect(namesA).toContain(nomeUnicoA);
    expect(namesA).not.toContain(nomeUnicoB);

    const getB = await ctxB.get('/api/config/creator-registry');
    const dataB = await getB.json();
    const creatorsB = Array.isArray(dataB) ? dataB : (dataB.criadores ?? dataB.creators ?? []);
    const namesB = creatorsB.map((c: any) => c.nome);
    expect(namesB).toContain(nomeUnicoB);
    expect(namesB).not.toContain(nomeUnicoA);

    await ctxA.dispose();
    await ctxB.dispose();
  });

  test('INT-04: tenant_id vem do JWT (nao do body) — forjar tenant no body e ignorado', async () => {
    // Tenant A envia body com tenant_id=B forjado
    // Backend deve usar o tenant_id do JWT (A) e ignorar o body
    const ctxA = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${tokenA}` },
    });
    const ctxB = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${tokenB}` },
    });

    const marker = `tenant-jwt-${Date.now()}`;
    await ctxA.put('/api/config/brand-palette', {
      data: {
        tenant_id: tenantB,  // Tenta forjar — deve ser ignorado
        cores: {
          fundo_principal: '#111111',
          destaque_primario: '#222222',
          destaque_secundario: '#333333',
          texto_principal: '#FFFFFF',
          texto_secundario: '#CCCCCC',
        },
        fonte: 'Inter',
        elementos_obrigatorios: [marker],
        estilo: marker,
      },
    });

    // Tenant B busca — NAO deve ver o marker
    const getB = await ctxB.get('/api/config/brand-palette');
    const dataB = await getB.json();
    expect(JSON.stringify(dataB)).not.toContain(marker);

    // Tenant A busca — DEVE ver o marker
    const getA = await ctxA.get('/api/config/brand-palette');
    const dataA = await getA.json();
    expect(JSON.stringify(dataA)).toContain(marker);

    await ctxA.dispose();
    await ctxB.dispose();
  });
});
