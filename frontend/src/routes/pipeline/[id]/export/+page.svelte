<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { jsPDF } from 'jspdf';
	import { ExportService } from '$lib/services/ExportService';
	import { ImagemService } from '$lib/services/ImagemService';
	import { PipelineService } from '$lib/services/PipelineService';
	import { getDims } from '$lib/utils/dimensions';
	import { ScoreDTO, scoreCor } from '$lib/dtos/ScoreDTO';
	import Skeleton from '$lib/components/ui/Skeleton.svelte';
	import Banner from '$lib/components/ui/Banner.svelte';
	import SlideDotsNav from '$lib/components/ui/SlideDotsNav.svelte';
	import PipelineBreadcrumb from '$lib/components/pipeline/PipelineBreadcrumb.svelte';
	import { getToken } from '$lib/stores/auth.svelte';
	import { API_BASE } from '$lib/api';

	function authHeadersIfBackend(src: string): Record<string, string> | undefined {
		// Se a URL aponta para nossa API, incluir Bearer. Caso contrario (CDN externo), nao enviar header.
		if (src.startsWith(API_BASE) || src.startsWith('/api/')) {
			return { 'Authorization': `Bearer ${getToken()}` };
		}
		return undefined;
	}

	const pipelineId = $derived(page.params.id);

	let score = $state<ScoreDTO | null>(null);
	let legenda = $state('');
	let slides = $state<any[]>([]);
	let slideAtual = $state(0);
	let carregando = $state(true);
	let salvandoDrive = $state(false);
	let exportandoPdf = $state(false);
	let baixandoPngs = $state(false);
	let driveLink = $state('');
	let copiado = $state(false);
	let erro = $state('');
	let formato = $state('carrossel');

	function scoreBg(valor: number): string {
		if (valor >= 8) return 'bg-green/10';
		if (valor >= 6) return 'bg-amber/10';
		return 'bg-red/9';
	}

	async function copiarLegenda() {
		try {
			await navigator.clipboard.writeText(legenda);
			copiado = true;
			setTimeout(() => copiado = false, 3000);
		} catch {}
	}

	function getSlideUrl(slide: any): string | null {
		const v = slide?.variacoes?.[0];
		return v?.url || v?.base64 || null;
	}

	async function loadImageAsDataUrl(src: string): Promise<string> {
		if (src.startsWith('data:')) return src;
		const headers = authHeadersIfBackend(src);
		const resp = await fetch(src, headers ? { headers } : undefined);
		const blob = await resp.blob();
		return new Promise((resolve, reject) => {
			const reader = new FileReader();
			reader.onload = () => resolve(reader.result as string);
			reader.onerror = reject;
			reader.readAsDataURL(blob);
		});
	}

	async function exportarPdf() {
		exportandoPdf = true;
		erro = '';
		try {
			const dims = getDims(formato);
			const pxToMm = 0.2645833333;
			const wMm = dims.w * pxToMm;
			const hMm = dims.h * pxToMm;

			const pdf = new jsPDF({
				orientation: dims.w > dims.h ? 'landscape' : 'portrait',
				unit: 'mm',
				format: [wMm, hMm]
			});

			for (let i = 0; i < slides.length; i++) {
				const url = getSlideUrl(slides[i]);
				if (!url) continue;

				if (i > 0) pdf.addPage([wMm, hMm]);
				const dataUrl = await loadImageAsDataUrl(url);
				pdf.addImage(dataUrl, 'PNG', 0, 0, wMm, hMm);
			}

			pdf.save(`carrossel-${pipelineId}.pdf`);
		} catch (e) {
			console.error('Erro ao gerar PDF:', e);
			erro = 'Erro ao gerar PDF';
		} finally {
			exportandoPdf = false;
		}
	}

	async function downloadPngs() {
		baixandoPngs = true;
		erro = '';
		try {
			for (let i = 0; i < slides.length; i++) {
				const url = getSlideUrl(slides[i]);
				if (!url) continue;

				const dataUrl = await loadImageAsDataUrl(url);
				const a = document.createElement('a');
				a.href = dataUrl;
				a.download = `slide-${String(i + 1).padStart(2, '0')}.png`;
				document.body.appendChild(a);
				a.click();
				document.body.removeChild(a);

				// Small delay between downloads to avoid browser blocking
				if (i < slides.length - 1) await new Promise(r => setTimeout(r, 200));
			}
		} catch (e) {
			console.error('Erro ao baixar PNGs:', e);
			erro = 'Erro ao baixar PNGs';
		} finally {
			baixandoPngs = false;
		}
	}

	async function salvarDrive() {
		salvandoDrive = true;
		try {
			const result = await ExportService.salvarDrive(pipelineId);
			driveLink = result.link;
		} catch {
			erro = 'Erro ao salvar no Drive';
		} finally {
			salvandoDrive = false;
		}
	}

	onMount(async () => {
		try {
			const [s, l, img, pip] = await Promise.all([
				ExportService.buscarScore(pipelineId),
				ExportService.buscarLegenda(pipelineId),
				ImagemService.buscar(pipelineId),
				PipelineService.buscar(pipelineId)
			]);
			score = s;
			legenda = l;
			slides = img.slides;
			formato = pip.formato || 'carrossel';
		} catch {
			erro = 'Erro ao carregar dados de export';
		} finally {
			carregando = false;
		}
	});
