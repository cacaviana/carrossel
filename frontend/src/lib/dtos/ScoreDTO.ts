export function scoreCor(score: number): string {
  if (score >= 8) return 'text-green';
  if (score >= 6) return 'text-amber';
  return 'text-red';
}

export type ScoreDecision = 'approved' | 'needs_revision';

export class ScoreDTO {
  readonly pipeline_id: string;
  readonly clarity: number;
  readonly impact: number;
  readonly originality: number;
  readonly scroll_stop: number;
  readonly cta_strength: number;
  readonly final_score: number;
  readonly decision: ScoreDecision;
  readonly best_variation: string;

  constructor(data: Record<string, any>) {
    this.pipeline_id = data.pipeline_id ?? '';
    this.clarity = data.clarity ?? 0;
    this.impact = data.impact ?? 0;
    this.originality = data.originality ?? 0;
    this.scroll_stop = data.scroll_stop ?? 0;
    this.cta_strength = data.cta_strength ?? 0;
    this.final_score = data.final_score ?? 0;
    this.decision = data.decision ?? 'needs_revision';
    this.best_variation = data.best_variation ?? '';
  }

  get isAprovado(): boolean {
    return this.decision === 'approved';
  }

  get dimensoes(): { label: string; valor: number }[] {
    return [
      { label: 'Clareza', valor: this.clarity },
      { label: 'Impacto', valor: this.impact },
      { label: 'Originalidade', valor: this.originality },
      { label: 'Scroll Stop', valor: this.scroll_stop },
      { label: 'CTA Strength', valor: this.cta_strength },
      { label: 'Score Final', valor: this.final_score }
    ];
  }

  get scoreCor(): string {
    return scoreCor(this.final_score);
  }

  isValid(): boolean {
    return this.pipeline_id.length > 0 && this.final_score >= 0 && this.final_score <= 10;
  }

  toPayload(): Record<string, any> {
    return {
      pipeline_id: this.pipeline_id,
      clarity: this.clarity,
      impact: this.impact,
      originality: this.originality,
      scroll_stop: this.scroll_stop,
      cta_strength: this.cta_strength,
      final_score: this.final_score,
      decision: this.decision,
      best_variation: this.best_variation
    };
  }
}
