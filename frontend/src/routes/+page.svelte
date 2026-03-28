<script lang="ts">
	import { disciplinas } from '$lib/data/disciplinas';
	import { config, isProduction } from '$lib/stores/config';
	import { carrosselAtual, gerandoConteudo } from '$lib/stores/carrossel';
	import { goto } from '$app/navigation';

	const isProd = isProduction();

	let modo = $state<'disciplina' | 'texto'>('disciplina');
	let disciplinaSelecionada = $state('');
	let techSelecionada = $state('');
	let temaCustom = $state('');
	let textoLivre = $state('');
	let erro = $state('');
	let modoCli = $state(false);
	let totalSlides = $state<3 | 7 | 10>(10);

	const disciplinaAtual = $derived(disciplinas.find((d) => d.id === disciplinaSelecionada));
	const techsDisponiveis = $derived(disciplinaAtual?.techs ?? []);

	const podeContinuar = $derived(
		modo === 'texto'
			? textoLivre.trim().length > 20
			: !!disciplinaSelecionada && !!techSelecionada
	);

	async function gerarConteudo(useCli: boolean) {
		if (!podeContinuar) {
			erro = modo === 'texto'
				? 'Escreva um texto com pelo menos 20 caracteres.'
				: 'Selecione uma disciplina e uma tecnologia.';
			return;
		}

		let currentConfig: typeof $config | undefined;
		config.subscribe((v) => (currentConfig = v))();

		modoCli = useCli;
		erro = '';
		gerandoConteudo.set(true);

		const endpoint = useCli ? '/api/gerar-conteudo-cli' : '/api/gerar-conteudo';
		const body = modo === 'texto'
			? { texto_livre: textoLivre, total_slides: totalSlides }
			: { disciplina: disciplinaSelecionada, tecnologia: techSelecionada, tema_custom: temaCustom || undefined, total_slides: totalSlides };

		try {
			const res = await fetch(`${currentConfig.backendUrl}${endpoint}`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(body)
			});

			if (!res.ok) {
				const data = await res.json();
				throw new Error(data.detail || 'Erro ao gerar conteudo');
			}

			const data = await res.json();
			carrosselAtual.set({ ...data, createdAt: new Date().toISOString() });

			const saved = localStorage.getItem('carrossel-historico');
			const historico = saved ? JSON.parse(saved) : [];
			historico.unshift({ ...data, createdAt: new Date().toISOString() });
			localStorage.setItem('carrossel-historico', JSON.stringify(historico.slice(0, 50)));

			goto('/carrossel');
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro desconhecido';
		} finally {
			gerandoConteudo.set(false);
		}
	}
</script>

<svelte:head>
	<title>Home — Carrossel System</title>
</svelte:head>

