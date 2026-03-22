export class Slide {
	readonly type: 'cover' | 'content' | 'code' | 'comparison' | 'cta';
	readonly headline?: string;
	readonly subline?: string;
	readonly title?: string;
	readonly bullets?: string[];
	readonly etapa?: string;
	readonly code?: string;
	readonly caption?: string;
	readonly left_label?: string;
	readonly left_items?: string[];
	readonly right_label?: string;
	readonly right_items?: string[];
	readonly tags?: string[];
	readonly imageBase64?: string;

	constructor(data: Record<string, unknown>) {
		this.type = (data.type as Slide['type']) ?? 'content';
		this.headline = data.headline as string | undefined;
		this.subline = data.subline as string | undefined;
		this.title = data.title as string | undefined;
		this.bullets = data.bullets as string[] | undefined;
		this.etapa = data.etapa as string | undefined;
		this.code = data.code as string | undefined;
		this.caption = data.caption as string | undefined;
		this.left_label = data.left_label as string | undefined;
		this.left_items = data.left_items as string[] | undefined;
		this.right_label = data.right_label as string | undefined;
		this.right_items = data.right_items as string[] | undefined;
		this.tags = data.tags as string[] | undefined;
		this.imageBase64 = data.imageBase64 as string | undefined;
	}

	isValid(): boolean {
		if (!this.type) return false;
		if (this.type === 'cover') return !!this.headline;
		if (this.type === 'code') return !!this.code;
		if (this.type === 'cta') return !!this.headline;
		return !!this.title;
	}

	toPayload(): Record<string, unknown> {
		const payload: Record<string, unknown> = { type: this.type };
		if (this.headline !== undefined) payload.headline = this.headline;
		if (this.subline !== undefined) payload.subline = this.subline;
		if (this.title !== undefined) payload.title = this.title;
		if (this.bullets !== undefined) payload.bullets = this.bullets;
		if (this.etapa !== undefined) payload.etapa = this.etapa;
		if (this.code !== undefined) payload.code = this.code;
		if (this.caption !== undefined) payload.caption = this.caption;
		if (this.left_label !== undefined) payload.left_label = this.left_label;
		if (this.left_items !== undefined) payload.left_items = this.left_items;
		if (this.right_label !== undefined) payload.right_label = this.right_label;
		if (this.right_items !== undefined) payload.right_items = this.right_items;
		if (this.tags !== undefined) payload.tags = this.tags;
		return payload;
	}
}

export class CarrosselData {
	readonly title: string;
	readonly disciplina: string;
	readonly tecnologia_principal: string;
	readonly hook_formula: string;
	readonly slides: Slide[];
	readonly legenda_linkedin: string;
	readonly createdAt?: string;

	constructor(data: Record<string, unknown>) {
		this.title = (data.title as string) ?? '';
		this.disciplina = (data.disciplina as string) ?? '';
		this.tecnologia_principal = (data.tecnologia_principal as string) ?? '';
		this.hook_formula = (data.hook_formula as string) ?? '';
		this.slides = ((data.slides as Record<string, unknown>[]) ?? []).map(
			(s) => new Slide(s)
		);
		this.legenda_linkedin = (data.legenda_linkedin as string) ?? '';
		this.createdAt = data.createdAt as string | undefined;
	}

	isValid(): boolean {
		return this.slides.length >= 3 && this.slides.every((s) => s.isValid());
	}

	toPayload(): Record<string, unknown> {
		return {
			title: this.title,
			disciplina: this.disciplina,
			tecnologia_principal: this.tecnologia_principal,
			hook_formula: this.hook_formula,
			slides: this.slides.map((s) => s.toPayload()),
			legenda_linkedin: this.legenda_linkedin
		};
	}
}
