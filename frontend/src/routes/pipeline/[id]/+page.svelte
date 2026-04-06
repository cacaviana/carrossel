<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { API_BASE } from '$lib/api';
	import { PipelineService } from '$lib/services/PipelineService';
	import { PipelineDTO } from '$lib/dtos/PipelineDTO';
	import { PipelineStepDTO } from '$lib/dtos/PipelineStepDTO';
	import Spinner from '$lib/components/ui/Spinner.svelte';
	import Skeleton from '$lib/components/ui/Skeleton.svelte';
	import Banner from '$lib/components/ui/Banner.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';

	let pipeline = $state<PipelineDTO | null>(null);
	let steps = $state<PipelineStepDTO[]>([]);
	let carregando = $state(true);
	let erro = $state('');
	let showCancelModal = $state(false);
	let cancelando = $state(false);

	const pipelineId = $derived(page.params.id);

	const progresso = $derived(() => {
		if (steps.length === 0) return { pct: 0, label: '' };
		const total = steps.length;
		const concluidos = steps.filter(s => s.status === 'aprovado' || s.status === 'completo').length;
		const executando = steps.find(s => s.status === 'em_execucao');
		const aguardando = steps.find(s => s.status === 'aguardando_aprovacao');
		const pct = Math.round((concluidos / total) * 100);
		let label = `${pct}% concluido`;
		if (executando) {
			const cfg = etapasConfig.find(e => e.agente === executando.agente);
			label = `${cfg?.sublabel ?? executando.agente} processando... (${cfg?.estimativa ?? ''})`;
		} else if (aguardando) {
			const cfg = etapasConfig.find(e => e.agente === aguardando.agente);
			label = `Aguardando aprovacao: ${cfg?.label ?? aguardando.agente}`;
		}
		return { pct, label };
	});

	const etapasConfig = [
		{ agente: 'strategist', label: 'Estrategia', sublabel: 'Strategist', icon: 'M13 10V3L4 14h7v7l9-11h-7z', rota: 'briefing', estimativa: '~15s' },
		{ agente: 'copywriter', label: 'Copywriting', sublabel: 'Copywriter', icon: 'M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z', rota: null, estimativa: '~20s', autoAprovar: true },
		{ agente: 'hook_specialist', label: 'Hooks', sublabel: 'Hook Specialist', icon: 'M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101', rota: 'copy', estimativa: '~10s' },
		{ agente: 'art_director', label: 'Direcao de Arte', sublabel: 'Art Director', icon: 'M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01', rota: 'visual', estimativa: '~15s' },
		{ agente: 'image_generator', label: 'Imagens', sublabel: 'Image Generator', icon: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z', rota: null, estimativa: '~2min', autoAprovar: true },
		{ agente: 'brand_gate', label: 'Brand Gate', sublabel: 'Validacao de Marca', icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z', rota: null, estimativa: '~5s' },
		{ agente: 'content_critic', label: 'Avaliacao Final', sublabel: 'Content Critic', icon: 'M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z', rota: null, estimativa: '~10s' }
	];

	function getStepForAgent(agente: string): PipelineStepDTO | undefined {
		return steps.find(s => s.agente === agente);
	}

	function getStatusClasses(status: string): string {
		switch (status) {
			case 'aprovado': return 'bg-green text-white';
			case 'em_execucao': return 'bg-purple/8 border-2 border-purple animate-pulse';
			case 'aguardando_aprovacao': return 'bg-amber/10 border-2 border-amber animate-pulse-border';
			case 'rejeitado': return 'bg-red text-white';
			case 'erro': return 'bg-red text-white';
			default: return 'border-2 border-dashed border-text-muted';
		}
	}

	function getStatusIcon(status: string): string {
		switch (status) {
			case 'aprovado': return 'M5 13l4 4L19 7';
			case 'rejeitado': case 'erro': return 'M6 18L18 6M6 6l12 12';
			case 'aguardando_aprovacao': return 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z';
			default: return '';
		}
	}

	function getApprovalRoute(agente: string): string | null {
		const config = etapasConfig.find(e => e.agente === agente);
		return config?.rota ?? null;
	}

	async function cancelarPipeline() {
		cancelando = true;
		try {
			await PipelineService.cancelar(pipelineId);
			goto('/historico');
		} catch {
			erro = 'Erro ao cancelar pipeline';
		} finally {
			cancelando = false;
			showCancelModal = false;
		}
	}

	async function retomarPipeline() {
		try {
			await PipelineService.retomar(pipelineId);
			// Reload
			carregando = true;
			const [p, s] = await Promise.all([
				PipelineService.buscar(pipelineId),
				PipelineService.listarSteps(pipelineId)
			]);
			pipeline = p;
			steps = s;
		} catch {
			erro = 'Erro ao retomar pipeline';
		} finally {
			carregando = false;
		}
	}

	let pollingInterval: ReturnType<typeof setInterval> | null = null;

	async function recarregar() {
		const [p, s] = await Promise.all([
			PipelineService.buscar(pipelineId),
			PipelineService.listarSteps(pipelineId)
		]);
		pipeline = p;
		steps = s;

		// Auto-aprovar etapas que nao precisam de review (copywriter)
		const etapaAutoAprovar = steps.find(st => {
			if (st.status !== 'aguardando_aprovacao') return false;
			const cfg = etapasConfig.find(e => e.agente === st.agente);
			return cfg && 'autoAprovar' in cfg && (cfg as any).autoAprovar;
		});
		if (etapaAutoAprovar) {
			try {
				const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/${etapaAutoAprovar.agente}/aprovar`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({})
				});
				if (res.ok) {
					// Executar proxima etapa
					PipelineService.executar(pipelineId).catch(() => {});
					// Marcar localmente como aprovado + proxima como executando
					steps = steps.map(st => {
						if (st.agente === etapaAutoAprovar.agente) {
							return new PipelineStepDTO({ ...st.toPayload(), status: 'aprovado' });
						}
						return st;
					});
					// Marcar proxima como executando
					const nextPending = steps.find(st => st.status === 'pendente');
					if (nextPending) {
						steps = steps.map(st =>
							st.agente === nextPending.agente
								? new PipelineStepDTO({ ...st.toPayload(), status: 'em_execucao' })
								: st
						);
					}
					if (!pollingInterval) iniciarPolling();
				}
			} catch { /* ignora */ }
		}
	}

	function iniciarPolling() {
		if (pollingInterval) return;
		pollingInterval = setInterval(async () => {
			await recarregar();
			// Parar polling só quando pipeline estiver completo, cancelado ou com erro terminal
			const status = pipeline?.status;
			if (status === 'completo' || status === 'cancelado') {
				clearInterval(pollingInterval!);
				pollingInterval = null;
			}
		}, 3000);
	}

	onMount(async () => {
		try {
			// 1. Carregar dados e mostrar UI imediatamente
			await recarregar();
			carregando = false;

			// 2. Se ha etapa pendente e nenhuma executando/aguardando, disparar execucao
			const temPendente = steps.some(s => s.status === 'pendente');
			const temExecutando = steps.some(s => s.status === 'em_execucao');
			const temAguardando = steps.some(s => s.status === 'aguardando_aprovacao');

			if (temPendente && !temExecutando && !temAguardando) {
				// Disparar execucao sem bloquear a UI
				PipelineService.executar(pipelineId)
					.then(() => recarregar())
					.catch(() => recarregar());
				// Atualizar status para "executando" localmente enquanto espera
				const primeiraEtapaPendente = steps.find(s => s.status === 'pendente');
				if (primeiraEtapaPendente) {
					steps = steps.map(s =>
						s.agente === primeiraEtapaPendente.agente
							? new PipelineStepDTO({ ...s.toPayload(), status: 'em_execucao' })
							: s
					);
				}
				iniciarPolling();
			} else if (temExecutando) {
				iniciarPolling();
			}
			// Sempre iniciar polling se pipeline nao esta completo
			if (pipeline && pipeline.status !== 'completo' && pipeline.status !== 'cancelado') {
				iniciarPolling();
			}
		} catch {
			erro = 'Pipeline nao encontrado';
			carregando = false;
		}

		return () => {
			if (pollingInterval) clearInterval(pollingInterval);
		};
	});
</script>

<svelte:head>
	<title>Pipeline — Content Factory</title>
</svelte:head>

<div class="animate-fade-up max-w-[900px] mx-auto">
	{#if carregando}
		<!-- Skeleton -->
		<div class="space-y-4">
			<Skeleton variant="block" height="h-20" />
			{#each Array(7) as _}
				<div class="flex gap-4 items-start">
					<Skeleton variant="circle" />
					<Skeleton variant="block" height="h-16" />
				</div>
			{/each}
		</div>
	{:else if erro && !pipeline}
		<div class="text-center py-16">
			<p class="text-text-secondary text-lg mb-2">Pipeline nao encontrado</p>
			<p class="text-text-muted text-sm mb-6">Verifique o ID ou crie um novo conteudo.</p>
			<a href="/" class="px-6 py-3 rounded-full bg-purple text-bg-global font-medium text-sm no-underline hover:opacity-90 transition-all">Ir para Home</a>
		</div>
	{:else if pipeline}
		<!-- Header -->
		<div class="bg-bg-card rounded-xl border border-border-default p-5 mb-8">
			<div class="flex flex-wrap items-start justify-between gap-3">
				<div class="flex-1 min-w-0">
					<h1 class="text-lg font-semibold text-text-primary mb-2 line-clamp-2">{pipeline.tema}</h1>
					<div class="flex flex-wrap gap-2">
						<span class="px-2.5 py-0.5 rounded-full text-xs font-mono bg-purple/8 text-purple border border-purple/20">{pipeline.formatoLabel}</span>
						<span class="px-2.5 py-0.5 rounded-full text-xs font-mono
							{pipeline.status === 'aprovado' ? 'bg-green/10 text-green border border-green/25' :
							 pipeline.status === 'erro' ? 'bg-red/9 text-red border border-red/15' :
							 pipeline.status === 'aguardando_aprovacao' ? 'bg-amber/10 text-amber border border-amber/25' :
							 'bg-purple/8 text-purple border border-purple/20'}">
							{pipeline.status.replace(/_/g, ' ')}
						</span>
						{#if pipeline.modo_funil}
							<span class="px-2.5 py-0.5 rounded-full text-xs font-mono bg-amber/10 text-amber border border-amber/25">Funil</span>
						{/if}
					</div>
				</div>
				<button data-testid="btn-cancelar-pipeline" onclick={() => showCancelModal = true}
					class="px-3 py-1.5 rounded-full text-xs font-medium text-red bg-red/9 border border-red/15 hover:bg-red/15 transition-all cursor-pointer">
					Cancelar
				</button>
			</div>
		</div>

		{#if erro}
			<div class="mb-4"><Banner type="error">{erro}</Banner></div>
		{/if}

		<!-- Wizard -->
		<div class="relative">
			<!-- Linha vertical -->
			<div class="absolute left-4 top-4 bottom-4 w-0.5 bg-purple/20"></div>

			<div class="space-y-3">
				{#each etapasConfig as etapaConfig, i}
					{@const step = getStepForAgent(etapaConfig.agente)}
					{@const status = step?.status ?? 'pendente'}
					{@const approvalRoute = getApprovalRoute(etapaConfig.agente)}

					<div class="flex gap-4 items-start relative">
						<!-- Indicador circular -->
						<div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 z-10 {getStatusClasses(status)}">
							{#if status === 'em_execucao'}
								<Spinner size="sm" />
							{:else if getStatusIcon(status)}
								<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={getStatusIcon(status)} />
								</svg>
							{:else}
								<span class="text-xs text-text-muted font-mono">{i + 1}</span>
							{/if}
						</div>

						<!-- Card da etapa -->
						<div class="flex-1 bg-bg-card rounded-xl border border-border-default p-4 hover:border-purple/30 transition-all
							{status === 'aguardando_aprovacao' ? 'border-amber/40' : ''}
							{status === 'erro' ? 'border-red/40' : ''}">
							<div class="flex items-center justify-between mb-1">
								<div class="flex items-center gap-2">
									<svg class="w-4 h-4 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d={etapaConfig.icon} />
									</svg>
									<span class="text-sm font-medium text-text-primary">{etapaConfig.label}</span>
								</div>
								<span class="text-xs font-mono text-text-muted px-2 py-0.5 rounded-full
									{status === 'aprovado' ? 'bg-green/10 text-green' :
									 status === 'em_execucao' ? 'bg-purple/8 text-purple' :
									 status === 'aguardando_aprovacao' ? 'bg-amber/10 text-amber' :
									 status === 'erro' ? 'bg-red/9 text-red' :
									 'bg-bg-elevated text-text-muted'}">
									{status.replace(/_/g, ' ')}
								</span>
							</div>
							<p class="text-xs text-text-secondary">{etapaConfig.sublabel}</p>

							{#if step && step.duracao_ms > 0}
								<p class="text-[10px] text-text-muted font-mono mt-1">{step.duracaoFormatada}</p>
							{/if}

							{#if status === 'em_execucao'}
								<div class="mt-3">
									<div class="flex items-center gap-2 text-xs text-purple mb-2">
										<Spinner size="sm" />
										{#if step?.progresso}
											<span>{step.progresso.detalhe} — {step.progresso.atual}/{step.progresso.total}</span>
										{:else}
											<span>Agente {etapaConfig.sublabel} trabalhando... ({etapaConfig.estimativa})</span>
										{/if}
									</div>
									{#if step?.progresso}
										<div class="w-full h-1.5 rounded-full bg-bg-elevated overflow-hidden">
											<div class="h-full rounded-full bg-purple transition-all duration-500"
												style="width: {Math.round((step.progresso.atual / step.progresso.total) * 100)}%"></div>
										</div>
										<p class="text-[10px] text-text-muted mt-1 font-mono">{Math.round((step.progresso.atual / step.progresso.total) * 100)}%</p>
									{/if}
								</div>
							{/if}

							{#if status === 'aguardando_aprovacao' && approvalRoute}
								<a href="/pipeline/{pipelineId}/{approvalRoute}"
									class="inline-flex mt-3 px-4 py-2 rounded-full bg-purple text-bg-global text-xs font-medium
										hover:opacity-90 transition-all no-underline cursor-pointer">
									Revisar {etapaConfig.label}
								</a>
							{/if}

							{#if status === 'aprovado' && approvalRoute}
								<a href="/pipeline/{pipelineId}/{approvalRoute}"
									class="inline-flex mt-3 px-3 py-1.5 rounded-full text-xs font-medium text-text-secondary
										border border-border-default hover:border-purple/40 hover:text-purple transition-all no-underline cursor-pointer">
									Ver aprovado
								</a>
							{/if}

							{#if status === 'erro'}
								<div class="mt-3">
									<p class="text-xs text-red mb-2">Falha na execucao do {etapaConfig.sublabel}.</p>
									<div class="flex gap-2">
										<button onclick={retomarPipeline}
											class="px-4 py-2 rounded-full text-xs font-medium text-purple border border-purple/20 hover:bg-purple/8 transition-all cursor-pointer">
											Retomar
										</button>
										<a href="/editor?pipeline={pipelineId}&brand={pipeline?.brand_slug || ''}"
											class="px-4 py-2 rounded-full text-xs font-medium text-green-400 border border-green-500/30 hover:bg-green-500/10 transition-all no-underline">
											Abrir no Editor
										</a>
									</div>
								</div>
							{/if}
						</div>
					</div>
				{/each}
			</div>
		</div>

		<!-- Ver Resultado - aparece quando imagens foram geradas -->
		{@const temImagens = steps.some(s => (s.agente === 'image_generator' || s.agente === 'brand_gate') && (s.status === 'aprovado' || s.status === 'completo' || s.status === 'aguardando_aprovacao'))}
		{#if temImagens || pipeline.isCompleto}
			<div class="mt-8 text-center">
				<a data-testid="btn-ver-resultado" href="/editor?pipeline={pipelineId}&brand={pipeline?.brand_slug || ''}"
					class="inline-flex px-8 py-3.5 rounded-full bg-purple text-bg-global font-medium text-sm
						hover:shadow-[0_0_30px_rgba(167,139,250,0.3)] hover:opacity-90 transition-all no-underline cursor-pointer">
					Ver Imagens
				</a>
			</div>
		{/if}

		<!-- Cancel Modal -->
		<Modal open={showCancelModal} size="sm" title="Cancelar pipeline?" onclose={() => showCancelModal = false}>
			<p class="text-sm text-text-secondary">O progresso sera mantido no historico, mas o pipeline nao podera ser retomado.</p>
			{#snippet footer()}
				<button onclick={() => showCancelModal = false}
					class="px-4 py-2 rounded-full text-sm text-text-secondary hover:text-text-primary transition-all cursor-pointer">
					Voltar
				</button>
				<button onclick={cancelarPipeline} disabled={cancelando}
					class="px-4 py-2 rounded-full text-sm font-medium text-red bg-red/9 border border-red/15 hover:bg-red/15 transition-all cursor-pointer disabled:opacity-50">
					{cancelando ? 'Cancelando...' : 'Sim, cancelar'}
				</button>
			{/snippet}
		</Modal>
	{/if}
</div>
