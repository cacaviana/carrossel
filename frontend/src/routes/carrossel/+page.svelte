<script lang="ts">
	import { carrosselAtual, gerandoImagens, slideAtual } from '$lib/stores/carrossel';
	import { config } from '$lib/stores/config';
	import { fotos } from '$lib/stores/fotos';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import type { Slide } from '$lib/stores/carrossel';

	let legendaCopiada = $state(false);
	let erro = $state('');
	let salvandoDrive = $state(false);
	let driveSalvo = $state('');
	let modoEdicao = $state(false);
	let gerandoSlide = $state<number | null>(null);

	// Design Systems
	type DesignSystemItem = { id: string; name: string };
	let designSystems = $state<DesignSystemItem[]>([]);
	let designSystemSelecionado = $state('');
	let designSystemConteudo = $state('');
	let carregandoDS = $state(false);

	onMount(async () => {
		let currentConfig: typeof $config | undefined;
		config.subscribe((v) => (currentConfig = v))();
		try {
			const res = await fetch(`${currentConfig.backendUrl}/api/drive/design-systems`);
			if (res.ok) designSystems = await res.json();
		} catch {}
	});

	async function selecionarDesignSystem(id: string) {
		if (!id) { designSystemSelecionado = ''; designSystemConteudo = ''; return; }
		let currentConfig: typeof $config | undefined;
		config.subscribe((v) => (currentConfig = v))();
		carregandoDS = true;
		try {
			const res = await fetch(`${currentConfig.backendUrl}/api/drive/design-systems/${id}`);
			if (res.ok) {
				const data = await res.json();
				designSystemSelecionado = id;
				designSystemConteudo = data.content;
			}
		} catch {} finally { carregandoDS = false; }
	}

	const totalSlides = $derived($carrosselAtual?.slides.length ?? 0);
	const slideData = $derived($carrosselAtual?.slides[$slideAtual]);
	const hasImages = $derived($carrosselAtual?.slides.some((s) => s.imageBase64) ?? false);
	const hasCode = $derived($carrosselAtual?.slides.some((s) => s.type === 'code') ?? false);
	const hasCta = $derived($carrosselAtual?.slides.some((s) => s.type === 'cta') ?? false);

	function prevSlide() { slideAtual.update((n) => Math.max(0, n - 1)); }
	function nextSlide() { slideAtual.update((n) => Math.min(totalSlides - 1, n + 1)); }

	// Touch swipe
	let touchStartX = 0;
	function handleTouchStart(e: TouchEvent) { touchStartX = e.touches[0].clientX; }
	function handleTouchEnd(e: TouchEvent) {
		const diff = touchStartX - e.changedTouches[0].clientX;
		if (Math.abs(diff) > 50) { diff > 0 ? nextSlide() : prevSlide(); }
	}

	async function copiarLegenda() {
		if (!$carrosselAtual?.legenda_linkedin) return;
		await navigator.clipboard.writeText($carrosselAtual.legenda_linkedin);
		legendaCopiada = true;
		setTimeout(() => legendaCopiada = false, 2000);
	}

	// Edição de slides
	function updateSlide(index: number, field: string, value: string | string[]) {
		carrosselAtual.update((c) => {
			if (!c) return c;
			const slides = [...c.slides];
			slides[index] = { ...slides[index], [field]: value };
			return { ...c, slides };
		});
	}

	function updateBullet(slideIndex: number, bulletIndex: number, value: string) {
		carrosselAtual.update((c) => {
			if (!c) return c;
			const slides = [...c.slides];
			const bullets = [...(slides[slideIndex].bullets ?? [])];
			bullets[bulletIndex] = value;
			slides[slideIndex] = { ...slides[slideIndex], bullets };
			return { ...c, slides };
		});
	}

	function addBullet(slideIndex: number) {
		carrosselAtual.update((c) => {
			if (!c) return c;
			const slides = [...c.slides];
			const bullets = [...(slides[slideIndex].bullets ?? []), ''];
			slides[slideIndex] = { ...slides[slideIndex], bullets };
			return { ...c, slides };
		});
	}

	function removeBullet(slideIndex: number, bulletIndex: number) {
		carrosselAtual.update((c) => {
			if (!c) return c;
			const slides = [...c.slides];
			const bullets = (slides[slideIndex].bullets ?? []).filter((_, i) => i !== bulletIndex);
			slides[slideIndex] = { ...slides[slideIndex], bullets };
			return { ...c, slides };
		});
	}

	async function gerarImagemSlide(index: number) {
		if (!$carrosselAtual) return;
		let currentConfig: typeof $config | undefined;
		config.subscribe((v) => (currentConfig = v))();

		gerandoSlide = index;
		erro = '';

		try {
			const res = await fetch(`${currentConfig.backendUrl}/api/gerar-imagem-slide`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					slide: $carrosselAtual.slides[index],
					slide_index: index,
					total_slides: $carrosselAtual.slides.length,
					foto_criador: currentConfig.fotoCriadorBase64 || undefined,
					design_system: designSystemConteudo || undefined
				})
			});
			if (!res.ok) { const d = await res.json(); throw new Error(d.detail); }
			const data = await res.json();
			if (data.image) {
				carrosselAtual.update((c) => {
					if (!c) return c;
					const slides = [...c.slides];
					slides[index] = { ...slides[index], imageBase64: data.image };
					return { ...c, slides };
				});
			}
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro ao gerar imagem';
		} finally {
			gerandoSlide = null;
		}
	}

	async function gerarImagens() {
		if (!$carrosselAtual) return;
		let currentConfig: typeof $config | undefined;
		config.subscribe((v) => (currentConfig = v))();

		erro = '';
		gerandoImagens.set(true);
		modoEdicao = false;

		try {
			const res = await fetch(`${currentConfig.backendUrl}/api/gerar-imagem`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					slides: $carrosselAtual.slides,
					foto_criador: currentConfig.fotoCriadorBase64 || undefined,
					design_system: designSystemConteudo || undefined
				})
			});

			if (!res.ok) {
				const data = await res.json();
				throw new Error(data.detail || 'Erro ao gerar imagens');
			}

			const data = await res.json();
			carrosselAtual.update((c) => {
				if (!c) return c;
				return { ...c, slides: c.slides.map((s, i) => ({ ...s, imageBase64: data.images[i] || undefined })) };
			});
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro desconhecido';
		} finally {
			gerandoImagens.set(false);
		}
	}

	async function exportarPDF() {
		if (!$carrosselAtual) return;
		const imagesWithData = $carrosselAtual.slides.filter((s) => s.imageBase64);
		if (imagesWithData.length === 0) { erro = 'Gere as imagens primeiro.'; return; }

		const { jsPDF } = await import('jspdf');
		const pdf = new jsPDF({ orientation: 'portrait', unit: 'px', format: [1080, 1350] });
		for (let i = 0; i < $carrosselAtual.slides.length; i++) {
			const slide = $carrosselAtual.slides[i];
			if (!slide.imageBase64) continue;
			if (i > 0) pdf.addPage([1080, 1350]);
			pdf.addImage(slide.imageBase64, 'PNG', 0, 0, 1080, 1350);
		}
		pdf.save(`${$carrosselAtual.title || 'carrossel'}.pdf`);
	}

	async function salvarNoDrive() {
		if (!$carrosselAtual) return;
		let currentConfig: typeof $config | undefined;
		config.subscribe((v) => (currentConfig = v))();

		const imagesWithData = $carrosselAtual.slides.filter((s) => s.imageBase64);
		if (imagesWithData.length === 0) { erro = 'Gere as imagens primeiro.'; return; }

		erro = ''; driveSalvo = ''; salvandoDrive = true;

		try {
			const { jsPDF } = await import('jspdf');
			const pdf = new jsPDF({ orientation: 'portrait', unit: 'px', format: [1080, 1350] });
			for (let i = 0; i < $carrosselAtual.slides.length; i++) {
				const slide = $carrosselAtual.slides[i];
				if (!slide.imageBase64) continue;
				if (i > 0) pdf.addPage([1080, 1350]);
				pdf.addImage(slide.imageBase64, 'PNG', 0, 0, 1080, 1350);
			}
			const pdfBase64 = pdf.output('datauristring').split(',')[1];
			const images = $carrosselAtual.slides.map((s) => s.imageBase64 || null);

			const res = await fetch(`${currentConfig.backendUrl}/api/google-drive/carrossel`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
						title: $carrosselAtual.title || 'carrossel',
						pdf_base64: pdfBase64,
						images_base64: images,
						disciplina: $carrosselAtual.disciplina || null,
						tecnologia_principal: $carrosselAtual.tecnologia_principal || null,
						tipo_carrossel: $carrosselAtual.slides[0]?.type === 'infographic' ? 'infografico' : 'texto',
						legenda_linkedin: $carrosselAtual.legenda_linkedin || null
					})
			});

			if (!res.ok) { const data = await res.json(); throw new Error(data.detail || 'Erro ao salvar no Drive'); }
			const data = await res.json();
			driveSalvo = data.web_view_link;
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro ao salvar no Drive';
		} finally {
			salvandoDrive = false;
		}
	}
