<script lang="ts">
	import { disciplinas } from '$lib/data/disciplinas';
	import { config } from '$lib/stores/config';
	import { carrosselAtual, gerandoConteudo } from '$lib/stores/carrossel';
	import { goto } from '$app/navigation';

	type TipoCarrossel = 'codigo' | 'editorial' | 'infografico' | 'tabela-ti' | 'misto' | 'card-unico';

	const agentes = [
		{
			id: 'codigo' as TipoCarrossel,
			nome: 'Codigo',
			desc: 'Storytelling tecnico com blocos de codigo real na janela macOS. O padrao IT Valley.',
			icone: '{ }',
			cor: 'from-green-500 to-emerald-600',
			corBorda: 'border-green-500/30',
			corTexto: 'text-green-400',
			slides: [3, 7, 10]
		},
		{
			id: 'editorial' as TipoCarrossel,
			nome: 'Editorial',
			desc: 'Texto puro, storytelling e narrativa tecnica. Sem codigo — foco em insights e licoes.',
			icone: 'Aa',
			cor: 'from-purple-500 to-violet-600',
			corBorda: 'border-purple-500/30',
			corTexto: 'text-purple-400',
			slides: [3, 7, 10]
		},
		{
			id: 'infografico' as TipoCarrossel,
			nome: 'Infografico',
			desc: 'Data-driven: metricas, benchmarks, rankings e numeros de impacto visual.',
			icone: '#',
			cor: 'from-amber-500 to-orange-600',
			corBorda: 'border-amber-500/30',
			corTexto: 'text-amber-400',
			slides: [3, 7, 10]
		},
		{
			id: 'tabela-ti' as TipoCarrossel,
			nome: 'Tabela TI',
			desc: 'Comparacoes em tabela: framework vs framework, cloud vs cloud. O dev adora.',
			icone: '[]',
			cor: 'from-cyan-500 to-blue-600',
			corBorda: 'border-cyan-500/30',
			corTexto: 'text-cyan-400',
			slides: [3, 7, 10]
		},
		{
			id: 'misto' as TipoCarrossel,
			nome: 'Misto',
			desc: 'Texto + codigo + dados. O mais completo — combina todos os estilos num so carrossel.',
			icone: '*',
			cor: 'from-rose-500 to-pink-600',
			corBorda: 'border-rose-500/30',
			corTexto: 'text-rose-400',
			slides: [3, 7, 10]
		},
		{
			id: 'card-unico' as TipoCarrossel,
			nome: 'Card Unico',
			desc: '1 slide so — post single impactante. Dica rapida, dado chocante ou snippet.',
			icone: '1',
			cor: 'from-indigo-500 to-purple-600',
			corBorda: 'border-indigo-500/30',
			corTexto: 'text-indigo-400',
			slides: [1]
		}
	];

	let tipoSelecionado = $state<TipoCarrossel | null>(null);
	let modo = $state<'disciplina' | 'texto'>('disciplina');
	let disciplinaSelecionada = $state('');
	let techSelecionada = $state('');
	let temaCustom = $state('');
	let textoLivre = $state('');
	let erro = $state('');
	let modoCli = $state(false);
	let totalSlides = $state<number>(10);

	const agenteAtual = $derived(agentes.find((a) => a.id === tipoSelecionado));
	const disciplinaAtual = $derived(disciplinas.find((d) => d.id === disciplinaSelecionada));
	const techsDisponiveis = $derived(disciplinaAtual?.techs ?? []);

	const podeContinuar = $derived(
		modo === 'texto'
			? textoLivre.trim().length > 20
			: !!disciplinaSelecionada && !!techSelecionada
	);

	function selecionarAgente(id: TipoCarrossel) {
		tipoSelecionado = id;
		const agente = agentes.find((a) => a.id === id);
		if (agente) {
			totalSlides = agente.slides[agente.slides.length - 1];
		}
		// Scroll para o wizard
		setTimeout(() => {
			document.getElementById('wizard')?.scrollIntoView({ behavior: 'smooth' });
		}, 100);
	}

	function voltarAgentes() {
		tipoSelecionado = null;
		erro = '';
	}

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
			? { texto_livre: textoLivre, total_slides: totalSlides, tipo_carrossel: tipoSelecionado }
			: {
				disciplina: disciplinaSelecionada,
				tecnologia: techSelecionada,
				tema_custom: temaCustom || undefined,
				total_slides: totalSlides,
				tipo_carrossel: tipoSelecionado
			};

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
		<p class="text-steel-4 font-light">Escolha o agente e gere conteudo tecnico real — Carlos Viana / IT Valley School.</p>
	</div>

	<!-- GRID DE AGENTES -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
		{#each agentes as agente}
			<button
				onclick={() => selecionarAgente(agente.id)}
				class="group text-left p-5 rounded-2xl border transition-all duration-300 cursor-pointer
					{tipoSelecionado === agente.id
						? `bg-gradient-to-br ${agente.cor} text-white border-transparent shadow-lg scale-[1.02]`
						: `bg-bg-card ${agente.corBorda} hover:border-opacity-60 hover:-translate-y-1 hover:shadow-md`}"
			>
				<div class="flex items-center gap-3 mb-3">
					<div class="w-10 h-10 rounded-xl flex items-center justify-center font-mono font-bold text-sm
						{tipoSelecionado === agente.id ? 'bg-white/20 text-white' : `bg-steel-0 ${agente.corTexto}`}">
						{agente.icone}
					</div>
					<div>
						<h3 class="font-semibold text-sm">{agente.nome}</h3>
						<span class="text-[10px] font-mono opacity-70">
							{agente.slides.length === 1 ? '1 slide' : `${agente.slides.join('/')} slides`}
						</span>
					</div>
				</div>
				<p class="text-xs font-light leading-relaxed
					{tipoSelecionado === agente.id ? 'text-white/80' : 'text-steel-4'}">
					{agente.desc}
				</p>
			</button>
		{/each}
	</div>

	<!-- WIZARD (aparece ao selecionar agente) -->
	{#if tipoSelecionado}
		<div id="wizard" class="animate-fade-up">
			<div class="flex items-center gap-3 mb-6">
				<button
					onclick={voltarAgentes}
					class="px-4 py-2 rounded-full text-sm font-medium border border-steel-3/30 text-steel-3 hover:bg-steel-0 transition-all cursor-pointer"
				>
					Trocar agente
				</button>
				<div class="flex items-center gap-2">
					<div class="w-6 h-6 rounded-lg flex items-center justify-center font-mono font-bold text-xs bg-gradient-to-br {agenteAtual?.cor} text-white">
						{agenteAtual?.icone}
					</div>
					<span class="text-sm font-semibold text-steel-6">{agenteAtual?.nome}</span>
				</div>
			</div>

			<!-- Quantidade de slides (se nao for card unico) -->
			{#if tipoSelecionado !== 'card-unico'}
				<div class="flex items-center gap-3 mb-6">
					<span class="text-sm font-medium text-steel-5">Slides:</span>
					{#each (agenteAtual?.slides ?? []) as count}
						<button
							onclick={() => totalSlides = count}
							class="w-10 h-10 rounded-full text-sm font-bold transition-all cursor-pointer
								{totalSlides === count ? 'bg-steel-6 text-white shadow' : 'bg-bg-card text-steel-4 border border-teal-4/30 hover:border-steel-3/40'}"
						>
							{count}
						</button>
					{/each}
					<span class="text-xs text-steel-4 font-light">
						{totalSlides === 3 ? 'Micro — rapido e direto' : totalSlides === 7 ? 'Compacto — bom equilibrio' : 'Completo — maximo impacto'}
					</span>
				</div>
			{/if}

			<!-- Tabs modo -->
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

			<!-- Modo: Por disciplina -->
			{#if modo === 'disciplina'}
				<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
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
					<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-6 animate-fade-up">
						<h3 class="font-semibold text-steel-6 mb-4">{disciplinaAtual.id} — {disciplinaAtual.nome}</h3>

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

						<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
							<button onclick={() => gerarConteudo(true)} disabled={$gerandoConteudo || !podeContinuar}
								class="py-3 px-4 rounded-full font-medium text-white transition-all duration-300 cursor-pointer
									bg-gradient-to-r from-steel-6 via-steel-5 to-steel-4
									hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed">
								{#if $gerandoConteudo && modoCli}
									<span class="inline-flex items-center gap-2">
										<span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
										Gerando com Claude Code...
									</span>
								{:else}Claude Code (gratis){/if}
							</button>
							<button onclick={() => gerarConteudo(false)} disabled={$gerandoConteudo || !podeContinuar}
								class="py-3 px-4 rounded-full font-medium text-white transition-all duration-300 cursor-pointer
									bg-gradient-to-r from-steel-4 via-steel-3 to-steel-2
									hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed">
								{#if $gerandoConteudo && !modoCli}
									<span class="inline-flex items-center gap-2">
										<span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
										Gerando com API...
									</span>
								{:else}Gerar com API (pago){/if}
							</button>
						</div>
					</div>
				{/if}

			<!-- Modo: Texto livre -->
			{:else}
				<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-6 animate-fade-up">
					<h3 class="font-semibold text-steel-6 mb-2">Cole ou escreva seu conteudo</h3>
					<p class="text-xs text-steel-4 font-light mb-4">
						O Claude vai formatar seu texto criando os slides automaticamente.
					</p>

					<textarea
						bind:value={textoLivre}
						placeholder="Ex: Hoje vou falar sobre como implementei deteccao de objetos em tempo real com YOLO v8 e Python. O problema era processar 30fps numa camera de seguranca com hardware limitado..."
						rows="8"
						class="w-full px-4 py-3 rounded-xl border border-teal-4/30 bg-white text-steel-6 text-sm
							focus:border-steel-3 focus:ring-2 focus:ring-steel-3/20 outline-none transition-all resize-y mb-4"
					></textarea>

					{#if erro}<div class="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">{erro}</div>{/if}

					<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
						<button onclick={() => gerarConteudo(true)} disabled={$gerandoConteudo || !podeContinuar}
							class="py-3 px-4 rounded-full font-medium text-white transition-all duration-300 cursor-pointer
								bg-gradient-to-r from-steel-6 via-steel-5 to-steel-4
								hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed">
							{#if $gerandoConteudo && modoCli}
								<span class="inline-flex items-center gap-2">
									<span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
									Formatando com Claude Code...
								</span>
							{:else}Claude Code (gratis){/if}
						</button>
						<button onclick={() => gerarConteudo(false)} disabled={$gerandoConteudo || !podeContinuar}
							class="py-3 px-4 rounded-full font-medium text-white transition-all duration-300 cursor-pointer
								bg-gradient-to-r from-steel-4 via-steel-3 to-steel-2
								hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed">
							{#if $gerandoConteudo && !modoCli}
								<span class="inline-flex items-center gap-2">
									<span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
									Formatando com API...
								</span>
							{:else}Gerar com API (pago){/if}
						</button>
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>
