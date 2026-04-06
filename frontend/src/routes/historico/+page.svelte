<script lang="ts">
	import { onMount } from 'svelte';
	import { HistoricoService } from '$lib/services/HistoricoService';
	import { HistoricoItemDTO } from '$lib/dtos/HistoricoItemDTO';
	import Spinner from '$lib/components/ui/Spinner.svelte';
	import Banner from '$lib/components/ui/Banner.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import { scoreCor } from '$lib/dtos/ScoreDTO';

	let historico = $state<HistoricoItemDTO[]>([]);
	let filtroTexto = $state('');
	let filtroFormato = $state('');
	let filtroStatus = $state('');
	let carregando = $state(true);
	let erro = $state('');
	let showRemoveModal = $state(false);
	let itemToRemove = $state<HistoricoItemDTO | null>(null);

	const historicoFiltrado = $derived(
		historico.filter(h => {
			if (filtroTexto && !h.titulo.toLowerCase().includes(filtroTexto.toLowerCase()) &&
				!h.disciplina.toLowerCase().includes(filtroTexto.toLowerCase()) &&
				!h.tecnologia_principal.toLowerCase().includes(filtroTexto.toLowerCase())) return false;
			if (filtroFormato && h.formato !== filtroFormato) return false;
			if (filtroStatus && h.status !== filtroStatus) return false;
			return true;
		})
	);

	function statusBadge(status: string): string {
		switch (status) {
			case 'completo': return 'bg-green/10 text-green border-green/25';
			case 'em_andamento': return 'bg-purple/8 text-purple border-purple/20';
			case 'erro': return 'bg-red/9 text-red border-red/15';
			case 'cancelado': return 'bg-bg-elevated text-text-muted border-border-default';
			default: return 'bg-bg-elevated text-text-muted border-border-default';
		}
	}

	async function confirmarRemover() {
		if (!itemToRemove) return;
		try {
			await HistoricoService.remover(itemToRemove.id);
			historico = historico.filter(h => h.id !== itemToRemove!.id);
		} catch {}
		showRemoveModal = false;
		itemToRemove = null;
	}

	onMount(async () => {
		try {
			historico = await HistoricoService.listar();
		} catch {
			erro = 'Nao foi possivel carregar o historico.';
		} finally {
			carregando = false;
		}
	});
</script>

<svelte:head>
	<title>Historico — Content Factory</title>
</svelte:head>

