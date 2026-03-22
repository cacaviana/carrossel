<script lang="ts">
	import { browser } from '$app/environment';
	import type { CarrosselData } from '$lib/stores/carrossel';
	import { carrosselAtual, slideAtual } from '$lib/stores/carrossel';
	import { goto } from '$app/navigation';

	let historico = $state<CarrosselData[]>([]);
	let filtro = $state('');

	if (browser) {
		const saved = localStorage.getItem('carrossel-historico');
		if (saved) {
			try {
				historico = JSON.parse(saved);
			} catch {
				historico = [];
			}
		}
	}

	const historicoFiltrado = $derived(
		filtro
			? historico.filter(
					(h) =>
						h.title.toLowerCase().includes(filtro.toLowerCase()) ||
						h.disciplina.toLowerCase().includes(filtro.toLowerCase()) ||
						h.tecnologia_principal.toLowerCase().includes(filtro.toLowerCase())
				)
			: historico
	);

	function abrirCarrossel(item: CarrosselData) {
		carrosselAtual.set(item);
		slideAtual.set(0);
		goto('/carrossel');
	}

	function remover(item: CarrosselData) {
		historico = historico.filter((h) => h !== item);
		if (browser) {
			localStorage.setItem('carrossel-historico', JSON.stringify(historico));
		}
	}
</script>

<svelte:head>
	<title>Histórico — Carrossel System</title>
</svelte:head>

<div class="animate-fade-up">
	<div class="flex items-center justify-between mb-8">
		<div>
			<h2 class="text-2xl font-semibold text-steel-6 mb-2">Histórico</h2>
			<p class="text-steel-4 font-light">Carrosséis gerados anteriormente.</p>
		</div>
	</div>

	<div class="mb-6">
		<input
			type="text"
			bind:value={filtro}
			placeholder="Filtrar por título, disciplina ou tecnologia..."
			class="w-full max-w-md px-4 py-3 rounded-xl border border-teal-4/30 bg-bg-card text-steel-6 text-sm
				focus:border-steel-3 focus:ring-2 focus:ring-steel-3/20 outline-none transition-all"
		/>
	</div>

	{#if historicoFiltrado.length === 0}
		<div class="text-center py-16">
			<p class="text-steel-4 text-lg mb-2">
				{filtro ? 'Nenhum resultado encontrado.' : 'Nenhum carrossel salvo ainda.'}
			</p>
			<p class="text-steel-4/60 text-sm font-light">Carrosséis aparecerão aqui após serem gerados.</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
			{#each historicoFiltrado as item, i}
				<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-5 hover:-translate-y-1 hover:shadow-md transition-all">
					<div class="flex items-start justify-between mb-3">
						<span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-steel-0 text-steel-3">
							{item.disciplina}
						</span>
						<button
							onclick={() => remover(item)}
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
							onclick={() => abrirCarrossel(item)}
							class="px-3 py-1.5 rounded-full text-xs font-medium bg-steel-3 text-white
								hover:bg-steel-4 transition-all cursor-pointer"
						>
							Abrir
						</button>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
