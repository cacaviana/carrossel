<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { API_BASE } from '$lib/api';
	import { CopyService } from '$lib/services/CopyService';
	import { PipelineService } from '$lib/services/PipelineService';
	import { CopyDTO } from '$lib/dtos/CopyDTO';
	import Spinner from '$lib/components/ui/Spinner.svelte';
	import Skeleton from '$lib/components/ui/Skeleton.svelte';
	import Banner from '$lib/components/ui/Banner.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import PipelineBreadcrumb from '$lib/components/pipeline/PipelineBreadcrumb.svelte';
	import ApprovalBar from '$lib/components/pipeline/ApprovalBar.svelte';

	const pipelineId = $derived(page.params.id);

	let copy = $state<CopyDTO | null>(null);
	let versoes = $state<CopyDTO[]>([]);
	let versaoAtiva = $state(0);
	let headline = $state('');
	let narrativa = $state('');
	let cta = $state('');
	let slides = $state<{ titulo: string; conteudo: string; tipo: string }[]>([]);
	let slideExpandido = $state<number>(-1);
	let carregando = $state(true);
	let aprovando = $state(false);
	let erro = $state('');
	let feedbackRejeicao = $state('');
	let showRejectModal = $state(false);

	function selecionarVersao(idx: number) {
		versaoAtiva = idx;
		const v = versoes[idx];
		if (!v) return;
		copy = v;
		headline = v.headline;
		narrativa = v.narrativa;
		cta = v.cta;
		slides = v.sequencia_slides.map(s => ({ titulo: s.titulo, conteudo: s.conteudo, tipo: s.tipo }));
		slideExpandido = -1;
	}

	const API = API_BASE;

	onMount(async () => {
		try {
			const vs = await CopyService.buscarVersoes(pipelineId);
			versoes = vs.length > 0 ? vs : [await CopyService.buscarCopy(pipelineId)];
			selecionarVersao(0);
		} catch {
			erro = 'Erro ao carregar copy';
		} finally {
			carregando = false;
		}
	});

	async function aprovar() {
		aprovando = true;
		try {
			await fetch(`${API}/api/pipelines/${pipelineId}/etapas/copywriter/aprovar`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ saida_editada: JSON.stringify({ headline, narrativa, cta, slides }) })
			});
			PipelineService.executar(pipelineId).catch(() => {});
			goto(`/pipeline/${pipelineId}`);
		} catch {
			erro = 'Erro ao aprovar copy';
		} finally {
			aprovando = false;
		}
	}

	let regerando = $state(false);

	async function rejeitar() {
		aprovando = true;
		showRejectModal = false;
		regerando = true;
		try {
			await fetch(`${API}/api/pipelines/${pipelineId}/etapas/copywriter/rejeitar`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ motivo: feedbackRejeicao || 'Rejeitado pelo usuario' })
			});
			feedbackRejeicao = '';
			aprovando = false;

			// Executar e ESPERAR o copywriter terminar (polling até aguardando_aprovacao)
			await PipelineService.executar(pipelineId);
			let tentativas = 0;
			while (tentativas < 30) {
				await new Promise(r => setTimeout(r, 3000));
				try {
					const step = await fetch(`${API}/api/pipelines/${pipelineId}/etapas/copywriter`);
					if (step.ok) {
						const data = await step.json();
						if (data.status === 'aguardando_aprovacao') break;
					}
				} catch {}
				tentativas++;
			}

			const c = await CopyService.buscarCopy(pipelineId);
			copy = c;
			headline = c.headline; narrativa = c.narrativa; cta = c.cta;
			slides = c.sequencia_slides.map(s => ({ titulo: s.titulo, conteudo: s.conteudo, tipo: s.tipo }));
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro ao regerar copy';
		} finally {
			aprovando = false;
			regerando = false;
		}
	}
</script>

<svelte:head>
	<title>Revisar Copy (AP-2) — Content Factory</title>
</svelte:head>

