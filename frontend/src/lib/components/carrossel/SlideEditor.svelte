<script lang="ts">
	import type { Slide } from '$lib/stores/carrossel';

	interface Props {
		slide: Slide;
		index: number;
		gerandoSlide: number | null;
		onUpdate: (index: number, field: string, value: string | string[]) => void;
		onUpdateBullet: (slideIndex: number, bulletIndex: number, value: string) => void;
		onAddBullet: (slideIndex: number) => void;
		onRemoveBullet: (slideIndex: number, bulletIndex: number) => void;
		onGerarImagem: (index: number) => void;
	}

	let { slide, index, gerandoSlide, onUpdate, onUpdateBullet, onAddBullet, onRemoveBullet, onGerarImagem }: Props = $props();
</script>

<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-5">
	<div class="flex items-center gap-3 mb-4">
		<span class="w-7 h-7 rounded-full bg-steel-6 text-white text-xs font-bold flex items-center justify-center shrink-0">{index + 1}</span>
		<span class="px-2.5 py-0.5 rounded-full text-xs bg-steel-0 text-steel-3 font-medium">{slide.type}</span>
		{#if slide.imageBase64}
			<span class="text-xs text-green-600 font-medium">✓ imagem gerada</span>
		{/if}
		<button
			onclick={() => onGerarImagem(index)}
			disabled={gerandoSlide !== null}
			class="ml-auto px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer
				{slide.imageBase64 ? 'border border-steel-3/30 text-steel-3 hover:bg-steel-0' : 'bg-steel-3 text-white hover:bg-steel-4'}
				disabled:opacity-50 disabled:cursor-not-allowed"
		>
			{gerandoSlide === index ? 'Gerando...' : slide.imageBase64 ? 'Regenerar' : 'Gerar imagem'}
		</button>
	</div>

	<div class="space-y-3">
		{#if slide.headline !== undefined}
			<div>
				<label class="block text-xs font-medium text-steel-4 mb-1">Headline</label>
				<input type="text" value={slide.headline}
					oninput={(e) => onUpdate(index, 'headline', (e.target as HTMLInputElement).value)}
					class="w-full px-3 py-2 rounded-lg border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 outline-none" />
			</div>
		{/if}
		{#if slide.subline !== undefined}
			<div>
				<label class="block text-xs font-medium text-steel-4 mb-1">Subline</label>
				<input type="text" value={slide.subline}
					oninput={(e) => onUpdate(index, 'subline', (e.target as HTMLInputElement).value)}
					class="w-full px-3 py-2 rounded-lg border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 outline-none" />
			</div>
		{/if}
		{#if slide.title !== undefined}
			<div>
				<label class="block text-xs font-medium text-steel-4 mb-1">Título</label>
				<input type="text" value={slide.title}
					oninput={(e) => onUpdate(index, 'title', (e.target as HTMLInputElement).value)}
					class="w-full px-3 py-2 rounded-lg border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 outline-none" />
			</div>
		{/if}
		{#if slide.bullets && slide.bullets.length > 0}
			<div>
				<label class="block text-xs font-medium text-steel-4 mb-1">Bullets</label>
				<div class="space-y-2">
					{#each slide.bullets as bullet, bi}
						<div class="flex gap-2">
							<input type="text" value={bullet}
								oninput={(e) => onUpdateBullet(index, bi, (e.target as HTMLInputElement).value)}
								class="flex-1 px-3 py-2 rounded-lg border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 outline-none" />
							<button onclick={() => onRemoveBullet(index, bi)}
								class="px-2.5 py-1 rounded-lg text-xs text-red-500 hover:bg-red-50 transition-all cursor-pointer">✕</button>
						</div>
					{/each}
					<button onclick={() => onAddBullet(index)}
						class="text-xs text-steel-3 hover:text-steel-4 font-medium cursor-pointer">+ Adicionar bullet</button>
				</div>
			</div>
		{/if}
		{#if slide.code !== undefined}
			<div>
				<label class="block text-xs font-medium text-steel-4 mb-1">Código</label>
				<textarea value={slide.code} rows="5"
					oninput={(e) => onUpdate(index, 'code', (e.target as HTMLTextAreaElement).value)}
					class="w-full px-3 py-2 rounded-lg border border-teal-4/30 bg-white text-steel-6 text-xs font-mono focus:border-steel-3 outline-none resize-y"></textarea>
			</div>
		{/if}
		{#if slide.caption !== undefined}
			<div>
				<label class="block text-xs font-medium text-steel-4 mb-1">Caption</label>
				<input type="text" value={slide.caption}
					oninput={(e) => onUpdate(index, 'caption', (e.target as HTMLInputElement).value)}
					class="w-full px-3 py-2 rounded-lg border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 outline-none" />
			</div>
		{/if}
		{#if slide.etapa !== undefined}
			<div>
				<label class="block text-xs font-medium text-steel-4 mb-1">Etapa</label>
				<input type="text" value={slide.etapa}
					oninput={(e) => onUpdate(index, 'etapa', (e.target as HTMLInputElement).value)}
					class="w-full px-3 py-2 rounded-lg border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 outline-none" />
			</div>
		{/if}
	</div>
</div>
