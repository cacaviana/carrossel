<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { AnuncioService } from '$lib/services/AnuncioService';
	import { AnuncioDTO } from '$lib/dtos/AnuncioDTO';
	import { ListarAnunciosFiltroDTO } from '$lib/dtos/ListarAnunciosFiltroDTO';
	import { getFiltro, setFiltro } from '$lib/stores/anuncio.svelte';
	import AnuncioFiltros from '$lib/components/anuncio/AnuncioFiltros.svelte';
	import AnuncioCard from '$lib/components/anuncio/AnuncioCard.svelte';
	import AnuncioExcluirModal from '$lib/components/anuncio/AnuncioExcluirModal.svelte';
	import PageHeader from '$lib/components/ui/PageHeader.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import Banner from '$lib/components/ui/Banner.svelte';

	let anuncios = $state<AnuncioDTO[]>([]);
	let carregando = $state(true);
	let erro = $state('');
	let anuncioParaExcluir = $state<AnuncioDTO | null>(null);
	let excluindo = $state(false);
	let erroExcluir = $state('');
	let toast = $state('');

	// Refresh automatico: so fica ativo quando ha algum anuncio em_andamento na pagina.
	// Backend MVP usa polling (FA-003). Intervalo de 3s pra lista (mais lenta que detalhe).
	let intervalId: ReturnType<typeof setInterval> | null = null;

	async function carregar(mostrarLoading = true) {
		try {
			if (mostrarLoading) carregando = true;
			erro = '';
			anuncios = await AnuncioService.listar(getFiltro());
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro ao carregar';
		} finally {
			carregando = false;
		}
	}

	function temEmAndamento(): boolean {
		return anuncios.some(a => a.isEmAndamento);
	}

	onMount(() => {
		carregar();
		intervalId = setInterval(() => {
			if (temEmAndamento()) carregar(false);
		}, 3000);
		return () => { if (intervalId) clearInterval(intervalId); };
	});

	function handleFiltroChange(novo: ListarAnunciosFiltroDTO) {
		setFiltro(novo);
		carregar();
	}

	// Anuncio reusa o fluxo universal (igual post_unico):
	// - concluido -> /editor?pipeline=X&brand=Y (ver/editar resultado)
	// - em_andamento / rascunho / erro -> /pipeline/[id] (acompanhar / AP)
	function rotaAnuncio(anuncio: AnuncioDTO): string {
		if (!anuncio.pipeline_id) return '/anuncios';
		if (anuncio.isConcluido) return `/editor?pipeline=${anuncio.pipeline_id}`;
		return `/pipeline/${anuncio.pipeline_id}`;
	}

	function handleClick(id: string) {
		const anuncio = anuncios.find(a => a.id === id);
		if (anuncio) goto(rotaAnuncio(anuncio));
	}

	function handleEditar(id: string) {
		const anuncio = anuncios.find(a => a.id === id);
		if (anuncio) goto(rotaAnuncio(anuncio));
	}

	function handleExcluir(anuncio: AnuncioDTO) {
		anuncioParaExcluir = anuncio;
		erroExcluir = '';
	}

	async function confirmarExclusao() {
		if (!anuncioParaExcluir) return;
		try {
			excluindo = true;
			erroExcluir = '';
			await AnuncioService.excluir(anuncioParaExcluir.id);
			toast = `Anuncio "${anuncioParaExcluir.titulo}" excluido`;
			anuncioParaExcluir = null;
			await carregar();
			setTimeout(() => (toast = ''), 3000);
		} catch (e) {
			erroExcluir = e instanceof Error ? e.message : 'Erro ao excluir';
		} finally {
			excluindo = false;
		}
	}

	function handleAbrirDrive(url: string) {
		window.open(url, '_blank', 'noopener');
	}

	function limparFiltros() {
		setFiltro(new ListarAnunciosFiltroDTO({}));
		carregar();
	}

	const filtroAtual = $derived(getFiltro());
	const temFiltroAtivo = $derived(filtroAtual.temFiltroAtivo);