<div class="animate-fade-up max-w-[900px] mx-auto">
	<PipelineBreadcrumb {pipelineId} etapaLabel="Revisar Copy (AP-2)" />

	<div class="flex items-center gap-3 mb-6">
		<h1 class="text-xl font-semibold text-text-primary">Revisar Copy</h1>
		<span class="px-2.5 py-0.5 rounded-full text-xs font-mono bg-amber/10 text-amber border border-amber/25">AP-2</span>
	</div>

	{#if regerando}
		<div class="flex flex-col items-center justify-center py-20 gap-4">
			<Spinner size="lg" />
			<p class="text-sm text-text-secondary">Regerando copy com seu feedback...</p>
			<p class="text-xs text-text-muted">Isso pode levar ~30 segundos</p>
		</div>
	{:else if carregando}
		<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
			{#each Array(3) as _}<Skeleton variant="block" height="h-40" />{/each}
		</div>
		<Skeleton variant="block" height="h-60" />
	{:else if copy}
		{#if erro}
			<div class="mb-4"><Banner type="error" ondismiss={() => erro = ''}>{erro}</Banner></div>
		{/if}

		<!-- Versoes (Anthropic vs OpenAI) -->
		{#if versoes.length > 1}
			<div class="mb-6">
				<p class="label-upper mb-3">Versao da copy</p>
				<div class="flex gap-2">
					{#each versoes as v, i}
						<button
							onclick={() => selecionarVersao(i)}
							class="px-4 py-2 rounded-full text-sm font-medium transition-all cursor-pointer
								{versaoAtiva === i
									? 'bg-purple text-bg-global'
									: 'text-text-secondary border border-border-default hover:border-purple/40'}"
						>
							{v.provider === 'openai' ? 'OpenAI' : 'Anthropic'}
							<span class="text-xs opacity-60 ml-1">({v.model})</span>
						</button>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Copy editavel -->
		<div class="bg-bg-card rounded-xl border border-border-default p-5 mb-6">
			<p class="label-upper mb-3">Copy</p>

			<div class="space-y-4">
				<div>
					<label for="headline" class="block text-xs text-text-muted mb-1.5">Headline</label>
					<input data-testid="campo-headline" id="headline" type="text" bind:value={headline}
						class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
							focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all" />
				</div>
				<div>
					<label for="narrativa" class="block text-xs text-text-muted mb-1.5">Narrativa</label>
					<textarea id="narrativa" bind:value={narrativa} rows="4"
						class="w-full px-4 py-3 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
							focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all resize-y"></textarea>
				</div>
				<div>
					<label for="cta" class="block text-xs text-text-muted mb-1.5">CTA</label>
					<input data-testid="campo-cta" id="cta" type="text" bind:value={cta}
						class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
							focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all" />
				</div>
			</div>
		</div>

		<!-- Sequencia de slides -->
		<div class="bg-bg-card rounded-xl border border-border-default p-5 mb-8">
			<p class="label-upper mb-3">Sequencia de slides ({slides.length}) <span class="text-text-muted font-normal">— clique para editar</span></p>
			<div class="space-y-2">
				{#each slides as slide, i}
					<div class="rounded-lg bg-bg-elevated border border-border-default overflow-hidden">
						<button
							onclick={() => slideExpandido = slideExpandido === i ? -1 : i}
							class="w-full flex items-center gap-2 p-3 cursor-pointer hover:bg-white/2 transition-all"
						>
							<span class="text-xs font-mono text-text-muted">{i + 1}</span>
							<span class="text-sm font-medium text-text-primary flex-1 text-left">{slide.titulo}</span>
							<span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-bg-card text-text-muted border border-border-default">{slide.tipo}</span>
							<svg class="w-4 h-4 text-text-muted transition-transform {slideExpandido === i ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
							</svg>
						</button>

						{#if slideExpandido === i}
							<div class="px-3 pb-3 border-t border-border-default pt-3 space-y-2">
								<div>
									<label class="block text-[10px] text-text-muted mb-1">Titulo</label>
									<input type="text" bind:value={slides[i].titulo}
										class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
											focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all" />
								</div>
								<div>
									<label class="block text-[10px] text-text-muted mb-1">Conteudo</label>
									<textarea bind:value={slides[i].conteudo} rows="4"
										class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
											focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all resize-y"></textarea>
								</div>
							</div>
						{:else}
							<div class="px-3 pb-3">
								<p class="text-xs text-text-secondary whitespace-pre-line line-clamp-2">{slide.conteudo}</p>
							</div>
						{/if}
					</div>
				{/each}
			</div>
		</div>

		<!-- Acoes -->
		<ApprovalBar {pipelineId} {aprovando} rejeitando={false} onaprovar={aprovar} onrejeitar={() => showRejectModal = true} />

	{/if}
</div>

<!-- Modal fora do animate-fade-up para nao quebrar position:fixed -->
<Modal open={showRejectModal} size="sm" title="Regerar copy?" onclose={() => showRejectModal = false}>
	<p class="text-sm text-text-secondary mb-3">Descreva o que quer diferente. O Copywriter vai regerar com seu feedback.</p>
	<textarea bind:value={feedbackRejeicao} placeholder="Ex: quero tom mais humano, menos lista de IA. Cada hábito deve ter o porquê e 2 estratégias práticas..." rows="4"
		class="w-full px-4 py-3 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
			focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all resize-y placeholder:text-text-muted" />
	{#snippet footer()}
		<button onclick={() => showRejectModal = false}
			class="px-4 py-2 rounded-full text-sm text-text-secondary hover:text-text-primary transition-all cursor-pointer">Cancelar</button>
		<button onclick={rejeitar} disabled={aprovando}
			class="px-4 py-2 rounded-full text-sm font-medium text-red bg-red/9 border border-red/15 hover:bg-red/15 transition-all cursor-pointer disabled:opacity-50">
			{aprovando ? 'Regerando...' : 'Regerar'}
		</button>
	{/snippet}
</Modal>
