<script lang="ts">
	import { disciplinas } from '$lib/data/disciplinas';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { API_BASE } from '$lib/api';
	import { PipelineService } from '$lib/services/PipelineService';
	import Banner from '$lib/components/ui/Banner.svelte';
	import type { FormatoConteudo } from '$lib/dtos/PipelineDTO';

	let modoEntrada = $state<'texto_pronto' | 'ideia' | 'disciplina'>('ideia');
	let textoLivre = $state('');
	let disciplinaSelecionada = $state('');
	let techSelecionada = $state('');
	let temaCustom = $state('');
	let criando = $state(false);
	let erro = $state('');

	// Marca
	type Brand = { slug: string; nome: string; cor_principal: string; cor_fundo: string };
	let brands = $state<Brand[]>([]);
	let brandSelecionada = $state('');

	import { onMount } from 'svelte';
	onMount(async () => {
		try {
			const res = await fetch(`${API_BASE}/api/brands`);
			if (res.ok) {
				brands = await res.json();
				if (brands.length > 0) brandSelecionada = brands[0].slug;
			}
		} catch {}
	});

	// Avatar
	type AvatarMode = 'capa' | 'livre' | 'sem' | 'sim';
	let avatarMode = $state<AvatarMode>('livre');

	const avatarOptions = $derived(
		formatoAtual === 'thumbnail_youtube'
			? [{ id: 'sim' as AvatarMode, label: 'Com avatar' }]
			: formatoAtual === 'post_unico' || formatoAtual === 'capa_reels'
				? [{ id: 'sim' as AvatarMode, label: 'Com avatar' }, { id: 'sem' as AvatarMode, label: 'Sem avatar' }]
				: [{ id: 'capa' as AvatarMode, label: 'Avatar na capa' }, { id: 'livre' as AvatarMode, label: 'Avatar livre' }, { id: 'sem' as AvatarMode, label: 'Sem avatar' }]
	);

	// Thumbnail sempre com avatar
	$effect(() => {
		if (formatoAtual === 'thumbnail_youtube') avatarMode = 'sim';
	});

	// Texto pronto — slide a slide
	type SlideTexto = { principal: string; alternativo: string };
	const FORMATOS_SLIDE_UNICO = ['post_unico', 'thumbnail_youtube', 'capa_reels'];
	const isSlideUnico = $derived(FORMATOS_SLIDE_UNICO.includes(formatoAtual));
	let slidesTexto = $state<SlideTexto[]>(Array.from({ length: 3 }, () => ({ principal: '', alternativo: '' })));

	// Quando muda pra formato de slide unico, ajustar pra 1 slide
	$effect(() => {
		if (isSlideUnico && slidesTexto.length > 1) {
			slidesTexto = [slidesTexto[0]];
		}
	});

	function adicionarSlide() {
		if (slidesTexto.length >= 7) return;
		slidesTexto = [...slidesTexto, { principal: '', alternativo: '' }];
	}

	function removerSlide(index: number) {
		if (slidesTexto.length <= 1) return;
		slidesTexto = slidesTexto.filter((_, i) => i !== index);
	}

	const formatoLabels: Record<string, string> = {
		carrossel: 'Carrossel',
		post_unico: 'Post Unico',
		thumbnail_youtube: 'Thumbnail YouTube',
		capa_reels: 'Capa Reels',
		funil: 'Funil de Conteudo'
	};

	const formatoDims: Record<string, string> = {
		carrossel: '1080 x 1350 · LinkedIn, Instagram',
		post_unico: '1080 x 1080 · Instagram, Facebook, LinkedIn',
		thumbnail_youtube: '1280 x 720 · YouTube',
		capa_reels: '1080 x 1920 · Instagram Reels, TikTok',
		funil: 'Mix de formatos · Todas as plataformas'
	};

	const formatoAtual = $derived(page.url.searchParams.get('formato') ?? 'carrossel');
	const isFunil = $derived(formatoAtual === 'funil');
	const labelFormato = $derived(formatoLabels[formatoAtual] ?? 'Carrossel');
	const dimFormato = $derived(formatoDims[formatoAtual] ?? '');

	const disciplinaAtual = $derived(disciplinas.find(d => d.id === disciplinaSelecionada));
	const techsDisponiveis = $derived(disciplinaAtual?.techs ?? []);

	const podeCriar = $derived(
		modoEntrada === 'disciplina'
			? !!disciplinaSelecionada && !!techSelecionada
			: modoEntrada === 'texto_pronto'
				? slidesTexto.some(s => s.principal.trim().length > 0)
				: textoLivre.trim().length >= 20
	);

	async function criarPipeline() {
		if (!podeCriar) return;
		erro = '';
		criando = true;
		try {
			const tema = modoEntrada === 'disciplina'
				? [disciplinaSelecionada, techSelecionada, temaCustom].filter(Boolean).join(' - ')
				: modoEntrada === 'texto_pronto'
					? (slidesTexto[0]?.principal || 'Texto pronto pelo usuario')
					: textoLivre;

			const formatos: FormatoConteudo[] = isFunil
				? ['carrossel', 'post_unico', 'thumbnail_youtube']
				: [formatoAtual as FormatoConteudo];

			const payload: Record<string, any> = {
				tema,
				formatos,
				modo_funil: isFunil,
				modo_entrada: modoEntrada,
				brand_slug: brandSelecionada || undefined,
				avatar_mode: avatarMode,
			};

			if (modoEntrada === 'texto_pronto') {
				payload.slides_texto_pronto = slidesTexto
					.filter(s => s.principal.trim().length > 0)
					.map(s => ({ principal: s.principal, alternativo: s.alternativo }));
			}

			const pipeline = await PipelineService.criar(payload);
			goto(`/pipeline/${pipeline.id}`);
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro ao iniciar pipeline';
		} finally {
			criando = false;
		}
	}