<div class="animate-fade-up">
	<div class="flex items-center justify-between mb-6">
		<div>
			<h1 class="text-2xl font-light text-text-primary mb-1">Historico</h1>
			<p class="text-sm text-text-secondary">{historicoFiltrado.length} resultado{historicoFiltrado.length !== 1 ? 's' : ''}</p>
		</div>
	</div>

	<!-- Filtros -->
	<div class="flex flex-wrap gap-3 mb-6">
		<input data-testid="campo-busca-historico" type="text" bind:value={filtroTexto} placeholder="Buscar por titulo..."
			class="flex-1 min-w-[200px] max-w-sm px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
				focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all placeholder:text-text-muted" />
		<select bind:value={filtroFormato}
			class="px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
				focus:border-purple outline-none cursor-pointer">
			<option value="">Todos os formatos</option>
			<option value="carrossel">Carrossel</option>
			<option value="post_unico">Post Unico</option>
			<option value="thumbnail_youtube">Thumbnail YouTube</option>
		</select>
		<select bind:value={filtroStatus}
			class="px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
				focus:border-purple outline-none cursor-pointer">
			<option value="">Todos os status</option>
			<option value="completo">Completo</option>
			<option value="em_andamento">Em andamento</option>
			<option value="erro">Erro</option>
			<option value="cancelado">Cancelado</option>
		</select>
	</div>

	{#if erro}
		<Banner type="error">{erro}</Banner>
	{:else if carregando}
		<div class="text-center py-16">
			<Spinner size="lg" />
			<p class="text-text-secondary mt-3 text-sm">Carregando historico...</p>
		</div>
	{:else if historicoFiltrado.length === 0}
		<div class="text-center py-16">
			<p class="text-text-secondary text-lg mb-2">
				{filtroTexto || filtroFormato || filtroStatus ? 'Nenhum resultado encontrado.' : 'Nenhum conteudo salvo ainda.'}
			</p>
			{#if filtroTexto || filtroFormato || filtroStatus}
				<button onclick={() => { filtroTexto = ''; filtroFormato = ''; filtroStatus = ''; }}
					class="text-sm text-purple hover:text-purple-soft cursor-pointer">Limpar filtros</button>
			{:else}
				<p class="text-text-muted text-sm mb-4">Crie conteudo e salve no Google Drive para ve-lo aqui.</p>
				<a href="/" class="inline-flex px-6 py-3 rounded-full bg-purple text-bg-global font-medium text-sm no-underline hover:opacity-90 transition-all">Criar Conteudo</a>
			{/if}
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
			{#each historicoFiltrado as item}
				<div class="bg-bg-card rounded-xl border border-border-default p-5 hover:-translate-y-1 hover:shadow-md hover:border-purple/30 transition-all">
					<!-- Badges -->
					<div class="flex items-center gap-2 mb-3 flex-wrap">
						<span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-purple/8 text-purple border border-purple/20">{item.formato || 'carrossel'}</span>
						<span class="px-2 py-0.5 rounded-full text-[10px] font-mono border {statusBadge(item.status)}">{item.status}</span>
						{#if !item.isPipelineV3}
							<span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-amber/10 text-amber border border-amber/25">legado</span>
						{/if}
					</div>

					<!-- Titulo -->
					<h3 class="text-sm font-medium text-text-primary mb-1 line-clamp-2">{item.titulo}</h3>
					{#if item.disciplina}
						<p class="text-xs text-text-secondary mb-2">{item.disciplina} — {item.tecnologia_principal}</p>
					{/if}

					<!-- Score + Data -->
					<div class="flex items-center justify-between mt-3">
						<span class="text-xs text-text-muted font-mono">
							{item.total_slides} slide{item.total_slides !== 1 ? 's' : ''}
							{#if item.criado_em} — {item.dataFormatada}{/if}
						</span>
						{#if item.temScore && item.final_score !== null}
							<span class="text-lg font-bold font-mono {scoreCor(item.final_score)}">{item.final_score.toFixed(1)}</span>
						{/if}
					</div>

					<!-- Actions -->
					<div class="flex items-center gap-2 mt-3 pt-3 border-t border-border-default">
						{#if item.temDriveLink}
							<a href={item.google_drive_link} target="_blank" rel="noopener"
								class="text-xs text-purple hover:text-purple-soft no-underline cursor-pointer">Drive</a>
						{/if}
						{#if item.isPipelineV3}
							<a href="/pipeline/{item.pipeline_id}" class="text-xs text-purple hover:text-purple-soft no-underline cursor-pointer">Reabrir</a>
						{/if}
						<button onclick={() => { itemToRemove = item; showRemoveModal = true; }}
							class="text-xs text-text-muted hover:text-red transition-colors cursor-pointer ml-auto">Remover</button>
					</div>
				</div>
			{/each}
		</div>
	{/if}

	<!-- Remove Modal -->
	<Modal open={showRemoveModal} size="sm" title="Remover conteudo?" onclose={() => showRemoveModal = false}>
		<p class="text-sm text-text-secondary">A acao nao pode ser desfeita.</p>
		{#snippet footer()}
			<button onclick={() => showRemoveModal = false}
				class="px-4 py-2 rounded-full text-sm text-text-secondary cursor-pointer">Cancelar</button>
			<button onclick={confirmarRemover}
				class="px-4 py-2 rounded-full text-sm font-medium text-red bg-red/9 border border-red/15 hover:bg-red/15 transition-all cursor-pointer">Remover</button>
		{/snippet}
	</Modal>
</div>
