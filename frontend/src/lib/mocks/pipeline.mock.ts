import type { EtapaPipeline, PipelineStatus } from '$lib/dtos/PipelineDTO';

export const pipelinesMock = [
  {
    id: 'pip-001',
    tenant_id: 'itvalley-default',
    tema: 'Como RAG resolve o problema de alucinacao em LLMs — arquitetura completa com LangChain e ChromaDB',
    formato: 'carrossel' as const,
    status: 'aguardando_aprovacao' as PipelineStatus,
    etapa_atual: 'strategist' as EtapaPipeline,
    modo_funil: false,
    created_at: '2026-04-01T14:30:00Z',
    updated_at: '2026-04-01T14:32:15Z'
  },
  {
    id: 'pip-002',
    tenant_id: 'itvalley-default',
    tema: 'Transfer Learning: de 14h de treino para 8 minutos com a mesma accuracy usando ResNet50',
    formato: 'post_unico' as const,
    status: 'aprovado' as PipelineStatus,
    etapa_atual: 'content_critic' as EtapaPipeline,
    modo_funil: false,
    created_at: '2026-03-28T09:00:00Z',
    updated_at: '2026-03-28T10:45:00Z'
  },
  {
    id: 'pip-003',
    tenant_id: 'itvalley-default',
    tema: 'MLOps na pratica: CI/CD para modelos de Machine Learning com GitHub Actions e SageMaker',
    formato: 'thumbnail_youtube' as const,
    status: 'em_execucao' as PipelineStatus,
    etapa_atual: 'image_generator' as EtapaPipeline,
    modo_funil: false,
    created_at: '2026-04-02T08:15:00Z',
    updated_at: '2026-04-02T08:20:00Z'
  },
  {
    id: 'pip-004',
    tenant_id: 'itvalley-default',
    tema: 'Data Drift: como detectar quando seu modelo perde performance em producao',
    formato: 'carrossel' as const,
    status: 'erro' as PipelineStatus,
    etapa_atual: 'art_director' as EtapaPipeline,
    modo_funil: false,
    created_at: '2026-03-30T16:00:00Z',
    updated_at: '2026-03-30T16:12:00Z'
  }
];

export const pipelineStepsMock: Record<string, any[]> = {
  'pip-001': [
    { id: 'step-001-1', pipeline_id: 'pip-001', agente: 'strategist', status: 'aguardando_aprovacao', entrada: {}, saida: {}, duracao_ms: 12400, aprovado_por: '', approved_at: '' },
    { id: 'step-001-2', pipeline_id: 'pip-001', agente: 'copywriter', status: 'pendente', entrada: {}, saida: {}, duracao_ms: 0, aprovado_por: '', approved_at: '' },
    { id: 'step-001-3', pipeline_id: 'pip-001', agente: 'hook_specialist', status: 'pendente', entrada: {}, saida: {}, duracao_ms: 0, aprovado_por: '', approved_at: '' },
    { id: 'step-001-4', pipeline_id: 'pip-001', agente: 'art_director', status: 'pendente', entrada: {}, saida: {}, duracao_ms: 0, aprovado_por: '', approved_at: '' },
    { id: 'step-001-5', pipeline_id: 'pip-001', agente: 'image_generator', status: 'pendente', entrada: {}, saida: {}, duracao_ms: 0, aprovado_por: '', approved_at: '' },
    { id: 'step-001-6', pipeline_id: 'pip-001', agente: 'brand_gate', status: 'pendente', entrada: {}, saida: {}, duracao_ms: 0, aprovado_por: '', approved_at: '' },
    { id: 'step-001-7', pipeline_id: 'pip-001', agente: 'content_critic', status: 'pendente', entrada: {}, saida: {}, duracao_ms: 0, aprovado_por: '', approved_at: '' }
  ],
  'pip-002': [
    { id: 'step-002-1', pipeline_id: 'pip-002', agente: 'strategist', status: 'aprovado', entrada: {}, saida: {}, duracao_ms: 11200, aprovado_por: 'carlos', approved_at: '2026-03-28T09:15:00Z' },
    { id: 'step-002-2', pipeline_id: 'pip-002', agente: 'copywriter', status: 'aprovado', entrada: {}, saida: {}, duracao_ms: 18500, aprovado_por: '', approved_at: '' },
    { id: 'step-002-3', pipeline_id: 'pip-002', agente: 'hook_specialist', status: 'aprovado', entrada: {}, saida: {}, duracao_ms: 8900, aprovado_por: 'carlos', approved_at: '2026-03-28T09:45:00Z' },
    { id: 'step-002-4', pipeline_id: 'pip-002', agente: 'art_director', status: 'aprovado', entrada: {}, saida: {}, duracao_ms: 14300, aprovado_por: 'carlos', approved_at: '2026-03-28T10:05:00Z' },
    { id: 'step-002-5', pipeline_id: 'pip-002', agente: 'image_generator', status: 'aprovado', entrada: {}, saida: {}, duracao_ms: 45200, aprovado_por: '', approved_at: '' },
    { id: 'step-002-6', pipeline_id: 'pip-002', agente: 'brand_gate', status: 'aprovado', entrada: {}, saida: {}, duracao_ms: 1800, aprovado_por: 'carlos', approved_at: '2026-03-28T10:35:00Z' },
    { id: 'step-002-7', pipeline_id: 'pip-002', agente: 'content_critic', status: 'aprovado', entrada: {}, saida: {}, duracao_ms: 9600, aprovado_por: '', approved_at: '' }
  ]
};

export function simularDelay(ms: number = 300): Promise<void> {
  return new Promise(r => setTimeout(r, ms));
}
