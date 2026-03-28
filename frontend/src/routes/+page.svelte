<script lang="ts">
	import { disciplinas } from '$lib/data/disciplinas';
	import { config, isProduction } from '$lib/stores/config';
	import { fotos } from '$lib/stores/fotos';
	import { carrosselAtual, gerandoConteudo } from '$lib/stores/carrossel';
	import { goto } from '$app/navigation';

	const isProd = isProduction();

	// Wizard state
	let modo = $state<'disciplina' | 'texto'>('texto');
	let tipoCarrossel = $state<'texto' | 'visual' | 'infografico'>('texto');
	let disciplinaSelecionada = $state('');
	let techSelecionada = $state('');
	let temaCustom = $state('');
	let textoLivre = $state('');
	let erro = $state('');
	let modoCli = $state(false);
	let totalSlides = $state<number>(10);

	const disciplinaAtual = $derived(disciplinas.find((d) => d.id === disciplinaSelecionada));
	const techsDisponiveis = $derived(disciplinaAtual?.techs ?? []);

	const podeContinuar = $derived(
		modo === 'texto'
			? textoLivre.trim().length > 20
			: !!disciplinaSelecionada && !!techSelecionada
	);

	// Quando muda para infográfico, força 1 slide
	$effect(() => {
		if (tipoCarrossel === 'infografico') totalSlides = 1;
		else if (totalSlides === 1) totalSlides = 10;
	});

	const tipos = [
		{ id: 'texto' as const, label: 'Texto', desc: 'Slides com texto, código e bullets' },
		{ id: 'visual' as const, label: 'Visual', desc: 'Texto + diagramas e ilustrações' },
		{ id: 'infografico' as const, label: 'Infográfico', desc: '1 slide visual de alto impacto' },
	];

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
		const base = modo === 'texto'
			? { texto_livre: textoLivre }
			: { disciplina: disciplinaSelecionada, tecnologia: techSelecionada, tema_custom: temaCustom || undefined };

		const body = { ...base, total_slides: totalSlides, tipo_carrossel: tipoCarrossel };

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
	<div class="mb-6">
		<h2 class="text-xl sm:text-2xl font-semibold text-steel-6 mb-1">Criar Carrossel LinkedIn</h2>
		<p class="text-sm text-steel-4 font-light">Carlos Viana / IT Valley School</p>
	</div>

	<!-- PASSO 1: Tipo de carrossel -->
	<div class="mb-5">
		<p class="text-xs font-medium text-steel-5 mb-2">Tipo</p>
		<div class="grid grid-cols-3 gap-2 sm:gap-3">
			{#each tipos as tipo}
				<button
					onclick={() => tipoCarrossel = tipo.id}
					class="p-3 sm:p-4 rounded-xl text-left transition-all cursor-pointer active:scale-[0.97]
						{tipoCarrossel === tipo.id
							? 'bg-steel-6 text-white shadow-lg'
							: 'bg-bg-card border border-teal-4/30 hover:border-steel-3/40'}"
				>
					<span class="block text-sm font-semibold">{tipo.label}</span>
					<span class="block text-xs mt-0.5 {tipoCarrossel === tipo.id ? 'text-teal-4' : 'text-steel-4'} font-light">
						{tipo.desc}
					</span>
				</button>
			{/each}
		</div>
	</div>

	<!-- PASSO 2: Foto + Slides (inline) -->
	<div class="flex flex-col sm:flex-row gap-4 mb-5">
		<!-- Foto -->
		<div class="flex-1">
			<p class="text-xs font-medium text-steel-5 mb-2">Sua foto</p>
			<div class="flex gap-2 items-center flex-wrap">
				{#if $fotos.length > 0}
					{#each $fotos as foto}
						<button
							onclick={() => config.update(c => ({ ...c, fotoCriadorBase64: foto.dataUrl }))}
							class="w-10 h-10 rounded-full overflow-hidden cursor-pointer transition-all
								{$config.fotoCriadorBase64 === foto.dataUrl ? 'ring-2 ring-[#A78BFA] scale-110' : 'opacity-50 hover:opacity-100'}"
						>
							<img src={foto.dataUrl} alt={foto.name} class="w-full h-full object-cover" />
						</button>
					{/each}
					<button
						onclick={() => config.update(c => ({ ...c, fotoCriadorBase64: '' }))}
						class="w-10 h-10 rounded-full border border-teal-4/30 flex items-center justify-center text-xs text-steel-4 cursor-pointer hover:bg-teal-1 transition-all
							{!$config.fotoCriadorBase64 ? 'ring-2 ring-[#A78BFA]' : ''}"
					>Sem</button>
				{:else}
					<a href="/configuracoes" class="text-xs text-steel-3 underline">Adicionar fotos em Config</a>
				{/if}
			</div>
		</div>
		<!-- Slides -->
		{#if tipoCarrossel !== 'infografico'}
			<div>
				<p class="text-xs font-medium text-steel-5 mb-2">Slides</p>
				<div class="flex gap-2">
					{#each [1, 3, 7, 10] as count}
						<button
							onclick={() => totalSlides = count}
							class="w-10 h-10 rounded-full text-sm font-bold transition-all cursor-pointer active:scale-95
								{totalSlides === count ? 'bg-steel-6 text-white shadow' : 'bg-bg-card text-steel-4 border border-teal-4/30 hover:border-steel-3/40'}"
						>{count}</button>
					{/each}
				</div>
			</div>
		{:else}
			<div>
				<p class="text-xs font-medium text-steel-5 mb-2">Slides</p>
				<div class="flex gap-2 items-center">
					<span class="w-10 h-10 rounded-full bg-steel-6 text-white text-sm font-bold flex items-center justify-center shadow">1</span>
					<span class="text-xs text-steel-4 font-light">Infográfico único</span>
				</div>
			</div>
		{/if}
	</div>

	<!-- PASSO 3: Fonte do conteúdo -->
	<div class="flex gap-2 mb-4">
		<button
			onclick={() => { modo = 'texto'; erro = ''; }}
			class="px-4 py-2 rounded-full text-sm font-medium transition-all cursor-pointer
				{modo === 'texto' ? 'bg-steel-6 text-white shadow' : 'bg-bg-card text-steel-4 border border-teal-4/30 hover:border-steel-3/40'}"
		>Texto livre</button>
		<button
			onclick={() => { modo = 'disciplina'; erro = ''; }}
			class="px-4 py-2 rounded-full text-sm font-medium transition-all cursor-pointer
				{modo === 'disciplina' ? 'bg-steel-6 text-white shadow' : 'bg-bg-card text-steel-4 border border-teal-4/30 hover:border-steel-3/40'}"
		>Por disciplina</button>
	</div>

	<!-- Modo: Texto livre -->
	{#if modo === 'texto'}
		<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-4 sm:p-6 animate-fade-up">
			<textarea
				bind:value={textoLivre}
				placeholder={tipoCarrossel === 'infografico'
					? 'Descreva o tema do infográfico. Ex: Pipeline de MLOps — do treinamento ao deploy com métricas de cada etapa...'
					: tipoCarrossel === 'visual'
					? 'Descreva o tema. Ex: Como funciona o algoritmo de garbage collection em Python — com diagramas explicativos...'
					: 'Cole ou escreva seu conteúdo. Ex: Hoje implementei detecção de objetos em tempo real com YOLO v8...'}
				rows="5"
				class="w-full px-4 py-3 rounded-xl border border-teal-4/30 bg-white text-steel-6 text-sm
					focus:border-steel-3 focus:ring-2 focus:ring-steel-3/20 outline-none transition-all resize-y mb-4"
			></textarea>

			{#if erro}<div class="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">{erro}</div>{/if}

			<div class="flex flex-col gap-3">
				{#if !isProd}
					<button onclick={() => gerarConteudo(true)} disabled={$gerandoConteudo || !podeContinuar}
						class="w-full py-3.5 px-4 rounded-full font-medium text-white transition-all duration-300 cursor-pointer
							bg-gradient-to-r from-steel-6 via-steel-5 to-steel-4
							hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]">
						{#if $gerandoConteudo && modoCli}
							<span class="inline-flex items-center gap-2">
								<span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
								Gerando...
							</span>
						{:else}Claude Code (grátis){/if}
					</button>
				{/if}
				<button onclick={() => gerarConteudo(false)} disabled={$gerandoConteudo || !podeContinuar}
					class="w-full py-3.5 px-4 rounded-full font-medium text-white transition-all duration-300 cursor-pointer
						bg-gradient-to-r from-steel-4 via-steel-3 to-steel-2
						hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]">
					{#if $gerandoConteudo && !modoCli}
						<span class="inline-flex items-center gap-2">
							<span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
							{tipoCarrossel === 'infografico' ? 'Gerando infográfico...' : 'Gerando carrossel...'}
						</span>
					{:else}
						{tipoCarrossel === 'infografico' ? 'Gerar Infográfico' : 'Gerar Carrossel'}
					{/if}
				</button>
			</div>
		</div>

	<!-- Modo: Por disciplina -->
	{:else}
		<div class="grid grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4 mb-6">
			{#each disciplinas as disc}
				<button
					onclick={() => { disciplinaSelecionada = disc.id; techSelecionada = ''; }}
					class="text-left p-4 sm:p-5 rounded-2xl border transition-all duration-300 cursor-pointer
						{disciplinaSelecionada === disc.id
							? 'bg-steel-6 text-white border-steel-3 shadow-lg scale-[1.02]'
							: 'bg-bg-card border-teal-4/30 hover:border-steel-3/40 hover:-translate-y-1 hover:shadow-md'}"
				>
					<div class="flex items-center gap-2 mb-1">
						<span class="inline-flex px-2 py-0.5 rounded-full text-xs font-medium
							{disciplinaSelecionada === disc.id ? 'bg-steel-3 text-white' : 'bg-steel-0 text-steel-3'}">
							{disc.id}
						</span>
						<h3 class="font-semibold text-xs sm:text-sm">{disc.nome}</h3>
					</div>
					<p class="text-xs {disciplinaSelecionada === disc.id ? 'text-teal-4' : 'text-steel-4'} font-light line-clamp-2">
						{disc.descricao}
					</p>
				</button>
			{/each}
		</div>

		{#if disciplinaAtual}
			<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-4 sm:p-6 animate-fade-up">
				<h3 class="font-semibold text-steel-6 mb-3 text-sm sm:text-base">{disciplinaAtual.id} — {disciplinaAtual.nome}</h3>

				<div class="mb-4">
					<label class="block text-xs font-medium text-steel-5 mb-2">Tecnologia</label>
					<div class="flex flex-wrap gap-2">
						{#each techsDisponiveis as tech}
							<button
								onclick={() => techSelecionada = tech}
								class="px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 cursor-pointer
									{techSelecionada === tech ? 'bg-steel-3 text-white shadow-md' : 'bg-teal-3 text-steel-5 hover:bg-teal-4'}"
							>{tech}</button>
						{/each}
					</div>
				</div>

				<div class="mb-4">
					<label for="tema" class="block text-xs font-medium text-steel-5 mb-2">Tema (opcional)</label>
					<input id="tema" type="text" bind:value={temaCustom}
						placeholder="Ex: Como reduzir custo de inferencia..."
						class="w-full px-4 py-3 rounded-xl border border-teal-4/30 bg-bg-card text-steel-6 text-sm
							focus:border-steel-3 focus:ring-2 focus:ring-steel-3/20 outline-none transition-all" />
				</div>

				{#if erro}<div class="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">{erro}</div>{/if}

				<div class="flex flex-col gap-3">
					{#if !isProd}
						<button onclick={() => gerarConteudo(true)} disabled={$gerandoConteudo || !podeContinuar}
							class="w-full py-3.5 px-4 rounded-full font-medium text-white transition-all duration-300 cursor-pointer
								bg-gradient-to-r from-steel-6 via-steel-5 to-steel-4
								hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]">
							{#if $gerandoConteudo && modoCli}
								<span class="inline-flex items-center gap-2">
									<span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
									Gerando...
								</span>
							{:else}Claude Code (grátis){/if}
						</button>
					{/if}
					<button onclick={() => gerarConteudo(false)} disabled={$gerandoConteudo || !podeContinuar}
						class="w-full py-3.5 px-4 rounded-full font-medium text-white transition-all duration-300 cursor-pointer
							bg-gradient-to-r from-steel-4 via-steel-3 to-steel-2
							hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]">
						{#if $gerandoConteudo && !modoCli}
							<span class="inline-flex items-center gap-2">
								<span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
								{tipoCarrossel === 'infografico' ? 'Gerando infográfico...' : 'Gerando carrossel...'}
							</span>
						{:else}
							{tipoCarrossel === 'infografico' ? 'Gerar Infográfico' : 'Gerar Carrossel'}
						{/if}
					</button>
				</div>
			</div>
		{/if}
	{/if}
</div>
