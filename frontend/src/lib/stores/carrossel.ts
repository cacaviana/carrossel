import { writable } from 'svelte/store';

export interface Slide {
	type: 'cover' | 'content' | 'code' | 'comparison' | 'cta' | 'infographic';
	headline?: string;
	subline?: string;
	title?: string;
	bullets?: string[];
	etapa?: string;
	code?: string;
	caption?: string;
	left_label?: string;
	left_items?: string[];
	right_label?: string;
	right_items?: string[];
	tags?: string[];
	illustration_description?: string;
	imageBase64?: string;
}

export interface CarrosselData {
	title: string;
	disciplina: string;
	tecnologia_principal: string;
	hook_formula: string;
	slides: Slide[];
	legenda_linkedin: string;
	createdAt?: string;
	// Contexto de geracao (Fase 4) — necessario pra regenerar slides
	// individualmente mantendo consistencia de refs
	brand_slug?: string;
	avatar_mode?: 'sem' | 'capa' | 'livre' | 'sim';
	max_slides?: number;
	pipeline_id?: string;
	formato?: string;
}

export const carrosselAtual = writable<CarrosselData | null>(null);
export const gerandoConteudo = writable(false);
export const gerandoImagens = writable(false);
export const slideAtual = writable(0);
