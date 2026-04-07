<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { API_BASE } from '$lib/api';
	import { VisualService } from '$lib/services/VisualService';
	import { PipelineService } from '$lib/services/PipelineService';
	import { PromptVisualDTO } from '$lib/dtos/PromptVisualDTO';
	import Skeleton from '$lib/components/ui/Skeleton.svelte';
	import Banner from '$lib/components/ui/Banner.svelte';
	import PipelineBreadcrumb from '$lib/components/pipeline/PipelineBreadcrumb.svelte';
	import ApprovalBar from '$lib/components/pipeline/ApprovalBar.svelte';

	const pipelineId = $derived(page.params.id);

	let promptVisual = $state<PromptVisualDTO | null>(null);
	let prompts = $state<any[]>([]);
	let preferencias = $state<any[]>([]);
	let brandPalette = $state<any>(null);
	let carregando = $state(true);
	let aprovando = $state(false);
	let erro = $state('');
	let expandedSlide = $state<number>(0);
	let showPreferencias = $state(false);

	onMount(async () => {
		try {
			const API = API_BASE;

			// Carregar pipeline pra pegar brand_slug
			const pipeline = await PipelineService.buscar(pipelineId);
			const brandSlug = pipeline.brand_slug;

			const [pv, prefs] = await Promise.all([
				VisualService.buscar(pipelineId),
				VisualService.buscarPreferencias(),
			]);
			promptVisual = pv;
			prompts = pv.prompts.map(p => ({ ...p }));
			preferencias = prefs;

			// Carregar brand palette da marca do pipeline (ou fallback)
			if (brandSlug) {
				try {
					const res = await fetch(`${API}/api/brands/${brandSlug}`);
					if (res.ok) brandPalette = await res.json();
				} catch {}
			}
			if (!brandPalette) {
				brandPalette = await VisualService.buscarBrandPalette();
			}
		} catch {
			erro = 'Erro ao carregar prompts visuais';
		} finally {
			carregando = false;
		}
	});

	async function aprovar() {
		aprovando = true;
		try {
			await VisualService.aprovar(pipelineId, prompts);
			PipelineService.executar(pipelineId).catch(() => {});
			goto(`/pipeline/${pipelineId}`);
		} catch { erro = 'Erro ao aprovar prompts visuais'; }
		finally { aprovando = false; }
	}

	async function rejeitar() {
		aprovando = true;
		try {
			await VisualService.rejeitar(pipelineId, '');
			carregando = true;

			await PipelineService.executar(pipelineId);
			let tentativas = 0;
			while (tentativas < 30) {
				await new Promise(r => setTimeout(r, 3000));
				try {
					const res = await fetch(`${API}/api/pipelines/${pipelineId}/etapas/art_director`);
					if (res.ok) {
						const data = await res.json();
						if (data.status === 'aguardando_aprovacao') break;
					}
				} catch {}
				tentativas++;
			}

			promptVisual = await VisualService.buscar(pipelineId);
			prompts = promptVisual.prompts.map(p => ({ ...p }));
		} catch { erro = 'Erro ao rejeitar'; }
		finally { aprovando = false; carregando = false; }
	}
</script>

<svelte:head>
	<title>Prompts Visuais (AP-3) — Content Factory</title>
</svelte:head>

