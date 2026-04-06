<script lang="ts">
	import { fotos, fotoPrincipalId } from '$lib/stores/fotos';
	import { config } from '$lib/stores/config';
	import { ConfigRepository } from '$lib/repositories/ConfigRepository';
	import { CreatorEntryDTO } from '$lib/dtos/CreatorEntryDTO';
	import Banner from '$lib/components/ui/Banner.svelte';
	import Tabs from '$lib/components/ui/Tabs.svelte';
	import Spinner from '$lib/components/ui/Spinner.svelte';
	import PageHeader from '$lib/components/ui/PageHeader.svelte';

	let tabAtiva = $state('marcas');
	let salvando = $state(false);
	let sucesso = $state('');
	let erro = $state('');
	let carregando = $state(false);

	// API Keys
	let claudeKey = $state('');
	let geminiKey = $state('');
	let driveCredentials = $state('');
	let driveFolderId = $state('');

	// Marcas (Design Systems)
	let marcas = $state<Record<string, any>[]>([]);
	let marcaAberta = $state('');
	let marcaVisualizando = $state('');

	// Creator Registry
	let creators = $state<Record<string, any>[]>([]);
	let novoNome = $state('');
	let novaFuncao = $state('TECH_SOURCE');
	let novaPlataforma = $state('YouTube');
	let novaUrl = $state('');

	const tabs = [
		{ id: 'marcas', label: 'Marcas' },
		{ id: 'api', label: 'API Keys' },
		{ id: 'creators', label: 'Creators' },
		{ id: 'fotos', label: 'Foto Perfil' }
	];

	const funcoes = ['TECH_SOURCE', 'EXPLAINER', 'VIRAL_ENGINE', 'THOUGHT_LEADER', 'DINAMICA'];
	const plataformasCreator = ['YouTube', 'Twitter', 'dev.to', 'Hacker News', 'Blog'];
	const backendUrl = $derived($config.backendUrl);

	function showSucesso(msg: string) {
		sucesso = msg;
		setTimeout(() => sucesso = '', 4000);
	}

	// --- Marcas (Design Systems) ---
	async function carregarMarcas() {
		carregando = true;
		try {
			const res = await fetch(`${backendUrl}/api/brands`);
			if (!res.ok) throw new Error('Erro ao carregar marcas');
			const lista = await res.json();
			// Carregar perfil completo de cada marca
			const completas = await Promise.all(
				lista.map(async (b: any) => {
					try {
						const r = await fetch(`${backendUrl}/api/brands/${b.slug}`);
						if (r.ok) return await r.json();
					} catch {}
					return b;
				})
			);
			// Inicializar sem foto/assets (carregam ao clicar "Ver")
			for (const m of completas) {
				m._fotoPreview = null;
				m._assets = [];
				m._loaded = false;
			}
			marcas = completas;
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro ao carregar marcas';
		} finally {
			carregando = false;
		}
	}

	async function verMarca(slug: string) {
		if (marcaVisualizando === slug) { marcaVisualizando = ''; return; }
		try {
			const res = await fetch(`${backendUrl}/api/brands/${slug}`);
			if (!res.ok) throw new Error('Erro ao buscar marca');
			const ds = await res.json();
			// Carregar foto e assets sob demanda
			try {
				const fotoRes = await fetch(`${backendUrl}/api/brands/${slug}/foto`);
				if (fotoRes.ok) {
					const fotoData = await fotoRes.json();
					if (fotoData.foto) ds._fotoPreview = fotoData.foto;
				}
			} catch {}
			try {
				const assetsRes = await fetch(`${backendUrl}/api/brands/${slug}/assets`);
				if (assetsRes.ok) {
					const assetsData = await assetsRes.json();
					ds._assets = assetsData.assets || [];
				}
			} catch {}
			ds._loaded = true;
			marcas = marcas.map(m => m.slug === slug ? ds : m);
			marcaVisualizando = slug;
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro ao buscar marca';
		}
	}

	async function removerMarca(slug: string) {
		try {
			const res = await fetch(`${backendUrl}/api/brands/${slug}`, { method: 'DELETE' });
			if (!res.ok) throw new Error('Erro ao remover');
			marcas = marcas.filter(m => m.slug !== slug);
			showSucesso('Marca removida!');
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro ao remover marca';
		}
	}

	async function salvarMarca(slug: string) {
		salvando = true;
		erro = '';
		try {
			const marca = marcas.find(m => m.slug === slug);
			if (!marca) throw new Error('Marca nao encontrada');
			const res = await fetch(`${backendUrl}/api/brands/${slug}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(marca)
			});
			if (!res.ok) throw new Error('Erro ao salvar');
			showSucesso(`${marca.nome} salva!`);
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro ao salvar marca';
		} finally {
			salvando = false;
		}
	}

	// Upload de .md / .html
	async function handleUploadMarca(event: Event) {
		const input = event.target as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;

		const text = await file.text();
		const nome = file.name.replace(/\.(md|html)$/, '').replace(/[-_]/g, ' ');

		// Parse basico do conteudo para extrair cores se possivel
		const ds: Record<string, any> = {
			nome,
			slug: nome.toLowerCase().replace(/\s+/g, '-'),
			cores: extrairCores(text),
			fontes: extrairFontes(text),
			pesos: { titulo_light: 300, titulo_bold: 600, corpo: 400, badge: 500 },
			elementos: {
				badge_topo: nome,
				badge_topo_cor: 'principal',
				rodape_nome: nome,
				rodape_instituicao: '',
				rodape_extra: '',
				cta_texto: 'Saiba mais',
				glow_cores: [],
				glow_opacidade: 0.08
			},
			estilo: 'dark_mode_premium',
			_raw_content: text
		};

		// Tenta extrair mais dados do texto
		const acentoMatch = text.match(/Acento principal[:\s]*([#][0-9A-Fa-f]{6})/i);
		if (acentoMatch) ds.elementos.glow_cores = [acentoMatch[1]];

		try {
			const res = await fetch(`${backendUrl}/api/brands`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(ds)
			});
			if (!res.ok) throw new Error('Erro ao criar marca');
			await carregarMarcas();
			showSucesso(`"${nome}" adicionada!`);
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro ao criar marca';
		}
		input.value = '';
	}

	function extrairCores(text: string): Record<string, string> {
		const cores: Record<string, string> = {
			fundo: '#0A0A0F', gradiente_de: '#1a0a2e', gradiente_ate: '#0a1628',
			card: '#12121A', card_borda: 'rgba(167,139,250,0.2)',
			acento_principal: '#A78BFA', acento_secundario: '#34D399',
			acento_terciario: '#FBBF24', acento_negativo: '#F87171',
			texto_principal: '#FFFFFF', texto_secundario: '#9896A3', texto_muted: '#5A5A66',
			terminal_barra: '#1a1a2a', terminal_corpo: '#0D0D18', terminal_borda: '#1E1E35'
		};
		const mappings: [RegExp, string][] = [
			[/Fundo[:\s]*([#][0-9A-Fa-f]{6})/i, 'fundo'],
			[/Acento principal[:\s]*([#][0-9A-Fa-f]{6})/i, 'acento_principal'],
			[/Acento secund[aá]rio[:\s]*([#][0-9A-Fa-f]{6})/i, 'acento_secundario'],
			[/Acento terci[aá]rio[:\s]*([#][0-9A-Fa-f]{6})/i, 'acento_terciario'],
			[/Texto.*principal[:\s]*([#][0-9A-Fa-f]{6})/i, 'texto_principal'],
			[/Texto.*secund[aá]rio[:\s]*([#][0-9A-Fa-f]{6})/i, 'texto_secundario'],
			[/Cards?[:\s]*([#][0-9A-Fa-f]{6})/i, 'card'],
			[/Gradiente[:\s]*([#][0-9A-Fa-f]{6})\s*[→\->]+\s*([#][0-9A-Fa-f]{6})/i, 'gradiente_de'],
		];
		for (const [regex, key] of mappings) {
			const m = text.match(regex);
			if (m) {
				cores[key] = m[1];
				if (key === 'gradiente_de' && m[2]) cores.gradiente_ate = m[2];
			}
		}
		return cores;
	}

	function extrairFontes(text: string): Record<string, string> {
		const fontes: Record<string, string> = { titulo: 'Outfit', corpo: 'Outfit', codigo: 'JetBrains Mono', google_fonts: '' };
		const tituloMatch = text.match(/t[ií]tulos?[:\s]*(\w[\w\s]*?)(?:\s*[\(—\-\n])/i);
		if (tituloMatch) fontes.titulo = tituloMatch[1].trim();
		const corpoMatch = text.match(/corpo[:\s]*(\w[\w\s]*?)(?:\s*[\(—\-\n])/i);
		if (corpoMatch) fontes.corpo = corpoMatch[1].trim();
		const codeMatch = text.match(/(?:c[oó]digo|m[eé]tricas|dados)[:\s]*(\w[\w\s]*?)(?:\s*[\(—\-\n])/i);
		if (codeMatch) fontes.codigo = codeMatch[1].trim();
		return fontes;
	}

	// --- API Keys ---
	async function salvarKeys() {
		salvando = true;
		erro = '';
		try {
			await ConfigRepository.salvarApiKeys({
				claude_api_key: claudeKey, gemini_api_key: geminiKey,
				google_drive_credentials: driveCredentials, google_drive_folder_id: driveFolderId
			});
			showSucesso('Chaves salvas!');
		} catch (e) { erro = e instanceof Error ? e.message : 'Erro ao salvar chaves'; }
		finally { salvando = false; }
	}

	// --- Creators ---
	async function carregarCreators() {
		carregando = true;
		try {
			const list = await ConfigRepository.buscarCreatorRegistry();
			creators = list.map((c: any) => ({ ...c }));
		} catch (e) { erro = e instanceof Error ? e.message : 'Erro ao carregar creators'; }
		finally { carregando = false; }
	}
	function adicionarCreator() {
		if (!novoNome.trim()) return;
		creators = [...creators, { id: `c-${Date.now()}`, nome: novoNome, funcao: novaFuncao, plataforma: novaPlataforma, url: novaUrl, ativo: true }];
		novoNome = ''; novaUrl = '';
	}
	function removerCreator(index: number) { creators = creators.filter((_, i) => i !== index); }
	async function salvarCreators() {
		salvando = true; erro = '';
		try {
			const dtos = creators.map(c => new CreatorEntryDTO(c));
			await ConfigRepository.salvarCreatorRegistry(dtos.map(d => d.toPayload()));
			showSucesso('Creators salvos!');
		} catch (e) { erro = e instanceof Error ? e.message : 'Erro ao salvar creators'; }
		finally { salvando = false; }
	}

	// --- Fotos ---
	async function handleFotoUpload(event: Event) {
		const input = event.target as HTMLInputElement;
		if (!input.files) return;
		for (const file of input.files) await fotos.add(file);
		syncFotoPrincipal();
	}
	function removerFoto(id: string) { fotos.remove(id); syncFotoPrincipal(); }
	function selecionarPrincipal(id: string) { fotoPrincipalId.set(id); syncFotoPrincipal(); }
	function syncFotoPrincipal() {
		const principal = $fotos.find((f) => f.id === $fotoPrincipalId);
		config.update((c) => ({ ...c, fotoCriadorBase64: principal?.dataUrl || '' }));
	}
	$effect(() => { if ($fotos.length > 0 && $fotoPrincipalId) syncFotoPrincipal(); });

	// Carregar ao trocar de tab
	$effect(() => {
		erro = '';
		if (tabAtiva === 'marcas') carregarMarcas();
		if (tabAtiva === 'creators') carregarCreators();
	});
</script>

<svelte:head>
	<title>Configuracoes — Content Factory</title>
</svelte:head>

<div class="animate-fade-up max-w-3xl mx-auto">
	<PageHeader title="Configuracoes" subtitle="Marcas, chaves de API, criadores e foto de perfil" />

	{#if sucesso}
		<div class="mb-4"><Banner type="success">{sucesso}</Banner></div>
	{/if}
	{#if erro}
		<div class="mb-4"><Banner type="error" ondismiss={() => erro = ''}>{erro}</Banner></div>
	{/if}

	<Tabs {tabs} active={tabAtiva} onchange={(id) => tabAtiva = id} />

	<div class="mt-6">

		{#if tabAtiva === 'marcas'}
			<!-- ==================== MARCAS (Design Systems) ==================== -->
			{#if carregando}
				<div class="text-center py-12"><Spinner size="lg" /></div>
			{:else}
				<div class="mb-4 flex items-center justify-between">
					<div>
						<p class="text-xs text-text-muted font-mono uppercase tracking-wider">Design Systems ({marcas.length})</p>
						<p class="text-xs text-text-secondary mt-0.5">Cada marca tem suas cores, fontes e estilo. Suba um arquivo .md ou .html para adicionar.</p>
					</div>
					<button onclick={async () => {
						const nome = prompt('Nome da marca:');
						if (!nome) return;
						const slug = nome.toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 20);
						try {
							const res = await fetch(`${backendUrl}/api/brands`, {
								method: 'POST',
								headers: { 'Content-Type': 'application/json' },
								body: JSON.stringify({
									nome, slug,
									cores: { fundo: '#0A0A0F', acento_principal: '#A78BFA', acento_secundario: '#34D399', texto_principal: '#FFFFFF', texto_secundario: '#9896A3' },
									fontes: { titulo: 'Outfit', corpo: 'Outfit' },
									visual: { estilo_fundo: '', estilo_desenho: '', estilo_card: '', estilo_texto: '', regras_extras: '' },
									comunicacao: { persona: '', tom: '', linguagem: '', publico: '' },
									elementos: { badge_topo: nome, rodape_nome: nome },
								})
							});
							if (res.ok) { await carregarMarcas(); showSucesso(`"${nome}" criada!`); }
							else { const d = await res.json(); erro = d.detail || 'Erro'; }
						} catch (e) { erro = 'Erro ao criar marca'; }
					}}
						class="inline-flex px-4 py-2 rounded-full text-xs font-medium text-purple border border-purple/20 hover:bg-purple/8 transition-all cursor-pointer shrink-0">
						+ Nova marca
					</button>
				</div>

				{#if marcas.length === 0}
					<div class="text-center py-16 bg-bg-card rounded-xl border border-border-default">
						<p class="text-text-secondary text-sm mb-2">Nenhuma marca cadastrada</p>
						<p class="text-text-muted text-xs">Suba um .md com o design system da marca</p>
					</div>
				{:else}
					<div class="space-y-3">
						{#each marcas as marca, mi}
							{@const expandida = marcaVisualizando === marca.slug}
							{@const ds = marca}
							<div class="bg-bg-card rounded-xl border {expandida ? 'border-purple/30' : 'border-border-default'} transition-all overflow-hidden">
								<!-- Header -->
								<div class="flex items-center gap-3 p-4">
									<!-- Bolinha de cor principal -->
									{#if ds.cores?.acento_principal}
										<div class="w-5 h-5 rounded-full shrink-0 border border-white/10" style="background-color: {ds.cores.acento_principal}"></div>
									{/if}
									<span class="text-sm text-text-primary font-medium flex-1">{marca.nome}</span>
									{#if marca.estilo}
										<span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-bg-elevated text-text-muted border border-border-default">{marca.estilo}</span>
									{/if}
									<button onclick={() => verMarca(marca.slug)}
										class="px-3 py-1 rounded-full text-xs font-medium text-purple border border-purple/20 hover:bg-purple/8 transition-all cursor-pointer">
										{expandida ? 'Fechar' : 'Ver'}
									</button>
									<button onclick={() => removerMarca(marca.slug)}
										class="px-3 py-1 rounded-full text-xs font-medium text-red border border-red/20 hover:bg-red/8 transition-all cursor-pointer">
										Remover
									</button>
								</div>

								<!-- Detalhes expandidos -->
								{#if expandida}
									<div class="px-4 pb-5 space-y-5 border-t border-border-default pt-4">
										<!-- Cores -->
										{#if ds.cores}
										<div>
											<p class="text-xs text-text-muted font-mono uppercase tracking-wider mb-3">Cores</p>
											<div class="flex gap-2 flex-wrap mb-3">
												{#each Object.entries(ds.cores) as [key, val]}
													{#if typeof val === 'string' && val.startsWith('#')}
														<div class="text-center">
															<div class="w-8 h-8 rounded-lg border border-white/10 mx-auto mb-0.5" style="background-color: {val}"></div>
															<p class="text-[8px] text-text-muted max-w-[48px] truncate">{key}</p>
														</div>
													{/if}
												{/each}
											</div>
											<div class="grid grid-cols-2 gap-2">
												{#each Object.entries(ds.cores) as [key, val]}
													<div class="flex items-center gap-2">
														{#if typeof val === 'string' && val.startsWith('#')}
															<input type="color" bind:value={marcas[mi].cores[key]} class="w-6 h-6 rounded border-0 cursor-pointer shrink-0" />
														{/if}
														<span class="text-[10px] text-text-muted w-24 shrink-0 truncate">{key}</span>
														<input type="text" bind:value={marcas[mi].cores[key]}
															class="flex-1 px-2 py-1 rounded border border-border-default bg-bg-input text-text-primary text-[11px] font-mono focus:border-purple outline-none" />
													</div>
												{/each}
											</div>
										</div>
										{/if}

										<!-- Fontes -->
										{#if ds.fontes}
											<div>
												<p class="text-xs text-text-muted font-mono uppercase tracking-wider mb-3">Fontes</p>
												<div class="grid grid-cols-2 gap-2">
													{#each Object.entries(ds.fontes) as [key, val]}
														<div>
															<label class="block text-[10px] text-text-muted mb-0.5">{key}</label>
															<input type="text" bind:value={marcas[mi].fontes[key]}
																class="w-full px-2 py-1 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
														</div>
													{/each}
												</div>
											</div>
										{/if}

										<!-- Elementos -->
										{#if ds.elementos}
											<div>
												<p class="text-xs text-text-muted font-mono uppercase tracking-wider mb-3">Elementos</p>
												<div class="grid grid-cols-2 gap-2">
													{#each Object.entries(ds.elementos).filter(([_, v]) => typeof v === 'string') as [key, val]}
														<div>
															<label class="block text-[10px] text-text-muted mb-0.5">{key}</label>
															<input type="text" bind:value={marcas[mi].elementos[key]}
																class="w-full px-2 py-1 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
														</div>
													{/each}
												</div>
											</div>
										{/if}

										<!-- Visual -->
										<div>
											<p class="text-xs text-text-muted font-mono uppercase tracking-wider mb-3">Visual (Identidade)</p>
											{#if !marcas[mi].visual}
												{@const _ = (marcas[mi].visual = { estilo_fundo: '', estilo_desenho: '', estilo_card: '', estilo_texto: '', regras_extras: '' })}
											{/if}
											<div class="space-y-2">
												<div>
													<label class="block text-[10px] text-text-muted mb-0.5">Estilo do fundo</label>
													<textarea bind:value={marcas[mi].visual.estilo_fundo} rows="2"
														placeholder="Ex: Fundo preto profundo com gradiente roxo, luzes difusas com bokeh..."
														class="w-full px-2 py-1.5 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none resize-y"></textarea>
												</div>
												<div>
													<label class="block text-[10px] text-text-muted mb-0.5">Estilo do desenho / ilustracao</label>
													<textarea bind:value={marcas[mi].visual.estilo_desenho} rows="2"
														placeholder="Ex: Wireframe 3D em linhas neon roxas, estilo holograma tech..."
														class="w-full px-2 py-1.5 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none resize-y"></textarea>
												</div>
												<div>
													<label class="block text-[10px] text-text-muted mb-0.5">Estilo dos cards</label>
													<textarea bind:value={marcas[mi].visual.estilo_card} rows="1"
														placeholder="Ex: Glassmorphism, vidro fosco semi-transparente..."
														class="w-full px-2 py-1.5 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none resize-y"></textarea>
												</div>
												<div>
													<label class="block text-[10px] text-text-muted mb-0.5">Estilo dos textos</label>
													<textarea bind:value={marcas[mi].visual.estilo_texto} rows="1"
														placeholder="Ex: Titulos grandes em branco bold, palavras-chave em roxo..."
														class="w-full px-2 py-1.5 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none resize-y"></textarea>
												</div>
												<div>
													<label class="block text-[10px] text-text-muted mb-0.5">Regras extras</label>
													<input type="text" bind:value={marcas[mi].visual.regras_extras}
														placeholder="Ex: SEM emojis. SEM clipart. Atmosfera premium."
														class="w-full px-2 py-1.5 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
												</div>
											</div>
										</div>

										<!-- Comunicacao -->
										<div>
											<p class="text-xs text-text-muted font-mono uppercase tracking-wider mb-3">Comunicacao (Voz da Marca)</p>
											{#if !marcas[mi].comunicacao}
												{@const _ = (marcas[mi].comunicacao = { persona: '', tom: '', linguagem: '', publico: '', palavras_proibidas: [], exemplos_frase: [] })}
											{/if}
											<div class="space-y-2">
												<div>
													<label class="block text-[10px] text-text-muted mb-0.5">Persona</label>
													<textarea bind:value={marcas[mi].comunicacao.persona} rows="2"
														placeholder="Ex: Carlos Viana — dev brasileiro no Canada, especialista em IA..."
														class="w-full px-2 py-1.5 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none resize-y"></textarea>
												</div>
												<div>
													<label class="block text-[10px] text-text-muted mb-0.5">Tom</label>
													<input type="text" bind:value={marcas[mi].comunicacao.tom}
														placeholder="Ex: Tecnico mas acessivel. Direto, anti-guru."
														class="w-full px-2 py-1.5 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
												</div>
												<div>
													<label class="block text-[10px] text-text-muted mb-0.5">Linguagem</label>
													<input type="text" bind:value={marcas[mi].comunicacao.linguagem}
														placeholder="Ex: Portugues BR informal tech. Frases curtas e impactantes."
														class="w-full px-2 py-1.5 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
												</div>
												<div>
													<label class="block text-[10px] text-text-muted mb-0.5">Publico-alvo</label>
													<input type="text" bind:value={marcas[mi].comunicacao.publico}
														placeholder="Ex: Devs brasileiros que querem trabalhar no exterior."
														class="w-full px-2 py-1.5 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
												</div>
											</div>
										</div>

										<!-- Foto / Logo da marca -->
										<div>
											<p class="text-xs text-text-muted font-mono uppercase tracking-wider mb-3">Foto / Logo</p>
											<div class="flex items-center gap-4">
												{#if marcas[mi]._fotoPreview}
													<img src={marcas[mi]._fotoPreview} alt="Foto" class="w-16 h-16 rounded-full object-cover border-2" style="border-color: {ds.cores?.acento_principal || '#A78BFA'}" />
												{:else}
													<div class="w-16 h-16 rounded-full bg-bg-elevated border border-border-default flex items-center justify-center text-text-muted text-xs">Sem foto</div>
												{/if}
												<div>
													<label class="inline-flex px-4 py-2 rounded-full text-xs font-medium text-purple border border-purple/20 hover:bg-purple/8 cursor-pointer">
														{marcas[mi]._fotoPreview ? 'Trocar foto' : 'Upload foto'}
														<input type="file" accept="image/*" onchange={async (e) => {
															const input = e.target as HTMLInputElement;
															const file = input.files?.[0];
															if (!file) return;
															const reader = new FileReader();
															reader.onload = async () => {
																const dataUrl = reader.result as string;
																marcas[mi]._fotoPreview = dataUrl;
																try {
																	await fetch(`${backendUrl}/api/brands/${marca.slug}/foto`, {
																		method: 'PUT', headers: { 'Content-Type': 'application/json' },
																		body: JSON.stringify({ foto: dataUrl })
																	});
																	showSucesso('Foto salva!');
																} catch {}
															};
															reader.readAsDataURL(file);
														}} class="hidden" />
													</label>
													<p class="text-[10px] text-text-muted mt-1">A logo aparece no editor de slides pra voce posicionar manualmente</p>
												</div>
											</div>
										</div>

										<!-- Assets da marca (banco de imagens) -->
										<div>
											<p class="text-xs text-text-muted font-mono uppercase tracking-wider mb-3">Assets da Marca (mascotes, fotos, elementos)</p>
											<div class="flex gap-2 flex-wrap mb-3">
												{#each marcas[mi]._assets as asset}
													<div class="relative group">
														<img src={asset.preview} alt={asset.nome} class="w-16 h-16 rounded-lg object-cover border border-border-default" />
														<button onclick={async () => {
															try {
																await fetch(`${backendUrl}/api/brands/${marca.slug}/assets/${asset.nome}`, { method: 'DELETE' });
																marcas[mi]._assets = marcas[mi]._assets.filter((a: any) => a.nome !== asset.nome);
																showSucesso('Asset removido');
															} catch {}
														}}
															class="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-red text-white text-[8px] flex items-center justify-center opacity-0 group-hover:opacity-100 cursor-pointer">x</button>
														<p class="text-[8px] text-text-muted text-center mt-0.5 truncate w-16">{asset.nome}</p>
													</div>
												{/each}
												{#if marcas[mi]._assets.length < 6}
													<label class="w-16 h-16 rounded-lg border border-dashed border-purple/30 flex items-center justify-center text-purple text-lg cursor-pointer hover:bg-purple/5">
														+
														<input type="file" accept="image/*" onchange={async (e) => {
															const input = e.target as HTMLInputElement;
															const file = input.files?.[0];
															if (!file) return;
															const nome = file.name.replace(/\.[^.]+$/, '').replace(/[^a-zA-Z0-9]/g, '_').slice(0, 20);
															const reader = new FileReader();
															reader.onload = async () => {
																try {
																	const res = await fetch(`${backendUrl}/api/brands/${marca.slug}/assets`, {
																		method: 'POST', headers: { 'Content-Type': 'application/json' },
																		body: JSON.stringify({ nome, imagem: reader.result })
																	});
																	if (res.ok) {
																		marcas[mi]._assets = [...marcas[mi]._assets, { nome, preview: reader.result as string }];
																		showSucesso('Asset adicionado!');
																	}
																} catch {}
															};
															reader.readAsDataURL(file);
															input.value = '';
														}} class="hidden" />
													</label>
												{/if}
											</div>
											<p class="text-[10px] text-text-muted">Ate 6 imagens. Mascotes, fotos, elementos visuais da marca. Usados como referencia na geracao.</p>
										</div>

										<button onclick={() => salvarMarca(marca.slug)} disabled={salvando}
											class="px-5 py-2 rounded-full text-xs font-medium text-bg-global bg-purple hover:opacity-90 transition-all cursor-pointer disabled:opacity-50">
											{salvando ? 'Salvando...' : `Salvar ${marca.nome}`}
										</button>
									</div>
								{/if}
							</div>
						{/each}
					</div>
				{/if}
			{/if}

		{:else if tabAtiva === 'api'}
			<!-- ==================== API KEYS ==================== -->
			<div class="bg-bg-card rounded-xl border border-border-default p-6 space-y-5">
				<div>
					<label class="block text-xs text-text-muted mb-1.5">Claude API Key</label>
					<input type="password" bind:value={claudeKey} placeholder="sk-ant-..."
						class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm font-mono
							focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all placeholder:text-text-muted" />
				</div>
				<div>
					<label class="block text-xs text-text-muted mb-1.5">Gemini API Key</label>
					<input type="password" bind:value={geminiKey} placeholder="AIza..."
						class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm font-mono
							focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all placeholder:text-text-muted" />
				</div>
				<div>
					<label class="block text-xs text-text-muted mb-1.5">Google Drive Credentials (JSON)</label>
					<textarea bind:value={driveCredentials} placeholder='&#123;"type": "service_account", ...&#125;' rows="3"
						class="w-full px-4 py-3 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs font-mono
							focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all resize-y placeholder:text-text-muted" />
				</div>
				<div>
					<label class="block text-xs text-text-muted mb-1.5">Google Drive Folder ID</label>
					<input type="text" bind:value={driveFolderId} placeholder="1FRsxT62esou..."
						class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm font-mono
							focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all placeholder:text-text-muted" />
				</div>
				<button onclick={salvarKeys} disabled={salvando}
					class="px-6 py-2.5 rounded-full text-sm font-medium text-bg-global bg-purple hover:opacity-90 transition-all cursor-pointer disabled:opacity-50">
					{salvando ? 'Salvando...' : 'Salvar Chaves'}
				</button>
			</div>

		{:else if tabAtiva === 'creators'}
			<!-- ==================== CREATORS ==================== -->
			{#if carregando}
				<div class="text-center py-12"><Spinner size="lg" /></div>
			{:else}
				<div class="bg-bg-card rounded-xl border border-border-default p-6">
					<p class="text-xs text-text-muted font-mono uppercase tracking-wider mb-4">Criadores ({creators.length})</p>
					{#if creators.length > 0}
						<div class="space-y-2 mb-6 max-h-[400px] overflow-y-auto">
							{#each creators as creator, i}
								<div class="flex items-center gap-3 p-3 rounded-lg bg-bg-elevated border border-border-default">
									<span class="text-sm text-text-primary flex-1 min-w-0 truncate">{creator.nome}</span>
									<span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-purple/8 text-purple border border-purple/20 shrink-0">{creator.funcao}</span>
									<span class="text-xs text-text-muted shrink-0">{creator.plataforma}</span>
									<button onclick={() => removerCreator(i)}
										class="w-6 h-6 rounded-full bg-red/9 text-red text-xs flex items-center justify-center hover:bg-red/15 transition-all cursor-pointer shrink-0">x</button>
								</div>
							{/each}
						</div>
					{:else}
						<p class="text-sm text-text-secondary mb-6">Nenhum criador cadastrado.</p>
					{/if}
					<div class="border-t border-border-default pt-4">
						<p class="text-xs text-text-muted mb-3">Adicionar criador</p>
						<div class="flex flex-wrap gap-3">
							<input type="text" bind:value={novoNome} placeholder="Nome..."
								class="flex-1 min-w-[150px] px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm focus:border-purple outline-none placeholder:text-text-muted" />
							<select bind:value={novaFuncao}
								class="px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm focus:border-purple outline-none cursor-pointer">
								{#each funcoes as f}<option value={f}>{f}</option>{/each}
							</select>
							<select bind:value={novaPlataforma}
								class="px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm focus:border-purple outline-none cursor-pointer">
								{#each plataformasCreator as p}<option value={p}>{p}</option>{/each}
							</select>
							<input type="text" bind:value={novaUrl} placeholder="URL..."
								class="flex-1 min-w-[150px] px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm focus:border-purple outline-none placeholder:text-text-muted" />
							<button onclick={adicionarCreator}
								class="px-4 py-2 rounded-full text-sm font-medium text-purple border border-purple/20 hover:bg-purple/8 transition-all cursor-pointer">+ Adicionar</button>
						</div>
					</div>
					<div class="mt-6">
						<button onclick={salvarCreators} disabled={salvando}
							class="px-6 py-2.5 rounded-full text-sm font-medium text-bg-global bg-purple hover:opacity-90 transition-all cursor-pointer disabled:opacity-50">
							{salvando ? 'Salvando...' : 'Salvar Creators'}
						</button>
					</div>
				</div>
			{/if}

		{:else if tabAtiva === 'fotos'}
			<!-- ==================== FOTO PERFIL ==================== -->
			<div class="bg-bg-card rounded-xl border border-border-default p-6">
				<p class="text-xs text-text-muted font-mono uppercase tracking-wider mb-1">Foto de perfil dos slides</p>
				<p class="text-xs text-text-secondary mb-5">Essa foto aparece na moldura redondinha no rodape de todo slide. Clique pra definir como principal.</p>

				{#each $fotos.filter((f) => f.id === $fotoPrincipalId) as principal}
					<div class="flex items-center gap-4 mb-6 p-4 rounded-xl bg-purple/5 border border-purple/20">
						<img src={principal.dataUrl} alt="Foto principal" class="w-16 h-16 rounded-full object-cover border-2 border-purple shadow-[0_0_20px_rgba(167,139,250,0.3)]" />
						<div>
							<p class="text-sm text-text-primary font-medium">Foto principal ativa</p>
							<p class="text-xs text-text-muted">{principal.name}</p>
							<p class="text-xs text-purple mt-1">Usada em todos os slides gerados</p>
						</div>
					</div>
				{:else}
					<div class="mb-6 p-4 rounded-xl bg-bg-elevated border border-border-default text-center">
						<div class="w-16 h-16 rounded-full bg-bg-input border-2 border-dashed border-border-default mx-auto mb-2 flex items-center justify-center">
							<span class="text-2xl text-text-muted">?</span>
						</div>
						<p class="text-sm text-text-secondary">Nenhuma foto selecionada</p>
						<p class="text-xs text-text-muted">A Gemini vai inventar um rosto se nao tiver foto</p>
					</div>
				{/each}

				{#if $fotos.length > 0}
					<div class="flex gap-4 flex-wrap mb-6">
						{#each $fotos as foto}
							<div class="relative group">
								<button onclick={() => selecionarPrincipal(foto.id)}
									class="rounded-full transition-all cursor-pointer {foto.id === $fotoPrincipalId ? 'ring-3 ring-purple ring-offset-2 ring-offset-bg-card' : 'hover:ring-2 hover:ring-purple/40 hover:ring-offset-1 hover:ring-offset-bg-card'}">
									<img src={foto.dataUrl} alt={foto.name} class="w-20 h-20 rounded-full object-cover border-2 {foto.id === $fotoPrincipalId ? 'border-purple' : 'border-border-default'}" />
								</button>
								{#if foto.id === $fotoPrincipalId}
									<span class="absolute -bottom-1 left-1/2 -translate-x-1/2 px-1.5 py-0.5 rounded-full text-[9px] font-mono bg-purple text-white whitespace-nowrap">principal</span>
								{/if}
								<button onclick={() => removerFoto(foto.id)}
									class="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-red text-white text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">x</button>
							</div>
						{/each}
					</div>
				{/if}

				<label class="inline-flex px-5 py-2.5 rounded-full text-sm font-medium text-purple border border-purple/20 hover:bg-purple/8 transition-all cursor-pointer">
					+ Adicionar foto
					<input type="file" accept="image/*" multiple onchange={handleFotoUpload} class="hidden" />
				</label>
			</div>
		{/if}
	</div>
</div>
