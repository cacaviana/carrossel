<script lang="ts">
	import { fotos, fotoPrincipalId } from '$lib/stores/fotos';
	import { config } from '$lib/stores/config';
	import { ConfigRepository } from '$lib/repositories/ConfigRepository';
	import { CreatorEntryDTO } from '$lib/dtos/CreatorEntryDTO';
	import Banner from '$lib/components/ui/Banner.svelte';
	import Tabs from '$lib/components/ui/Tabs.svelte';
	import Spinner from '$lib/components/ui/Spinner.svelte';
	import PageHeader from '$lib/components/ui/PageHeader.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import { API_BASE } from '$lib/api';
	import SlidePreviewMini from '$lib/components/brand/SlidePreviewMini.svelte';

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

	// Nova marca com analise de referencias
	let showNovaMarca = $state(false);
	let novaMarcaNome = $state('');
	let novaMarcaDescricao = $state('');
	let novaMarcaImagens = $state<string[]>([]);
	let novaMarcaAnalisando = $state(false);
	let novaMarcaResultado = $state<any>(null);
	let novaMarcaCriando = $state(false);

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
					if (fotoData.foto) ds._fotoPreview = fotoData.foto.startsWith('http') ? fotoData.foto : `${backendUrl}${fotoData.foto}`;
				}
			} catch {}
			try {
				const assetsRes = await fetch(`${backendUrl}/api/brands/${slug}/assets`);
				if (assetsRes.ok) {
					const assetsData = await assetsRes.json();
					ds._assets = (assetsData.assets || []).map((a: any) => ({
						...a,
						preview: a.preview.startsWith('http') || a.preview.startsWith('data:') ? a.preview : `${backendUrl}${a.preview}`,
					}));
				}
			} catch {}
			ds._loaded = true;
			// Carregar analise salva se existir
			if (ds._analise_referencia) {
				analiseRef = { ...analiseRef, [slug]: ds._analise_referencia };
			}
			marcas = marcas.map(m => m.slug === slug ? ds : m);
			marcaVisualizando = slug;
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro ao buscar marca';
		}
	}

	let menuAberto = $state('');
	let brandTab = $state<Record<string, string>>({});
	let regenerandoDna = $state<Record<string, boolean>>({});

	async function autoGerarDnaSeVazio(slug: string, mi: number) {
		const dna = marcas[mi].dna;
		const vazio = !dna || (!dna.estilo && !dna.cores && !dna.tipografia && !dna.elementos);
		if (!vazio || regenerandoDna[slug]) return;
		regenerandoDna = { ...regenerandoDna, [slug]: true };
		try {
			const res = await fetch(`${backendUrl}/api/brands/${slug}/dna/regenerate`, {
				method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}'
			});
			if (res.ok) {
				const body = await res.json();
				marcas[mi].dna = body.dna;
				marcas = [...marcas];
				showSucesso('DNA gerado automaticamente!');
			}
		} catch {}
		regenerandoDna = { ...regenerandoDna, [slug]: false };
	}
	function getBrandTab(slug: string) { return brandTab[slug] || 'aparencia'; }
	function setBrandTab(slug: string, tab: string) { brandTab = { ...brandTab, [slug]: tab }; }
	let showClonarModal = $state(false);
	let showRenomearModal = $state(false);
	let renomearSlug = $state('');
	let renomearNome = $state('');
	let renomeando = $state(false);

	function abrirRenomear(slug: string, nome: string) {
		renomearSlug = slug;
		renomearNome = nome;
		showRenomearModal = true;
	}

	async function executarRenomear() {
		if (!renomearNome) return;
		renomeando = true;
		try {
			const res = await fetch(`${API_BASE}/api/brands/${renomearSlug}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ nome: renomearNome, slug: renomearSlug }),
			});
			if (!res.ok) throw new Error('Erro ao renomear');
			showRenomearModal = false;
			showSucesso(`Marca renomeada para "${renomearNome}"!`);
			await carregarMarcas();
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro ao renomear';
		} finally {
			renomeando = false;
		}
	}
	let clonarOrigem = $state('');
	let clonarSlug = $state('');
	let clonarNome = $state('');
	let clonando = $state(false);

	function gerarSlug(nome: string): string {
		return nome.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '').replace(/-+/g, '-').slice(0, 30);
	}

	function abrirClonar(slug: string, nome: string) {
		clonarOrigem = slug;
		clonarNome = nome + ' (Copia)';
		clonarSlug = gerarSlug(clonarNome);
		showClonarModal = true;
	}

	async function executarClonar() {
		if (!clonarSlug || !clonarNome) return;
		clonando = true;
		try {
			const res = await fetch(`${API_BASE}/api/brands/${clonarOrigem}/clonar`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ slug_destino: clonarSlug, nome_destino: clonarNome }),
			});
			if (!res.ok) {
				const err = await res.json().catch(() => ({}));
				throw new Error(err.detail || 'Erro ao clonar');
			}
			showClonarModal = false;
			showSucesso(`Marca "${clonarNome}" clonada!`);
			await carregarMarcas();
		} catch (e) {
			erro = e instanceof Error ? e.message : 'Erro ao clonar marca';
		} finally {
			clonando = false;
		}
	}

	let showRemoverModal = $state(false);
	let removerSlug = $state('');
	let removerNome = $state('');

	function abrirRemover(slug: string, nome: string) {
		removerSlug = slug;
		removerNome = nome;
		showRemoverModal = true;
	}

	async function confirmarRemover() {
		showRemoverModal = false;
		try {
			const res = await fetch(`${API_BASE}/api/brands/${removerSlug}`, { method: 'DELETE' });
			if (!res.ok) throw new Error('Erro ao remover');
			marcas = marcas.filter(m => m.slug !== removerSlug);
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

	// --- Nova Marca (analise de referencias) ---
	function handleImagensUpload(e: Event) {
		const files = (e.target as HTMLInputElement).files;
		if (!files) return;
		const promises = Array.from(files).slice(0, 5).map(file => {
			return new Promise<string>((resolve) => {
				const reader = new FileReader();
				reader.onload = () => resolve(reader.result as string);
				reader.readAsDataURL(file);
			});
		});
		Promise.all(promises).then(results => {
			novaMarcaImagens = [...novaMarcaImagens, ...results].slice(0, 5);
		});
	}

	async function analisarReferencias() {
		if (novaMarcaImagens.length === 0) return;
		novaMarcaAnalisando = true;
		try {
			const res = await fetch(`${backendUrl}/api/analisar-referencias`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					imagens: novaMarcaImagens.map(img => img.split(',')[1] || img),
					nome_marca: novaMarcaNome,
					descricao: novaMarcaDescricao,
				}),
			});
			if (res.ok) {
				novaMarcaResultado = await res.json();
			} else {
				const d = await res.json().catch(() => ({}));
				erro = d.detail || 'Erro ao analisar referencias';
			}
		} catch {
			erro = 'Erro ao conectar com o servidor';
		} finally {
			novaMarcaAnalisando = false;
		}
	}

	async function criarMarcaComReferencias() {
		if (!novaMarcaNome) return;
		novaMarcaCriando = true;
		const slug = novaMarcaNome.toLowerCase().replace(/[^a-z0-9-]/g, '-').replace(/-+/g, '-').slice(0, 30);
		try {
			const r = novaMarcaResultado;
			const payload: Record<string, any> = {
				nome: novaMarcaNome,
				slug,
				comunicacao: { persona: '', tom: '', linguagem: '', publico: novaMarcaDescricao || '', palavras_proibidas: [] },
			};
			if (r) {
				payload.cores = r.cores;
				payload.visual = r.visual;
				payload.elementos = { badge_topo: novaMarcaNome, badge_topo_cor: r.cores.acento_principal, rodape_nome: novaMarcaNome };
			} else {
				payload.cores = {
					fundo: '#0A0A0F', gradiente_de: '#1a0a2e', gradiente_ate: '#0a1628',
					card: '#12121A', card_borda: 'rgba(167,139,250,0.2)',
					acento_principal: '#A78BFA', acento_secundario: '#34D399',
					acento_terciario: '#FBBF24', acento_negativo: '#F87171',
					texto_principal: '#FFFFFF', texto_secundario: '#9896A3', texto_muted: '#5A5A66',
				};
				payload.elementos = { badge_topo: novaMarcaNome, badge_topo_cor: '#A78BFA', rodape_nome: novaMarcaNome };
			}
			const res = await fetch(`${backendUrl}/api/brands`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload),
			});
			if (res.ok) {
				await carregarMarcas();
				showSucesso(`"${novaMarcaNome}" criada com sucesso!`);
				showNovaMarca = false;
				novaMarcaNome = '';
				novaMarcaDescricao = '';
				novaMarcaImagens = [];
				novaMarcaResultado = null;
			} else {
				const d = await res.json().catch(() => ({}));
				erro = d.detail || 'Erro ao criar marca';
			}
		} catch { erro = 'Erro ao criar marca'; }
		finally { novaMarcaCriando = false; }
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

	// Analise de referencia visual
	let analisandoRef = $state<Record<string, boolean>>({});
	let analiseRef = $state<Record<string, any>>({});

	async function analisarReferencia(slug: string, imagemBase64: string, nomeAsset: string) {
		analisandoRef = { ...analisandoRef, [slug]: true };
		erro = '';
		console.log('[analisar] Iniciando analise para', slug, '- imagem:', imagemBase64?.slice(0, 50));
		try {
			const res = await fetch(`${backendUrl}/api/descrever-referencia`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ imagem: imagemBase64 }),
			});
			console.log('[analisar] Response status:', res.status);
			const rawText = await res.text();
			console.log('[analisar] Raw response (primeiros 500 chars):', rawText.slice(0, 500));
			if (res.ok) {
				const data = JSON.parse(rawText);
				console.log('[analisar] Campos:', Object.keys(data));
				console.log('[analisar] tem cores?', !!data.cores || !!data.dna_cores, '| tem tipografia?', !!data.tipografia || !!data.dna_tipografia);
				analiseRef = { ...analiseRef, [slug]: { ...data, asset: nomeAsset } };
			} else {
				const d = await res.json().catch(() => ({}));
				console.error('[analisar] Erro:', d);
				erro = d.detail || 'Erro ao analisar imagem';
			}
		} catch (e) {
			console.error('[analisar] Exception:', e);
			erro = 'Erro ao conectar com o servidor';
		} finally {
			analisandoRef = { ...analisandoRef, [slug]: false };
		}
	}

	async function aplicarAnaliseNaMarca(mi: number, slug: string) {
		const a = analiseRef[slug];
		if (!a) return;

		const bp = a.brand_profile;
		const lum = (hex: string) => {
			if (!hex || !hex.startsWith('#') || hex.length < 7) return 128;
			const r = parseInt(hex.slice(1,3),16), g = parseInt(hex.slice(3,5),16), b = parseInt(hex.slice(5,7),16);
			return (r*299 + g*587 + b*114) / 1000;
		};

		// 1. Cores
		if (bp?.cores_aplicar) {
			const cores = { ...bp.cores_aplicar };
			if (cores.fundo && cores.texto_principal) {
				const diff = Math.abs(lum(cores.fundo) - lum(cores.texto_principal));
				if (diff < 80) cores.texto_principal = lum(cores.fundo) > 128 ? '#2D2D2D' : '#F5F5F5';
			}
			marcas[mi].cores = { ...marcas[mi].cores, ...cores };
		}

		// 2. Fontes
		if (bp?.fontes_aplicar) {
			marcas[mi].fontes = { ...(marcas[mi].fontes || {}), ...bp.fontes_aplicar };
		}

		// 3. Visual — sobrescreve TUDO com os dados da análise
		marcas[mi].visual = {
			estilo_fundo: bp?.visual_aplicar?.estilo_fundo || a.prompt_replicar || '',
			estilo_desenho: bp?.visual_aplicar?.estilo_desenho || (a.decoracao ? JSON.stringify(a.decoracao, null, 0).slice(0, 500) : ''),
			estilo_card: bp?.visual_aplicar?.estilo_card || '',
			estilo_texto: bp?.visual_aplicar?.estilo_texto || '',
			regras_extras: [
				bp?.visual_aplicar?.regras_extras || '',
				a.estetica ? `Estetica: ${a.estetica}` : '',
				a.vibe ? `Vibe: ${a.vibe}` : '',
			].filter(Boolean).join('. '),
		};

		// 4. Regras do feed
		if (a.regras_feed) {
			marcas[mi].regras_feed = a.regras_feed;
		}
		if (a.hack_consistencia) {
			marcas[mi].hack_consistencia = a.hack_consistencia;
		}

		// 5. Salvar analise completa no brand (persiste no backend)
		marcas[mi]._analise_referencia = a;

		// 5. Forçar reatividade
		marcas = [...marcas];

		// 6. Auto-salvar no backend
		salvando = true;
		try {
			const res = await fetch(`${backendUrl}/api/brands/${slug}`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(marcas[mi])
			});
			if (res.ok) {
				showSucesso('Aplicado e SALVO! Veja nas abas Aparencia e Estilo.');
				// Trocar pra aba Aparencia pra ver resultado
				setBrandTab(slug, 'aparencia');
			} else {
				erro = 'Erro ao salvar marca';
			}
		} catch {
			erro = 'Erro ao salvar';
		} finally {
			salvando = false;
		}
	}

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
						<p class="text-xs text-text-secondary mt-0.5">Cada marca tem suas cores, fontes e estilo. Suba imagens de referencia e a IA extrai a paleta e o estilo automaticamente.</p>
					</div>
					<button data-testid="btn-nova-marca" onclick={() => showNovaMarca = true}
						class="inline-flex px-4 py-2 rounded-full text-xs font-medium text-purple border border-purple/20 hover:bg-purple/8 transition-all cursor-pointer shrink-0">
						+ Nova marca
					</button>
				</div>

				{#if marcas.length === 0}
					<div class="text-center py-16 bg-bg-card rounded-xl border border-border-default">
						<p class="text-text-secondary text-sm mb-2">Nenhuma marca cadastrada</p>
						<p class="text-text-muted text-xs">Crie sua primeira marca subindo imagens de referencia</p>
					</div>
				{:else}
					<div class="space-y-3">
						{#each marcas as marca, mi}
							{@const expandida = marcaVisualizando === marca.slug}
							{@const ds = marca}
							<div class="bg-bg-card rounded-xl border {expandida ? 'border-purple/30' : 'border-border-default'} transition-all">
								<!-- Header -->
								<div class="flex items-center gap-3 p-4">
									<!-- Bolinha de cor principal -->
									{#if ds.cores?.acento_principal}
										<div class="w-5 h-5 rounded-full shrink-0 border border-black/10" style="background-color: {ds.cores.acento_principal}"></div>
									{/if}
									<span class="text-sm text-text-primary font-medium flex-1">{marca.nome}</span>
									{#if marca.estilo}
										<span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-bg-elevated text-text-muted border border-border-default">{marca.estilo}</span>
									{/if}
									<button onclick={() => verMarca(marca.slug)}
										class="px-3 py-1 rounded-full text-xs font-medium text-purple border border-purple/20 hover:bg-purple/8 transition-all cursor-pointer">
										{expandida ? 'Fechar' : 'Ver'}
									</button>
									<div class="relative">
										<button onclick={() => menuAberto = menuAberto === marca.slug ? '' : marca.slug}
											class="p-1.5 rounded-lg hover:bg-black/5 transition-all cursor-pointer text-text-muted">
											<svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
												<path d="M10 6a2 2 0 110-4 2 2 0 010 4zm0 6a2 2 0 110-4 2 2 0 010 4zm0 6a2 2 0 110-4 2 2 0 010 4z" />
											</svg>
										</button>
										{#if menuAberto === marca.slug}
											<div class="absolute right-0 top-8 z-20 bg-bg-card border border-border-default rounded-xl shadow-xl py-1 min-w-[140px]">
												<button onclick={() => { menuAberto = ''; abrirRenomear(marca.slug, marca.nome); }}
													class="w-full text-left px-4 py-2 text-xs text-text-primary hover:bg-black/5 cursor-pointer">Renomear</button>
												<button onclick={() => { menuAberto = ''; abrirClonar(marca.slug, marca.nome); }}
													class="w-full text-left px-4 py-2 text-xs text-text-primary hover:bg-black/5 cursor-pointer">Clonar</button>
												<button onclick={() => { menuAberto = ''; abrirRemover(marca.slug, marca.nome); }}
													class="w-full text-left px-4 py-2 text-xs text-red hover:bg-red/5 cursor-pointer">Remover</button>
											</div>
										{/if}
									</div>
								</div>

								<!-- Detalhes expandidos -->
								{#if expandida}
									{@const currentTab = getBrandTab(marca.slug)}
									<div class="border-t border-border-default">
										<div class="flex border-b border-border-default bg-bg-elevated/50">
											{#each [
												{ id: 'aparencia', label: 'Aparencia', desc: 'Cores e fontes' },
												{ id: 'estilo', label: 'Estilo dos Slides', desc: 'Como a IA desenha' },
												{ id: 'voz', label: 'Voz da Marca', desc: 'Como a marca fala' },
												{ id: 'imagens', label: 'Imagens', desc: 'Logo e referencias' },
											] as tab}
												<button
													onclick={() => setBrandTab(marca.slug, tab.id)}
													class="flex-1 py-3 px-2 text-center transition-all cursor-pointer border-b-2
														{currentTab === tab.id
															? 'border-purple text-purple bg-bg-card'
															: 'border-transparent text-text-muted hover:text-text-secondary hover:bg-bg-card/50'}"
												>
													<span class="block text-xs font-medium">{tab.label}</span>
													<span class="block text-[9px] text-text-muted mt-0.5">{tab.desc}</span>
												</button>
											{/each}
										</div>

										<div class="px-5 py-5">

										<!-- ===== ABA: APARENCIA ===== -->
										{#if currentTab === 'aparencia'}
											<div class="space-y-6">

												<!-- DNA DA MARCA (4 linhas que definem a identidade) -->
												<div class="bg-purple/5 rounded-xl p-5 border border-purple/20">
													<div class="flex items-start justify-between gap-3 mb-1">
														<p class="text-sm text-text-primary font-semibold">DNA da marca</p>
														<button
															onclick={async () => {
																if (regenerandoDna[marca.slug]) return;
																regenerandoDna = { ...regenerandoDna, [marca.slug]: true };
																try {
																	const res = await fetch(`${backendUrl}/api/brands/${marca.slug}/dna/regenerate`, {
																		method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}'
																	});
																	if (res.ok) {
																		const body = await res.json();
																		marcas[mi].dna = body.dna;
																		marcas = [...marcas];
																		showSucesso('DNA regenerado!');
																	} else {
																		const err = await res.json().catch(() => ({}));
																		erro = err.detail || 'Erro ao gerar DNA (precisa ter pelo menos 1 referencia)';
																		setTimeout(() => erro = '', 5000);
																	}
																} catch {
																	erro = 'Erro de rede ao gerar DNA';
																	setTimeout(() => erro = '', 5000);
																} finally {
																	regenerandoDna = { ...regenerandoDna, [marca.slug]: false };
																}
															}}
															disabled={regenerandoDna[marca.slug]}
															class="text-[10px] text-purple border border-purple/30 px-2 py-0.5 rounded-full hover:bg-purple/10 disabled:opacity-50 disabled:cursor-wait cursor-pointer">
															{regenerandoDna[marca.slug] ? 'Gerando...' : 'Regerar com IA'}
														</button>
													</div>
													<p class="text-xs text-text-secondary mb-4">4 linhas que definem a identidade visual. Entram no prompt de geracao de imagem.</p>

													<div class="grid grid-cols-2 gap-3">
														<div>
															<label class="block text-[10px] text-text-muted mb-1">Estilo</label>
															<input type="text"
																value={marcas[mi].dna?.estilo || ''}
																oninput={(e) => {
																	if (!marcas[mi].dna) marcas[mi].dna = { estilo: '', cores: '', tipografia: '', elementos: '' };
																	marcas[mi].dna.estilo = (e.target as HTMLInputElement).value;
																	marcas = [...marcas];
																}}
																placeholder="cute, clean, moderno"
																class="w-full px-2 py-1.5 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
														</div>
														<div>
															<label class="block text-[10px] text-text-muted mb-1">Cores</label>
															<input type="text"
																value={marcas[mi].dna?.cores || ''}
																oninput={(e) => {
																	if (!marcas[mi].dna) marcas[mi].dna = { estilo: '', cores: '', tipografia: '', elementos: '' };
																	marcas[mi].dna.cores = (e.target as HTMLInputElement).value;
																	marcas = [...marcas];
																}}
																placeholder="rosa pastel, azul claro, branco"
																class="w-full px-2 py-1.5 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
														</div>
														<div>
															<label class="block text-[10px] text-text-muted mb-1">Tipografia</label>
															<input type="text"
																value={marcas[mi].dna?.tipografia || ''}
																oninput={(e) => {
																	if (!marcas[mi].dna) marcas[mi].dna = { estilo: '', cores: '', tipografia: '', elementos: '' };
																	marcas[mi].dna.tipografia = (e.target as HTMLInputElement).value;
																	marcas = [...marcas];
																}}
																placeholder="bold arredondada"
																class="w-full px-2 py-1.5 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
														</div>
														<div>
															<label class="block text-[10px] text-text-muted mb-1">Elementos</label>
															<input type="text"
																value={marcas[mi].dna?.elementos || ''}
																oninput={(e) => {
																	if (!marcas[mi].dna) marcas[mi].dna = { estilo: '', cores: '', tipografia: '', elementos: '' };
																	marcas[mi].dna.elementos = (e.target as HTMLInputElement).value;
																	marcas = [...marcas];
																}}
																placeholder="doodles leves"
																class="w-full px-2 py-1.5 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
														</div>
													</div>
													<p class="text-[10px] text-text-muted mt-2">Na Fase 2 esses campos serao gerados automaticamente ao subir a primeira referencia.</p>
												</div>

												<!-- REFERENCIAS VISUAIS - POOL COM AVATAR -->
												<div class="bg-amber/5 rounded-xl p-5 border border-amber/20">
													<p class="text-sm text-text-primary font-semibold mb-1">Referencias com avatar</p>
													<p class="text-xs text-text-secondary mb-4">Refs que mostram a pessoa. Usadas em slides com avatar (capa, CTA). Ate 5 imagens.</p>

													<div class="flex gap-3 flex-wrap mb-3">
														{#each marcas[mi]._assets.filter((a: any) => a.pool === 'com_avatar') as asset}
															<div class="relative group">
																<img src={asset.preview} alt={asset.nome}
																	class="w-20 h-20 rounded-xl object-cover border-2 border-amber ring-2 ring-amber/30 shadow-sm" />
																<button onclick={async () => {
																	try {
																		await fetch(`${backendUrl}/api/brands/${marca.slug}/assets/${asset.nome}`, { method: 'DELETE' });
																		marcas[mi]._assets = marcas[mi]._assets.filter((a: any) => a.nome !== asset.nome);
																		showSucesso('Referencia removida');
																	} catch {}
																}}
																	class="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-red text-white text-[9px] flex items-center justify-center opacity-0 group-hover:opacity-100 cursor-pointer">x</button>
															</div>
														{/each}
														{#if marcas[mi]._assets.filter((a: any) => a.pool === 'com_avatar').length < 5}
															<label class="w-20 h-20 rounded-xl border-2 border-dashed border-amber/40 flex flex-col items-center justify-center text-amber/70 cursor-pointer hover:bg-amber/5 transition-all gap-0.5">
																<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
																<span class="text-[8px] font-medium">{marcas[mi]._assets.filter((a: any) => a.pool === 'com_avatar').length}/5</span>
																<input type="file" accept="image/*" onchange={async (e) => {
																	const input = e.target as HTMLInputElement;
																	const file = input.files?.[0];
																	if (!file) return;
																	const nome = file.name.replace(/\.[^.]+$/, '').replace(/[^a-zA-Z0-9]/g, '_').slice(0, 15);
																	const reader = new FileReader();
																	reader.onload = async () => {
																		try {
																			const res = await fetch(`${backendUrl}/api/brands/${marca.slug}/assets`, {
																				method: 'POST', headers: { 'Content-Type': 'application/json' },
																				body: JSON.stringify({ nome, imagem: reader.result, pool: 'com_avatar' })
																			});
																			if (res.ok) {
																				const body = await res.json();
																				marcas[mi]._assets = [...marcas[mi]._assets, { nome: body.nome, preview: reader.result as string, is_referencia: true, pool: 'com_avatar' }]; autoGerarDnaSeVazio(marca.slug, mi);
																				showSucesso('Referencia adicionada!');
																			}
																		} catch {}
																	};
																	reader.readAsDataURL(file);
																	input.value = '';
																}} class="hidden" />
															</label>
														{/if}
													</div>
												</div>

												<!-- REFERENCIAS VISUAIS - POOL SEM AVATAR -->
												<div class="bg-amber/5 rounded-xl p-5 border border-amber/20">
													<p class="text-sm text-text-primary font-semibold mb-1">Referencias sem avatar</p>
													<p class="text-xs text-text-secondary mb-4">Refs puramente visuais, sem pessoa. Usadas em slides internos. Ate 5 imagens.</p>

													<div class="flex gap-3 flex-wrap mb-3">
														{#each marcas[mi]._assets.filter((a: any) => a.pool === 'sem_avatar') as asset}
															<div class="relative group">
																<img src={asset.preview} alt={asset.nome}
																	class="w-20 h-20 rounded-xl object-cover border-2 border-amber ring-2 ring-amber/30 shadow-sm" />
																<button onclick={async () => {
																	try {
																		await fetch(`${backendUrl}/api/brands/${marca.slug}/assets/${asset.nome}`, { method: 'DELETE' });
																		marcas[mi]._assets = marcas[mi]._assets.filter((a: any) => a.nome !== asset.nome);
																		showSucesso('Referencia removida');
																	} catch {}
																}}
																	class="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-red text-white text-[9px] flex items-center justify-center opacity-0 group-hover:opacity-100 cursor-pointer">x</button>
															</div>
														{/each}
														{#if marcas[mi]._assets.filter((a: any) => a.pool === 'sem_avatar').length < 5}
															<label class="w-20 h-20 rounded-xl border-2 border-dashed border-amber/40 flex flex-col items-center justify-center text-amber/70 cursor-pointer hover:bg-amber/5 transition-all gap-0.5">
																<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
																<span class="text-[8px] font-medium">{marcas[mi]._assets.filter((a: any) => a.pool === 'sem_avatar').length}/5</span>
																<input type="file" accept="image/*" onchange={async (e) => {
																	const input = e.target as HTMLInputElement;
																	const file = input.files?.[0];
																	if (!file) return;
																	const nome = file.name.replace(/\.[^.]+$/, '').replace(/[^a-zA-Z0-9]/g, '_').slice(0, 15);
																	const reader = new FileReader();
																	reader.onload = async () => {
																		try {
																			const res = await fetch(`${backendUrl}/api/brands/${marca.slug}/assets`, {
																				method: 'POST', headers: { 'Content-Type': 'application/json' },
																				body: JSON.stringify({ nome, imagem: reader.result, pool: 'sem_avatar' })
																			});
																			if (res.ok) {
																				const body = await res.json();
																				marcas[mi]._assets = [...marcas[mi]._assets, { nome: body.nome, preview: reader.result as string, is_referencia: true, pool: 'sem_avatar' }]; autoGerarDnaSeVazio(marca.slug, mi);
																				showSucesso('Referencia adicionada!');
																			}
																		} catch {}
																	};
																	reader.readAsDataURL(file);
																	input.value = '';
																}} class="hidden" />
															</label>
														{/if}
													</div>
													{#if marcas[mi]._assets.filter((a: any) => a.pool === 'com_avatar').length === 0 && marcas[mi]._assets.filter((a: any) => a.pool === 'sem_avatar').length === 0}
														<p class="text-[10px] text-text-muted mt-2">Sem referencias? A IA vai usar os campos de cores e estilo abaixo.</p>
													{/if}
												</div>

												<div class="bg-steel-0/50 rounded-xl p-4 border border-steel-3/10">
													<p class="text-sm text-text-primary font-medium mb-1">Paleta de cores e tipografia</p>
													<p class="text-xs text-text-secondary">Estas cores aparecem no fundo, nos textos e nos destaques de cada slide. O preview ao lado mostra como fica.</p>
												</div>

												<div>
													<div class="space-y-5">
														<!-- Cores -->
														{#if ds.cores}
															<div>
																<p class="text-xs text-text-primary font-medium mb-2">Cores da marca</p>
																<div class="flex gap-2 flex-wrap mb-3">
																	{#each Object.keys(ds.cores) as key}
																		{#if typeof marcas[mi].cores[key] === 'string' && marcas[mi].cores[key].startsWith('#')}
																			<div class="text-center">
																				<div class="w-8 h-8 rounded-lg border border-black/10 mx-auto mb-0.5" style="background-color: {marcas[mi].cores[key]}"></div>
																				<p class="text-[8px] text-text-muted max-w-[48px] truncate">{key}</p>
																			</div>
																		{/if}
																	{/each}
																</div>
																<div class="grid grid-cols-2 gap-2">
																	{#each Object.keys(ds.cores) as key}
																		<div class="flex items-center gap-2">
																			{#if typeof marcas[mi].cores[key] === 'string' && marcas[mi].cores[key].startsWith('#')}
																				<input type="color" bind:value={marcas[mi].cores[key]}
																					oninput={() => { marcas = [...marcas]; }}
																					class="w-6 h-6 rounded border-0 cursor-pointer shrink-0" />
																			{/if}
																			<span class="text-[10px] text-text-muted w-24 shrink-0 truncate">{key}</span>
																			<input type="text" bind:value={marcas[mi].cores[key]}
																				oninput={() => { marcas = [...marcas]; }}
																				class="flex-1 px-2 py-1 rounded border border-border-default bg-bg-input text-text-primary text-[11px] font-mono focus:border-purple outline-none" />
																		</div>
																	{/each}
																</div>
															</div>
														{/if}

														<!-- Fontes -->
														{#if ds.fontes}
															<div>
																<p class="text-xs text-text-primary font-medium mb-2">Fontes</p>
																<p class="text-[10px] text-text-secondary mb-2">Nomes das fontes usadas nos slides. Use fontes do Google Fonts.</p>
																<div class="grid grid-cols-2 gap-2">
																	{#each Object.entries(ds.fontes) as [key, val]}
																		<div>
																			<label class="block text-[10px] text-text-muted mb-0.5">{key}</label>
																			<input type="text" bind:value={marcas[mi].fontes[key]}
																				class="w-full px-2 py-1.5 rounded border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
																		</div>
																	{/each}
																</div>
															</div>
														{/if}
													</div>
												</div>
											</div>

										<!-- ===== ABA: ESTILO DOS SLIDES ===== -->
										{:else if currentTab === 'estilo'}
											<div class="space-y-6">

												<!-- MODO DE GERACAO -->
												<div class="bg-bg-card rounded-xl border border-border-default p-5">
													<p class="text-sm text-text-primary font-semibold mb-1">Como a IA gera as imagens?</p>
													<p class="text-xs text-text-secondary mb-4">Escolha se quer usar imagens de referencia (recomendado) ou descrever tudo com texto.</p>

													<div class="flex gap-3 mb-4">
														<button
															onclick={() => { if (!marcas[mi].modo_geracao) marcas[mi].modo_geracao = 'referencia'; marcas[mi].modo_geracao = 'referencia'; marcas = [...marcas]; }}
															class="flex-1 p-3 rounded-xl border-2 text-left transition-all cursor-pointer
																{(marcas[mi].modo_geracao || 'referencia') === 'referencia' ? 'border-amber bg-amber/5' : 'border-border-default hover:border-amber/40'}"
														>
															<p class="text-xs font-semibold text-text-primary">Com referencia</p>
															<p class="text-[10px] text-text-muted mt-0.5">Manda imagem de exemplo + texto curto. Melhor resultado.</p>
														</button>
														<button
															onclick={() => { marcas[mi].modo_geracao = 'prompt'; marcas = [...marcas]; }}
															class="flex-1 p-3 rounded-xl border-2 text-left transition-all cursor-pointer
																{marcas[mi].modo_geracao === 'prompt' ? 'border-purple bg-purple/5' : 'border-border-default hover:border-purple/40'}"
														>
															<p class="text-xs font-semibold text-text-primary">Sem referencia (prompt)</p>
															<p class="text-[10px] text-text-muted mt-0.5">Descreve tudo com texto. Preencha os campos abaixo.</p>
														</button>
													</div>

													<!-- OVERRIDES (só no modo referência) -->
													{#if (marcas[mi].modo_geracao || 'referencia') === 'referencia'}
														{#if !marcas[mi].overrides}
															{@const _ = (marcas[mi].overrides = { sempre: '', nunca: '', paleta: '' })}
														{/if}
														<div class="space-y-3 bg-amber/3 rounded-lg p-4 border border-amber/15">
															<p class="text-xs text-amber font-semibold uppercase tracking-wider">Ajustes sobre a referencia</p>
															<p class="text-[10px] text-text-muted">A referencia define o estilo base. Aqui voce ajusta o que quiser mudar.</p>

															<div>
																<label class="block text-[10px] text-text-primary font-medium mb-1">Sempre incluir</label>
																<input type="text" bind:value={marcas[mi].overrides.sempre}
																	placeholder="Ex: plantas ao fundo, xicara de cafe, livros, gato no canto"
																	class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-amber outline-none" />
															</div>
															<div>
																<label class="block text-[10px] text-text-primary font-medium mb-1">Nunca incluir</label>
																<input type="text" bind:value={marcas[mi].overrides.nunca}
																	placeholder="Ex: grid pattern, icone de reels, emojis, fundo escuro"
																	class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-amber outline-none" />
															</div>
															<div>
																<label class="block text-[10px] text-text-primary font-medium mb-1">Trocar paleta de cores</label>
																<input type="text" bind:value={marcas[mi].overrides.paleta}
																	placeholder="Deixe vazio pra usar as cores da referencia. Ou: tons de verde e bege, azul royal"
																	class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-amber outline-none" />
															</div>
														</div>
													{/if}
												</div>

												<!-- CAMPOS DE PROMPT (sempre visíveis no modo prompt, colapsados no modo referência) -->
												{#if marcas[mi].modo_geracao === 'prompt'}
												<div class="bg-steel-0/50 rounded-xl p-4 border border-steel-3/10">
													<p class="text-sm text-text-primary font-medium mb-1">Instrucoes visuais para a IA</p>
													<p class="text-xs text-text-secondary">Sem referencia — descreva com palavras como voce quer cada parte do slide.</p>
												</div>
												{/if}

												{#if !marcas[mi].visual}
													{@const _ = (marcas[mi].visual = { estilo_fundo: '', estilo_desenho: '', estilo_card: '', estilo_texto: '', regras_extras: '' })}
												{/if}

												<div class="space-y-4 {(marcas[mi].modo_geracao || 'referencia') === 'referencia' ? 'opacity-40' : ''}">
													<div class="bg-bg-card rounded-xl border border-border-default p-4">
														<label class="block text-xs text-text-primary font-medium mb-1">Fundo dos slides</label>
														<p class="text-[10px] text-text-muted mb-2">Como e o fundo? Escuro, claro, com gradiente, com texturas?</p>
														<textarea bind:value={marcas[mi].visual.estilo_fundo} rows="2"
															placeholder="Ex: Fundo preto profundo (#0A0A0F) com gradiente sutil roxo no canto superior direito. Luzes difusas com efeito bokeh em tons violeta."
															class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none resize-y"></textarea>
													</div>

													<div class="bg-bg-card rounded-xl border border-border-default p-4">
														<label class="block text-xs text-text-primary font-medium mb-1">Ilustracoes e desenhos</label>
														<p class="text-[10px] text-text-muted mb-2">Que estilo de ilustracao voce quer? 3D, flat, wireframe, realista?</p>
														<textarea bind:value={marcas[mi].visual.estilo_desenho} rows="2"
															placeholder="Ex: Wireframe 3D em linhas neon roxas, estilo holograma futurista. Objetos flutuando com transparencia e brilho."
															class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none resize-y"></textarea>
													</div>

													<div class="bg-bg-card rounded-xl border border-border-default p-4">
														<label class="block text-xs text-text-primary font-medium mb-1">Cards e caixas de conteudo</label>
														<p class="text-[10px] text-text-muted mb-2">Como sao os retangulos onde fica o texto? Vidro fosco, solidos, com borda?</p>
														<textarea bind:value={marcas[mi].visual.estilo_card} rows="1"
															placeholder="Ex: Glassmorphism — vidro fosco semi-transparente com borda clara e blur no fundo."
															class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none resize-y"></textarea>
													</div>

													<div class="bg-bg-card rounded-xl border border-border-default p-4">
														<label class="block text-xs text-text-primary font-medium mb-1">Textos e tipografia</label>
														<p class="text-[10px] text-text-muted mb-2">Titulos grandes ou discretos? Palavras-chave coloridas? Que cores?</p>
														<textarea bind:value={marcas[mi].visual.estilo_texto} rows="1"
															placeholder="Ex: Titulos grandes em branco bold, palavras-chave em roxo vibrante. Corpo em cinza claro, leve e legivel."
															class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none resize-y"></textarea>
													</div>

													<div class="bg-bg-card rounded-xl border border-border-default p-4">
														<label class="block text-xs text-text-primary font-medium mb-1">Regras e restricoes</label>
														<p class="text-[10px] text-text-muted mb-2">Alguma coisa que a IA NAO deve fazer? Emojis, clipart, fotos de stock?</p>
														<input type="text" bind:value={marcas[mi].visual.regras_extras}
															placeholder="Ex: SEM emojis. SEM clipart. SEM fotos de stock. Atmosfera premium e sofisticada."
															class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
													</div>
												</div>

												<!-- Elementos fixos do slide -->
												{#if ds.elementos}
													<div>
														<p class="text-xs text-text-primary font-medium mb-1">Elementos fixos</p>
														<p class="text-[10px] text-text-secondary mb-3">Textos que aparecem sempre: badge no topo, nome no rodape, botao de CTA.</p>
														<div class="grid grid-cols-2 gap-3">
															{#each Object.entries(ds.elementos).filter(([_, v]) => typeof v === 'string') as [key, val]}
																<div>
																	<label class="block text-[10px] text-text-muted mb-0.5">{key.replace(/_/g, ' ')}</label>
																	<input type="text" bind:value={marcas[mi].elementos[key]}
																		class="w-full px-2.5 py-1.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
																</div>
															{/each}
														</div>
													</div>
												{/if}
											</div>

										<!-- ===== ABA: VOZ DA MARCA ===== -->
										{:else if currentTab === 'voz'}
											<div class="space-y-6">
												<div class="bg-steel-0/50 rounded-xl p-4 border border-steel-3/10">
													<p class="text-sm text-text-primary font-medium mb-1">Como a marca se comunica</p>
													<p class="text-xs text-text-secondary">Estas informacoes guiam a IA na hora de escrever os textos dos slides e a legenda do LinkedIn. Preencha o que souber — campos vazios sao ignorados.</p>
												</div>

												{#if !marcas[mi].comunicacao}
													{@const _ = (marcas[mi].comunicacao = { persona: '', tom: '', linguagem: '', publico: '', palavras_proibidas: [], exemplos_frase: [] })}
												{/if}

												<div class="space-y-4">
													<div class="bg-bg-card rounded-xl border border-border-default p-4">
														<label class="block text-xs text-text-primary font-medium mb-1">Quem e a persona?</label>
														<p class="text-[10px] text-text-muted mb-2">Quem esta "falando" nos posts? Nome, profissao, experiencia.</p>
														<textarea bind:value={marcas[mi].comunicacao.persona} rows="2"
															placeholder="Ex: Carlos Viana — dev brasileiro morando no Canada, 8 anos de experiencia com IA. Fala como colega senior, nao como professor."
															class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none resize-y"></textarea>
													</div>

													<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
														<div class="bg-bg-card rounded-xl border border-border-default p-4">
															<label class="block text-xs text-text-primary font-medium mb-1">Tom de voz</label>
															<p class="text-[10px] text-text-muted mb-2">Serio? Divertido? Tecnico? Casual?</p>
															<input type="text" bind:value={marcas[mi].comunicacao.tom}
																placeholder="Ex: Tecnico mas acessivel. Direto, anti-guru."
																class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
														</div>

														<div class="bg-bg-card rounded-xl border border-border-default p-4">
															<label class="block text-xs text-text-primary font-medium mb-1">Linguagem</label>
															<p class="text-[10px] text-text-muted mb-2">Formal? Informal? Girias? Ingles misturado?</p>
															<input type="text" bind:value={marcas[mi].comunicacao.linguagem}
																placeholder="Ex: Portugues BR informal tech. Frases curtas."
																class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
														</div>
													</div>

													<div class="bg-bg-card rounded-xl border border-border-default p-4">
														<label class="block text-xs text-text-primary font-medium mb-1">Publico-alvo</label>
														<p class="text-[10px] text-text-muted mb-2">Pra quem sao os posts? Idade, nivel tecnico, objetivo.</p>
														<input type="text" bind:value={marcas[mi].comunicacao.publico}
															placeholder="Ex: Devs brasileiros de 22-35 anos que querem trabalhar remoto no exterior."
															class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
													</div>

													<div class="bg-bg-card rounded-xl border border-border-default p-4">
														<label class="block text-xs text-text-primary font-medium mb-1">Hooks favoritos</label>
														<p class="text-[10px] text-text-muted mb-2">Frases de abertura que funcionam bem pra essa marca. A IA vai se inspirar nesses exemplos.</p>
														<textarea bind:value={marcas[mi].comunicacao.hooks} rows="2"
															placeholder="Ex: Voce sabia que...? / O erro que 90% dos devs cometem / Ninguem te conta isso sobre..."
															class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none resize-y"></textarea>
													</div>

													<div class="bg-bg-card rounded-xl border border-border-default p-4">
														<label class="block text-xs text-text-primary font-medium mb-1">CTAs favoritos</label>
														<p class="text-[10px] text-text-muted mb-2">Como a marca pede acao? Salvar, comentar, clicar no link?</p>
														<textarea bind:value={marcas[mi].comunicacao.ctas} rows="2"
															placeholder="Ex: Salva pra depois / Comenta 'EU QUERO' / Link na bio"
															class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none resize-y"></textarea>
													</div>

													<div class="bg-bg-card rounded-xl border border-border-default p-4">
														<label class="block text-xs text-text-primary font-medium mb-1">Palavras proibidas</label>
														<p class="text-[10px] text-text-muted mb-2">Palavras que a IA NUNCA deve usar nos textos dessa marca.</p>
														<input type="text" bind:value={marcas[mi].comunicacao.palavras_proibidas_texto}
															placeholder="Ex: gratis, facil, guru, coach, hack, milagre"
															class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-xs focus:border-purple outline-none" />
														<p class="text-[9px] text-text-muted mt-1">Separe por virgula</p>
													</div>
												</div>
											</div>

										<!-- ===== ABA: IMAGENS ===== -->
										{:else if currentTab === 'imagens'}
											<div class="space-y-8">

												<!-- 1. LOGO DA MARCA -->
												<div>
													<div class="bg-steel-0/50 rounded-xl p-4 border border-steel-3/10 mb-4">
														<p class="text-sm text-text-primary font-medium mb-1">Logo da marca</p>
														<p class="text-xs text-text-secondary">O logo aparece no editor pra voce posicionar manualmente em cada slide.</p>
													</div>
													<div class="flex items-center gap-4">
														{#if marcas[mi]._fotoPreview}
															<img src={marcas[mi]._fotoPreview} alt="Foto" class="w-16 h-16 rounded-full object-cover border-2" style="border-color: {ds.cores?.acento_principal || '#A78BFA'}" />
														{:else}
															<div class="w-16 h-16 rounded-full bg-bg-elevated border border-border-default flex items-center justify-center text-text-muted text-xs">Sem logo</div>
														{/if}
														<div>
															<label class="inline-flex px-4 py-2 rounded-full text-xs font-medium text-purple border border-purple/20 hover:bg-purple/8 cursor-pointer">
																{marcas[mi]._fotoPreview ? 'Trocar logo' : 'Upload logo'}
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
																			showSucesso('Logo salvo!');
																		} catch {}
																	};
																	reader.readAsDataURL(file);
																}} class="hidden" />
															</label>
														</div>
													</div>
												</div>

												<!-- 2. AVATAR (pessoa que aparece nos posts) -->
												<div>
													<div class="bg-purple/5 rounded-xl p-4 border border-purple/15 mb-4">
														<p class="text-sm text-text-primary font-medium mb-1">Avatar — a pessoa dos posts</p>
														<p class="text-xs text-text-secondary">Suba fotos da pessoa que vai aparecer nas thumbnails e nos carrosseis quando voce selecionar "com avatar". A IA vai desenhar essa pessoa nas imagens geradas.</p>
													</div>

													<div class="flex gap-3 flex-wrap mb-3">
														{#each marcas[mi]._assets.filter((a: any) => !a.is_referencia) as asset}
															<div class="relative group">
																<img src={asset.preview} alt={asset.nome}
																	class="w-20 h-20 rounded-full object-cover border-2 border-border-default hover:border-purple/40 transition-all" />
																<button onclick={async () => {
																	try {
																		await fetch(`${backendUrl}/api/brands/${marca.slug}/assets/${asset.nome}`, { method: 'DELETE' });
																		marcas[mi]._assets = marcas[mi]._assets.filter((a: any) => a.nome !== asset.nome);
																		showSucesso('Foto removida');
																	} catch {}
																}}
																	class="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-red text-white text-[9px] flex items-center justify-center opacity-0 group-hover:opacity-100 cursor-pointer">x</button>
																<p class="text-[9px] text-text-muted text-center mt-1 truncate w-20">{asset.nome}</p>
															</div>
														{/each}
														<label class="w-20 h-20 rounded-full border-2 border-dashed border-purple/30 flex flex-col items-center justify-center text-purple cursor-pointer hover:bg-purple/5 transition-all">
															<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
															<span class="text-[8px] mt-0.5">Foto</span>
															<input type="file" accept="image/*" onchange={async (e) => {
																const input = e.target as HTMLInputElement;
																const file = input.files?.[0];
																if (!file) return;
																const nome = 'avatar_' + file.name.replace(/\.[^.]+$/, '').replace(/[^a-zA-Z0-9]/g, '_').slice(0, 15);
																const reader = new FileReader();
																reader.onload = async () => {
																	try {
																		const res = await fetch(`${backendUrl}/api/brands/${marca.slug}/assets`, {
																			method: 'POST', headers: { 'Content-Type': 'application/json' },
																			body: JSON.stringify({ nome, imagem: reader.result })
																		});
																		if (res.ok) {
																			marcas[mi]._assets = [...marcas[mi]._assets, { nome, preview: reader.result as string, is_referencia: false }];
																			showSucesso('Foto de avatar adicionada!');
																		}
																	} catch {}
																};
																reader.readAsDataURL(file);
																input.value = '';
															}} class="hidden" />
														</label>
													</div>
													<p class="text-[10px] text-text-muted">Suba 1-3 fotos da pessoa em angulos diferentes. A IA vai manter a aparencia consistente.</p>
												</div>

												<!-- 3. REFERENCIA VISUAL — movida pra aba Aparencia -->
												<div>
													<div class="bg-amber/5 rounded-xl p-4 border border-amber/20 mb-4">
														<p class="text-sm text-text-primary font-medium mb-1">Referencias visuais</p>
														<p class="text-xs text-text-secondary">As referencias de estilo ficam na aba <button onclick={() => setBrandTab(marca.slug, 'aparencia')} class="text-amber font-semibold underline cursor-pointer">Aparencia</button>.</p>
													</div>
												</div>

												<!-- ESCONDER SEÇÃO ANTIGA -->
												<div class="hidden">
													<div class="REMOVIDO">
														<p class="text-sm text-text-primary font-medium mb-1">Referencia visual — o estilo dos posts ANTIGO</p>
														<p class="text-xs text-text-secondary">Suba um print de um post que voce gostou. A IA vai copiar o ESTILO (cores, layout, atmosfera) mas NAO o conteudo. Isso e diferente do avatar — aqui voce ensina como o post deve PARECER.</p>
													</div>

													<!-- Upload de referencia -->
													<div class="flex gap-3 flex-wrap mb-4">
														{#each marcas[mi]._assets.filter((a: any) => a.is_referencia) as asset}
															<div class="relative group">
																<img src={asset.preview} alt={asset.nome}
																	class="w-24 h-30 rounded-xl object-cover border-2 border-amber ring-2 ring-amber/30 shadow-lg" />
																<button onclick={async () => {
																	try {
																		await fetch(`${backendUrl}/api/brands/${marca.slug}/referencia`, {
																			method: 'PUT', headers: { 'Content-Type': 'application/json' },
																			body: JSON.stringify({ nome: null })
																		});
																		await fetch(`${backendUrl}/api/brands/${marca.slug}/assets/${asset.nome}`, { method: 'DELETE' });
																		marcas[mi]._assets = marcas[mi]._assets.filter((a: any) => a.nome !== asset.nome);
																		analiseRef = { ...analiseRef, [marca.slug]: undefined };
																		showSucesso('Referencia removida');
																	} catch {}
																}}
																	class="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-red text-white text-[9px] flex items-center justify-center opacity-0 group-hover:opacity-100 cursor-pointer">x</button>
																<p class="text-[9px] text-amber text-center mt-1 font-semibold">REFERENCIA ATIVA</p>
															</div>
														{/each}

														{#if marcas[mi]._assets.filter((a: any) => a.is_referencia).length < 5}
															<label class="w-24 h-30 rounded-xl border-2 border-dashed border-amber/40 flex flex-col items-center justify-center text-amber/70 cursor-pointer hover:bg-amber/5 transition-all gap-1">
																<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
																<span class="text-[9px] font-medium">+ Referencia</span>
																<span class="text-[7px] text-text-muted">{marcas[mi]._assets.filter((a: any) => a.is_referencia).length}/5</span>
																<input type="file" accept="image/*" onchange={async (e) => {
																	const input = e.target as HTMLInputElement;
																	const file = input.files?.[0];
																	if (!file) return;
																	const nome = 'ref_' + file.name.replace(/\.[^.]+$/, '').replace(/[^a-zA-Z0-9]/g, '_').slice(0, 15);
																	const reader = new FileReader();
																	reader.onload = async () => {
																		try {
																			// Upload asset
																			const res = await fetch(`${backendUrl}/api/brands/${marca.slug}/assets`, {
																				method: 'POST', headers: { 'Content-Type': 'application/json' },
																				body: JSON.stringify({ nome, imagem: reader.result })
																			});
																			if (res.ok) {
																				marcas[mi]._assets = [...marcas[mi]._assets, { nome, preview: reader.result as string, is_referencia: true }];
																				showSucesso(`Referencia ${marcas[mi]._assets.filter((a: any) => a.is_referencia).length}/5 adicionada!`);
																			}
																		} catch {}
																	};
																	reader.readAsDataURL(file);
																	input.value = '';
																}} class="hidden" />
															</label>
														{/if}
													</div>

													<!-- Botao analisar (se tem referencia mas nao tem analise) -->
													{#if marcas[mi]._assets.find((a: any) => a.is_referencia) && !analiseRef[marca.slug]}
													{@const refAsset = marcas[mi]._assets.find((a: any) => a.is_referencia)}
														<button
															onclick={() => analisarReferencia(marca.slug, refAsset.preview, refAsset.nome)}
															disabled={analisandoRef[marca.slug]}
															class="w-full py-2.5 rounded-xl text-xs font-medium transition-all cursor-pointer mb-4
																{analisandoRef[marca.slug] ? 'bg-amber/10 text-amber' : 'bg-amber/10 text-amber border border-amber/20 hover:bg-amber/20'}
																disabled:opacity-60"
														>
															{analisandoRef[marca.slug] ? 'Analisando com IA...' : 'Analisar estilo desta referencia'}
														</button>
													{/if}

																			<!-- Resultado da analise - NARRATIVA -->
																			{#if analiseRef[marca.slug]}
																				{@const a = analiseRef[marca.slug]}
																				<div class="bg-bg-card rounded-xl border border-amber/20 overflow-hidden">
																					<!-- Header -->
																					<div class="bg-amber/5 px-5 py-3 border-b border-amber/15 flex items-center gap-2 flex-wrap">
																						<svg class="w-4 h-4 text-amber shrink-0" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
																						<p class="text-sm text-text-primary font-semibold">DNA Visual extraido pela IA</p>
																						{#if a.estetica}<span class="px-2 py-0.5 rounded-full text-[9px] font-medium bg-amber/10 text-amber border border-amber/20">{a.estetica}</span>{/if}
																						{#if a.vibe}<span class="px-2 py-0.5 rounded-full text-[9px] font-medium bg-purple/8 text-purple border border-purple/20">{a.vibe}</span>{/if}
																						{#if a.formato}<span class="ml-auto px-2 py-0.5 rounded-full text-[9px] font-mono bg-bg-elevated text-text-muted border border-border-default">{a.formato}</span>{/if}
																					</div>

																					<div class="p-5 space-y-5">
																						<!-- Resumo -->
																						<p class="text-[9px] text-text-muted font-mono bg-bg-elevated p-2 rounded">Campos recebidos: {Object.keys(a).join(", ")}</p>
																						{#if a.resumo}
																						<div class="bg-amber/5 rounded-lg p-4 border border-amber/15">
																							<p class="text-sm text-text-primary font-semibold leading-relaxed">{a.resumo}</p>
																						</div>
																						{/if}

																						<!-- CORES -->
																						{#if (a.dna_cores || a.cores)}
																						{@const c = (a.dna_cores || a.cores)}
																						<div class="bg-bg-card rounded-lg border border-border-default p-4">
																							<p class="text-xs text-amber font-semibold uppercase tracking-wider mb-2">Paleta de Cores</p>
																							{#if c.paleta_hex?.length}
																							<div class="flex gap-2 mb-3">
																								{#each c.paleta_hex as hex}
																								<div class="text-center"><div class="w-10 h-10 rounded-lg border border-black/10 shadow-sm" style="background-color: {hex}"></div><p class="text-[7px] text-text-muted mt-0.5 font-mono">{hex}</p></div>
																								{/each}
																							</div>
																							{/if}
																							{#if c.narrativa}
																								<p class="text-xs text-text-secondary leading-relaxed whitespace-pre-line">{c.narrativa}</p>
																							{:else}
																								<div class="space-y-1.5">
																									{#each Object.entries(c).filter(([k, v]) => k !== 'paleta_hex' && k !== 'extra' && v && typeof v === 'object' && v.hex) as [key, val]}
																										<div class="flex gap-2 text-xs items-center">
																											<div class="w-5 h-5 rounded shrink-0 border border-black/10" style="background-color: {val.hex}"></div>
																											<span class="text-text-muted capitalize font-medium w-28 shrink-0">{key.replace(/_/g, ' ')}</span>
																											<span class="text-text-secondary">{val.descricao} <span class="font-mono text-text-muted">({val.hex})</span></span>
																										</div>
																									{/each}
																									{#each Object.entries(c).filter(([k, v]) => typeof v === 'string' && k !== 'paleta_hex') as [key, val]}
																										<div class="flex gap-2 text-xs items-start">
																											<span class="text-text-muted capitalize font-medium w-28 shrink-0">{key.replace(/_/g, ' ')}</span>
																											<span class="text-text-secondary">{val}</span>
																										</div>
																									{/each}
																								</div>
																							{/if}
																							{#if c.erros_evitar}<p class="text-[10px] text-red mt-2">Evitar: {c.erros_evitar}</p>{/if}
																						</div>
																						{/if}

																						<!-- TIPOGRAFIA -->
																						{#if (a.dna_tipografia || a.tipografia)}
																						{@const t = (a.dna_tipografia || a.tipografia)}
																						<div class="bg-purple/3 rounded-lg border border-purple/15 p-4">
																							<p class="text-xs text-purple font-semibold uppercase tracking-wider mb-2">Tipografia</p>
																							{#if t.narrativa}<p class="text-xs text-text-primary leading-relaxed whitespace-pre-line mb-3">{t.narrativa}</p>{/if}
																							<div class="grid grid-cols-2 gap-3 mb-3">
																								<div class="p-3 rounded-lg bg-bg-card border border-border-default">
																									<p class="text-[9px] text-text-muted font-medium uppercase mb-1">Titulo</p>
																									<p class="text-sm text-text-primary font-bold">{t.titulo_fonte_google || t.titulo?.fonte || (typeof t.titulo === 'string' ? t.titulo : '?')}</p>
																									<p class="text-[10px] text-text-secondary mt-0.5">{t.titulo_caracteristicas || t.titulo?.peso || ''} {t.titulo?.tipo || ''} {t.titulo?.tamanho || ''} {t.titulo?.caixa || ''}</p>
																									{#if t.titulo?.observacao}<p class="text-[10px] text-amber mt-0.5">{t.titulo.observacao}</p>{/if}
																									{#if t.titulo?.efeito && t.titulo.efeito !== 'nenhum'}<p class="text-[10px] text-purple mt-0.5">Efeito: {t.titulo.efeito}</p>{/if}
																								</div>
																								<div class="p-3 rounded-lg bg-bg-card border border-border-default">
																									<p class="text-[9px] text-text-muted font-medium uppercase mb-1">Corpo</p>
																									<p class="text-sm text-text-primary font-bold">{t.corpo_fonte_google || t.corpo?.fonte || (typeof t.corpo === 'string' ? t.corpo : '?')}</p>
																									<p class="text-[10px] text-text-secondary mt-0.5">{t.corpo_caracteristicas || t.corpo?.peso || ''} {t.corpo?.tipo || ''}</p>
																									{#if t.corpo?.observacao}<p class="text-[10px] text-amber mt-0.5">{t.corpo.observacao}</p>{/if}
																								</div>
																							</div>
																							{#if t.google_fonts_sugeridas || t.google_fonts_url}
																								<div class="bg-purple/5 rounded-lg p-2.5 mb-2 border border-purple/15">
																									<p class="text-[9px] text-purple font-medium uppercase mb-0.5">Google Fonts</p>
																									<p class="text-xs text-text-primary font-medium">{t.google_fonts_sugeridas || t.google_fonts_url || ''}</p>
																								</div>
																							{/if}
																							{#if t.keywords_pra_ia}<div class="bg-bg-elevated rounded-lg p-2.5 mb-2"><p class="text-[9px] text-text-muted font-medium uppercase mb-1">Keywords pra IA</p><p class="text-xs text-text-secondary italic">{t.keywords_pra_ia}</p></div>{/if}
																							{#if t.destaque}<div class="bg-bg-elevated rounded-lg p-2.5 mb-2"><p class="text-[9px] text-text-muted font-medium uppercase mb-1">Destaques no texto</p><p class="text-xs text-text-secondary">{t.destaque?.como || t.destaque}</p></div>{/if}
																							{#if t.erros_evitar}<p class="text-[10px] text-red">Evitar: {t.erros_evitar}</p>{/if}
																						</div>
																						{/if}

																						<!-- COMPOSICAO -->
																						{#if (a.dna_composicao || a.composicao || a.layout)}
																						{@const lay = (a.dna_composicao || a.composicao || a.layout)}
																						<div class="bg-bg-card rounded-lg border border-border-default p-4">
																							<p class="text-xs text-steel-3 font-semibold uppercase tracking-wider mb-2">Composicao e Layout</p>
																							{#if lay.narrativa}
																								<p class="text-xs text-text-secondary leading-relaxed whitespace-pre-line">{lay.narrativa}</p>
																							{:else}
																								<div class="space-y-1.5">
																									{#each Object.entries(lay).filter(([_, v]) => v && typeof v === 'string') as [key, val]}
																										<div class="flex gap-2 text-xs"><span class="text-text-muted capitalize font-medium w-24 shrink-0">{key}:</span><span class="text-text-secondary">{val}</span></div>
																									{/each}
																								</div>
																							{/if}
																						</div>
																						{/if}

																						<!-- ELEMENTOS -->
																						{#if (a.dna_elementos || a.elementos || a.decoracao)}
																						{@const dec = (a.dna_elementos || a.elementos || a.decoracao)}
																						<div class="bg-bg-card rounded-lg border border-border-default p-4">
																							<p class="text-xs text-teal-6 font-semibold uppercase tracking-wider mb-2">Elementos e Decoracao</p>
																							{#if dec.narrativa}
																								<p class="text-xs text-text-secondary leading-relaxed whitespace-pre-line mb-2">{dec.narrativa}</p>
																							{:else}
																								<div class="space-y-1.5 mb-2">
																									{#each Object.entries(dec).filter(([k, v]) => v && typeof v === 'string' && k !== 'lista') as [key, val]}
																										<div class="flex gap-2 text-xs"><span class="text-text-muted capitalize font-medium w-24 shrink-0">{key.replace(/_/g, ' ')}:</span><span class="text-text-secondary">{val}</span></div>
																									{/each}
																								</div>
																							{/if}
																							{#if dec.lista?.length}
																							<div class="flex flex-wrap gap-1.5 mb-2">
																								{#each dec.lista as elem}<span class="px-2 py-0.5 rounded-full text-[10px] bg-amber/8 text-amber border border-amber/15">{elem}</span>{/each}
																							</div>
																							{/if}
																							{#if dec.elementos?.length}
																							<div class="flex flex-wrap gap-1.5 mb-2">
																								{#each dec.elementos as elem}<span class="px-2 py-0.5 rounded-full text-[10px] bg-amber/8 text-amber border border-amber/15">{elem}</span>{/each}
																							</div>
																							{/if}
																							{#if dec.keywords_pra_ia}<p class="text-[10px] text-text-muted italic">Keywords: {dec.keywords_pra_ia}</p>{/if}
																							{#if dec.erros_evitar}<p class="text-[10px] text-red mt-1">Evitar: {dec.erros_evitar}</p>{/if}
																						</div>
																						{/if}

																						<!-- PROMPT PERFEITO -->
																						{#if (a.prompt_perfeito || a.prompt_replicar)}
																						<div class="bg-green/5 rounded-lg border border-green/20 p-4">
																							<p class="text-xs text-green font-semibold uppercase tracking-wider mb-2">Prompt pra IA replicar esse estilo</p>
																							<p class="text-xs text-text-secondary leading-relaxed whitespace-pre-line">{(a.prompt_perfeito || a.prompt_replicar)}</p>
																						</div>
																						{/if}

																						<!-- HACK CONSISTENCIA -->
																						{#if a.hack_consistencia}
																						<div class="bg-steel-0 rounded-lg border border-steel-3/15 p-4">
																							<p class="text-xs text-steel-3 font-semibold uppercase tracking-wider mb-2">Hack de consistencia</p>
																							<p class="text-xs text-text-secondary leading-relaxed whitespace-pre-line">{a.hack_consistencia}</p>
																						</div>
																						{/if}

																						<!-- REGRAS DO FEED -->
																						{#if a.regras_feed}
																						<div class="bg-red/3 rounded-lg border border-red/15 p-4">
																							<p class="text-xs text-red font-semibold uppercase tracking-wider mb-3">Regras do Feed (nao repetir)</p>
																							<div class="space-y-2.5">
																								{#each Object.entries(a.regras_feed).filter(([_, v]) => v) as [key, val]}
																									<div>
																										<p class="text-[10px] text-text-primary font-semibold capitalize mb-0.5">{key.replace(/_/g, ' ')}</p>
																										<p class="text-[11px] text-text-secondary leading-relaxed">{val}</p>
																									</div>
																								{/each}
																							</div>
																						</div>
																						{/if}

																						<!-- BOTAO APLICAR -->
																						<button onclick={() => aplicarAnaliseNaMarca(mi, marca.slug)} class="w-full py-3 rounded-xl text-sm font-medium bg-amber text-white hover:opacity-90 transition-all cursor-pointer shadow-sm">
																							Aplicar tudo no perfil da marca
																						</button>
																						<p class="text-[10px] text-text-muted text-center">Preenche cores, fontes, estilo visual — tudo de uma vez. Auto-salva.</p>
																					</div>
																				</div>
																			{/if}
												</div>

											</div>
										{/if}

										<!-- Botao salvar (sempre visivel) -->
										<div class="mt-6 pt-4 border-t border-border-default flex items-center justify-between">
											<p class="text-[10px] text-text-muted">Alteracoes so sao salvas ao clicar no botao</p>
											<button onclick={() => salvarMarca(marca.slug)} disabled={salvando}
												class="px-6 py-2.5 rounded-full text-xs font-medium text-bg-global bg-purple hover:opacity-90 transition-all cursor-pointer disabled:opacity-50">
												{salvando ? 'Salvando...' : `Salvar ${marca.nome}`}
											</button>
										</div>

										</div>
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
						<img src={principal.dataUrl} alt="Foto principal" class="w-16 h-16 rounded-full object-cover border-2 border-purple shadow-[0_0_20px_rgba(53,120,176,0.25)]" />
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

{#if showClonarModal}
	<Modal open={true} onclose={() => showClonarModal = false}>
		<h3 class="text-lg font-semibold text-text-primary mb-4">Clonar Marca</h3>
		<p class="text-sm text-text-secondary mb-4">Criando copia de <strong>{clonarOrigem}</strong> com novo nome e slug.</p>
		<div class="space-y-3 mb-6">
			<div>
				<label for="clonar-nome" class="block text-xs text-text-muted mb-1">Nome da nova marca</label>
				<input id="clonar-nome" type="text" bind:value={clonarNome}
					oninput={() => { clonarSlug = gerarSlug(clonarNome); }}
					class="w-full px-3 py-2 rounded-lg bg-bg-input border border-border-default text-sm text-text-primary focus:border-purple focus:outline-none" />
			</div>
			<div>
				<label for="clonar-slug" class="block text-xs text-text-muted mb-1">Slug (gerado automaticamente)</label>
				<input id="clonar-slug" type="text" bind:value={clonarSlug} readonly
					class="w-full px-3 py-2 rounded-lg bg-bg-elevated border border-border-default text-sm text-text-muted font-mono cursor-not-allowed" />
			</div>
		</div>
		<div class="flex justify-end gap-3">
			<button onclick={() => showClonarModal = false}
				class="px-4 py-2 rounded-full text-sm text-text-secondary border border-border-default hover:bg-black/5 cursor-pointer transition-all">
				Cancelar
			</button>
			<button onclick={executarClonar} disabled={clonando || !clonarSlug || !clonarNome}
				class="px-4 py-2 rounded-full text-sm font-medium text-bg-global bg-green hover:opacity-90 cursor-pointer transition-all disabled:opacity-50">
				{clonando ? 'Clonando...' : 'Clonar Marca'}
			</button>
		</div>
	</Modal>
{/if}

{#if showRenomearModal}
	<Modal open={true} onclose={() => showRenomearModal = false}>
		<h3 class="text-lg font-semibold text-text-primary mb-4">Renomear Marca</h3>
		<div class="mb-6">
			<label for="renomear-nome" class="block text-xs text-text-muted mb-1">Novo nome</label>
			<input id="renomear-nome" type="text" bind:value={renomearNome}
				class="w-full px-3 py-2 rounded-lg bg-bg-input border border-border-default text-sm text-text-primary focus:border-purple focus:outline-none" />
		</div>
		<div class="flex justify-end gap-3">
			<button onclick={() => showRenomearModal = false}
				class="px-4 py-2 rounded-full text-sm text-text-secondary border border-border-default hover:bg-black/5 cursor-pointer transition-all">
				Cancelar
			</button>
			<button onclick={executarRenomear} disabled={renomeando || !renomearNome}
				class="px-4 py-2 rounded-full text-sm font-medium text-bg-global bg-purple hover:opacity-90 cursor-pointer transition-all disabled:opacity-50">
				{renomeando ? 'Salvando...' : 'Salvar'}
			</button>
		</div>
	</Modal>
{/if}

{#if showRemoverModal}
	<Modal open={true} onclose={() => showRemoverModal = false}>
		<h3 class="text-lg font-semibold text-text-primary mb-2">Remover Marca</h3>
		<p class="text-sm text-text-secondary mb-6">Tem certeza que deseja remover <strong class="text-text-primary">{removerNome}</strong>? Essa acao nao pode ser desfeita.</p>
		<div class="flex justify-end gap-3">
			<button onclick={() => showRemoverModal = false}
				class="px-4 py-2 rounded-full text-sm text-text-secondary border border-border-default hover:bg-black/5 cursor-pointer transition-all">
				Cancelar
			</button>
			<button onclick={confirmarRemover}
				class="px-4 py-2 rounded-full text-sm font-medium text-white bg-red hover:opacity-90 cursor-pointer transition-all">
				Remover
			</button>
		</div>
	</Modal>
{/if}

<Modal open={showNovaMarca} title="Nova marca" size="md" onclose={() => { showNovaMarca = false; novaMarcaResultado = null; novaMarcaImagens = []; }}>
	<div class="space-y-4">
		<!-- Nome -->
		<div>
			<label class="label-upper mb-1.5 block">Nome da marca</label>
			<input data-testid="campo-nova-marca-nome" type="text" bind:value={novaMarcaNome} placeholder="Ex: Jardim Verde, Doce Encanto..."
				class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
					focus:border-purple focus:ring-2 focus:ring-purple/12 outline-none transition-all placeholder:text-text-muted" />
		</div>

		<!-- Area / Descricao -->
		<div>
			<label class="label-upper mb-1.5 block">Area de atuacao</label>
			<input data-testid="campo-nova-marca-descricao" type="text" bind:value={novaMarcaDescricao} placeholder="Ex: loja de plantas, escola de tecnologia, doceria artesanal..."
				class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
					focus:border-purple focus:ring-2 focus:ring-purple/12 outline-none transition-all placeholder:text-text-muted" />
		</div>

		<p class="text-xs text-text-muted">Depois de criar, voce pode adicionar imagens de referencia e personalizar cores na pagina da marca.</p>
	</div>

	{#snippet footer()}
		<button data-testid="btn-cancelar-nova-marca" onclick={() => { showNovaMarca = false; novaMarcaResultado = null; novaMarcaImagens = []; }}
			class="px-4 py-2 rounded-full text-sm text-text-secondary hover:text-text-primary transition-all cursor-pointer">
			Cancelar
		</button>
		<button data-testid="btn-criar-marca" onclick={criarMarcaComReferencias} disabled={novaMarcaCriando || !novaMarcaNome}
			class="px-6 py-2 rounded-full text-sm font-medium text-bg-global bg-purple hover:opacity-90 transition-all cursor-pointer disabled:opacity-50">
			{novaMarcaCriando ? 'Criando...' : 'Criar marca'}
		</button>
	{/snippet}
</Modal>
