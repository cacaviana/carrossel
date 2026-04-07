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

	const MAX_SLIDES = 9; // incluindo capa e CTA
	const MAX_CHARS_SLIDE = 500;
	const MAX_CHARS_IDEIA = 2000;

	function adicionarSlide() {
		if (slidesTexto.length >= MAX_SLIDES) return;
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

	const formatoRaw = $derived(page.url.searchParams.get('formato'));
	const formatoAtual = $derived(formatoRaw ?? 'carrossel');
	const showLanding = $derived(!formatoRaw);
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
	<title>{showLanding ? 'Content Factory' : `${labelFormato} — Content Factory`}</title>
</svelte:head>

{#if showLanding}
<!-- ========== LANDING ========== -->
<div class="animate-fade-up max-w-4xl mx-auto">
	<!-- Hero -->
	<div class="text-center mb-12 pt-8">
		<div class="inline-flex items-center gap-3 mb-6">
			<div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple to-purple-deep flex items-center justify-center text-white font-bold text-lg shadow-[0_0_30px_rgba(167,139,250,0.2)]">
				CF
			</div>
			<h1 class="text-3xl font-light text-text-primary tracking-tight">Content <span class="font-semibold bg-gradient-to-r from-purple to-green bg-clip-text text-transparent">Factory</span></h1>
		</div>
		<p class="text-lg text-text-secondary font-light max-w-md mx-auto">Crie conteudo visual profissional em minutos com IA</p>
	</div>

	<!-- O que voce quer criar hoje? -->
	<div class="mb-8">
		<p class="text-center text-sm text-text-muted uppercase tracking-widest mb-6">O que voce quer criar hoje?</p>

		<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
			<!-- Carrossel -->
			<a href="/?formato=carrossel" class="group block p-6 rounded-2xl border border-border-default bg-bg-card hover:border-purple/40 hover:shadow-[0_0_30px_rgba(167,139,250,0.08)] transition-all duration-300 no-underline">
				<div class="flex items-center gap-3 mb-3">
					<div class="w-10 h-10 rounded-xl bg-purple/10 flex items-center justify-center text-purple">
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
					</div>
					<div>
						<h3 class="text-base font-semibold text-text-primary group-hover:text-purple transition-colors">Carrossel</h3>
						<p class="text-[11px] text-text-muted">1080 x 1350 · LinkedIn, Instagram</p>
					</div>
				</div>
				<p class="text-xs text-text-secondary leading-relaxed">Crie carrosseis de ate 9 slides com texto tecnico real, codigo funcional e visual dark mode premium.</p>
			</a>

			<!-- Post Unico -->
			<a href="/?formato=post_unico" class="group block p-6 rounded-2xl border border-border-default bg-bg-card hover:border-green/40 hover:shadow-[0_0_30px_rgba(52,211,153,0.08)] transition-all duration-300 no-underline">
				<div class="flex items-center gap-3 mb-3">
					<div class="w-10 h-10 rounded-xl bg-green/10 flex items-center justify-center text-green">
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
					</div>
					<div>
						<h3 class="text-base font-semibold text-text-primary group-hover:text-green transition-colors">Post Unico</h3>
						<p class="text-[11px] text-text-muted">1080 x 1080 · Instagram, Facebook, LinkedIn</p>
					</div>
				</div>
				<p class="text-xs text-text-secondary leading-relaxed">Uma imagem de impacto com texto grande e direto. Perfeita pra engajamento rapido no feed.</p>
			</a>

			<!-- Thumbnail YouTube -->
			<a href="/?formato=thumbnail_youtube" class="group block p-6 rounded-2xl border border-border-default bg-bg-card hover:border-red/40 hover:shadow-[0_0_30px_rgba(248,113,113,0.08)] transition-all duration-300 no-underline">
				<div class="flex items-center gap-3 mb-3">
					<div class="w-10 h-10 rounded-xl bg-red/10 flex items-center justify-center text-red">
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
					</div>
					<div>
						<h3 class="text-base font-semibold text-text-primary group-hover:text-red transition-colors">Thumbnail YouTube</h3>
						<p class="text-[11px] text-text-muted">1280 x 720 · YouTube</p>
					</div>
				</div>
				<p class="text-xs text-text-secondary leading-relaxed">Thumbnails com rosto grande e texto de impacto. Estilo YouTube moderno que maximiza CTR.</p>
			</a>

			<!-- Capa Reels -->
			<a href="/?formato=capa_reels" class="group block p-6 rounded-2xl border border-border-default bg-bg-card hover:border-amber/40 hover:shadow-[0_0_30px_rgba(251,191,36,0.08)] transition-all duration-300 no-underline">
				<div class="flex items-center gap-3 mb-3">
					<div class="w-10 h-10 rounded-xl bg-amber/10 flex items-center justify-center text-amber">
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
					</div>
					<div>
						<h3 class="text-base font-semibold text-text-primary group-hover:text-amber transition-colors">Capa Reels</h3>
						<p class="text-[11px] text-text-muted">1080 x 1920 · Instagram Reels, TikTok</p>
					</div>
				</div>
				<p class="text-xs text-text-secondary leading-relaxed">Capas verticais que param o scroll. Visual full-screen pra Reels e TikTok.</p>
			</a>
		</div>

		<!-- Funil -->
		<a href="/?formato=funil" class="group block mt-4 p-5 rounded-2xl border border-dashed border-purple/30 bg-bg-card hover:border-purple/60 hover:shadow-[0_0_30px_rgba(167,139,250,0.05)] transition-all duration-300 no-underline text-center">
			<div class="flex items-center justify-center gap-3">
				<div class="w-8 h-8 rounded-lg bg-purple/10 flex items-center justify-center text-purple">
					<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" /></svg>
				</div>
				<div class="text-left">
					<h3 class="text-sm font-semibold text-text-primary group-hover:text-purple transition-colors">Funil de Conteudo</h3>
					<p class="text-[11px] text-text-muted">3-5 pecas conectadas · Topo, Meio, Fundo, Conversao</p>
				</div>
				<span class="ml-auto px-2 py-0.5 rounded-full text-[10px] font-mono bg-purple/8 text-purple border border-purple/20">Em breve</span>
			</div>
		</a>
	</div>

	<!-- Stats -->
	<div class="grid grid-cols-3 gap-4 mt-8">
		<div class="text-center p-4 rounded-xl bg-bg-card border border-border-default">
			<p class="text-2xl font-light text-purple">{brands.length}</p>
			<p class="text-[11px] text-text-muted mt-1">Marcas</p>
		</div>
		<div class="text-center p-4 rounded-xl bg-bg-card border border-border-default">
			<p class="text-2xl font-light text-green">4</p>
			<p class="text-[11px] text-text-muted mt-1">Formatos</p>
		</div>
		<div class="text-center p-4 rounded-xl bg-bg-card border border-border-default">
			<p class="text-2xl font-light text-amber">6</p>
			<p class="text-[11px] text-text-muted mt-1">Agentes IA</p>
		</div>
	</div>
</div>

{:else}
<!-- ========== WIZARD (formato selecionado) ========== -->
<div class="animate-fade-up max-w-3xl mx-auto">
	<!-- Header -->
	<div class="mb-6">
		<a href="/" class="text-xs text-text-muted hover:text-purple transition-colors mb-2 inline-block">&larr; Voltar</a>
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
								maxlength={MAX_CHARS_SLIDE}
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

				{#if !isSlideUnico && slidesTexto.length < MAX_SLIDES}
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
					maxlength={MAX_CHARS_IDEIA}
					disabled={criando}
					class="w-full px-4 py-3 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
						focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all resize-y
						placeholder:text-text-muted"
				></textarea>
				<p class="text-xs text-text-muted mt-2">{textoLivre.trim().length}/20 min · {MAX_CHARS_IDEIA} max</p>
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
{/if}
