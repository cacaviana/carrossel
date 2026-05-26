<script lang="ts">
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { EditorService } from '$lib/services/EditorService';
	import { getDims } from '$lib/utils/dimensions';
	import { imgToBase64 } from '$lib/utils/imgToBase64';
	import { API_BASE } from '$lib/api';
	import { getToken } from '$lib/stores/auth.svelte';
	import SlideDotsNav from '$lib/components/ui/SlideDotsNav.svelte';

	function authHeaders(): Record<string, string> {
		return {
			'Content-Type': 'application/json',
			'Authorization': `Bearer ${getToken()}`
		};
	}

	let slides = $state<string[]>([]);
	let textos = $state<{ titulo: string; corpo: string; cta?: string }[]>([]);
	let logoSrc = $state('');
	let logoPositions = $state<{ x: number; y: number }[]>([]);
	let logoSize = $state<number[]>([]);
	let currentSlide = $state(0);
	let salvando = $state(false);
	let carregando = $state(true);
	let regenerando = $state(false);
	let logoBordaCor = $state('#3578B0');
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
	let qualidade = $state<'media' | 'alta'>('alta');
	let removendoTexto = $state(false);
	let corrigindoAvatar = $state(false);
	let feedbackRegenerar = $state('');
	let autoRegenerar = false;

	const total = $derived(slides.length);
	const currentImage = $derived(slides[currentSlide] || '');
	const dims = $derived(getDims(formato));

	/** Extrai string de estruturas variadas do LLM */
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

	function parseCopySlides(saida: any): { titulo: string; corpo: string; cta?: string }[] {
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
		// Fallback pra anuncio e formatos single-slide que vem com campos flat (headline/descricao/cta)
		if (copySlides.length === 0 && (saida.headline || saida.titulo || saida.descricao || saida.corpo)) {
			copySlides = [saida];
		}
		const ctaSaida = extractStr(saida.cta) || extractStr(saida.call_to_action) || '';
		return copySlides.map((s: any) => {
			let titulo = extractStr(s.titulo) || extractStr(s.headline) || '';
			let corpo = extractStr(s.corpo) || extractStr(s.descricao) || extractStr(s.conteudo) || extractStr(s.texto) || extractStr(s.texto_principal) || '';
			let cta = extractStr(s.cta) || extractStr(s.call_to_action) || ctaSaida || '';
			if ((!titulo || !corpo) && Array.isArray(s.elementos)) {
				for (const el of s.elementos) {
					const t = el.tipo ?? '';
					const val = extractStr(el.texto) || extractStr(el.conteudo) || extractStr(el);
					if (!titulo && t.includes('titulo')) titulo = val;
					if (!corpo && (t.includes('card') || t === 'corpo' || t === 'subtitulo' || t === 'call_to_action')) corpo = val;
				}
			}
			return { titulo, corpo, cta };
		});
	}

	function buildSlideData(txt: { titulo: string; corpo: string } | undefined, slideIndex: number) {
		const titulo = txt?.titulo || '';
		const corpo = txt?.corpo || '';
		const isUnico = slides.length === 1;
		const tipo = isUnico ? 'cover' : (slideIndex === 0 ? 'cover' : slideIndex === slides.length - 1 ? 'cta' : 'content');
		if (tipo === 'cover') return { type: 'cover', headline: titulo, subline: corpo };
		if (tipo === 'cta') return { type: 'cta', headline: titulo, subline: corpo, tags: [] };
		return { type: 'content', title: titulo, bullets: corpo.split('\n').filter((l: string) => l.trim()), etapa: '' };
	}

	onMount(async () => {
		const pipelineId = page.url.searchParams.get('pipeline');
		const brand = page.url.searchParams.get('brand') || '';
		brandSlug = brand;

		try {
			// Carregar TUDO em paralelo via Service
			const promises: Record<string, Promise<any>> = {};
			if (pipelineId) {
				promises.copy = EditorService.carregarCopywriter(pipelineId).catch(() => null);
				promises.pip = EditorService.carregarPipeline(pipelineId).catch(() => null);
				promises.imgs = EditorService.carregarImagens(pipelineId).catch(() => null);
			}
			if (brand) {
				promises.brand = EditorService.carregarBrand(brand).catch(() => null);
				promises.foto = EditorService.carregarFoto(brand).catch(() => '');
				if (!pipelineId) promises.editorSlides = EditorService.carregarEditorSlides(brand).catch(() => []);
			}

			const keys = Object.keys(promises);
			const values = await Promise.all(Object.values(promises));
			const resolved: Record<string, any> = {};
			keys.forEach((k, i) => { resolved[k] = values[i]; });

			// Processar textos e tema
			if (pipelineId) {
				if (resolved.copy) {
					const saida = resolved.copy.saida ?? resolved.copy;
					textos = parseCopySlides(saida);
				}
				if (resolved.pip) {
					pipelineTema = resolved.pip.tema || '';
					formato = resolved.pip.formato || 'carrossel';
				}
			}

			// Carregar slides
			let slidesCarregados = false;
			if (resolved.imgs) {
				const saida = resolved.imgs.saida ?? resolved.imgs;
				const allImgs = saida?.imagens || saida?.resultados || [];
				const imgs = allImgs.filter((i: any) => i.image_url || i.image_base64 || i.image_path);
				if (imgs.length > 0) {
					const slideUrls = imgs.map((i: any) => {
						if (i.image_base64) return i.image_base64.startsWith('data:') ? i.image_base64 : `data:image/png;base64,${i.image_base64}`;
						if (i.image_url) return i.image_url.startsWith('http') ? i.image_url : `${API_BASE}${i.image_url}`;
						if (i.image_path) return `${API_BASE}/api/pipeline-images/${i.image_path}`;
						return '';
					});
					// URLs internas da API exigem Bearer token (fix C1). Browser <img> nao
					// manda Authorization header, entao baixamos aqui e convertemos pra data URL.
					const validados = await Promise.all(slideUrls.map(async (url: string) => {
						if (!url || url.startsWith('data:')) return url;
						try {
							const isApiUrl = url.startsWith(API_BASE) || url.startsWith('/api/');
							const opts = isApiUrl ? { headers: { 'Authorization': `Bearer ${getToken()}` } } : undefined;
							const r = await fetch(url, opts);
							if (!r.ok) return '';
							if (!isApiUrl) return url;
							const blob = await r.blob();
							return await new Promise<string>((resolve) => {
								const reader = new FileReader();
								reader.onloadend = () => resolve(reader.result as string);
								reader.onerror = () => resolve('');
								reader.readAsDataURL(blob);
							});
						} catch { return ''; }
					}));
					const temValido = validados.some((v: string) => v !== '');
					if (temValido) {
						slides = validados;
						slidesCarregados = true;
					} else if (textos.length > 0) {
						// Todas as URLs deram 404 — auto-regenerar
						slides = imgs.map(() => '');
						slidesCarregados = true;
						autoRegenerar = true;
					}
				}
				// Pipeline tem slides mas imagens vazias — criar placeholders pra regenerar
				if (!slidesCarregados && allImgs.length > 0 && textos.length > 0) {
					slides = allImgs.map(() => '');
					slidesCarregados = true;
					autoRegenerar = true;
				}
			}
			if (!slidesCarregados && resolved.editorSlides?.length > 0) {
				slides = resolved.editorSlides;
			}
			// Se tem textos mas nenhum slide, criar placeholders
			if (!slidesCarregados && textos.length > 0) {
				slides = textos.map(() => '');
				slidesCarregados = true;
				autoRegenerar = true;
			}

			logoPositions = slides.map(() => ({ x: 50, y: getDims(formato).h - 70 }));
			logoSize = slides.map(() => 60);
			logoModo = slides.map(() => 'rodape' as const);
			slidesOriginal = [...slides];

			// Logo e cores da marca
			if (resolved.brand) {
				logoBordaCor = resolved.brand.foto?.borda_cor || resolved.brand.cores?.acento_principal || '#3578B0';
			}
			if (resolved.foto) {
				logoSrc = resolved.foto;
			}
		} catch (e) {
			console.error('Erro ao carregar editor:', e);
		} finally {
			carregando = false;
		}

		// Auto-regenerar se pipeline tinha imagens vazias
		if (autoRegenerar && textos.length > 0) {
			autoRegenerar = false;
			ultimoFeedback = 'Imagens nao foram geradas no pipeline. Regenerando...';
			await regenerarTodos();
		}
	});

	async function regenerarTodos() {
		if (regenerandoTodos || textos.length === 0) return;
		regenerandoTodos = true;

		const total = textos.length;
		let geradas = 0;
		regenerandoTodosProgresso = `0/${total}`;

		// Gerar slide por slide (sequencial) pra evitar rate limit do Gemini free tier
		for (let i = 0; i < total; i++) {
			if (slides[i] && slides[i] !== '') {
				geradas++;
				regenerandoTodosProgresso = `${i + 1}/${total}`;
				continue; // Ja tem imagem, pular
			}
			const slideData = buildSlideData(textos[i], i);
			try {
				const data = await EditorService.gerarImagem({
					slides: [slideData],
					brand_slug: brandSlug,
					formato,
					skip_validation: true,
				});
				if (data.images?.[0]) {
					const img = data.images[0];
					slides[i] = img.startsWith('data:') ? img : `data:image/png;base64,${img}`;
					geradas++;
				}
			} catch {}
			slides = [...slides];
			currentSlide = i;
			regenerandoTodosProgresso = `${i + 1}/${total}`;
		}

		if (geradas === 0) {
			ultimoFeedback = 'Gemini nao retornou imagens. Tente novamente.';
			setTimeout(() => ultimoFeedback = '', 8000);
		} else if (geradas < total) {
			ultimoFeedback = `${geradas}/${total} geradas. Clique "Regenerar slide" nos vazios.`;
			setTimeout(() => ultimoFeedback = '', 8000);
		}
		regenerandoTodos = false;
		currentSlide = 0;
	}

	async function regenerarSlide(modo: 'texto' | 'tudo') {
		const txt = textos[currentSlide];
		if (regenerando) return;
		regenerando = true;
		ultimoFeedback = modo === 'texto' ? 'Corrigindo texto...' : 'Regenerando imagem...';

		try {
			const slideData = buildSlideData(txt, currentSlide);

			if (modo === 'texto') {
				const imgOriginal = await imgToBase64(slidesOriginal[currentSlide] || slides[currentSlide]);
				const data = await EditorService.corrigirTexto({
					image: imgOriginal,
					slide: slideData,
					brand_slug: brandSlug,
				});
				if (data.image) {
					const newImg = data.image.startsWith('data:') ? data.image : `data:image/png;base64,${data.image}`;
					slides = slides.map((s, i) => i === currentSlide ? newImg : s);
					const t = data.tentativas || '?';
					const aviso = data.aviso || '';
					ultimoFeedback = `Tentativa ${t}/3${aviso ? ' — ' + aviso : ''}`;
					setTimeout(() => ultimoFeedback = '', 5000);
				}
			} else if (feedbackRegenerar.trim()) {
				const imgB64 = await imgToBase64(currentImage);
				const imgAtual = imgB64.startsWith('data:') ? imgB64.split(',')[1] : imgB64;
				const feedback = feedbackRegenerar.trim();
				feedbackRegenerar = '';
				const data = await EditorService.ajustarImagem({
					imagem: imgAtual,
					feedback,
					brand_slug: brandSlug,
				});
				if (data.image && data.ajustado) {
					const newImg = data.image.startsWith('data:') ? data.image : `data:image/png;base64,${data.image}`;
					slides[currentSlide] = newImg;
					slides = [...slides];
					ultimoFeedback = 'Ajuste aplicado!';
					setTimeout(() => ultimoFeedback = '', 3000);
				} else {
					ultimoFeedback = 'Gemini nao conseguiu ajustar. Tente com outro feedback.';
					setTimeout(() => ultimoFeedback = '', 5000);
				}
			} else {
				const data = await EditorService.gerarImagem({
					slides: [slideData],
					brand_slug: brandSlug,
					formato,
					skip_validation: true,
				});
				if (data.images?.[0]) {
					const newImg = data.images[0].startsWith('data:') ? data.images[0] : `data:image/png;base64,${data.images[0]}`;
					slides[currentSlide] = newImg;
					slides = [...slides];
					ultimoFeedback = `Imagem regenerada!`;
					setTimeout(() => ultimoFeedback = '', 3000);
				} else {
					ultimoFeedback = 'Gemini nao retornou imagem. Tente novamente.';
					setTimeout(() => ultimoFeedback = '', 5000);
				}
			}
		} catch (e) {
			ultimoFeedback = 'Erro: ' + (e instanceof Error ? e.message : 'falha na requisicao');
			setTimeout(() => ultimoFeedback = '', 5000);
		} finally {
			regenerando = false;
		}
	}

	async function removerTexto() {
		if (removendoTexto) return;
		removendoTexto = true;
		ultimoFeedback = 'Removendo texto da imagem...';
		try {
			const imgB64 = await imgToBase64(currentImage);
			const imgAtual = imgB64.startsWith('data:') ? imgB64.split(',')[1] : imgB64;
			const data = await EditorService.corrigirTexto({
				image: imgAtual,
				slide: { type: 'content', title: '', bullets: [] },
				brand_slug: brandSlug,
				instrucao: 'Remove EVERY SINGLE piece of text from this image. This includes: headlines, titles, body text, badge/pill text, footer text, page numbers, names, navigation text like "DESLIZA", ALL numbers, ALL letters. Remove text inside cards, text on badges, text on footer bars. Keep the EXACT same background, gradients, colors, decorative elements (wireframes, illustrations, glows), card shapes and layout. Fill the areas where text was with the surrounding background/card color seamlessly. The final image must have ZERO readable characters anywhere.',
			});
			if (data.image) {
				const newImg = data.image.startsWith('data:') ? data.image : `data:image/png;base64,${data.image}`;
				slides[currentSlide] = newImg;
				slides = [...slides];
				ultimoFeedback = 'Texto removido!';
				setTimeout(() => ultimoFeedback = '', 3000);
			} else {
				ultimoFeedback = 'Gemini nao conseguiu remover o texto.';
				setTimeout(() => ultimoFeedback = '', 5000);
			}
		} catch {
			ultimoFeedback = 'Erro na requisicao.';
			setTimeout(() => ultimoFeedback = '', 5000);
		} finally {
			removendoTexto = false;
		}
	}

	async function corrigirAvatar() {
		if (corrigindoAvatar || !brandSlug || !currentImage) return;
		corrigindoAvatar = true;
		ultimoFeedback = 'Corrigindo avatar...';
		try {
			const imgB64 = await imgToBase64(currentImage);
			const imgRaw = imgB64.startsWith('data:') ? imgB64.split(',')[1] : imgB64;
			const pipelineId = page.url.searchParams.get('pipeline') || '';
			const data = await EditorService.corrigirAvatar({
				imagem: imgRaw,
				brand_slug: brandSlug,
				pipeline_id: pipelineId || undefined,
				slide_index: currentSlide + 1,
			});
			if (data.image) {
				const newImg = data.image.startsWith('data:') ? data.image : `data:image/png;base64,${data.image}`;
				slides[currentSlide] = newImg;
				slides = [...slides];
				ultimoFeedback = 'Avatar corrigido!';
				setTimeout(() => ultimoFeedback = '', 3000);
			} else {
				ultimoFeedback = 'Gemini nao retornou imagem.';
				setTimeout(() => ultimoFeedback = '', 5000);
			}
		} catch (e) {
			ultimoFeedback = 'Erro: ' + (e instanceof Error ? e.message : 'falha');
			setTimeout(() => ultimoFeedback = '', 5000);
		} finally {
			corrigindoAvatar = false;
		}
	}

	function handleClick(e: MouseEvent) {
		if (!logoSrc) return;
		const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
		const scaleX = dims.w / rect.width;
		const scaleY = dims.h / rect.height;
		logoPositions[currentSlide] = {
			x: Math.min(dims.w, Math.max(0, Math.round((e.clientX - rect.left) * scaleX))),
			y: Math.min(dims.h, Math.max(0, Math.round((e.clientY - rect.top) * scaleY))),
		};
	}

	function aplicarPosicaoEmTodos() {
		const pos = logoPositions[currentSlide];
		const size = logoSize[currentSlide];
		const modo = logoModo[currentSlide];
		logoPositions = logoPositions.map(() => ({ ...pos }));
		logoSize = logoSize.map(() => size);
		logoModo = logoModo.map(() => modo);
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
			if (brandSlug) {
				try { await EditorService.salvarFoto(brandSlug, logoSrc); } catch {}
			}
		};
		reader.readAsDataURL(file);
	}

	async function gerarPdfBase64(): Promise<string> {
		const { jsPDF } = await import('jspdf');
		const pxToMm = 0.2645833333;
		const wMm = dims.w * pxToMm;
		const hMm = dims.h * pxToMm;

		const pdf = new jsPDF({
			orientation: dims.w > dims.h ? 'landscape' : 'portrait',
			unit: 'mm',
			format: [wMm, hMm]
		});

		const jpegQuality = qualidade === 'alta' ? 1.0 : 0.7;

		for (let i = 0; i < slides.length; i++) {
			if (!slides[i]) continue;
			if (i > 0) pdf.addPage([wMm, hMm]);
			const dataUrl = await imgToBase64(slides[i]);
			pdf.addImage(dataUrl, 'PNG', 0, 0, wMm, hMm, undefined, undefined, undefined);
		}

		return pdf.output('datauristring').split(',')[1];
	}

	async function baixarPDF() {
		if (slides.length === 0) return;
		salvando = true;
		try {
			const { jsPDF } = await import('jspdf');
			const pxToMm = 0.2645833333;
			const wMm = dims.w * pxToMm;
			const hMm = dims.h * pxToMm;

			const pdf = new jsPDF({
				orientation: dims.w > dims.h ? 'landscape' : 'portrait',
				unit: 'mm',
				format: [wMm, hMm]
			});

			for (let i = 0; i < slides.length; i++) {
				if (!slides[i]) continue;
				if (i > 0) pdf.addPage([wMm, hMm]);
				const dataUrl = await imgToBase64(slides[i]);
				pdf.addImage(dataUrl, 'PNG', 0, 0, wMm, hMm);
			}

			pdf.save(`carrossel-${pipelineTema || 'slides'}.pdf`);
		} catch (e) {
			console.error('Erro ao gerar PDF:', e);
			ultimoFeedback = 'Erro ao gerar PDF';
		} finally {
			salvando = false;
		}
	}

	async function _downloadViaCanvas(format: 'png' | 'jpeg') {
		if (slides.length === 0) return;
		salvando = true;
		try {
			for (let i = 0; i < slides.length; i++) {
				if (!slides[i]) continue;
				const dataUri = await imgToBase64(slides[i]);
				const filename = `slide-${String(i + 1).padStart(2, '0')}.${format}`;

				const res = await fetch(dataUri);
				const blob = await res.blob();
				const finalBlob = format === 'jpeg' && blob.type !== 'image/jpeg'
					? await _convertBlob(blob, 'image/jpeg')
					: blob;
				const url = URL.createObjectURL(finalBlob);
				const link = document.createElement('a');
				link.href = url;
				link.download = filename;
				document.body.appendChild(link);
				link.click();
				document.body.removeChild(link);
				// Delay entre downloads — navegador throttle consecutivos se rapido demais
				await new Promise(r => setTimeout(r, 250));
				URL.revokeObjectURL(url);
			}
		} catch (e) {
			console.error('Erro ao baixar imagens:', e);
			ultimoFeedback = 'Erro ao baixar imagens';
		} finally {
			salvando = false;
		}
	}

	async function _convertBlob(blob: Blob, mimeType: string): Promise<Blob> {
		const bitmap = await createImageBitmap(blob);
		const canvas = new OffscreenCanvas(bitmap.width, bitmap.height);
		const ctx = canvas.getContext('2d')!;
		ctx.drawImage(bitmap, 0, 0);
		return canvas.convertToBlob({ type: mimeType, quality: qualidade === 'alta' ? 0.95 : 0.7 });
	}

	function baixarPNG() { _downloadViaCanvas('png'); }
	function baixarJPEG() { _downloadViaCanvas('jpeg'); }

	async function salvarNoDrive() {
		if (slides.length === 0) return;
		if (!logoSrc) {
			ultimoFeedback = 'Upload uma logo antes de salvar no Drive';
			setTimeout(() => ultimoFeedback = '', 5000);
			return;
		}
		salvandoDrive = true;
		driveSalvo = '';
		try {
			const pdfBase64 = await gerarPdfBase64();
			const imagesClean = slides.map(img =>
				img.startsWith('data:') ? img.split(',')[1] : img
			);
			const pipelineIdUrl = page.url.searchParams.get('pipeline') || undefined;
			const data = await EditorService.salvarDrive({
				title: pipelineTema || 'carrossel',
				pdf_base64: pdfBase64,
				images_base64: imagesClean,
				pipeline_id: pipelineIdUrl,
			});
			driveSalvo = data.web_view_link;
		} catch (e) {
			ultimoFeedback = e instanceof Error ? e.message : 'Erro ao salvar no Drive';
			setTimeout(() => ultimoFeedback = '', 5000);
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
				<button data-testid="btn-regenerar-todos" onclick={regenerarTodos} disabled={regenerandoTodos || textos.length === 0}
					class="px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer
						{regenerandoTodos ? 'bg-red-500/20 text-red-400' : 'text-red-400 border border-red-500/30 hover:bg-red-500/10'}
						disabled:opacity-50">
					{regenerandoTodos ? `Gerando ${regenerandoTodosProgresso}...` : 'Regenerar todos'}
				</button>
				{#if !logoSrc}
					<label class="px-4 py-2 rounded-full text-sm font-medium text-purple border border-purple/20 hover:bg-purple/8 cursor-pointer">
						Upload logo
						<input data-testid="input-logo-upload" type="file" accept="image/*" onchange={handleLogoUpload} class="hidden" />
					</label>
				{:else}
					<img src={logoSrc} alt="Logo" class="w-8 h-8 rounded-full object-cover border border-purple" />
					<button data-testid="btn-igual-todos" onclick={aplicarPosicaoEmTodos}
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
			data-testid="slide-preview"
			class="relative mx-auto rounded-xl overflow-hidden shadow-2xl cursor-crosshair"
			style="max-width: 540px; aspect-ratio: {dims.cssRatio};"
			onclick={handleClick}
		>
			{#if currentImage}
				<img src={currentImage} alt="Slide {currentSlide + 1}" class="w-full h-full object-contain" />
			{:else}
				<div class="w-full h-full flex items-center justify-center bg-bg-elevated text-text-muted text-sm">
					Gerando imagem...
				</div>
			{/if}

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

		<!-- Navegacao slides (logo abaixo da imagem) -->
		<div class="mt-3 mx-auto flex items-center justify-between gap-2" style="max-width: 540px;">
			<button onclick={anterior} disabled={currentSlide === 0}
				class="px-4 py-1.5 rounded-full text-xs font-medium transition-all cursor-pointer shrink-0
					{currentSlide === 0 ? 'text-text-muted opacity-30' : 'text-text-secondary border border-border-default hover:border-purple/40'}">
				Anterior
			</button>
			<SlideDotsNav total={total} current={currentSlide} onSelect={(i) => currentSlide = i} />
			<button onclick={proximo} disabled={currentSlide >= total - 1}
				class="px-4 py-1.5 rounded-full text-xs font-medium transition-all cursor-pointer shrink-0
					{currentSlide >= total - 1 ? 'text-text-muted opacity-30' : 'text-bg-global bg-purple hover:opacity-90'}">
				Proximo
			</button>
		</div>

		<!-- Texto esperado -->
		{#if textos[currentSlide]}
			<div class="mt-3 mx-auto bg-bg-card rounded-xl border border-border-default p-4" style="max-width: 540px;">
				<p class="text-[10px] text-text-muted uppercase tracking-wider mb-1">
					{formato === 'anuncio' ? 'Copy do anuncio' : 'Texto esperado'}
				</p>
				{#if formato === 'anuncio'}
					<div class="space-y-2">
						<div>
							<p class="text-[9px] text-text-muted uppercase tracking-wider">Headline</p>
							<p class="text-sm text-text-primary font-semibold">{textos[currentSlide].titulo}</p>
						</div>
						{#if textos[currentSlide].corpo}
							<div>
								<p class="text-[9px] text-text-muted uppercase tracking-wider">Descricao</p>
								<p class="text-xs text-text-secondary whitespace-pre-line">{textos[currentSlide].corpo}</p>
							</div>
						{/if}
						{#if textos[currentSlide].cta}
							<div>
								<p class="text-[9px] text-text-muted uppercase tracking-wider">CTA</p>
								<span class="inline-block px-3 py-1 rounded-full bg-cyan-400/10 text-cyan-500 text-xs font-semibold border border-cyan-400/30">
									{textos[currentSlide].cta}
								</span>
							</div>
						{/if}
					</div>
				{:else}
					<p class="text-sm text-text-primary font-medium">{textos[currentSlide].titulo}</p>
					{#if textos[currentSlide].corpo}
						<p class="text-xs text-text-secondary mt-1 whitespace-pre-line">{textos[currentSlide].corpo}</p>
					{/if}
				{/if}
			</div>
		{/if}

		<!-- Feedback + Regenerar -->
		<div class="mt-3 mx-auto bg-bg-card rounded-xl border border-border-default p-4" style="max-width: 540px;">
			<div class="mb-2">
				<input
					data-testid="input-feedback"
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
				<button data-testid="btn-corrigir-texto" onclick={() => regenerarSlide('texto')} disabled={regenerando || removendoTexto}
					class="px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer
						{regenerando ? 'bg-amber/20 text-amber' : 'text-amber border border-amber/30 hover:bg-amber/10'}
						disabled:opacity-50">
					{regenerando ? 'Gerando...' : 'Corrigir texto'}
				</button>
				<button data-testid="btn-regenerar-slide" onclick={() => regenerarSlide('tudo')} disabled={regenerando || removendoTexto}
					class="px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer
						{regenerando ? 'bg-purple/20 text-purple' : 'text-purple border border-purple/30 hover:bg-purple/10'}
						disabled:opacity-50">
					{regenerando ? 'Gerando...' : feedbackRegenerar.trim() ? 'Regenerar com feedback' : 'Regenerar slide'}
				</button>
				<button data-testid="btn-tirar-texto" onclick={removerTexto} disabled={regenerando || removendoTexto}
					class="px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer
						{removendoTexto ? 'bg-red/20 text-red' : 'text-red border border-red/30 hover:bg-red/10'}
						disabled:opacity-50">
					{removendoTexto ? 'Gerando...' : 'Tirar texto'}
				</button>
				{#if brandSlug}
				<button data-testid="btn-corrigir-avatar" onclick={corrigirAvatar} disabled={regenerando || removendoTexto || corrigindoAvatar}
					class="px-4 py-2 rounded-full text-xs font-medium transition-all cursor-pointer
						{corrigindoAvatar ? 'bg-teal/20 text-teal' : 'text-teal border border-teal/30 hover:bg-teal/10'}
						disabled:opacity-50">
					{corrigindoAvatar ? 'Corrigindo...' : 'Corrigir avatar'}
				</button>
				{/if}
			</div>
		</div>

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
						<input data-testid="checkbox-logo" type="checkbox" bind:checked={logoVisivel} class="rounded" />
						Logo
					</label>

					{#if logoVisivel}
					<!-- Modo: rodape ou central -->
					<div class="flex gap-1">
						<button data-testid="btn-logo-rodape" onclick={() => { logoModo[currentSlide] = 'rodape'; logoSize[currentSlide] = logoTamRodape; }}
							class="px-3 py-1 rounded-full text-[11px] font-medium transition-all cursor-pointer
								{logoModo[currentSlide] === 'rodape' ? 'bg-purple/15 text-purple' : 'text-text-muted hover:text-text-secondary'}">
							Rodape
						</button>
						<button data-testid="btn-logo-central" onclick={() => { logoModo[currentSlide] = 'central'; logoSize[currentSlide] = logoTamCentral; }}
							class="px-3 py-1 rounded-full text-[11px] font-medium transition-all cursor-pointer
								{logoModo[currentSlide] === 'central' ? 'bg-purple/15 text-purple' : 'text-text-muted hover:text-text-secondary'}">
							Central
						</button>
					</div>

					<!-- Borda -->
					<label class="flex items-center gap-1 text-[11px] text-text-muted cursor-pointer">
						<input data-testid="checkbox-borda" type="checkbox" bind:checked={logoBordaAtiva} class="rounded" />
						Borda
						{#if logoBordaAtiva}
							<span class="w-3 h-3 rounded-full" style="background: {logoBordaCor}"></span>
						{/if}
					</label>

					<!-- Tamanhos -->
					<div class="w-full flex flex-wrap items-center gap-x-4 gap-y-2 pt-2 border-t border-border-default">
						<div class="flex items-center gap-1.5">
							<span class="text-[10px] text-text-muted">Rodape:</span>
							<input data-testid="slider-rodape" type="range" min="30" max="300" bind:value={logoTamRodape}
								oninput={() => { logoSize = logoSize.map((s, i) => logoModo[i] === 'rodape' ? logoTamRodape : s); }}
								class="w-20" />
							<span class="text-[9px] text-text-muted font-mono w-6">{logoTamRodape}</span>
						</div>
						<div class="flex items-center gap-1.5">
							<span class="text-[10px] text-text-muted">Central:</span>
							<input data-testid="slider-central" type="range" min="60" max="400" bind:value={logoTamCentral}
								oninput={() => { logoSize = logoSize.map((s, i) => logoModo[i] === 'central' ? logoTamCentral : s); }}
								class="w-20" />
							<span class="text-[9px] text-text-muted font-mono w-6">{logoTamCentral}</span>
						</div>
					</div>
					{/if}
				</div>
			</div>
		{/if}

		<!-- Feedback centralizado (fora do bloco logo para sempre aparecer) -->
		{#if driveSalvo}
			<p class="text-center text-xs text-green mt-2">Salvo no Drive! <a href={driveSalvo} target="_blank" class="underline font-medium">Abrir no Google Drive</a>
				<button onclick={() => driveSalvo = ''} class="ml-2 text-text-muted hover:text-text-secondary cursor-pointer">x</button>
			</p>
		{:else if ultimoFeedback}
			<p class="text-center text-xs text-amber mt-1">{ultimoFeedback}</p>
		{:else if logoSrc}
			<p class="text-center text-xs text-text-muted mt-1">Clique no slide pra posicionar</p>
		{/if}

		<!-- Exportar (ultimo slide) -->
		<div class="mt-6 space-y-3">
			{#if currentSlide === total - 1}
				<div class="bg-bg-card rounded-xl border border-border-default p-3">
					<p class="text-[10px] text-text-muted uppercase tracking-wider mb-2">Exportar</p>
					<div class="flex items-center gap-2 mb-2">
						<span class="text-[10px] text-text-muted">Qualidade:</span>
						<button data-testid="btn-qualidade-media" onclick={() => qualidade = 'media'}
							class="px-3 py-1 rounded-full text-[11px] font-medium transition-all cursor-pointer
								{qualidade === 'media' ? 'bg-purple/15 text-purple' : 'text-text-muted hover:text-text-secondary'}">
							Media
						</button>
						<button data-testid="btn-qualidade-alta" onclick={() => qualidade = 'alta'}
							class="px-3 py-1 rounded-full text-[11px] font-medium transition-all cursor-pointer
								{qualidade === 'alta' ? 'bg-purple/15 text-purple' : 'text-text-muted hover:text-text-secondary'}">
							Alta
						</button>
					</div>
					<div class="grid grid-cols-4 gap-2">
						<button data-testid="btn-baixar-png" onclick={baixarPNG}
							class="py-2 rounded-lg text-xs font-medium text-text-secondary border border-border-default hover:border-purple/40 cursor-pointer transition-all">
							PNG
						</button>
						<button data-testid="btn-baixar-jpeg" onclick={baixarJPEG}
							class="py-2 rounded-lg text-xs font-medium text-text-secondary border border-border-default hover:border-purple/40 cursor-pointer transition-all">
							JPEG
						</button>
						<button data-testid="btn-baixar-pdf" onclick={baixarPDF} disabled={salvando}
							class="py-2 rounded-lg text-xs font-medium text-bg-global bg-purple hover:opacity-90 cursor-pointer transition-all disabled:opacity-50">
							{salvando ? '...' : 'PDF'}
						</button>
						<button data-testid="btn-salvar-drive" onclick={salvarNoDrive} disabled={salvandoDrive || !logoSrc}
							class="py-2 rounded-lg text-xs font-medium text-purple border border-purple hover:bg-purple/10 cursor-pointer transition-all disabled:opacity-50">
							{salvandoDrive ? '...' : 'Drive'}
						</button>
					</div>
				</div>
			{/if}
		</div>
	{/if}
</div>