</script>

<svelte:head>
	<title>Anuncios - Content Factory</title>
</svelte:head>

<!-- Header -->
<div class="flex items-start justify-between flex-wrap gap-4 mb-6">
	<div>
		<h1 class="text-2xl font-light text-text-primary mb-1">Anuncios</h1>
		<p class="text-sm text-text-secondary">Historico de anuncios 1080x1350 com copy de venda — IT Valley School</p>
	</div>
	<Button variant="primary" size="md" onclick={() => goto('/?formato=anuncio')}>
		+ Novo Anuncio
	</Button>
</div>

<!-- Filtros -->
<div class="mb-4">
	<AnuncioFiltros filtro={filtroAtual} onChange={handleFiltroChange} />
</div>

<!-- Toast -->
{#if toast}
	<div class="mb-4">
		<Banner type="success">{toast}</Banner>
	</div>
{/if}

<!-- Erro -->
{#if erro}
	<div class="mb-4">
		<Banner type="error">
			{erro}
			<button class="ml-2 underline" onclick={() => carregar()}>Tentar novamente</button>
		</Banner>
	</div>
{/if}

<!-- Contador -->
{#if !carregando && !erro}
	<p class="text-xs font-mono text-text-muted mb-4">
		{anuncios.length} {anuncios.length === 1 ? 'anuncio encontrado' : 'anuncios encontrados'}
	</p>
{/if}

<!-- Conteudo -->
{#if carregando}
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
		{#each Array(6) as _, i (i)}
			<div class="bg-bg-card rounded-xl border border-border-default overflow-hidden">
				<div class="p-4 flex items-center gap-2">
					<div class="h-4 w-16 rounded-full bg-bg-elevated animate-pulse"></div>
					<div class="h-4 w-20 rounded-full bg-bg-elevated animate-pulse"></div>
				</div>
				<div class="mx-4 mb-3 aspect-[4/5] rounded-lg bg-bg-elevated animate-pulse"></div>
				<div class="px-4 pb-3 space-y-2">
					<div class="h-4 w-3/4 rounded bg-bg-elevated animate-pulse"></div>
					<div class="h-3 w-full rounded bg-bg-elevated animate-pulse"></div>
				</div>
			</div>
		{/each}
	</div>
{:else if anuncios.length === 0 && !temFiltroAtivo}
	<!-- Vazio sem filtro -->
	<div class="py-16 text-center">
		<svg class="w-16 h-16 mx-auto text-text-muted/30 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
		</svg>
		<h2 class="text-lg font-medium text-text-primary mb-1">Nenhum anuncio criado ainda.</h2>
		<p class="text-sm text-text-secondary mb-6">Crie seu primeiro anuncio com copy de venda</p>
		<Button variant="primary" size="lg" onclick={() => goto('/?formato=anuncio')}>
			Criar primeiro anuncio
		</Button>
	</div>
{:else if anuncios.length === 0}
	<!-- Vazio com filtro -->
	<div class="py-16 text-center">
		<svg class="w-12 h-12 mx-auto text-text-muted/30 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
		</svg>
		<p class="text-sm text-text-secondary mb-4">Nenhum anuncio encontrado para esses filtros.</p>
		<Button variant="outline" size="md" onclick={limparFiltros}>
			Limpar filtros
		</Button>
	</div>
{:else}
	<!-- Grid de anuncios -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
		{#each anuncios as anuncio (anuncio.id)}
			<AnuncioCard
				{anuncio}
				onClick={handleClick}
				onEditar={handleEditar}
				onExcluir={handleExcluir}
				onAbrirDrive={handleAbrirDrive}
			/>
		{/each}
	</div>
{/if}

<!-- Modal excluir -->
<AnuncioExcluirModal
	anuncio={anuncioParaExcluir}
	aberto={anuncioParaExcluir !== null}
	{excluindo}
	erro={erroExcluir}
	onConfirmar={confirmarExclusao}
	onCancelar={() => { anuncioParaExcluir = null; erroExcluir = ''; }}
/>