<div class="animate-fade-up">
	<div class="mb-8">
		<h2 class="text-2xl font-semibold text-steel-6 mb-2">Criar Carrossel LinkedIn</h2>
		<p class="text-steel-4 font-light">Gere conteúdo técnico real para LinkedIn — Carlos Viana / IT Valley School.</p>
	</div>

	<!-- Tabs -->
	<div class="flex gap-2 mb-6">
		<button
			onclick={() => { modo = 'disciplina'; erro = ''; }}
			class="px-5 py-2 rounded-full text-sm font-medium transition-all cursor-pointer
				{modo === 'disciplina' ? 'bg-steel-6 text-white shadow' : 'bg-bg-card text-steel-4 border border-teal-4/30 hover:border-steel-3/40'}"
		>
			Por disciplina
		</button>
		<button
			onclick={() => { modo = 'texto'; erro = ''; }}
			class="px-5 py-2 rounded-full text-sm font-medium transition-all cursor-pointer
				{modo === 'texto' ? 'bg-steel-6 text-white shadow' : 'bg-bg-card text-steel-4 border border-teal-4/30 hover:border-steel-3/40'}"
		>
			Enviar texto
		</button>
	</div>

	<!-- Quantidade de slides -->
	<div class="flex flex-wrap items-center gap-2 sm:gap-3 mb-6">
		<span class="text-sm font-medium text-steel-5">Slides:</span>
		{#each [3, 7, 10] as count}
			<button
				onclick={() => totalSlides = count as 3 | 7 | 10}
				class="w-11 h-11 sm:w-10 sm:h-10 rounded-full text-sm font-bold transition-all cursor-pointer active:scale-95
					{totalSlides === count ? 'bg-steel-6 text-white shadow' : 'bg-bg-card text-steel-4 border border-teal-4/30 hover:border-steel-3/40'}"
			>
				{count}
			</button>
		{/each}
		<span class="text-xs text-steel-4 font-light">
			{totalSlides === 3 ? 'Micro' : totalSlides === 7 ? 'Compacto' : 'Completo'}
		</span>
	</div>

	<!-- Modo: Por disciplina -->
	{#if modo === 'disciplina'}
		<div class="grid grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4 mb-8">
			{#each disciplinas as disc}
				<button
					onclick={() => { disciplinaSelecionada = disc.id; techSelecionada = ''; }}
					class="text-left p-5 rounded-2xl border transition-all duration-300 cursor-pointer
						{disciplinaSelecionada === disc.id
							? 'bg-steel-6 text-white border-steel-3 shadow-lg scale-[1.02]'
							: 'bg-bg-card border-teal-4/30 hover:border-steel-3/40 hover:-translate-y-1 hover:shadow-md'}"
				>
					<div class="flex items-center gap-3 mb-2">
						<span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium
							{disciplinaSelecionada === disc.id ? 'bg-steel-3 text-white' : 'bg-steel-0 text-steel-3'}">
							{disc.id}
						</span>
						<h3 class="font-semibold text-sm">{disc.nome}</h3>
					</div>
					<p class="text-xs {disciplinaSelecionada === disc.id ? 'text-teal-4' : 'text-steel-4'} font-light">
						{disc.descricao}
					</p>
				</button>
			{/each}
		</div>

		{#if disciplinaAtual}
			<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-4 sm:p-6 animate-fade-up">
				<h3 class="font-semibold text-steel-6 mb-4 text-sm sm:text-base">{disciplinaAtual.id} — {disciplinaAtual.nome}</h3>

				<div class="mb-4">
					<label class="block text-sm font-medium text-steel-5 mb-2">Tecnologia</label>
					<div class="flex flex-wrap gap-2">
						{#each techsDisponiveis as tech}
							<button
								onclick={() => techSelecionada = tech}
								class="px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 cursor-pointer
									{techSelecionada === tech ? 'bg-steel-3 text-white shadow-md' : 'bg-teal-3 text-steel-5 hover:bg-teal-4'}"
							>
								{tech}
							</button>
						{/each}
					</div>
				</div>

				<div class="mb-5">
					<label for="tema" class="block text-sm font-medium text-steel-5 mb-2">Tema customizado (opcional)</label>
					<input id="tema" type="text" bind:value={temaCustom}
						placeholder="Ex: Como reduzir custo de inferencia com quantizacao..."
						class="w-full px-4 py-3 rounded-xl border border-teal-4/30 bg-bg-card text-steel-6 text-sm
							focus:border-steel-3 focus:ring-2 focus:ring-steel-3/20 outline-none transition-all" />
				</div>

				{#if erro}<div class="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">{erro}</div>{/if}

				<div class="flex flex-col gap-3">
					{#if !isProd}
						<button onclick={() => gerarConteudo(true)} disabled={$gerandoConteudo || !podeContinuar}
							class="w-full py-3.5 px-4 rounded-full font-medium text-white transition-all duration-300 cursor-pointer
								bg-gradient-to-r from-steel-6 via-steel-5 to-steel-4
								hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed
								active:scale-[0.98]">
							{#if $gerandoConteudo && modoCli}
								<span class="inline-flex items-center gap-2">
									<span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
									Gerando com Claude Code...
								</span>
							{:else}Claude Code (grátis){/if}
						</button>
					{/if}
					<button onclick={() => gerarConteudo(false)} disabled={$gerandoConteudo || !podeContinuar}
						class="w-full py-3.5 px-4 rounded-full font-medium text-white transition-all duration-300 cursor-pointer
							bg-gradient-to-r from-steel-4 via-steel-3 to-steel-2
							hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed
							active:scale-[0.98]">
						{#if $gerandoConteudo && !modoCli}
							<span class="inline-flex items-center gap-2">
								<span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
								Gerando com API...
							</span>
						{:else}Gerar Carrossel{/if}
					</button>
				</div>
			</div>
		{/if}

	<!-- Modo: Texto livre -->
	{:else}
		<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-5 sm:p-6 animate-fade-up">
			<h3 class="font-semibold text-steel-6 mb-2">Cole ou escreva seu conteúdo</h3>
			<p class="text-xs text-steel-4 font-light mb-4">
				O Claude vai formatar seu texto criando os slides automaticamente.
			</p>

			<textarea
				bind:value={textoLivre}
				placeholder="Ex: Hoje vou falar sobre como implementei detecção de objetos em tempo real com YOLO v8 e Python..."
				rows="6"
				class="w-full px-4 py-3 rounded-xl border border-teal-4/30 bg-white text-steel-6 text-sm
					focus:border-steel-3 focus:ring-2 focus:ring-steel-3/20 outline-none transition-all resize-y mb-4"
			></textarea>

			{#if erro}<div class="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">{erro}</div>{/if}

			<div class="flex flex-col gap-3">
				{#if !isProd}
					<button onclick={() => gerarConteudo(true)} disabled={$gerandoConteudo || !podeContinuar}
						class="w-full py-3.5 px-4 rounded-full font-medium text-white transition-all duration-300 cursor-pointer
							bg-gradient-to-r from-steel-6 via-steel-5 to-steel-4
							hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed
							active:scale-[0.98]">
						{#if $gerandoConteudo && modoCli}
							<span class="inline-flex items-center gap-2">
								<span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
								Formatando com Claude Code...
							</span>
						{:else}Claude Code (grátis){/if}
					</button>
				{/if}
				<button onclick={() => gerarConteudo(false)} disabled={$gerandoConteudo || !podeContinuar}
					class="w-full py-3.5 px-4 rounded-full font-medium text-white transition-all duration-300 cursor-pointer
						bg-gradient-to-r from-steel-4 via-steel-3 to-steel-2
						hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed
						active:scale-[0.98]">
					{#if $gerandoConteudo && !modoCli}
						<span class="inline-flex items-center gap-2">
							<span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
							Formatando com API...
						</span>
					{:else}Gerar Carrossel{/if}
				</button>
			</div>
		</div>
	{/if}
</div>
