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
			? [{ id: 'sim' as AvatarMode, label: 'Com avatar', tip: 'Sua foto aparece na thumbnail' }]
			: formatoAtual === 'post_unico' || formatoAtual === 'capa_reels'
				? [
					{ id: 'sim' as AvatarMode, label: 'Com avatar', tip: 'Sua foto aparece na imagem' },
					{ id: 'sem' as AvatarMode, label: 'Sem avatar', tip: 'Imagem sem foto de pessoa' }
				]
				: [
					{ id: 'capa' as AvatarMode, label: 'Avatar na capa', tip: 'Foto so no primeiro slide' },
					{ id: 'livre' as AvatarMode, label: 'Avatar livre', tip: 'A IA decide onde encaixar sua foto' },
					{ id: 'sem' as AvatarMode, label: 'Sem avatar', tip: 'Nenhum slide tera foto de pessoa' }
				]
	);

	// Formatos de slide unico: default com avatar
	$effect(() => {
		if (formatoAtual === 'thumbnail_youtube' || formatoAtual === 'post_unico' || formatoAtual === 'capa_reels') avatarMode = 'sim';
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
	let maxSlidesIdeia = $state(7);

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

	const formatoDesc: Record<string, string> = {
		carrossel: 'Crie slides completos 10x mais rapido com muito mais engajamento.',
		post_unico: 'Uma imagem que para o scroll e gera conversa no feed.',
		thumbnail_youtube: 'A thumbnail que faz o clique acontecer antes do titulo.',
		capa_reels: 'A capa que transforma scroll em visualizacao completa.',
		funil: 'Conteudo conectado que leva sua audiencia do interesse a acao.'
	};

	const formatoRaw = $derived(page.url.searchParams.get('formato'));
	const formatoAtual = $derived(formatoRaw ?? 'carrossel');
	const showLanding = $derived(!formatoRaw);
	const isFunil = $derived(formatoAtual === 'funil');
	const labelFormato = $derived(formatoLabels[formatoAtual] ?? 'Carrossel');
	const dimFormato = $derived(formatoDims[formatoAtual] ?? '');
	const descFormato = $derived(formatoDesc[formatoAtual] ?? '');

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

			if (modoEntrada === 'ideia') {
				payload.max_slides = maxSlidesIdeia;
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
<!-- ========== LANDING — HERO BANNER ========== -->
<div class="hero-bg min-h-screen relative overflow-hidden">
		<!-- Subtle decorative blobs -->
		<div class="absolute inset-0 overflow-hidden pointer-events-none">
			<div class="absolute w-[500px] h-[500px] rounded-full top-[-10%] right-[-5%] opacity-20"
				style="background: radial-gradient(circle, rgba(53,120,176,0.25) 0%, rgba(53,120,176,0.08) 40%, transparent 70%); filter: blur(80px);"></div>
			<div class="absolute w-[400px] h-[400px] rounded-full bottom-[-15%] left-[10%] opacity-15"
				style="background: radial-gradient(circle, rgba(122,173,166,0.3) 0%, rgba(122,173,166,0.1) 50%, transparent 70%); filter: blur(60px);"></div>
			<div class="absolute w-[250px] h-[250px] rounded-full top-[30%] left-[40%] opacity-10"
				style="background: radial-gradient(circle, rgba(53,120,176,0.2) 0%, transparent 60%); filter: blur(50px);"></div>
		</div>

		<div class="max-w-[1200px] mx-auto px-6 sm:px-8 lg:px-10 py-2 sm:py-6 lg:py-10">
			<!-- Tag -->
			<div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-steel-3/8 border border-steel-3/20 mb-8">
				<span class="text-xs font-medium text-steel-3 tracking-wide">IA + Design que converte</span>
			</div>

			<!-- Headline -->
			<h1 class="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold text-steel-6 leading-[1.1] mb-5 max-w-5xl">
				Crie conteúdos virais<br>
				<span class="hero-galaxy-text">em segundos com IA</span>
			</h1>

			<!-- Subtitle -->
			<p class="text-lg sm:text-xl lg:text-2xl text-steel-4 font-light mb-8 max-w-2xl">
				Do zero ao post pronto para Instagram sem esforco.
			</p>

			<!-- Bullet points — staggered entrance -->
			<ul class="space-y-2.5 mb-8">
				{#each [
					'Escolha o formato e deixe a IA montar o briefing pra voce',
					'Decida o tema ou jogue uma ideia — o Strategist faz o resto',
					'Aprove o texto, edite se quiser, sem surpresas no resultado',
					'Gere imagens virais prontas pra postar em qualquer plataforma'
				] as item, i}
					<li class="hero-check flex items-center gap-2.5 text-sm sm:text-base text-steel-5" style="animation-delay: {0.3 + i * 0.2}s">
						<span class="w-6 h-6 rounded-full bg-steel-3/12 flex items-center justify-center shrink-0">
							<svg class="w-3.5 h-3.5 text-steel-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
						</span>
						{item}
					</li>
				{/each}
			</ul>

			<!-- O que voce quer criar -->
			<p class="text-sm text-steel-4 uppercase tracking-widest mb-4">O que voce quer criar hoje?</p>

			<!-- CTA -->
			<a
				href="/?formato=carrossel"
				class="group inline-flex items-center gap-2.5 px-7 py-3.5 rounded-full font-semibold text-sm text-white no-underline mb-8
					border border-steel-3/30 transition-all duration-300
					hover:shadow-[0_0_35px_rgba(53,120,176,0.2)] hover:border-steel-3/60"
				style="background: linear-gradient(135deg, #3578B0 0%, #265A87 100%);"
			>
				Gerar meu carrossel agora
				<svg class="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
			</a>

			<!-- Social proof -->
			<div class="flex items-center gap-3 mt-2">
				<div class="flex -space-x-2">
					<div class="w-8 h-8 rounded-full bg-steel-3/20 border-2 border-bg-global flex items-center justify-center text-[10px] text-steel-3 font-bold">C</div>
					<div class="w-8 h-8 rounded-full bg-teal-6/20 border-2 border-bg-global flex items-center justify-center text-[10px] text-teal-6 font-bold">V</div>
					<div class="w-8 h-8 rounded-full bg-amber/20 border-2 border-bg-global flex items-center justify-center text-[10px] text-amber font-bold">P</div>
				</div>
				<p class="text-sm text-steel-4">+2.847 criadores ja estao criando conteudo 10x mais rapido</p>
			</div>
		</div>
</div>

{:else}
<div class="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
<!-- ========== WIZARD (formato selecionado) ========== -->
<div class="animate-fade-up max-w-3xl mx-auto">
	<!-- Header -->
	<div class="mb-8">
		<a href="/" class="text-xs text-text-muted hover:text-steel-3 transition-colors mb-3 inline-flex items-center gap-1">
			<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
			Voltar
		</a>
		<h1 class="text-4xl sm:text-5xl font-bold text-steel-6 mb-2">
			{labelFormato}
		</h1>
		<p class="text-base sm:text-lg text-text-secondary font-light">{descFormato}</p>
		<div class="flex items-center gap-2 mt-3">
			<span class="px-2.5 py-1 rounded-full text-[11px] font-mono bg-bg-elevated border border-border-default text-text-muted">{dimFormato}</span>
		</div>
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
						title={opt.tip}
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
				<p class="text-sm text-text-secondary mb-3">Tenho uma ideia e preciso criar um design surpreendente.</p>

				<!-- Slides -->
				<div class="space-y-3 max-h-[60vh] overflow-y-auto pr-1 scrollbar-thin">
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
				<p class="text-sm text-text-secondary mb-3">Me surpreenda com algo viral do inicio ao fim.</p>
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
				<div class="flex items-center justify-between mt-3">
					<p class="text-xs text-text-muted">{textoLivre.trim().length}/20 min · {MAX_CHARS_IDEIA} max</p>
					{#if !isSlideUnico}
						<div class="flex items-center gap-2">
							<span class="text-xs text-text-muted">Max slides:</span>
							<div class="flex gap-1">
								{#each [3, 5, 7, 10] as n}
									<button
										onclick={() => maxSlidesIdeia = n}
										class="w-7 h-7 rounded-full text-xs font-medium transition-all cursor-pointer
											{maxSlidesIdeia === n ? 'bg-purple text-bg-global' : 'text-text-muted border border-border-default hover:border-purple/40'}"
									>{n}</button>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			</div>
		{:else}
			<!-- Disciplinas -->
			<div class="bg-bg-card rounded-xl border border-border-default p-5 mb-4">
				<p class="text-sm text-text-secondary mb-4">Escolha a disciplina e a IA monta o conteudo tecnico pra voce.</p>
			</div>
			<div class="grid grid-cols-2 sm:grid-cols-3 gap-3 mb-4">
				{#each disciplinas as disc}
					<button
						onclick={() => { disciplinaSelecionada = disc.id; techSelecionada = ''; }}
						disabled={criando}
						class="text-left p-4 rounded-xl border transition-all cursor-pointer
							{disciplinaSelecionada === disc.id
								? 'bg-bg-card border-purple shadow-[0_0_16px_rgba(53,120,176,0.08)]'
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
			bg-purple hover:shadow-[0_0_30px_rgba(53,120,176,0.25)] hover:opacity-90
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
</div>
{/if}
