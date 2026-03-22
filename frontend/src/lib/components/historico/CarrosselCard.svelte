<script lang="ts">
	import type { CarrosselData } from '$lib/stores/carrossel';

	interface Props {
		item: CarrosselData;
		onAbrir: () => void;
		onRemover: () => void;
	}

	let { item, onAbrir, onRemover }: Props = $props();
</script>

<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-5 hover:-translate-y-1 hover:shadow-md transition-all">
	<div class="flex items-start justify-between mb-3">
		<span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-steel-0 text-steel-3">
			{item.disciplina}
		</span>
		<button
			onclick={onRemover}
			class="text-steel-4 hover:text-red-500 text-xs transition-all cursor-pointer"
		>
			remover
		</button>
	</div>
	<h3 class="font-semibold text-steel-6 text-sm mb-1 line-clamp-2">{item.title}</h3>
	<p class="text-xs text-steel-4 font-light mb-3">{item.tecnologia_principal}</p>
	<div class="flex items-center justify-between">
		<span class="text-xs text-steel-4/60">
			{item.slides.length} slides
			{#if item.createdAt}
				— {new Date(item.createdAt).toLocaleDateString('pt-BR')}
			{/if}
		</span>
		<button
			onclick={onAbrir}
			class="px-3 py-1.5 rounded-full text-xs font-medium bg-steel-3 text-white
				hover:bg-steel-4 transition-all cursor-pointer"
		>
			Abrir
		</button>
	</div>
</div>
