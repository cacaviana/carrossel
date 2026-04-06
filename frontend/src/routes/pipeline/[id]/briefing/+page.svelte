<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { BriefingService } from '$lib/services/BriefingService';
	import { PipelineService } from '$lib/services/PipelineService';
	import { BriefingDTO } from '$lib/dtos/BriefingDTO';
	import Spinner from '$lib/components/ui/Spinner.svelte';
	import Skeleton from '$lib/components/ui/Skeleton.svelte';
	import Banner from '$lib/components/ui/Banner.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import PipelineBreadcrumb from '$lib/components/pipeline/PipelineBreadcrumb.svelte';
	import ApprovalBar from '$lib/components/pipeline/ApprovalBar.svelte';

	const pipelineId = $derived(page.params.id);

	let briefing = $state<BriefingDTO | null>(null);
	let briefingTexto = $state('');
	let carregando = $state(true);
	let aprovando = $state(false);
	let erro = $state('');
	let editado = $state(false);
	let showRejectModal = $state(false);
	let feedbackRejeicao = $state('');

	onMount(async () => {
		try {
			briefing = await BriefingService.buscar(pipelineId);
			briefingTexto = briefing.briefing_completo;
		} catch {
			erro = 'Erro ao carregar briefing';
		} finally {
			carregando = false;
		}
	});

	async function aprovar() {
		aprovando = true;
		try {
			await BriefingService.aprovar(pipelineId, briefingTexto);
			// Disparar proxima etapa sem esperar (o polling da pagina pipeline cuida)
			PipelineService.executar(pipelineId).catch(() => {});
			goto(`/pipeline/${pipelineId}`);
		} catch {
			erro = 'Erro ao aprovar briefing';
		} finally {
			aprovando = false;
		}
	}

	async function rejeitar() {
		aprovando = true;
		try {
			await BriefingService.rejeitar(pipelineId, feedbackRejeicao);
			showRejectModal = false;
			// Reload
			carregando = true;
			briefing = await BriefingService.buscar(pipelineId);
			briefingTexto = briefing.briefing_completo;
			editado = false;
		} catch {
			erro = 'Erro ao rejeitar briefing';
		} finally {
			aprovando = false;
			carregando = false;
		}
	}
</script>

<svelte:head>
	<title>Briefing (AP-1) — Content Factory</title>
</svelte:head>

<div class="animate-fade-up max-w-[1000px] mx-auto">
	<!-- Breadcrumb -->
	<PipelineBreadcrumb {pipelineId} etapaLabel="Briefing (AP-1)" />

	<div class="flex items-center gap-3 mb-6">
		<h1 class="text-xl font-semibold text-text-primary">Revisar Briefing</h1>
		<span class="px-2.5 py-0.5 rounded-full text-xs font-mono bg-amber/10 text-amber border border-amber/25">Aguardando Aprovacao</span>
		{#if editado}
			<span class="px-2.5 py-0.5 rounded-full text-xs font-mono bg-purple/8 text-purple border border-purple/20">Editado</span>
		{/if}
	</div>

	{#if carregando}
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<div class="lg:col-span-1"><Skeleton variant="block" height="h-48" /></div>
			<div class="lg:col-span-2"><Skeleton variant="block" height="h-80" /></div>
		</div>
	{:else if briefing}
		{#if erro}
			<div class="mb-4"><Banner type="error">{erro}</Banner></div>
		{/if}

		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			<!-- Coluna contexto -->
			<div class="space-y-4">
				<div class="bg-bg-card rounded-xl border border-border-default p-5">
					<p class="label-upper mb-3">Contexto</p>
					<div class="space-y-3">
						<div>
							<p class="text-xs text-text-muted mb-1">Tema original</p>
							<p class="text-sm text-text-secondary">{briefing.tema_original}</p>
						</div>
						<div>
							<p class="text-xs text-text-muted mb-1">Formato alvo</p>
							<p class="text-sm text-text-secondary">{briefing.formato_alvo}</p>
						</div>
					</div>
				</div>

				{#if briefing.tendencias_usadas.length > 0}
					<div class="bg-bg-card rounded-xl border border-border-default p-5">
						<p class="label-upper mb-3">Tendencias detectadas</p>
						<div class="space-y-2">
							{#each briefing.tendencias_usadas as t}
								<span class="inline-block px-2.5 py-1 rounded-full text-xs bg-bg-elevated text-text-secondary border border-border-default mr-1 mb-1">{t}</span>
							{/each}
						</div>
					</div>
				{/if}
			</div>

			<!-- Coluna briefing editavel -->
			<div class="lg:col-span-2">
				<div class="bg-bg-card rounded-xl border border-border-default p-5">
					<p class="label-upper mb-3">Briefing</p>
					<textarea
						data-testid="campo-briefing"
						bind:value={briefingTexto}
						oninput={() => editado = briefingTexto !== briefing?.briefing_completo}
						class="w-full min-h-[300px] px-4 py-3 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
							focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all resize-y font-light leading-relaxed"
					></textarea>
				</div>

				{#if briefing.temFunil}
					<div class="mt-4 bg-bg-card rounded-xl border border-border-default p-5">
						<p class="label-upper mb-3">Pecas do funil ({briefing.totalPecas})</p>
						<div class="space-y-2">
							{#each briefing.pecas_funil as peca}
								<div class="flex items-center gap-2 p-3 rounded-lg bg-bg-elevated border border-border-default">
									<span class="text-sm text-text-primary flex-1">{peca.titulo}</span>
									<span class="px-2 py-0.5 rounded-full text-[10px] font-mono
										{peca.etapa_funil === 'topo' ? 'bg-purple/8 text-purple' :
										 peca.etapa_funil === 'meio' ? 'bg-green/10 text-green' :
										 'bg-amber/10 text-amber'}">{peca.etapa_funil}</span>
									<span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-bg-card text-text-muted border border-border-default">{peca.formato}</span>
								</div>
							{/each}
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Acoes -->
		<ApprovalBar {pipelineId} {aprovando} rejeitando={false} onaprovar={aprovar} onrejeitar={() => showRejectModal = true} className="mt-8" />

		<!-- Reject Modal -->
		<Modal open={showRejectModal} size="sm" title="Rejeitar briefing?" onclose={() => showRejectModal = false}>
			<p class="text-sm text-text-secondary mb-3">O Strategist sera re-executado com seu feedback.</p>
			<textarea bind:value={feedbackRejeicao} placeholder="Feedback para o Strategist (opcional)..." rows="3"
				class="w-full px-4 py-3 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
					focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all resize-y placeholder:text-text-muted" />
			{#snippet footer()}
				<button onclick={() => showRejectModal = false}
					class="px-4 py-2 rounded-full text-sm text-text-secondary hover:text-text-primary transition-all cursor-pointer">Cancelar</button>
				<button onclick={rejeitar} disabled={aprovando}
					class="px-4 py-2 rounded-full text-sm font-medium text-red bg-red/9 border border-red/15 hover:bg-red/15 transition-all cursor-pointer disabled:opacity-50">
					{aprovando ? 'Rejeitando...' : 'Rejeitar'}
				</button>
			{/snippet}
		</Modal>
	{/if}
</div>