</script>

<svelte:head>
	<title>Export — Content Factory</title>
</svelte:head>

<div class="animate-fade-up max-w-[1100px] mx-auto">
	<PipelineBreadcrumb {pipelineId} etapaLabel="Preview e Export" />

	{#if carregando}
		<div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
			<div class="lg:col-span-3"><Skeleton variant="block" height="h-96" /></div>
			<div class="lg:col-span-2 space-y-3">
				<Skeleton variant="block" height="h-48" />
				<Skeleton variant="block" height="h-32" />
			</div>
		</div>
	{:else}
		{#if erro}
			<div class="mb-4"><Banner type="error">{erro}</Banner></div>
		{/if}

		{#if driveLink}
			<div class="mb-4">
				<Banner type="success" dismissible={false}>
					Salvo no Drive!
					<a href={driveLink} target="_blank" rel="noopener" class="underline ml-1">Abrir pasta</a>
				</Banner>
			</div>
		{/if}

		{#if score && !score.isAprovado}
			<div class="mb-4">
				<Banner type="warning" dismissible={false}>
					O Content Critic recomenda ajustes. Score: {score.final_score.toFixed(1)}/10. Dimensoes abaixo de 7 precisam de atencao.
				</Banner>
			</div>
		{/if}

		<div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
			<!-- Preview slides -->
			<div class="lg:col-span-3">
				<div class="bg-bg-code rounded-xl overflow-hidden">
					{#if slides.length > 0}
						{@const currentSlide = slides[slideAtual]}
						<div class="flex items-center justify-center relative" style="aspect-ratio: {getDims(formato).cssRatio}">
							{#if currentSlide?.variacoes?.[0]?.url || currentSlide?.variacoes?.[0]?.base64}
								<img src={currentSlide.variacoes[0].url || currentSlide.variacoes[0].base64} alt="Slide {slideAtual + 1}" class="w-full h-full object-contain" />
							{:else}
								<span class="text-text-muted">Sem preview</span>
							{/if}

							<!-- Nav arrows -->
							{#if slideAtual > 0}
								<button onclick={() => slideAtual--}
									class="absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/50 flex items-center justify-center text-white hover:bg-black/70 transition-all cursor-pointer">
									<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
									</svg>
								</button>
							{/if}
							{#if slideAtual < slides.length - 1}
								<button onclick={() => slideAtual++}
									class="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/50 flex items-center justify-center text-white hover:bg-black/70 transition-all cursor-pointer">
									<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
									</svg>
								</button>
							{/if}

							<!-- Counter -->
							<span class="absolute bottom-3 right-3 px-2 py-1 rounded-full bg-black/50 text-xs font-mono text-white/70">
								{String(slideAtual + 1).padStart(2, '0')} / {String(slides.length).padStart(2, '0')}
							</span>
						</div>

						<!-- Dots -->
						<div class="flex justify-center py-3">
							<SlideDotsNav total={slides.length} current={slideAtual} onSelect={(i) => slideAtual = i} inactiveClass="bg-text-muted/40 hover:bg-text-muted" />
						</div>
					{/if}
				</div>
			</div>

			<!-- Score + Acoes -->
			<div class="lg:col-span-2 space-y-4">
				{#if score}
					<!-- Score geral -->
					<div class="bg-bg-card rounded-xl border border-border-default p-5">
						<div class="flex items-center justify-between mb-4">
							<p class="label-upper">Score do Content Critic</p>
							<span class="px-3 py-1 rounded-full text-xs font-mono
								{score.isAprovado ? 'bg-green/10 text-green border border-green/25' : 'bg-amber/10 text-amber border border-amber/25'}">
								{score.isAprovado ? 'Aprovado' : 'Recomenda Ajustes'}
							</span>
						</div>

						<!-- Score final grande -->
						<div class="text-center mb-4">
							<span class="text-4xl font-bold font-mono {scoreCor(score.final_score)}">{score.final_score.toFixed(1)}</span>
							<span class="text-text-muted text-sm">/10</span>
						</div>

						<!-- Grid de dimensoes -->
						<div class="grid grid-cols-2 gap-2">
							{#each score.dimensoes.slice(0, -1) as dim}
								<div class="p-3 rounded-lg {scoreBg(dim.valor)} text-center">
									<span class="block text-xl font-bold font-mono {scoreCor(dim.valor)}">{dim.valor.toFixed(1)}</span>
									<span class="block text-[10px] font-semibold uppercase tracking-wide text-text-muted mt-0.5">{dim.label}</span>
								</div>
							{/each}
						</div>
					</div>
				{/if}

				<!-- Legenda -->
				{#if legenda}
					<div class="bg-bg-card rounded-xl border border-border-default p-5">
						<div class="flex items-center justify-between mb-3">
							<p class="label-upper">Legenda LinkedIn</p>
							<button onclick={copiarLegenda}
								class="px-3 py-1 rounded-full text-xs font-medium text-purple border border-purple/20 hover:bg-purple/8 transition-all cursor-pointer">
								{copiado ? 'Copiada!' : 'Copiar'}
							</button>
						</div>
						<p class="text-xs text-text-secondary whitespace-pre-line leading-relaxed max-h-40 overflow-y-auto">{legenda}</p>
					</div>
				{/if}

				<!-- Botoes de Export -->
				<div class="space-y-2">
					<button data-testid="btn-exportar-pdf" onclick={exportarPdf} disabled={exportandoPdf}
						class="w-full py-3 rounded-full text-sm font-medium text-bg-global bg-purple hover:opacity-90 transition-all cursor-pointer disabled:opacity-50">
						{exportandoPdf ? 'Gerando PDF...' : 'Exportar PDF'}
					</button>
					<button data-testid="btn-download-pngs" onclick={downloadPngs} disabled={baixandoPngs}
						class="w-full py-3 rounded-full text-sm font-medium text-purple border border-purple/20 hover:bg-purple/8 transition-all cursor-pointer disabled:opacity-50">
						{baixandoPngs ? 'Baixando PNGs...' : 'Download PNGs'}
					</button>
					<button data-testid="btn-salvar-drive" onclick={salvarDrive} disabled={salvandoDrive}
						class="w-full py-3 rounded-full text-sm font-medium text-bg-global bg-green hover:opacity-90 transition-all cursor-pointer disabled:opacity-50">
						{salvandoDrive ? 'Salvando no Drive...' : 'Salvar no Drive'}
					</button>
					<a href="/" class="block text-center py-3 rounded-full text-sm text-text-secondary hover:text-text-primary transition-all no-underline cursor-pointer">
						Novo Conteudo
					</a>
				</div>
			</div>
		</div>
	{/if}
</div>
