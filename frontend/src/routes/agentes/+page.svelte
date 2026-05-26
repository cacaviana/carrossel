<script lang="ts">
	import { onMount } from 'svelte';
	import { AgenteService } from '$lib/services/AgenteService';
	import { AgenteDTO } from '$lib/dtos/AgenteDTO';
	import Tabs from '$lib/components/ui/Tabs.svelte';
	import Spinner from '$lib/components/ui/Spinner.svelte';
	import PageHeader from '$lib/components/ui/PageHeader.svelte';

	let agentesLLM = $state<AgenteDTO[]>([]);
	let skills = $state<AgenteDTO[]>([]);
	let selecionado = $state('');
	let tabAtiva = $state('llm');
	let carregando = $state(true);
	let erro = $state('');

	const listaAtual = $derived(tabAtiva === 'llm' ? agentesLLM : skills);
	const agenteSelecionado = $derived([...agentesLLM, ...skills].find(a => a.slug === selecionado));

	const tabs = $derived([
		{ id: 'llm', label: 'Agentes LLM', count: agentesLLM.length },
		{ id: 'skill', label: 'Skills', count: skills.length }
	]);

	const pipelineEtapas = [
		{ label: 'Strategist', tipo: 'llm' },
		{ label: 'Copywriter', tipo: 'llm' },
		{ label: 'Hook Specialist', tipo: 'llm' },
		{ label: 'Art Director', tipo: 'llm' },
		{ label: 'Image Generator', tipo: 'llm' },
		{ label: 'Brand Gate', tipo: 'skill' },
		{ label: 'Content Critic', tipo: 'llm' }
	];

	onMount(async () => {
		try {
			const [llm, sk] = await Promise.all([
				AgenteService.listarLLM(),
				AgenteService.listarSkills()
			]);
			agentesLLM = llm;
			skills = sk;
			if (llm.length > 0) selecionado = llm[0].slug;
		} catch {
			erro = 'Erro ao carregar agentes';
		} finally {
			carregando = false;
		}
	});
</script>

<svelte:head>
	<title>Agentes e Skills — Content Factory</title>
</svelte:head>

<div class="animate-fade-up">
	<PageHeader title="Agentes e Skills" subtitle="Pipeline de {agentesLLM.length} agentes LLM + {skills.length} skills deterministicas" />

	{#if carregando}
		<div class="text-center py-16"><Spinner size="lg" /></div>
	{:else if erro}
		<div class="text-center py-16 text-red text-sm">{erro}</div>
	{:else}
		<!-- Tabs -->
		<div class="mb-6">
			<Tabs {tabs} active={tabAtiva} onchange={(id) => {
				tabAtiva = id;
				const lista = id === 'llm' ? agentesLLM : skills;
				if (lista.length > 0) selecionado = lista[0].slug;
			}} />
		</div>

		<!-- Master-Detail -->
		<div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
			<!-- Lista -->
			<div class="space-y-2">
				{#each listaAtual as agente}
					<button
						onclick={() => selecionado = agente.slug}
						class="w-full text-left p-4 rounded-xl border transition-all cursor-pointer
							{selecionado === agente.slug
								? 'bg-bg-card border-l-[3px] border-purple bg-purple/4'
								: 'bg-bg-card border-border-default hover:bg-black/3'}"
					>
						<div class="flex items-center justify-between mb-1">
							<span class="text-sm font-medium text-text-primary">{agente.nome}</span>
							<span class="px-1.5 py-0.5 rounded-full text-[10px] font-mono
								{agente.isLLM ? 'bg-purple/8 text-purple border border-purple/20' : 'bg-green/10 text-green border border-green/25'}">
								{agente.tipo}
							</span>
						</div>
						<p class="text-xs text-text-secondary line-clamp-1">{agente.descricao}</p>
					</button>
				{/each}
			</div>

			<!-- Detalhes -->
			<div class="lg:col-span-3">
				{#if agenteSelecionado}
					<div class="bg-bg-card rounded-xl border border-border-default p-6">
						<div class="flex items-center gap-3 mb-4">
							<h2 class="text-lg font-semibold text-text-primary">{agenteSelecionado.nome}</h2>
							<span class="px-2 py-0.5 rounded-full text-xs font-mono
								{agenteSelecionado.isLLM ? 'bg-purple/8 text-purple border border-purple/20' : 'bg-green/10 text-green border border-green/25'}">
								{agenteSelecionado.tipo}
							</span>
						</div>
						<p class="text-sm text-text-secondary mb-4">{agenteSelecionado.descricao}</p>

						{#if agenteSelecionado.conteudo}
							<div class="bg-bg-code rounded-lg p-4 overflow-x-auto border border-border-default">
								<pre class="text-xs text-text-secondary font-mono whitespace-pre-wrap leading-relaxed">{agenteSelecionado.conteudo}</pre>
							</div>
						{/if}
					</div>
				{/if}
			</div>
		</div>

		<!-- Pipeline Visual -->
		<div class="mt-10">
			<p class="label-upper mb-4">Pipeline Visual</p>
			<div class="flex items-center gap-2 overflow-x-auto pb-4">
				{#each pipelineEtapas as etapa, i}
					<div class="flex items-center shrink-0">
						<div class="px-4 py-2.5 rounded-full text-xs font-medium border
							{etapa.tipo === 'llm' ? 'bg-purple/8 text-purple border-purple/20' : 'bg-green/10 text-green border-green/25'}">
							{etapa.label}
						</div>
						{#if i < pipelineEtapas.length - 1}
							<svg class="w-6 h-6 text-text-muted mx-1 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
							</svg>
						{/if}
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>
