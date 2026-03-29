<script lang="ts">
	import { config } from '$lib/stores/config';
	import { onMount } from 'svelte';

	type HistoricoItem = {
		id: number;
		titulo: string;
		disciplina: string | null;
		tecnologia_principal: string | null;
		tipo_carrossel: string | null;
		total_slides: number | null;
		google_drive_link: string | null;
		google_drive_folder_name: string | null;
		criado_em: string | null;
	};

	let historico = $state<HistoricoItem[]>([]);
	let filtro = $state('');
	let carregando = $state(true);
	let erro = $state('');

	onMount(async () => {
		let currentConfig: typeof $config | undefined;
		config.subscribe((v) => (currentConfig = v))();
		try {
			const res = await fetch(`${currentConfig.backendUrl}/api/historico`);
			if (res.ok) historico = await res.json();
			else erro = 'Erro ao carregar histórico';
		} catch {
			erro = 'Backend indisponível';
		} finally {
			carregando = false;
		}
	});

	const historicoFiltrado = $derived(
		filtro
			? historico.filter(
					(h) =>
						h.titulo?.toLowerCase().includes(filtro.toLowerCase()) ||
						h.disciplina?.toLowerCase().includes(filtro.toLowerCase()) ||
						h.tecnologia_principal?.toLowerCase().includes(filtro.toLowerCase())
				)
			: historico
	);

	async function remover(item: HistoricoItem) {
		let currentConfig: typeof $config | undefined;
		config.subscribe((v) => (currentConfig = v))();
		try {
			await fetch(`${currentConfig.backendUrl}/api/historico/${item.id}`, { method: 'DELETE' });
			historico = historico.filter((h) => h.id !== item.id);
		} catch {}
	}

	const tipoBadge: Record<string, string> = {
		texto: 'bg-steel-0 text-steel-3',
		visual: 'bg-purple-50 text-purple-600',
		infografico: 'bg-amber-50 text-amber-600',
	};
</script>

<svelte:head>
	<title>Histórico — Carrossel System</title>
</svelte:head>

<div class="animate-fade-up">
	<div class="mb-6">
		<h2 class="text-xl sm:text-2xl font-semibold text-steel-6 mb-1">Histórico</h2>
		<p class="text-sm text-steel-4 font-light">Carrosséis salvos no Google Drive.</p>
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

	{#if carregando}
		<div class="text-center py-16">
			<span class="inline-flex items-center gap-2 text-steel-4">
				<span class="w-4 h-4 border-2 border-steel-3/30 border-t-steel-3 rounded-full animate-spin"></span>
				Carregando...
			</span>
		</div>
	{:else if erro}
		<div class="text-center py-16">
			<p class="text-red-500 text-sm">{erro}</p>
		</div>
	{:else if historicoFiltrado.length === 0}
		<div class="text-center py-16">
			<p class="text-steel-4 text-lg mb-2">
				{filtro ? 'Nenhum resultado encontrado.' : 'Nenhum carrossel salvo ainda.'}
			</p>
			<p class="text-steel-4/60 text-sm font-light">Salve carrosséis no Google Drive para vê-los aqui.</p>
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
			{#each historicoFiltrado as item}
				<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-5 hover:-translate-y-1 hover:shadow-md transition-all">
					<div class="flex items-start justify-between mb-3">
						<div class="flex gap-2 flex-wrap">
							{#if item.disciplina}
								<span class="px-2.5 py-0.5 rounded-full text-xs font-medium bg-steel-0 text-steel-3">
									{item.disciplina}
								</span>
							{/if}
							{#if item.tipo_carrossel}
								<span class="px-2.5 py-0.5 rounded-full text-xs font-medium {tipoBadge[item.tipo_carrossel] || tipoBadge.texto}">
									{item.tipo_carrossel}
								</span>
							{/if}
						</div>
						<button
							onclick={() => remover(item)}
							class="text-steel-4 hover:text-red-500 text-xs transition-all cursor-pointer"
						>remover</button>
					</div>
					<h3 class="font-semibold text-steel-6 text-sm mb-1 line-clamp-2">{item.titulo}</h3>
					{#if item.tecnologia_principal}
						<p class="text-xs text-steel-4 font-light mb-3">{item.tecnologia_principal}</p>
					{/if}
					<div class="flex items-center justify-between">
						<span class="text-xs text-steel-4/60">
							{item.total_slides || '?'} {(item.total_slides || 0) === 1 ? 'slide' : 'slides'}
							{#if item.criado_em}
								— {new Date(item.criado_em).toLocaleDateString('pt-BR')}
							{/if}
						</span>
						{#if item.google_drive_link}
							<a
								href={item.google_drive_link}
								target="_blank"
								rel="noopener"
								class="px-3 py-1.5 rounded-full text-xs font-medium bg-steel-3 text-white
									hover:bg-steel-4 transition-all cursor-pointer"
							>Abrir no Drive</a>
						{/if}
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
