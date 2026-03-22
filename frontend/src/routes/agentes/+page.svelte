<script lang="ts">
	import { config } from '$lib/stores/config';
	import { get } from 'svelte/store';
	import { onMount } from 'svelte';

	type Agente = {
		slug: string;
		nome: string;
		descricao: string;
		conteudo: string;
	};

	let agentes = $state<Agente[]>([]);
	let selecionado = $state<string>('');
	let carregando = $state(true);
	let erro = $state('');

	const agenteSelecionado = $derived(agentes.find((a) => a.slug === selecionado));

	onMount(async () => {
		const backendUrl = get(config).backendUrl;
		try {
			const res = await fetch(`${backendUrl}/api/agentes`);
			if (!res.ok) throw new Error('Erro ao carregar agentes');
			agentes = await res.json();
			if (agentes.length > 0) selecionado = agentes[0].slug;
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro desconhecido';
		} finally {
			carregando = false;
		}
	});
</script>

<svelte:head>
	<title>Agentes — Carrossel System</title>
</svelte:head>

<div class="animate-fade-up">
	<div class="mb-8">
		<h2 class="text-2xl font-semibold text-steel-6 mb-2">Agentes & Skills</h2>
		<p class="text-steel-4 font-light">Skills utilizadas na pipeline de geração de carrosséis.</p>
	</div>

	{#if carregando}
		<div class="text-center py-20 text-steel-4">Carregando...</div>
	{:else if erro}
		<div class="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">{erro}</div>
	{:else}
		<div class="grid grid-cols-1 lg:grid-cols-4 gap-6">

			<!-- Lista de agentes -->
			<div class="space-y-3">
				{#each agentes as agente}
					<button
						onclick={() => selecionado = agente.slug}
						class="w-full text-left p-4 rounded-2xl border transition-all duration-200 cursor-pointer
							{selecionado === agente.slug
								? 'bg-steel-6 text-white border-steel-3 shadow-lg'
								: 'bg-bg-card border-teal-4/30 hover:border-steel-3/40 hover:shadow-md'}"
					>
						<p class="font-semibold text-sm mb-1">{agente.nome}</p>
						<p class="text-xs {selecionado === agente.slug ? 'text-teal-4' : 'text-steel-4'} font-light leading-relaxed">
							{agente.descricao}
						</p>
					</button>
				{/each}

				<!-- Sequência da pipeline -->
				<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-4 mt-4">
					<p class="font-semibold text-steel-6 text-sm mb-3">Pipeline</p>
					<ol class="space-y-2 text-xs text-steel-5">
						<li class="flex items-start gap-2">
							<span class="w-5 h-5 rounded-full bg-steel-3 text-white flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">1</span>
							<span><strong>Gerador de Conteúdo</strong> — gera o roteiro JSON dos slides via Claude</span>
						</li>
						<li class="flex items-start gap-2">
							<span class="w-5 h-5 rounded-full bg-teal-5 text-white flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">2</span>
							<span><strong>Gerador de Imagens</strong> — renderiza imagens de cada slide via Gemini</span>
						</li>
					</ol>
				</div>
			</div>

			<!-- Conteúdo da skill -->
			<div class="lg:col-span-3">
				{#if agenteSelecionado}
					<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-6">
						<div class="mb-4 pb-4 border-b border-teal-4/20">
							<h3 class="font-semibold text-steel-6 text-lg">{agenteSelecionado.nome}</h3>
							<p class="text-sm text-steel-4 font-light mt-1">{agenteSelecionado.descricao}</p>
						</div>
						<pre class="text-xs text-steel-5 whitespace-pre-wrap leading-relaxed font-mono overflow-auto max-h-[70vh]">{agenteSelecionado.conteudo}</pre>
					</div>
				{/if}
			</div>

		</div>
	{/if}
</div>
