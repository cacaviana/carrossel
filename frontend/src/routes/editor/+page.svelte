<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { API_BASE } from '$lib/api';
	import { getDims } from '$lib/utils/dimensions';
	import SlideDotsNav from '$lib/components/ui/SlideDotsNav.svelte';

	const API = API_BASE;

	let slides = $state<string[]>([]);
	let textos = $state<{ titulo: string; corpo: string }[]>([]);
	let logoSrc = $state('');
	let logoPositions = $state<{ x: number; y: number }[]>([]);
	let logoSize = $state<number[]>([]);
	let currentSlide = $state(0);
	let salvando = $state(false);
	let carregando = $state(true);
	let regenerando = $state(false);
	let logoBordaCor = $state('#A78BFA');
	let logoVisivel = $state(true);
	let logoBordaAtiva = $state(true);
	let logoTamRodape = $state(60);
	let logoTamCentral = $state(200);
	let logoModo = $state<('rodape' | 'central')[]>([]);
	let regenerandoTodos = $state(false);
	let regenerandoTodosProgresso = $state('');
	let brandSlug = $state('');
	let ultimoFeedback = $state('');
	let slidesOriginal = $state<string[]>([]);
	let salvandoDrive = $state(false);
	let driveSalvo = $state('');
	let pipelineTema = $state('');
	let formato = $state('carrossel');

	const total = $derived(slides.length);
	const currentImage = $derived(slides[currentSlide] || '');
	const dims = $derived(getDims(formato));

	onMount(async () => {
		const pipelineId = page.url.searchParams.get('pipeline');
		const brand = page.url.searchParams.get('brand') || '';
		brandSlug = brand;

		// Carregar textos e tema da pipeline
		if (pipelineId) {
			try {
				const [copyRes, pipRes] = await Promise.all([
					fetch(`${API}/api/pipelines/${pipelineId}/etapas/copywriter`),
					fetch(`${API}/api/pipelines/${pipelineId}`),
				]);
				if (copyRes.ok) {
					const copyData = await copyRes.json();
					const saida = copyData.saida ?? {};
					// LLM retorna slides em formatos variados
					let copySlides: any[] = [];
					if (Array.isArray(saida.slides) && saida.slides.length > 0) copySlides = saida.slides;
					else if (saida.slide && typeof saida.slide === 'object') copySlides = [saida.slide];
					else {
						for (const k of Object.keys(saida)) {
							const v = saida[k];
							if (v && typeof v === 'object' && !Array.isArray(v) && Array.isArray(v.slides)) { copySlides = v.slides; break; }
							if (v && typeof v === 'object' && !Array.isArray(v) && v.titulo) { copySlides = [v]; break; }
						}
					}
					// Extrair texto de qualquer estrutura que o LLM retornar
					function extractStr(val: any): string {
						if (typeof val === 'string') return val;
						if (!val) return '';
						if (Array.isArray(val)) return val.map((item: any) => extractStr(item?.texto ?? item?.conteudo ?? item)).filter(Boolean).join(' ');
						if (typeof val !== 'object') return '';
						if (typeof val.texto === 'string') return val.texto;
						if (typeof val.conteudo === 'string') return val.conteudo;
						if (Array.isArray(val.conteudo)) return extractStr(val.conteudo);
						for (const k of Object.keys(val)) { if (typeof val[k] === 'string' && val[k].length > 3) return val[k]; }
						return '';
					}
					textos = copySlides.map((s: any) => {
						let titulo = extractStr(s.titulo) || extractStr(s.headline) || '';
						let corpo = extractStr(s.corpo) || extractStr(s.conteudo) || extractStr(s.texto) || extractStr(s.texto_principal) || '';
						if ((!titulo || !corpo) && Array.isArray(s.elementos)) {
							for (const el of s.elementos) {
								const t = el.tipo ?? '';
								const val = extractStr(el.texto) || extractStr(el.conteudo) || extractStr(el);
								if (!titulo && t.includes('titulo')) titulo = val;
								if (!corpo && (t.includes('card') || t === 'corpo' || t === 'subtitulo' || t === 'call_to_action')) corpo = val;
							}
						}
						return { titulo, corpo };
					});
				}
				if (pipRes.ok) {
					const pipData = await pipRes.json();
					pipelineTema = pipData.tema || '';
					formato = pipData.formato || 'carrossel';
				}
			} catch {}
		}

		// Carregar slides: tenta pipeline primeiro, senao pega do JSON da marca
		let slidesCarregados = false;
		if (pipelineId) {
			try {
				const res = await fetch(`${API}/api/pipelines/${pipelineId}/etapas/image_generator`);
				const data = await res.json();
				const imgs = (data.saida?.imagens || []).filter((i: any) => i.image_base64);
				if (imgs.length > 0) {
					slides = imgs.map((i: any) => i.image_base64.startsWith('data:') ? i.image_base64 : `data:image/png;base64,${i.image_base64}`);
					slidesCarregados = true;
				}
			} catch {}
		}
		if (!slidesCarregados && brand) {
			try {
				const res = await fetch(`${API}/api/editor/slides/${brand}`);
				if (res.ok) {
					const data = await res.json();
					slides = (data.imagens || []).map((i: any) => i.image_base64.startsWith('data:') ? i.image_base64 : `data:image/png;base64,${i.image_base64}`);
				}
			} catch {}
		}

		logoPositions = slides.map(() => ({ x: 50, y: getDims(formato).h - 70 }));
		logoSize = slides.map(() => 60);
		logoModo = slides.map(() => 'rodape' as const);
		slidesOriginal = [...slides];

		// Carregar foto da marca
		if (brand) {
			try {
				const brandRes2 = await fetch(`${API}/api/brands/${brand}`);
				if (brandRes2.ok) {
					const bd = await brandRes2.json();
					logoBordaCor = bd.foto?.borda_cor || bd.cores?.acento_principal || '#A78BFA';
				}
			} catch {}
			try {
				const res = await fetch(`${API}/api/brands/${brand}/foto`);
				if (res.ok) {
					const data = await res.json();
					if (data.foto) logoSrc = data.foto;
				}
			} catch {}
		}

		carregando = false;
	});

	async function regenerarTodos() {
		if (regenerandoTodos || textos.length === 0) return;
		regenerandoTodos = true;

		// Montar todos os slides de uma vez
		const allSlides = textos.map((txt, i) => {
			const tipo = i === 0 ? 'cover' : i === slides.length - 1 ? 'cta' : 'content';
			return tipo === 'cover'
				? { type: 'cover', headline: txt.titulo, subline: txt.corpo }
				: tipo === 'cta'
					? { type: 'cta', headline: txt.titulo, subline: txt.corpo, tags: [] }
					: { type: 'content', title: txt.titulo, bullets: (txt.corpo || '').split('\n').filter((l: string) => l.trim()), etapa: '' };
		});

		// Gerar todos de uma vez (o backend gera sequencialmente com referencia do primeiro)
		regenerandoTodosProgresso = `0/${allSlides.length}`;
		try {
			const res = await fetch(`${API}/api/gerar-imagem`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ slides: allSlides, brand_slug: brandSlug, formato }),
			});
			if (res.ok) {
				const data = await res.json();
				const imgs = data.images || [];
				for (let i = 0; i < imgs.length; i++) {
					if (imgs[i]) {
						slides[i] = imgs[i].startsWith('data:') ? imgs[i] : `data:image/png;base64,${imgs[i]}`;
					}
					regenerandoTodosProgresso = `${i + 1}/${allSlides.length}`;
				}
			}
		} catch {}
		regenerandoTodos = false;
		currentSlide = 0;
	}

	async function regenerarSlide(modo: 'texto' | 'tudo') {
		const txt = textos[currentSlide];
		if (regenerando) return;
		regenerando = true;
		ultimoFeedback = modo === 'texto' ? 'Corrigindo texto...' : 'Regenerando imagem...';
		try {
			// Pra slide unico (thumb/post), sempre usar type 'cover'
			const isUnico = slides.length === 1;
			const tipo = isUnico ? 'cover' : (currentSlide === 0 ? 'cover' : currentSlide === slides.length - 1 ? 'cta' : 'content');
			const titulo = txt?.titulo || '';
			const corpo = txt?.corpo || '';
			const slideData = tipo === 'cover'
				? { type: 'cover', headline: titulo, subline: corpo }
				: tipo === 'cta'
					? { type: 'cta', headline: titulo, subline: corpo, tags: [] }
					: { type: 'content', title: titulo, bullets: corpo.split('\n').filter((l: string) => l.trim()), etapa: '' };

			if (modo === 'texto') {
				// Sempre mandar a imagem ORIGINAL (nao a ultima tentativa falha)
				const imgOriginal = slidesOriginal[currentSlide] || slides[currentSlide];
				const res = await fetch(`${API}/api/editor/corrigir-texto`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						image: imgOriginal,
						slide: slideData,
						brand_slug: brandSlug,
					}),
				});
				if (res.ok) {
					const data = await res.json();
					if (data.image) {
						const newImg = data.image.startsWith('data:') ? data.image : `data:image/png;base64,${data.image}`;
						slides = slides.map((s, i) => i === currentSlide ? newImg : s);
						const t = data.tentativas || '?';
						const aviso = data.aviso || '';
						ultimoFeedback = `Tentativa ${t}/3${aviso ? ' — ' + aviso : ''}`;
						setTimeout(() => ultimoFeedback = '', 5000);
					}
				}
			} else {
				const res = await fetch(`${API}/api/gerar-imagem`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						slides: [slideData],
						brand_slug: brandSlug,
						formato,
						...(feedbackRegenerar.trim() ? { instrucao_extra: feedbackRegenerar.trim() } : {}),
					}),
				});
				feedbackRegenerar = '';
				if (res.ok) {
					const data = await res.json();
					if (data.images?.[0]) {
						const newImg = data.images[0].startsWith('data:') ? data.images[0] : `data:image/png;base64,${data.images[0]}`;
						slides = slides.map((s, i) => i === currentSlide ? newImg : s);
						ultimoFeedback = 'Imagem regenerada!';
						setTimeout(() => ultimoFeedback = '', 3000);
					} else {
						ultimoFeedback = 'Gemini nao retornou imagem. Tente novamente.';
						setTimeout(() => ultimoFeedback = '', 5000);
					}
				} else {
					ultimoFeedback = 'Erro ao regenerar imagem.';
					setTimeout(() => ultimoFeedback = '', 5000);
				}
			}
		} catch (e) {
			ultimoFeedback = 'Erro: ' + (e instanceof Error ? e.message : 'falha na requisicao');
			setTimeout(() => ultimoFeedback = '', 5000);
		}
		finally { regenerando = false; }
	}

	function handleClick(e: MouseEvent) {
		if (!logoSrc) return;
		const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
		const scaleX = dims.w / rect.width;
		const scaleY = dims.h / rect.height;
		logoPositions[currentSlide] = {
			x: Math.round((e.clientX - rect.left) * scaleX),
			y: Math.round((e.clientY - rect.top) * scaleY),
		};
	}

	function aplicarPosicaoEmTodos() {
		const pos = logoPositions[currentSlide];
		const size = logoSize[currentSlide];
		logoPositions = logoPositions.map(() => ({ ...pos }));
		logoSize = logoSize.map(() => size);
	}

	function proximo() {
		if (currentSlide < total - 1) currentSlide++;
	}

	function anterior() {
		if (currentSlide > 0) currentSlide--;
	}

	function handleLogoUpload(e: Event) {
		const file = (e.target as HTMLInputElement).files?.[0];
		if (!file) return;
		const reader = new FileReader();
		reader.onload = async () => {
			logoSrc = reader.result as string;
			// Salvar na config da marca tambem
			if (brandSlug) {
				try {
					await fetch(`${API}/api/brands/${brandSlug}/foto`, {
						method: 'PUT',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify({ foto: logoSrc }),
					});
				} catch {}
			}
		};
		reader.readAsDataURL(file);
	}

	function _buildPdfPayload() {
		return {
			slides: slides.map((img, i) => ({
				image: img,
				logo_x: logoVisivel ? (logoPositions[i]?.x ?? 50) : 0,
				logo_y: logoVisivel ? (logoPositions[i]?.y ?? 1280) : 0,
				logo_size: logoVisivel ? (logoSize[i] || 60) : 0,
			})),
			logo: logoVisivel ? logoSrc : '',
			borda_cor: logoVisivel && logoBordaAtiva ? logoBordaCor : null,
			formato,
		};
	}

	async function _gerarPdfBase64(): Promise<{ pdf_base64: string; images: string[] } | null> {
		const res = await fetch(`${API}/api/editor/salvar-pdf`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(_buildPdfPayload()),
		});
		if (!res.ok) return null;
		const data = await res.json();
		return { pdf_base64: data.pdf_base64, images: slides };
	}

	let qualidade = $state<'media' | 'alta'>('alta');
	let removendoTexto = $state(false);
	let feedbackRegenerar = $state('');

	async function baixarPDF() {
		if (!logoSrc || slides.length === 0) return;
		salvando = true;
		try {
			const result = await _gerarPdfBase64();
			if (result) {
				const link = document.createElement('a');
				link.href = `data:application/pdf;base64,${result.pdf_base64}`;
				link.download = 'carrossel.pdf';
				link.click();
			}
		} catch {}
		finally { salvando = false; }
	}

	function _downloadViaCanvas(format: 'png' | 'jpeg') {
		const img = new Image();
		img.onload = () => {
			const scale = qualidade === 'alta' ? 1 : 0.6;
			const canvas = document.createElement('canvas');
			canvas.width = img.naturalWidth * scale;
			canvas.height = img.naturalHeight * scale;
			const ctx = canvas.getContext('2d')!;
			ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
			const mimeType = format === 'jpeg' ? 'image/jpeg' : 'image/png';
			const jpegQuality = qualidade === 'alta' ? 0.95 : 0.75;
			const dataUrl = canvas.toDataURL(mimeType, jpegQuality);
			const link = document.createElement('a');
			link.href = dataUrl;
			link.download = `slide-${String(currentSlide + 1).padStart(2, '0')}.${format}`;
			link.click();
		};
		img.src = currentImage;
	}

	function baixarPNG() { _downloadViaCanvas('png'); }
	function baixarJPEG() { _downloadViaCanvas('jpeg'); }

	async function removerTexto() {
		if (removendoTexto) return;
		removendoTexto = true;
		ultimoFeedback = 'Gerando versao sem texto...';
		try {
			const res = await fetch(`${API}/api/gerar-imagem`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					slides: [{
						type: 'content',
						title: '',
						bullets: [],
						etapa: 'SEM_TEXTO',
						sem_texto: true,
					}],
					brand_slug: brandSlug,
					formato,
					instrucao_extra: 'Gere a imagem SEM NENHUM TEXTO. Apenas o fundo, elementos decorativos e ilustracao. NENHUMA letra, NENHUMA palavra, NENHUM numero visivel na imagem.',
				}),
			});
			if (res.ok) {
				const data = await res.json();
				if (data.images?.[0]) {
					const newImg = data.images[0].startsWith('data:') ? data.images[0] : `data:image/png;base64,${data.images[0]}`;
					slides = slides.map((s, i) => i === currentSlide ? newImg : s);
					ultimoFeedback = 'Imagem sem texto gerada!';
					setTimeout(() => ultimoFeedback = '', 3000);
				}
			} else {
				ultimoFeedback = 'Erro ao gerar sem texto.';
				setTimeout(() => ultimoFeedback = '', 5000);
			}
		} catch {
			ultimoFeedback = 'Erro na requisicao.';
			setTimeout(() => ultimoFeedback = '', 5000);
		} finally {
			removendoTexto = false;
		}
	}

	async function salvarNoDrive() {
		if (!logoSrc || slides.length === 0) return;
		salvandoDrive = true;
		driveSalvo = '';
		try {
			const result = await _gerarPdfBase64();
			if (!result) throw new Error('Falha ao gerar PDF');

			const imagesClean = result.images.map(img =>
				img.startsWith('data:') ? img.split(',')[1] : img
			);

			const res = await fetch(`${API}/api/google-drive/carrossel`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					title: pipelineTema || 'carrossel',
					pdf_base64: result.pdf_base64,
					images_base64: imagesClean,
					disciplina: null,
					tecnologia_principal: null,
					tipo_carrossel: 'texto',
					legenda_linkedin: null,
				}),
			});
			if (!res.ok) {
				const err = await res.json().catch(() => ({}));
				throw new Error(err.detail || 'Erro ao salvar no Drive');
			}
			const data = await res.json();
			driveSalvo = data.web_view_link;
		} catch (e) {
			alert(e instanceof Error ? e.message : 'Erro ao salvar no Drive');
		} finally {
			salvandoDrive = false;
		}
	}
