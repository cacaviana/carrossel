export function carrosselMock(): Record<string, unknown> {
	return {
		title: 'Transfer Learning: 14h → 8min (MOCK)',
		disciplina: 'D5 — Deep Learning',
		tecnologia_principal: 'Transfer Learning',
		hook_formula: 'F2 RESULTADO IMPOSSÍVEL',
		slides: [
			{
				type: 'cover',
				headline: '14 horas de treino → 8 minutos.\nMesma accuracy.\nA diferença: 4 linhas de código.',
				subline: 'NOTÍCIA REAL'
			},
			{
				type: 'content',
				title: 'O problema',
				bullets: ['Treinar do zero = milhões de imagens', 'Colab gratuito não aguenta', 'Timeout após 3h'],
				etapa: 'CONTEXTO'
			},
			{
				type: 'content',
				title: 'Transfer Learning resolve',
				bullets: ['Congela camadas já treinadas', 'Só treina a cabeça', '94% accuracy com 500 imagens'],
				etapa: 'REVELAÇÃO'
			},
			{
				type: 'code',
				title: 'Transfer Learning em 4 linhas',
				code: 'base = ResNet50(weights="imagenet", include_top=False)\nbase.trainable = False\nmodel = Sequential([base, GlobalAveragePooling2D(), Dense(5, activation="softmax")])',
				caption: 'ResNet50 já aprendeu features visuais',
				etapa: 'CÓDIGO'
			},
			{
				type: 'comparison',
				title: 'Com vs Sem Transfer Learning',
				left_label: 'Sem TL',
				left_items: ['14h treino', '67% accuracy', 'Milhões de imagens'],
				right_label: 'Com TL',
				right_items: ['8min treino', '94% accuracy', '500 imagens'],
				etapa: 'COMPARATIVO'
			},
			{
				type: 'content',
				title: 'Quando NÃO usar',
				bullets: ['Domínio muito diferente (raio-X, satélite)', 'Dados tabulares', 'Problemas de NLP simples'],
				etapa: 'LIÇÕES'
			},
			{
				type: 'content',
				title: 'Se você já treinou 14h...',
				bullets: ['E levou timeout no Colab', 'E a accuracy ficou em 67%', 'Transfer Learning era a resposta'],
				etapa: 'ESPELHO'
			},
			{
				type: 'cta',
				headline: 'Qual base model você mais usa?',
				subline: 'Disciplina D5 da pós de IA e ML',
				tags: ['#TransferLearning', '#DeepLearning', '#ITValleySchool']
			}
		],
		legenda_linkedin: '14 horas de treino → 8 minutos (MOCK)'
	};
}

export function imagensMock(count: number): { images: (string | null)[] } {
	return { images: Array(count).fill(null) };
}

export function imagemSlideMock(): { image: string | null } {
	return { image: null };
}
