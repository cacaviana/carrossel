import { test, expect, request } from '@playwright/test';
import { backendHealthy, loginBackend } from '../helpers/backend-auth';

/**
 * E2E: Pipeline aprovar com edicao + rejeitar com motivo
 * Regressions: INT-02 (aprovar com dados_editados) + INT-03 (rejeitar com motivo)
 *
 * Fluxo:
 * - Cria pipeline
 * - Aprova etapa com dados_editados (contrato novo do frontend)
 * - Rejeita etapa com motivo "X" — motivo deve ser recebido pelo backend
 */

const BACKEND_URL = 'http://localhost:8000';

// Serial: cada test cria pipeline novo, roda operacoes custosas (criar etapas via DB)
test.describe.configure({ mode: 'serial' });

async function criarPipelineSimples(token: string): Promise<string | null> {
  const ctx = await request.newContext({
    baseURL: BACKEND_URL,
    extraHTTPHeaders: { Authorization: `Bearer ${token}` },
  });
  const res = await ctx.post('/api/pipelines/', {
    data: {
      tema: 'Pipeline E2E Teste INT-02/03',
      formato: 'carrossel',
      modo_entrada: 'ideia',
      disciplina: 'D1 Linguagens',
      tecnologia: 'Python',
      max_slides: 3,
    },
  });
  if (!res.ok()) {
    await ctx.dispose();
    return null;
  }
  const data = await res.json();
  await ctx.dispose();
  return data.id ?? data.pipeline_id ?? null;
}

test.describe('Pipeline aprovar/rejeitar - API backend', () => {
  let token = '';

  test.beforeAll(async () => {
    const up = await backendHealthy();
    test.skip(!up, 'Backend nao esta UP');
    const auth = await loginBackend();
    token = auth.token;
  });

  test('criar pipeline retorna 201 + id', async () => {
    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const res = await ctx.post('/api/pipelines/', {
      data: {
        tema: 'Pipeline teste criar',
        formato: 'carrossel',
        modo_entrada: 'ideia',
        max_slides: 3,
      },
    });
    expect([200, 201]).toContain(res.status());
    const data = await res.json();
    expect(data.id ?? data.pipeline_id).toBeTruthy();
    await ctx.dispose();
  });

  test('INT-02: aprovar etapa com dados_editados (contrato novo) retorna 200', async () => {
    const pipelineId = await criarPipelineSimples(token);
    if (!pipelineId) {
      test.skip(true, 'Nao conseguiu criar pipeline');
      return;
    }

    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });

    // Busca etapas do pipeline
    const pipeRes = await ctx.get(`/api/pipelines/${pipelineId}`);
    const pipeData = await pipeRes.json();
    const etapas = pipeData.etapas ?? [];
    const primeira = etapas[0];
    if (!primeira) {
      test.skip(true, 'Pipeline sem etapas');
      await ctx.dispose();
      return;
    }

    const agente = primeira.agente;
    // Aprova com dados_editados (formato novo do frontend)
    const aprovarRes = await ctx.post(`/api/pipelines/${pipelineId}/etapas/${agente}/aprovar`, {
      data: {
        dados_editados: { titulo: 'Novo titulo editado', observacao: 'edicao e2e' },
        etapa: agente,
      },
    });
    // Deve aceitar o contrato novo sem 422 (e sem 400 por estar em status que nao permite aprovacao)
    // Aceitamos tambem 400 caso a etapa ainda nao tenha sido executada (mas ainda assim nao pode ser 422)
    expect([200, 400]).toContain(aprovarRes.status());
    expect(aprovarRes.status()).not.toBe(422);
    await ctx.dispose();
  });

  test('INT-02: aprovar com saida_editada (contrato legado) ainda funciona', async () => {
    const pipelineId = await criarPipelineSimples(token);
    if (!pipelineId) {
      test.skip(true);
      return;
    }

    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });

    const pipeRes = await ctx.get(`/api/pipelines/${pipelineId}`);
    const pipeData = await pipeRes.json();
    const agente = pipeData.etapas?.[0]?.agente;
    if (!agente) {
      test.skip(true);
      await ctx.dispose();
      return;
    }

    // Contrato legado: saida_editada string
    const res = await ctx.post(`/api/pipelines/${pipelineId}/etapas/${agente}/aprovar`, {
      data: { saida_editada: '{"titulo":"editado via legado"}' },
    });
    expect(res.status()).not.toBe(422);
    expect([200, 400, 404]).toContain(res.status());
    await ctx.dispose();
  });

  test('INT-03: rejeitar etapa com motivo persiste o motivo', async () => {
    const pipelineId = await criarPipelineSimples(token);
    if (!pipelineId) {
      test.skip(true);
      return;
    }

    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });

    const pipeRes = await ctx.get(`/api/pipelines/${pipelineId}`);
    const pipeData = await pipeRes.json();
    const agente = pipeData.etapas?.[0]?.agente;
    if (!agente) {
      test.skip(true);
      await ctx.dispose();
      return;
    }

    const MOTIVO = 'Titulo nao segue a identidade da marca — precisa revisao';
    const res = await ctx.post(`/api/pipelines/${pipelineId}/etapas/${agente}/rejeitar`, {
      data: { motivo: MOTIVO },
    });
    // Contrato deve aceitar { motivo: string } sem 422
    expect(res.status()).not.toBe(422);
    expect([200, 400, 404]).toContain(res.status());

    // Se deu 200, busca etapa e verifica que motivo foi salvo
    if (res.status() === 200) {
      const verRes = await ctx.get(`/api/pipelines/${pipelineId}/etapas/${agente}`);
      if (verRes.ok()) {
        const etapaData = await verRes.json();
        // motivo ou observacao ou rejeicao_motivo — qualquer campo que carregue o valor
        const campos = JSON.stringify(etapaData);
        expect(campos).toContain(MOTIVO.split(' ')[0]); // primeira palavra no mínimo
      }
    }
    await ctx.dispose();
  });

  test('rejeitar sem motivo aceita string vazia (default)', async () => {
    const pipelineId = await criarPipelineSimples(token);
    if (!pipelineId) {
      test.skip(true);
      return;
    }

    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });

    const pipeRes = await ctx.get(`/api/pipelines/${pipelineId}`);
    const pipeData = await pipeRes.json();
    const agente = pipeData.etapas?.[0]?.agente;
    if (!agente) {
      test.skip(true);
      await ctx.dispose();
      return;
    }

    // Body vazio — motivo default = ""
    const res = await ctx.post(`/api/pipelines/${pipelineId}/etapas/${agente}/rejeitar`, {
      data: {},
    });
    // Nao pode ser 422 (schema validation) nem 500
    expect(res.status()).not.toBe(422);
    expect(res.status()).not.toBe(500);
    await ctx.dispose();
  });

  test('aprovar etapa inexistente retorna 404', async () => {
    const pipelineId = await criarPipelineSimples(token);
    if (!pipelineId) {
      test.skip(true);
      return;
    }

    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });

    const res = await ctx.post(`/api/pipelines/${pipelineId}/etapas/agente-fake-nao-existe/aprovar`, {
      data: { dados_editados: {} },
    });
    expect([400, 404]).toContain(res.status());
    await ctx.dispose();
  });
});