</script>

<svelte:head><title>Editor — Posicionar Logo</title></svelte:head>

<div class="max-w-4xl mx-auto p-4">

	{#if carregando}
		<div class="text-center py-20 text-text-muted">Carregando slides...</div>

	{:else if slides.length === 0}
		<div class="text-center py-20 text-text-muted">Nenhum slide encontrado.</div>

	{:else}
		<!-- Header -->
		<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
			<h1 class="text-lg font-medium text-text-primary">
				Slide {currentSlide + 1} de {total}
			</h1>
			<div class="flex flex-wrap items-center gap-2">
				<button onclick={regenerarTodos} disabled={regenerandoTodos}
					class="px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer
						{regenerandoTodos ? 'bg-red-500/20 text-red-400' : 'text-red-400 border border-red-500/30 hover:bg-red-500/10'}
						disabled:opacity-50">
					{regenerandoTodos ? `Gerando ${regenerandoTodosProgresso}...` : 'Regenerar todos'}
				</button>
				{#if !logoSrc}
					<label class="px-4 py-2 rounded-full text-sm font-medium text-purple border border-purple/20 hover:bg-purple/8 cursor-pointer">
						Upload logo
						<input type="file" accept="image/*" onchange={handleLogoUpload} class="hidden" />
					</label>
				{:else}
					<img src={logoSrc} alt="Logo" class="w-8 h-8 rounded-full object-cover border border-purple" />
					<button onclick={aplicarPosicaoEmTodos}
						class="px-3 py-1.5 rounded-full text-xs font-medium text-text-secondary border border-border-default hover:border-purple/40 cursor-pointer">
						Igual em todos
					</button>
				{/if}
			</div>
		</div>

		<!-- Slide preview -->
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div
			class="relative mx-auto rounded-xl overflow-hidden shadow-2xl cursor-crosshair"
			style="max-width: 540px; aspect-ratio: {dims.cssRatio};"
			onclick={handleClick}
		>
			<img src={currentImage} alt="Slide {currentSlide + 1}" class="w-full h-full object-cover" />

			{#if logoVisivel && logoSrc && logoPositions[currentSlide]}
				<div
					class="absolute rounded-full overflow-hidden shadow-lg pointer-events-none"
					style="
						left: {logoPositions[currentSlide].x / dims.w * 100}%;
						top: {logoPositions[currentSlide].y / dims.h * 100}%;
						width: {(logoSize[currentSlide] || 60) / dims.w * 100}%;
						aspect-ratio: 1;
						transform: translate(-50%, -50%);
						{logoBordaAtiva ? `border: 2px solid ${logoBordaCor}50; box-shadow: 0 0 12px ${logoBordaCor}40;` : ''}
					opacity: 0.9;
					"
				>
					<img src={logoSrc} alt="Logo" class="w-full h-full object-cover" />
				</div>
			{/if}
		</div>

		<!-- Texto esperado + Regenerar -->
		{#if textos[currentSlide]}
			<div class="mt-3 mx-auto bg-bg-card rounded-xl border border-border-default p-4" style="max-width: 540px;">
				<div>
					<div class="mb-3">
						<p class="text-[10px] text-text-muted uppercase tracking-wider mb-1">Texto esperado</p>
						<p class="text-sm text-text-primary font-medium">{textos[currentSlide].titulo}</p>
						{#if textos[currentSlide].corpo}
							<p class="text-xs text-text-secondary mt-1 whitespace-pre-line">{textos[currentSlide].corpo}</p>
						{/if}
					</div>
					<!-- Feedback para regenerar -->
					<div class="mb-2">
						<input
							type="text"
							bind:value={feedbackRegenerar}
							placeholder="Feedback: ex. mais escuro, menos texto, trocar ilustracao..."
							disabled={regenerando || removendoTexto}
							class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs
								focus:border-purple focus:ring-2 focus:ring-purple/12 outline-none transition-all
								placeholder:text-text-muted disabled:opacity-50"
						/>
					</div>
					<div class="flex flex-wrap gap-2">
						<button onclick={() => regenerarSlide('texto')} disabled={regenerando || removendoTexto}
							class="px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer
								{regenerando ? 'bg-amber/20 text-amber' : 'text-amber border border-amber/30 hover:bg-amber/10'}
								disabled:opacity-50">
							{regenerando ? 'Gerando...' : 'Corrigir texto'}
						</button>
						<button onclick={() => regenerarSlide('tudo')} disabled={regenerando || removendoTexto}
							class="px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer
								{regenerando ? 'bg-purple/20 text-purple' : 'text-purple border border-purple/30 hover:bg-purple/10'}
								disabled:opacity-50">
							{regenerando ? 'Gerando...' : feedbackRegenerar.trim() ? 'Regenerar com feedback' : 'Regenerar slide'}
						</button>
						<button onclick={removerTexto} disabled={regenerando || removendoTexto}
							class="px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer
								{removendoTexto ? 'bg-red/20 text-red' : 'text-red border border-red/30 hover:bg-red/10'}
								disabled:opacity-50">
							{removendoTexto ? 'Gerando...' : 'Tirar texto'}
						</button>
					</div>
				</div>
			</div>
		{/if}

		{#if !logoSrc}
			<div class="mt-3 mx-auto text-center bg-amber/10 border border-amber/30 rounded-xl p-4" style="max-width: 540px;">
				<p class="text-sm text-amber font-medium mb-2">Logo nao encontrada na config da marca</p>
				<p class="text-xs text-text-muted mb-3">Va em Configuracoes → Marcas → Upload foto, ou faca upload aqui:</p>
				<label class="inline-flex px-4 py-2 rounded-full text-xs font-medium text-purple border border-purple/20 hover:bg-purple/8 cursor-pointer">
					Upload logo agora
					<input type="file" accept="image/*" onchange={handleLogoUpload} class="hidden" />
				</label>
			</div>
		{:else}
			<div class="mt-3 mx-auto bg-bg-card rounded-xl border border-border-default p-3" style="max-width: 540px;">
				<div class="flex flex-wrap items-center gap-3">
					<!-- Toggle logo -->
					<label class="flex items-center gap-1.5 text-[11px] text-text-muted cursor-pointer shrink-0">
						<input type="checkbox" bind:checked={logoVisivel} class="rounded" />
						Logo
					</label>

					{#if logoVisivel}
					<!-- Modo: rodape ou central -->
					<div class="flex gap-1">
						<button onclick={() => { logoModo[currentSlide] = 'rodape'; logoSize[currentSlide] = logoTamRodape; }}
							class="px-3 py-1 rounded-full text-[11px] font-medium transition-all cursor-pointer
								{logoModo[currentSlide] === 'rodape' ? 'bg-purple/15 text-purple' : 'text-text-muted hover:text-text-secondary'}">
							Rodape
						</button>
						<button onclick={() => { logoModo[currentSlide] = 'central'; logoSize[currentSlide] = logoTamCentral; }}
							class="px-3 py-1 rounded-full text-[11px] font-medium transition-all cursor-pointer
								{logoModo[currentSlide] === 'central' ? 'bg-purple/15 text-purple' : 'text-text-muted hover:text-text-secondary'}">
							Central
						</button>
					</div>

					<!-- Borda -->
					<label class="flex items-center gap-1 text-[11px] text-text-muted cursor-pointer">
						<input type="checkbox" bind:checked={logoBordaAtiva} class="rounded" />
						Borda
						{#if logoBordaAtiva}
							<span class="w-3 h-3 rounded-full" style="background: {logoBordaCor}"></span>
						{/if}
					</label>

					<!-- Tamanhos — linha separada -->
					<div class="w-full flex flex-wrap items-center gap-x-4 gap-y-2 pt-2 border-t border-border-default">
						<div class="flex items-center gap-1.5">
							<span class="text-[10px] text-text-muted">Rodape:</span>
							<input type="range" min="30" max="300" bind:value={logoTamRodape}
								oninput={() => { logoSize = logoSize.map((s, i) => logoModo[i] === 'rodape' ? logoTamRodape : s); }}
								class="w-20" />
							<span class="text-[9px] text-text-muted font-mono w-6">{logoTamRodape}</span>
						</div>
						<div class="flex items-center gap-1.5">
							<span class="text-[10px] text-text-muted">Central:</span>
							<input type="range" min="60" max="400" bind:value={logoTamCentral}
								oninput={() => { logoSize = logoSize.map((s, i) => logoModo[i] === 'central' ? logoTamCentral : s); }}
								class="w-20" />
							<span class="text-[9px] text-text-muted font-mono w-6">{logoTamCentral}</span>
						</div>
					</div>
					{/if}
				</div>
			</div>
			{#if driveSalvo}
				<p class="text-center text-xs text-green mt-2">Salvo no Drive! <a href={driveSalvo} target="_blank" class="underline font-medium">Abrir no Google Drive</a></p>
			{:else if ultimoFeedback}
				<p class="text-center text-xs text-amber mt-1">{ultimoFeedback}</p>
			{:else}
				<p class="text-center text-xs text-text-muted mt-1">Clique no slide pra posicionar</p>
			{/if}
		{/if}

		<!-- Navegacao -->
		<div class="mt-6 space-y-3">
			<!-- Dots -->
			<div class="flex justify-center">
				<SlideDotsNav total={total} current={currentSlide} onSelect={(i) => currentSlide = i} />
			</div>

			<div class="flex flex-wrap items-center justify-between gap-3">
				<button onclick={anterior} disabled={currentSlide === 0}
					class="px-6 py-2.5 rounded-full text-sm font-medium transition-all cursor-pointer
						{currentSlide === 0 ? 'text-text-muted opacity-30' : 'text-text-secondary border border-border-default hover:border-purple/40'}">
					Anterior
				</button>

				{#if currentSlide < total - 1}
					<button onclick={proximo}
						class="px-6 py-2.5 rounded-full text-sm font-medium text-bg-global bg-purple hover:opacity-90 cursor-pointer transition-all">
						Proximo
					</button>
				{:else}
					<div class="flex flex-col sm:flex-row flex-wrap gap-2 items-center">
						<!-- Qualidade -->
						<div class="flex gap-1 mr-2">
							<button onclick={() => qualidade = 'media'}
								class="px-3 py-1.5 rounded-full text-[11px] font-medium transition-all cursor-pointer
									{qualidade === 'media' ? 'bg-purple/15 text-purple' : 'text-text-muted hover:text-text-secondary'}">
								Media
							</button>
							<button onclick={() => qualidade = 'alta'}
								class="px-3 py-1.5 rounded-full text-[11px] font-medium transition-all cursor-pointer
									{qualidade === 'alta' ? 'bg-purple/15 text-purple' : 'text-text-muted hover:text-text-secondary'}">
								Alta
							</button>
						</div>
						<!-- Formatos -->
						<button onclick={baixarPNG}
							class="px-4 py-2.5 rounded-full text-sm font-medium text-text-secondary border border-border-default hover:border-purple/40 cursor-pointer transition-all">
							PNG
						</button>
						<button onclick={baixarJPEG}
							class="px-4 py-2.5 rounded-full text-sm font-medium text-text-secondary border border-border-default hover:border-purple/40 cursor-pointer transition-all">
							JPEG
						</button>
						<button onclick={baixarPDF} disabled={salvando || !logoSrc}
							class="px-4 py-2.5 rounded-full text-sm font-medium text-bg-global bg-purple hover:opacity-90 cursor-pointer transition-all disabled:opacity-50">
							{salvando ? 'Gerando...' : 'PDF'}
						</button>
						<button onclick={salvarNoDrive} disabled={salvandoDrive || !logoSrc}
							class="px-4 py-2.5 rounded-full text-sm font-medium text-purple border border-purple hover:bg-purple/10 cursor-pointer transition-all disabled:opacity-50">
							{salvandoDrive ? 'Salvando...' : 'Drive'}
						</button>
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>