</script>

<svelte:head>
	<title>{labelFormato} — Content Factory</title>
</svelte:head>

<div class="animate-fade-up max-w-3xl mx-auto">
	<!-- Header -->
	<div class="mb-8">
		<h1 class="text-2xl font-light text-text-primary mb-1">{labelFormato}</h1>
		<p class="text-sm text-text-secondary">{dimFormato}</p>
		{#if isFunil}
			<p class="text-xs text-purple mt-2">O Strategist criara 5-7 pecas conectadas (carrossel + post + thumb) a partir do seu tema.</p>
		{/if}
	</div>

	<!-- Marca -->
	{#if brands.length > 0}
		<div class="mb-6">
			<p class="label-upper mb-3">Marca</p>
			<div class="flex gap-2 flex-wrap">
				{#each brands as brand}
					<button
						onclick={() => { brandSelecionada = brand.slug; }}
						class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all cursor-pointer
							{brandSelecionada === brand.slug
								? 'bg-bg-card border-2 shadow-sm'
								: 'border border-border-default hover:border-purple/40'}"
						style={brandSelecionada === brand.slug ? `border-color: ${brand.cor_principal}` : ''}
					>
						<span
							class="w-3 h-3 rounded-full shrink-0"
							style="background: {brand.cor_principal}"
						></span>
						{brand.nome}
					</button>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Avatar -->
	{#if avatarOptions.length > 0}
		<div class="mb-6">
			<p class="label-upper mb-3">Avatar / Foto</p>
			<div class="flex gap-2">
				{#each avatarOptions as opt}
					<button
						onclick={() => { avatarMode = opt.id; }}
						class="px-4 py-2 rounded-full text-sm font-medium transition-all cursor-pointer
							{avatarMode === opt.id
								? 'bg-purple text-bg-global'
								: 'text-text-secondary border border-border-default hover:border-purple/40'}"
					>{opt.label}</button>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Modo de entrada -->
	<div class="mb-6">
		<p class="label-upper mb-3">Fonte do conteudo</p>
		<div class="flex gap-2 mb-4">
			<button
				onclick={() => { modoEntrada = 'texto_pronto'; erro = ''; }}
				class="px-4 py-2 rounded-full text-sm font-medium transition-all cursor-pointer
					{modoEntrada === 'texto_pronto'
						? 'bg-purple text-bg-global'
						: 'text-text-secondary border border-border-default hover:border-purple/40'}"
			>Texto pronto</button>
			<button
				onclick={() => { modoEntrada = 'ideia'; erro = ''; }}
				class="px-4 py-2 rounded-full text-sm font-medium transition-all cursor-pointer
					{modoEntrada === 'ideia'
						? 'bg-purple text-bg-global'
						: 'text-text-secondary border border-border-default hover:border-purple/40'}"
			>Ideia livre</button>
			<button
				onclick={() => { modoEntrada = 'disciplina'; erro = ''; }}
				class="px-4 py-2 rounded-full text-sm font-medium transition-all cursor-pointer
					{modoEntrada === 'disciplina'
						? 'bg-purple text-bg-global'
						: 'text-text-secondary border border-border-default hover:border-purple/40'}"
			>Por disciplina</button>
		</div>

		{#if modoEntrada === 'texto_pronto'}
			<div class="bg-bg-card rounded-xl border border-border-default p-5">
				<p class="text-xs text-text-secondary mb-3">{isSlideUnico ? 'Escreva o texto que vai na imagem (max 4-6 palavras).' : 'Preencha slide a slide. O texto vai direto pro visual — sem reescrita.'}</p>

				<!-- Slides -->
				<div class="space-y-3 max-h-[60vh] overflow-y-auto pr-1">
					{#each slidesTexto as slide, i}
						<div class="rounded-lg border border-border-default p-4 bg-bg-global">
							<div class="flex items-center gap-2 mb-2">
								<span class="w-6 h-6 rounded-full bg-purple text-bg-global text-xs font-bold flex items-center justify-center shrink-0">{i + 1}</span>
								<span class="text-xs text-text-muted">
									{isSlideUnico ? 'Texto da imagem' : (i === 0 ? 'Capa' : i === slidesTexto.length - 1 ? 'CTA' : `Slide ${i + 1}`)}
								</span>
								{#if !isSlideUnico && slidesTexto.length > 1}
									<button
										onclick={() => removerSlide(i)}
										class="ml-auto px-2 py-0.5 rounded-full text-xs text-red-400 hover:bg-red-50 transition-all cursor-pointer"
									>remover</button>
								{/if}
							</div>
							<textarea
								bind:value={slide.principal}
								placeholder="Texto principal do slide {i + 1}..."
								rows="3"
								disabled={criando}
								class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
									focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all resize-y
									placeholder:text-text-muted mb-2"
							></textarea>
							<textarea
								bind:value={slide.alternativo}
								placeholder="Texto alternativo (opcional)..."
								rows="2"
								disabled={criando}
								class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-secondary text-xs
									focus:border-purple/60 focus:ring-3 focus:ring-purple/8 outline-none transition-all resize-y
									placeholder:text-text-muted"
							></textarea>
						</div>
					{/each}
				</div>

				{#if !isSlideUnico && slidesTexto.length < 7}
					<button
						onclick={adicionarSlide}
						disabled={criando}
						class="mt-3 w-full py-2.5 rounded-lg border border-dashed border-purple/30 text-purple text-sm font-medium
							hover:bg-purple/5 transition-all cursor-pointer disabled:opacity-50"
					>+ Adicionar slide</button>
				{/if}

				{#if !isSlideUnico}
					<p class="text-xs text-text-muted mt-2">
						{slidesTexto.filter(s => s.principal.trim().length > 0).length}/{slidesTexto.length} slides preenchidos
					</p>
				{/if}
			</div>
		{:else if modoEntrada === 'ideia'}
			<div class="bg-bg-card rounded-xl border border-border-default p-5">
				<p class="text-xs text-text-secondary mb-3">De uma ideia ou tema. O Strategist cria o briefing e o Copywriter escreve tudo.</p>
				<textarea
					data-testid="campo-tema"
					bind:value={textoLivre}
					placeholder="Ex: 7 habitos para conquistar sua vaga de dev na gringa, ou: vi que teve vazamento no Axios, criar post focando em seguranca..."
					rows="5"
					disabled={criando}
					class="w-full px-4 py-3 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
						focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all resize-y
						placeholder:text-text-muted"
				></textarea>
				<p class="text-xs text-text-muted mt-2">{textoLivre.trim().length}/20 caracteres minimos</p>
			</div>
		{:else}
			<!-- Disciplinas -->
			<div class="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
				{#each disciplinas as disc}
					<button
						onclick={() => { disciplinaSelecionada = disc.id; techSelecionada = ''; }}
						disabled={criando}
						class="text-left p-4 rounded-xl border transition-all cursor-pointer
							{disciplinaSelecionada === disc.id
								? 'bg-bg-card border-purple shadow-[0_0_16px_rgba(167,139,250,0.08)]'
								: 'bg-bg-card border-border-default hover:border-purple/40'}"
					>
						<div class="flex items-center gap-2 mb-1">
							<span class="text-[10px] font-mono px-1.5 py-0.5 rounded-full
								{disciplinaSelecionada === disc.id ? 'bg-purple/8 text-purple' : 'bg-bg-elevated text-text-muted'}">
								{disc.id}
							</span>
							<span class="text-xs font-medium text-text-primary truncate">{disc.nome}</span>
						</div>
						<p class="text-xs text-text-secondary line-clamp-2">{disc.descricao}</p>
					</button>
				{/each}
			</div>

			{#if disciplinaAtual}
				<div class="bg-bg-card rounded-xl border border-border-default p-5 animate-fade-up">
					<p class="text-sm font-medium text-text-primary mb-3">{disciplinaAtual.id} — {disciplinaAtual.nome}</p>

					<p class="label-upper mb-2">Tecnologia</p>
					<div class="flex flex-wrap gap-2 mb-4">
						{#each techsDisponiveis as tech}
							<button
								onclick={() => techSelecionada = tech}
								disabled={criando}
								class="px-3 py-1.5 rounded-full text-sm font-medium transition-all cursor-pointer
									{techSelecionada === tech
										? 'bg-purple text-bg-global'
										: 'bg-purple/8 text-purple border border-purple/20 hover:bg-purple/15'}"
							>{tech}</button>
						{/each}
					</div>

					<label class="block text-xs text-text-muted mb-1.5">Tema (opcional)</label>
					<input type="text" bind:value={temaCustom} placeholder="Ex: Como reduzir custo de inferencia..."
						disabled={criando}
						class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
							focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all placeholder:text-text-muted" />
				</div>
			{/if}
		{/if}
	</div>

	<!-- Erro -->
	{#if erro}
		<div class="mb-4" data-testid="msg-erro">
			<Banner type="error" ondismiss={() => erro = ''}>{erro}</Banner>
		</div>
	{/if}

	<!-- Botao Criar -->
	<button
		data-testid="btn-criar-pipeline"
		onclick={criarPipeline}
		disabled={!podeCriar || criando}
		class="w-full py-3.5 px-6 rounded-full font-medium text-bg-global transition-all duration-300 cursor-pointer
			bg-purple hover:shadow-[0_0_30px_rgba(167,139,250,0.3)] hover:opacity-90
			disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]"
	>
		{#if criando}
			<span class="inline-flex items-center gap-2">
				<span class="w-4 h-4 border-2 border-bg-global/30 border-t-bg-global rounded-full animate-spin"></span>
				Iniciando pipeline...
			</span>
		{:else}
			{isFunil ? 'Criar Funil de Conteudo' : `Criar ${labelFormato}`}
		{/if}
	</button>
</div>