<div class="animate-fade-up max-w-[1000px] mx-auto">
	<PipelineBreadcrumb {pipelineId} etapaLabel="Prompts Visuais (AP-3)" />

	<div class="flex items-center gap-3 mb-6">
		<h1 class="text-xl font-semibold text-text-primary">Revisar Prompts Visuais</h1>
		<span class="px-2.5 py-0.5 rounded-full text-xs font-mono bg-amber/10 text-amber border border-amber/25">AP-3</span>
	</div>

	{#if carregando}
		<div class="space-y-3">
			{#each Array(5) as _}<Skeleton variant="block" height="h-16" />{/each}
		</div>
	{:else}
		{#if erro}
			<div class="mb-4"><Banner type="error" ondismiss={() => erro = ''}>{erro}</Banner></div>
		{/if}

		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Accordion de prompts -->
			<div class="lg:col-span-2 space-y-2">
				{#each prompts as prompt, i}
					<div class="bg-bg-card rounded-xl border border-border-default overflow-hidden">
						<button
							onclick={() => expandedSlide = expandedSlide === i ? -1 : i}
							class="w-full flex items-center justify-between p-4 cursor-pointer hover:bg-white/2 transition-all"
						>
							<div class="flex items-center gap-3">
								<span class="text-sm font-medium text-text-primary">Slide {prompt.slide_index + 1}: {prompt.titulo}</span>
								<span class="px-2 py-0.5 rounded-full text-[10px] font-mono
									{prompt.modelo_sugerido === 'pro' ? 'bg-purple/8 text-purple border border-purple/20' : 'bg-green/10 text-green border border-green/25'}">
									{prompt.modelo_sugerido}
								</span>
							</div>
							<svg class="w-4 h-4 text-text-muted transition-transform {expandedSlide === i ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
							</svg>
						</button>

						{#if expandedSlide === i}
							<div class="px-4 pb-4 border-t border-border-default pt-3">
								<textarea
									bind:value={prompts[i].prompt_imagem}
									rows="5"
									class="w-full px-3 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
										focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all resize-y font-light"
								></textarea>
								<p class="text-[10px] text-text-muted mt-1">{prompt.prompt_imagem.length} caracteres (min: 50)</p>
							</div>
						{/if}
					</div>
				{/each}
			</div>

			<!-- Sidebar: Brand Palette + Visual Memory -->
			<div class="space-y-4">
				{#if brandPalette}
					<div class="bg-bg-card rounded-xl border border-border-default p-5">
						<p class="label-upper mb-3">Brand Palette</p>
						<div class="flex gap-2 mb-3">
							{#each Object.entries(brandPalette.cores) as [, cor]}
								<div class="w-8 h-8 rounded-full border border-border-default" style="background-color: {cor}"></div>
							{/each}
						</div>
						<p class="text-xs text-text-secondary">Fonte: {brandPalette.fonte}</p>
						<p class="text-xs text-text-muted mt-1">Estilo: {brandPalette.estilo}</p>
						<div class="mt-2">
							{#each brandPalette.elementos_obrigatorios as elem}
								<span class="inline-block px-2 py-0.5 rounded-full text-[10px] font-mono bg-bg-elevated text-text-muted border border-border-default mr-1 mb-1">{elem}</span>
							{/each}
						</div>
					</div>
				{/if}

				<div class="bg-bg-card rounded-xl border border-border-default p-5">
					<button onclick={() => showPreferencias = !showPreferencias} class="flex items-center justify-between w-full cursor-pointer">
						<p class="label-upper">Visual Memory ({preferencias.length})</p>
						<svg class="w-4 h-4 text-text-muted transition-transform {showPreferencias ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
						</svg>
					</button>
					{#if showPreferencias}
						<div class="mt-3 space-y-2">
							{#each preferencias as pref}
								<div class="flex items-start gap-2 p-2 rounded-lg bg-bg-elevated">
									<span class="shrink-0 px-1.5 py-0.5 rounded-full text-[10px] font-mono
										{pref.aprovado ? 'bg-green/10 text-green' : 'bg-red/9 text-red'}">
										{pref.aprovado ? 'OK' : 'NAO'}
									</span>
									<div>
										<p class="text-xs text-text-primary">{pref.estilo}</p>
										<p class="text-[10px] text-text-muted">{pref.contexto}</p>
									</div>
								</div>
							{/each}
						</div>
					{/if}
				</div>
			</div>
		</div>

		<!-- Acoes -->
		<!-- Acoes -->
		<ApprovalBar {pipelineId} {aprovando} rejeitando={false} onaprovar={aprovar} onrejeitar={rejeitar} aprovarLabel="Aprovar e Gerar Imagens" aprovandoLabel="Enviando..." className="mt-8" />
	{/if}
</div>