</script>

<svelte:head><title>Carrossel — Preview</title></svelte:head>

{#if !$carrosselAtual}
	<div class="text-center py-20 animate-fade-up">
		<p class="text-steel-4 text-lg mb-4">Nenhum carrossel gerado ainda.</p>
		<a href="/" class="inline-flex px-6 py-3 rounded-full font-medium text-white no-underline
			bg-gradient-to-r from-steel-4 via-steel-3 to-steel-2 hover:-translate-y-0.5 hover:shadow-lg transition-all">
			Criar carrossel
		</a>
	</div>
{:else}
	<div class="animate-fade-up">
		<!-- Header -->
		<div class="mb-6">
			<div class="mb-4">
				<h2 class="text-lg sm:text-2xl font-semibold text-steel-6 leading-tight">{$carrosselAtual.title}</h2>
				<p class="text-xs sm:text-sm text-steel-4 font-light mt-1">{$carrosselAtual.disciplina} — {$carrosselAtual.tecnologia_principal}</p>
			</div>
			<div class="grid grid-cols-2 sm:flex sm:flex-wrap gap-2">
				<button
					onclick={() => modoEdicao = !modoEdicao}
					class="py-2.5 px-4 rounded-full text-xs sm:text-sm font-medium transition-all cursor-pointer active:scale-[0.97]
						{modoEdicao ? 'bg-steel-6 text-white' : 'border border-steel-3/30 text-steel-3 hover:bg-steel-0'}"
				>
					{modoEdicao ? 'Visualizar' : 'Editar'}
				</button>
				<button onclick={gerarImagens} disabled={$gerandoImagens}
					class="py-2.5 px-4 rounded-full text-xs sm:text-sm font-medium text-white cursor-pointer
						bg-gradient-to-r from-steel-4 via-steel-3 to-steel-2
						hover:-translate-y-0.5 hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.97]">
					{$gerandoImagens ? 'Gerando...' : 'Imagens'}
				</button>
				<button onclick={exportarPDF}
					class="py-2.5 px-4 rounded-full text-xs sm:text-sm font-medium border border-steel-3/30 text-steel-3 hover:bg-steel-0 transition-all cursor-pointer active:scale-[0.97]">
					PDF
				</button>
				<button onclick={salvarNoDrive} disabled={salvandoDrive}
					class="py-2.5 px-4 rounded-full text-xs sm:text-sm font-medium border border-steel-3/30 text-steel-3 hover:bg-steel-0 transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.97]">
					{salvandoDrive ? 'Salvando...' : 'Drive'}
				</button>
			</div>
		</div>

		{#if erro}
			<div class="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">{erro}</div>
		{/if}
		{#if driveSalvo}
			<div class="mb-4 p-3 rounded-xl bg-green-50 border border-green-200 text-green-700 text-sm">
				Salvo no Drive! <a href={driveSalvo} target="_blank" class="underline font-medium">Abrir no Google Drive</a>
			</div>
		{/if}

		<!-- MODO EDIÇÃO -->
		{#if modoEdicao}
			<div class="space-y-4">
				<!-- Opções rápidas: Design System + Foto -->
				<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-4 flex flex-col sm:flex-row gap-4">
					<!-- Design System -->
					<div class="flex-1">
						<p class="text-xs font-medium text-steel-5 mb-2">Design System</p>
						<select
							onchange={(e) => selecionarDesignSystem((e.target as HTMLSelectElement).value)}
							disabled={carregandoDS}
							class="w-full px-3 py-2.5 rounded-xl border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 outline-none"
						>
							<option value="">Padrão (dark mode premium)</option>
							{#each designSystems as ds}
								<option value={ds.id} selected={designSystemSelecionado === ds.id}>{ds.name.replace(/\.(md|txt)$/, '')}</option>
							{/each}
						</select>
					</div>
					<!-- Foto -->
					<div class="flex-1">
						<p class="text-xs font-medium text-steel-5 mb-2">Foto do criador</p>
						{#if $fotos.length > 0}
							<div class="flex gap-2 flex-wrap">
								{#each $fotos as foto}
									<button
										onclick={() => config.update(c => ({ ...c, fotoCriadorBase64: foto.dataUrl }))}
										class="w-10 h-10 rounded-full overflow-hidden cursor-pointer transition-all
											{$config.fotoCriadorBase64 === foto.dataUrl ? 'ring-2 ring-[#A78BFA] scale-110' : 'opacity-60 hover:opacity-100'}"
									>
										<img src={foto.dataUrl} alt={foto.name} class="w-full h-full object-cover" />
									</button>
								{/each}
								<button
									onclick={() => config.update(c => ({ ...c, fotoCriadorBase64: '' }))}
									class="w-10 h-10 rounded-full border border-teal-4/30 flex items-center justify-center text-xs text-steel-4 cursor-pointer hover:bg-teal-1
										{!$config.fotoCriadorBase64 ? 'ring-2 ring-[#A78BFA]' : ''}"
								>
									Sem
								</button>
							</div>
						{:else}
							<p class="text-xs text-steel-4 italic">Nenhuma foto. Adicione em Config.</p>
						{/if}
					</div>
				</div>

				<div class="flex items-center justify-between mb-2">
					<p class="text-sm text-steel-4 font-light">{totalSlides} slides — edite o texto antes de gerar imagens</p>
					<span class="text-xs text-steel-4 bg-teal-1 border border-teal-4/30 px-3 py-1 rounded-full">
						~R$2,25/carrossel (3 Pro + {totalSlides - 3} Flash grátis)
					</span>
				</div>
				{#each $carrosselAtual.slides as slide, i}
					<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-5">
						<div class="flex items-center gap-3 mb-4">
							<span class="w-7 h-7 rounded-full bg-steel-6 text-white text-xs font-bold flex items-center justify-center shrink-0">{i + 1}</span>
							<span class="px-2.5 py-0.5 rounded-full text-xs bg-steel-0 text-steel-3 font-medium">{slide.type}</span>
							{#if slide.imageBase64}
								<span class="text-xs text-green-600 font-medium">✓ imagem gerada</span>
							{/if}
							<button
								onclick={() => gerarImagemSlide(i)}
								disabled={gerandoSlide !== null}
								class="ml-auto px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer
									{slide.imageBase64 ? 'border border-steel-3/30 text-steel-3 hover:bg-steel-0' : 'bg-steel-3 text-white hover:bg-steel-4'}
									disabled:opacity-50 disabled:cursor-not-allowed"
							>
								{gerandoSlide === i ? 'Gerando...' : slide.imageBase64 ? 'Regenerar' : 'Gerar imagem'}
							</button>
						</div>

						<div class="space-y-3">
							{#if slide.headline !== undefined}
								<div>
									<label class="block text-xs font-medium text-steel-4 mb-1">Headline</label>
									<input type="text" value={slide.headline}
										oninput={(e) => updateSlide(i, 'headline', (e.target as HTMLInputElement).value)}
										class="w-full px-3 py-2 rounded-lg border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 outline-none" />
								</div>
							{/if}
							{#if slide.subline !== undefined}
								<div>
									<label class="block text-xs font-medium text-steel-4 mb-1">Subline</label>
									<input type="text" value={slide.subline}
										oninput={(e) => updateSlide(i, 'subline', (e.target as HTMLInputElement).value)}
										class="w-full px-3 py-2 rounded-lg border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 outline-none" />
								</div>
							{/if}
							{#if slide.title !== undefined}
								<div>
									<label class="block text-xs font-medium text-steel-4 mb-1">Título</label>
									<input type="text" value={slide.title}
										oninput={(e) => updateSlide(i, 'title', (e.target as HTMLInputElement).value)}
										class="w-full px-3 py-2 rounded-lg border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 outline-none" />
								</div>
							{/if}
							{#if slide.bullets && slide.bullets.length > 0}
								<div>
									<label class="block text-xs font-medium text-steel-4 mb-1">Bullets</label>
									<div class="space-y-2">
										{#each slide.bullets as bullet, bi}
											<div class="flex gap-2">
												<input type="text" value={bullet}
													oninput={(e) => updateBullet(i, bi, (e.target as HTMLInputElement).value)}
													class="flex-1 px-3 py-2 rounded-lg border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 outline-none" />
												<button onclick={() => removeBullet(i, bi)}
													class="px-2.5 py-1 rounded-lg text-xs text-red-500 hover:bg-red-50 transition-all cursor-pointer">✕</button>
											</div>
										{/each}
										<button onclick={() => addBullet(i)}
											class="text-xs text-steel-3 hover:text-steel-4 font-medium cursor-pointer">+ Adicionar bullet</button>
									</div>
								</div>
							{/if}
							{#if slide.code !== undefined}
								<div>
									<label class="block text-xs font-medium text-steel-4 mb-1">Código</label>
									<textarea value={slide.code} rows="5"
										oninput={(e) => updateSlide(i, 'code', (e.target as HTMLTextAreaElement).value)}
										class="w-full px-3 py-2 rounded-lg border border-teal-4/30 bg-white text-steel-6 text-xs font-mono focus:border-steel-3 outline-none resize-y"></textarea>
								</div>
							{/if}
							{#if slide.caption !== undefined}
								<div>
									<label class="block text-xs font-medium text-steel-4 mb-1">Caption</label>
									<input type="text" value={slide.caption}
										oninput={(e) => updateSlide(i, 'caption', (e.target as HTMLInputElement).value)}
										class="w-full px-3 py-2 rounded-lg border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 outline-none" />
								</div>
							{/if}
							{#if slide.etapa !== undefined}
								<div>
									<label class="block text-xs font-medium text-steel-4 mb-1">Etapa</label>
									<input type="text" value={slide.etapa}
										oninput={(e) => updateSlide(i, 'etapa', (e.target as HTMLInputElement).value)}
										class="w-full px-3 py-2 rounded-lg border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 outline-none" />
								</div>
							{/if}
							{#if slide.illustration_description !== undefined}
								<div>
									<label class="block text-xs font-medium text-steel-4 mb-1">Descrição da ilustração (Gemini vai gerar isso)</label>
									<textarea value={slide.illustration_description} rows="3"
										oninput={(e) => updateSlide(i, 'illustration_description', (e.target as HTMLTextAreaElement).value)}
										class="w-full px-3 py-2 rounded-lg border border-teal-4/30 bg-white text-steel-6 text-xs focus:border-steel-3 outline-none resize-y"></textarea>
								</div>
							{/if}
						</div>
					</div>
				{/each}

				<div class="pt-2">
					<button onclick={() => { modoEdicao = false; gerarImagens(); }}
						class="w-full py-3 rounded-full font-medium text-white cursor-pointer
							bg-gradient-to-r from-steel-4 via-steel-3 to-steel-2
							hover:-translate-y-0.5 hover:shadow-lg transition-all">
						Pronto — Gerar Imagens
					</button>
				</div>
			</div>

		<!-- MODO PREVIEW -->
		{:else}
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
				<div class="lg:col-span-2">
					<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-3 sm:p-6">
						<!-- svelte-ignore a11y_no_static_element_interactions -->
						<div
							class="aspect-[4/5] bg-steel-6 rounded-xl overflow-hidden flex items-center justify-center mb-3 sm:mb-4"
							ontouchstart={handleTouchStart}
							ontouchend={handleTouchEnd}
						>
							{#if slideData?.imageBase64}
								<img src={slideData.imageBase64} alt="Slide {$slideAtual + 1}" class="w-full h-full object-contain" />
							{:else}
								<div class="text-center p-8">
									<p class="text-teal-4 text-sm font-light mb-2">Slide {$slideAtual + 1} / {totalSlides}</p>
									<p class="text-white font-semibold text-lg mb-1">{slideData?.headline || slideData?.title || slideData?.type || ''}</p>
									{#if slideData?.subline}<p class="text-teal-5 text-sm">{slideData.subline}</p>{/if}
									{#if slideData?.bullets}
										<ul class="text-left text-teal-4 text-sm mt-4 space-y-1.5">
											{#each slideData.bullets as bullet}<li>→ {bullet}</li>{/each}
										</ul>
									{/if}
									{#if slideData?.code}
										<pre class="text-left text-green-400 text-xs mt-4 p-3 bg-black/50 rounded-lg overflow-auto font-mono">{slideData.code}</pre>
									{/if}
									<p class="text-steel-4 text-xs mt-4 italic">Clique "Editar slides" para ajustar o texto</p>
								</div>
							{/if}
						</div>

						<div class="flex items-center justify-between">
							<button onclick={prevSlide} disabled={$slideAtual === 0}
								class="px-4 py-2 rounded-full text-sm font-medium bg-teal-3 text-steel-5 hover:bg-teal-4 transition-all cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed">
								Anterior
							</button>
							<div class="flex gap-1.5">
								{#each Array(totalSlides) as _, i}
									<button onclick={() => slideAtual.set(i)}
										class="w-2.5 h-2.5 rounded-full transition-all cursor-pointer
											{i === $slideAtual ? 'bg-steel-3 scale-125' : 'bg-teal-4 hover:bg-teal-5'}">
									</button>
								{/each}
							</div>
							<button onclick={nextSlide} disabled={$slideAtual === totalSlides - 1}
								class="px-4 py-2 rounded-full text-sm font-medium bg-teal-3 text-steel-5 hover:bg-teal-4 transition-all cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed">
								Próximo
							</button>
						</div>
					</div>
				</div>

				<div class="space-y-4">
					<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-5">
						<h4 class="font-semibold text-steel-6 text-sm mb-3">Slide {$slideAtual + 1}</h4>
						<div class="space-y-2 text-xs">
							<div class="flex justify-between">
								<span class="text-steel-4">Tipo</span>
								<span class="px-2 py-0.5 rounded-full bg-steel-0 text-steel-3 font-medium">{slideData?.type}</span>
							</div>
							{#if slideData?.etapa}
								<div class="flex justify-between">
									<span class="text-steel-4">Etapa</span>
									<span class="text-steel-6 font-medium">{slideData.etapa}</span>
								</div>
							{/if}
						</div>
					</div>

					<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-5">
						<div class="flex items-center justify-between mb-3">
							<h4 class="font-semibold text-steel-6 text-sm">Legenda LinkedIn</h4>
							<button onclick={copiarLegenda}
								class="px-3 py-1 rounded-full text-xs font-medium cursor-pointer
									{legendaCopiada ? 'bg-teal-3 text-teal-6' : 'bg-steel-0 text-steel-3 hover:bg-steel-1'} transition-all">
								{legendaCopiada ? 'Copiada!' : 'Copiar'}
							</button>
						</div>
						<p class="text-xs text-steel-5 whitespace-pre-wrap leading-relaxed font-light">{$carrosselAtual.legenda_linkedin}</p>
					</div>

					<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-5">
						<h4 class="font-semibold text-steel-6 text-sm mb-3">Checklist</h4>
						<div class="space-y-2 text-xs">
							<div class="flex items-center gap-2">
								<span class="text-green-500">✓</span>
								<span>{totalSlides} {totalSlides === 1 ? 'slide' : 'slides'}</span>
							</div>
							{#if totalSlides > 1}
								<div class="flex items-center gap-2">
									<span class="{hasCode ? 'text-green-500' : 'text-steel-4'}">{hasCode ? '✓' : '○'}</span>
									<span>Slide de código</span>
								</div>
								<div class="flex items-center gap-2">
									<span class="{hasCta ? 'text-green-500' : 'text-steel-4'}">{hasCta ? '✓' : '○'}</span>
									<span>CTA com IT Valley</span>
								</div>
							{/if}
							<div class="flex items-center gap-2">
								<span class="{hasImages ? 'text-green-500' : 'text-steel-4'}">{hasImages ? '✓' : '○'}</span>
								<span>Imagens geradas</span>
							</div>
						</div>
					</div>
				</div>
			</div>
		{/if}
	</div>
{/if}
