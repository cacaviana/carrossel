<script lang="ts">
	import { config, type AppConfig } from '$lib/stores/config';
	import { fotos, type FotoItem } from '$lib/stores/fotos';
	import { get } from 'svelte/store';
	import { onMount } from 'svelte';

	let formData = $state<AppConfig>(get(config));

	let claudeApiKey = $state('');
	let openaiApiKey = $state('');
	let geminiApiKey = $state('');
	let googleDriveCredentials = $state('');
	let folderIdManual = $state('');

	type KeysStatus = {
		claude_api_key_set: boolean;
		openai_api_key_set: boolean;
		gemini_api_key_set: boolean;
		google_drive_credentials_set: boolean;
		google_drive_folder_id: string;
	};

	let keysStatus = $state<KeysStatus>({
		claude_api_key_set: false,
		openai_api_key_set: false,
		gemini_api_key_set: false,
		google_drive_credentials_set: false,
		google_drive_folder_id: ''
	});

	type Pasta = { id: string; name: string };
	let pastas = $state<Pasta[]>([]);
	let carregandoPastas = $state(false);
	let erroPastas = $state('');
	let pastaSelecionada = $state('');

	let salvo = $state(false);
	let salvando = $state(false);
	let erroSalvar = $state('');
	let fileInput: HTMLInputElement;
	let dsFileInput: HTMLInputElement;

	// Design Systems
	type DSItem = { id: string; name: string };
	let designSystems = $state<DSItem[]>([]);
	let carregandoDS = $state(false);
	let dsPreview = $state<{ name: string; content: string; isHtml: boolean } | null>(null);
	let uploadingDS = $state(false);

	config.subscribe((v) => {
		formData = { ...v };
	});

	onMount(async () => {
		const backendUrl = get(config).backendUrl;
		try {
			const res = await fetch(`${backendUrl}/api/config`);
			if (res.ok) {
				keysStatus = await res.json();
				pastaSelecionada = keysStatus.google_drive_folder_id;
				folderIdManual = keysStatus.google_drive_folder_id;
			}
		} catch {}
		carregarDesignSystems();
	});

	async function listarPastas() {
		carregandoPastas = true;
		erroPastas = '';
		pastas = [];
		try {
			const res = await fetch(`${formData.backendUrl}/api/drive/pastas`);
			if (!res.ok) {
				const d = await res.json();
				throw new Error(d.detail || 'Erro ao listar pastas');
			}
			pastas = await res.json();
			if (pastas.length === 0) erroPastas = 'Nenhuma pasta encontrada. Compartilhe uma pasta com a service account.';
		} catch (e) {
			erroPastas = e instanceof Error ? e.message : 'Erro ao listar pastas';
		} finally {
			carregandoPastas = false;
		}
	}

	async function salvarPasta(id: string) {
		pastaSelecionada = id;
		folderIdManual = id;
		const res = await fetch(`${formData.backendUrl}/api/config`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ google_drive_folder_id: id })
		});
		if (res.ok) {
			const statusRes = await fetch(`${formData.backendUrl}/api/config`);
			if (statusRes.ok) keysStatus = await statusRes.json();
		}
	}

	async function salvar() {
		salvando = true;
		erroSalvar = '';

		try {
			const payload: Record<string, string> = {};
			if (claudeApiKey) payload.claude_api_key = claudeApiKey;
			if (openaiApiKey) payload.openai_api_key = openaiApiKey;
			if (geminiApiKey) payload.gemini_api_key = geminiApiKey;
			if (googleDriveCredentials) payload.google_drive_credentials = googleDriveCredentials;
			if (folderIdManual && folderIdManual !== keysStatus.google_drive_folder_id) {
				payload.google_drive_folder_id = folderIdManual;
			}

			if (Object.keys(payload).length > 0) {
				const res = await fetch(`${formData.backendUrl}/api/config`, {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(payload)
				});
				if (!res.ok) throw new Error('Erro ao salvar no servidor');

				const statusRes = await fetch(`${formData.backendUrl}/api/config`);
				if (statusRes.ok) {
					keysStatus = await statusRes.json();
					pastaSelecionada = keysStatus.google_drive_folder_id;
				}

				claudeApiKey = '';
				openaiApiKey = '';
				geminiApiKey = '';
				googleDriveCredentials = '';
			}

			config.set({ ...formData });
			salvo = true;
			setTimeout(() => (salvo = false), 2000);
		} catch (e) {
			erroSalvar = e instanceof Error ? e.message : 'Erro desconhecido';
		} finally {
			salvando = false;
		}
	}

	function resetar() {
		config.reset();
		config.subscribe((v) => {
			formData = { ...v };
		})();
	}

	async function handleFotos(e: Event) {
		const target = e.target as HTMLInputElement;
		const files = target.files;
		if (!files) return;
		for (const file of files) {
			await fotos.add(file);
		}
		// Seleciona a primeira automaticamente se nenhuma ativa
		const all = get(fotos);
		if (all.length > 0 && !formData.fotoCriadorBase64) {
			formData.fotoCriadorBase64 = all[all.length - 1].dataUrl;
		}
	}

	function usarFoto(foto: FotoItem) {
		formData.fotoCriadorBase64 = foto.dataUrl;
	}

	async function carregarDesignSystems() {
		carregandoDS = true;
		try {
			const res = await fetch(`${formData.backendUrl}/api/drive/design-systems`);
			if (res.ok) designSystems = await res.json();
		} catch {} finally { carregandoDS = false; }
	}

	async function uploadDesignSystem(e: Event) {
		const target = e.target as HTMLInputElement;
		const file = target.files?.[0];
		if (!file) return;
		uploadingDS = true;
		try {
			const reader = new FileReader();
			const base64 = await new Promise<string>((resolve) => {
				reader.onload = () => {
					const result = reader.result as string;
					resolve(result.split(',')[1] || result);
				};
				reader.readAsDataURL(file);
			});
			const res = await fetch(`${formData.backendUrl}/api/drive/design-systems`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ file_base64: base64, file_name: file.name, mime_type: file.type || 'text/markdown' })
			});
			if (res.ok) await carregarDesignSystems();
		} catch {} finally { uploadingDS = false; target.value = ''; }
	}

	async function previewDS(ds: DSItem) {
		try {
			const res = await fetch(`${formData.backendUrl}/api/drive/design-systems/${ds.id}`);
			if (res.ok) {
				const data = await res.json();
				dsPreview = { name: data.name, content: data.content, isHtml: data.name.endsWith('.html') };
			}
		} catch {}
	}

	async function deletarDS(ds: DSItem) {
		try {
			await fetch(`${formData.backendUrl}/api/drive/design-systems/${ds.id}`, { method: 'DELETE' });
			designSystems = designSystems.filter(d => d.id !== ds.id);
			if (dsPreview?.name === ds.name) dsPreview = null;
		} catch {}
	}

	function removerFoto(id: string) {
		const foto = get(fotos).find(f => f.id === id);
		fotos.remove(id);
		if (foto && formData.fotoCriadorBase64 === foto.dataUrl) {
			const restante = get(fotos);
			formData.fotoCriadorBase64 = restante.length > 0 ? restante[0].dataUrl : '';
		}
	}
</script>

<svelte:head>
	<title>Configurações — Carrossel System</title>
</svelte:head>

<div class="animate-fade-up max-w-2xl">
	<div class="mb-8">
		<h2 class="text-2xl font-semibold text-steel-6 mb-2">Configurações</h2>
		<p class="text-steel-4 font-light">API keys salvas com segurança no servidor (.env). Preencha só o que quiser atualizar.</p>
	</div>

	<!-- API Keys -->
	<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-6 mb-6">
		<h3 class="font-semibold text-steel-6 mb-4 flex items-center gap-2">
			<span class="w-2 h-2 rounded-full bg-steel-3"></span>
			API Keys
		</h3>

		<div class="space-y-4">
			<div>
				<label for="claude-key" class="block text-sm font-medium text-steel-5 mb-1.5">
					Claude API Key (Anthropic)
					{#if keysStatus.claude_api_key_set}
						<span class="ml-2 text-xs text-green-600 font-normal">✓ configurada</span>
					{:else}
						<span class="ml-2 text-xs text-red-500 font-normal">não configurada</span>
					{/if}
				</label>
				<input id="claude-key" type="password" bind:value={claudeApiKey}
					placeholder={keysStatus.claude_api_key_set ? 'Deixe em branco para manter a atual' : 'sk-ant-...'}
					class="w-full px-4 py-3 rounded-xl border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 focus:ring-2 focus:ring-steel-3/20 outline-none transition-all" />
			</div>

			<div>
				<label for="openai-key" class="block text-sm font-medium text-steel-5 mb-1.5">
					OpenAI API Key
					{#if keysStatus.openai_api_key_set}
						<span class="ml-2 text-xs text-green-600 font-normal">✓ configurada</span>
					{:else}
						<span class="ml-2 text-xs text-red-500 font-normal">não configurada</span>
					{/if}
				</label>
				<input id="openai-key" type="password" bind:value={openaiApiKey}
					placeholder={keysStatus.openai_api_key_set ? 'Deixe em branco para manter a atual' : 'sk-...'}
					class="w-full px-4 py-3 rounded-xl border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 focus:ring-2 focus:ring-steel-3/20 outline-none transition-all" />
			</div>

			<div>
				<label for="gemini-key" class="block text-sm font-medium text-steel-5 mb-1.5">
					Gemini API Key (Google)
					{#if keysStatus.gemini_api_key_set}
						<span class="ml-2 text-xs text-green-600 font-normal">✓ configurada</span>
					{:else}
						<span class="ml-2 text-xs text-red-500 font-normal">não configurada</span>
					{/if}
				</label>
				<input id="gemini-key" type="password" bind:value={geminiApiKey}
					placeholder={keysStatus.gemini_api_key_set ? 'Deixe em branco para manter a atual' : 'AI...'}
					class="w-full px-4 py-3 rounded-xl border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 focus:ring-2 focus:ring-steel-3/20 outline-none transition-all" />
			</div>

			<div>
				<label for="gdrive-creds" class="block text-sm font-medium text-steel-5 mb-1.5">
					Google Drive Credentials (JSON)
					{#if keysStatus.google_drive_credentials_set}
						<span class="ml-2 text-xs text-green-600 font-normal">✓ configurada</span>
					{:else}
						<span class="ml-2 text-xs text-red-500 font-normal">não configurada</span>
					{/if}
				</label>
				<textarea id="gdrive-creds" bind:value={googleDriveCredentials}
					placeholder={keysStatus.google_drive_credentials_set ? 'Deixe em branco para manter a atual' : '{"type": "service_account", ...}'}
					rows="3"
					class="w-full px-4 py-3 rounded-xl border border-teal-4/30 bg-white text-steel-6 text-sm font-mono focus:border-steel-3 focus:ring-2 focus:ring-steel-3/20 outline-none transition-all resize-y"></textarea>
			</div>
		</div>
	</div>

	<!-- Pasta do Google Drive -->
	<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-6 mb-6">
		<h3 class="font-semibold text-steel-6 mb-1 flex items-center gap-2">
			<span class="w-2 h-2 rounded-full bg-teal-5"></span>
			Pasta do Google Drive
		</h3>
		<p class="text-xs text-steel-4 font-light mb-4">
			Carrosséis são salvos em subpastas automáticas com nome + data dentro desta pasta.
			A pasta precisa ser compartilhada com a service account.
		</p>

		{#if keysStatus.google_drive_folder_id}
			<div class="mb-3 px-3 py-2 rounded-xl bg-teal-1 border border-teal-4/30 text-xs text-teal-6 flex items-center gap-2">
				<span class="font-medium">Pasta atual:</span>
				<code class="font-mono">{keysStatus.google_drive_folder_id}</code>
			</div>
		{/if}

		<!-- Listar pastas -->
		{#if keysStatus.google_drive_credentials_set}
			<button
				onclick={listarPastas}
				disabled={carregandoPastas}
				class="mb-4 px-4 py-2 rounded-full text-sm font-medium border border-teal-5/40 text-teal-6
					hover:bg-teal-2 transition-all cursor-pointer disabled:opacity-50"
			>
				{carregandoPastas ? 'Carregando...' : 'Listar pastas do Drive'}
			</button>

			{#if erroPastas}
				<p class="text-xs text-red-500 mb-3">{erroPastas}</p>
			{/if}

			{#if pastas.length > 0}
				<div class="mb-4 space-y-1.5 max-h-48 overflow-y-auto">
					{#each pastas as pasta}
						<button
							onclick={() => salvarPasta(pasta.id)}
							class="w-full text-left px-4 py-2.5 rounded-xl text-sm transition-all cursor-pointer
								{pastaSelecionada === pasta.id
									? 'bg-steel-6 text-white'
									: 'bg-teal-1 text-steel-6 hover:bg-teal-2'}"
						>
							<span class="font-medium">{pasta.name}</span>
							<span class="ml-2 text-xs opacity-60 font-mono">{pasta.id.slice(0, 12)}...</span>
						</button>
					{/each}
				</div>
			{/if}
		{:else}
			<p class="text-xs text-steel-4 mb-4">Configure as credenciais do Google Drive primeiro para listar pastas.</p>
		{/if}

		<!-- Input manual -->
		<div>
			<label for="folder-id" class="block text-xs font-medium text-steel-4 mb-1.5">
				Ou cole o ID da pasta manualmente
			</label>
			<input id="folder-id" type="text" bind:value={folderIdManual}
				placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgVE2upms"
				class="w-full px-4 py-3 rounded-xl border border-teal-4/30 bg-white text-steel-6 text-sm font-mono focus:border-steel-3 focus:ring-2 focus:ring-steel-3/20 outline-none transition-all" />
			<p class="text-xs text-steel-4 mt-1.5 font-light">
				O ID está na URL do Drive: drive.google.com/drive/folders/<strong>ID_AQUI</strong>
			</p>
		</div>
	</div>

	<!-- Design Systems -->
	<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-5 sm:p-6 mb-6">
		<h3 class="font-semibold text-steel-6 mb-1 flex items-center gap-2">
			<span class="w-2 h-2 rounded-full bg-[#A78BFA]"></span>
			Design Systems (Marcas)
		</h3>
		<p class="text-xs text-steel-4 mb-4 font-light">Cada marca tem suas cores, fontes e estilo. Suba um arquivo .md ou .html para adicionar.</p>

		{#if designSystems.length > 0}
			<div class="space-y-2 mb-4">
				{#each designSystems as ds}
					<div class="flex items-center gap-3 px-4 py-3 rounded-xl bg-teal-1 border border-teal-4/20">
						<span class="w-2 h-2 rounded-full bg-[#A78BFA]"></span>
						<span class="flex-1 text-sm font-medium text-steel-6">{ds.name.replace(/\.(md|txt|html)$/, '')}</span>
						<button onclick={() => previewDS(ds)}
							class="px-3 py-1 rounded-full text-xs font-medium bg-white border border-steel-3/30 text-steel-3 hover:bg-steel-0 transition-all cursor-pointer">
							Ver
						</button>
						<button onclick={() => deletarDS(ds)}
							class="px-3 py-1 rounded-full text-xs text-red-500 hover:bg-red-50 transition-all cursor-pointer">
							Remover
						</button>
					</div>
				{/each}
			</div>
		{:else if !carregandoDS}
			<p class="text-xs text-steel-4 mb-4 italic">Nenhum design system cadastrado.</p>
		{/if}

		{#if carregandoDS}
			<p class="text-xs text-steel-4 mb-4">Carregando...</p>
		{/if}

		<!-- Preview modal -->
		{#if dsPreview}
			<div class="mb-4 rounded-xl border border-[#A78BFA]/30 overflow-hidden">
				<div class="flex items-center justify-between px-4 py-2 bg-steel-6 text-white text-xs">
					<span class="font-medium">{dsPreview.name}</span>
					<button onclick={() => dsPreview = null} class="hover:text-teal-4 cursor-pointer">Fechar</button>
				</div>
				{#if dsPreview.isHtml}
					<iframe srcdoc={dsPreview.content} class="w-full h-80 bg-white border-0" sandbox="allow-same-origin" title="Preview"></iframe>
				{:else}
					<pre class="p-4 text-xs text-steel-5 bg-white overflow-auto max-h-80 whitespace-pre-wrap font-mono">{dsPreview.content}</pre>
				{/if}
			</div>
		{/if}

		<input bind:this={dsFileInput} type="file" accept=".md,.html,.txt" onchange={uploadDesignSystem} class="hidden" />
		<button onclick={() => dsFileInput.click()} disabled={uploadingDS}
			class="px-5 py-2.5 rounded-full text-sm font-medium border border-steel-3/30 text-steel-3 hover:bg-steel-0 transition-all cursor-pointer active:scale-[0.97] disabled:opacity-50">
			{uploadingDS ? 'Enviando...' : 'Upload Design System (.md ou .html)'}
		</button>
	</div>

	<!-- Backend URL -->
	<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-6 mb-6">
		<h3 class="font-semibold text-steel-6 mb-4 flex items-center gap-2">
			<span class="w-2 h-2 rounded-full bg-teal-6"></span>
			Backend
		</h3>
		<div>
			<label for="backend-url" class="block text-sm font-medium text-steel-5 mb-1.5">URL do Backend (FastAPI)</label>
			<input id="backend-url" type="url" bind:value={formData.backendUrl}
				placeholder="http://localhost:8000"
				class="w-full px-4 py-3 rounded-xl border border-teal-4/30 bg-white text-steel-6 text-sm focus:border-steel-3 focus:ring-2 focus:ring-steel-3/20 outline-none transition-all" />
		</div>
	</div>

	<!-- Galeria de Fotos -->
	<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-5 sm:p-6 mb-6">
		<h3 class="font-semibold text-steel-6 mb-1 flex items-center gap-2">
			<span class="w-2 h-2 rounded-full bg-steel-2"></span>
			Suas Fotos
		</h3>
		<p class="text-xs text-steel-4 mb-4 font-light">Escolha qual foto aparece nos slides. A foto ativa tem borda roxa.</p>

		{#if $fotos.length > 0}
			<div class="flex flex-wrap gap-3 mb-4">
				{#each $fotos as foto}
					<div class="relative group">
						<button
							onclick={() => usarFoto(foto)}
							class="w-16 h-16 sm:w-20 sm:h-20 rounded-full overflow-hidden cursor-pointer transition-all
								{formData.fotoCriadorBase64 === foto.dataUrl
									? 'ring-3 ring-[#A78BFA] ring-offset-2 scale-110'
									: 'opacity-70 hover:opacity-100 hover:scale-105'}"
						>
							<img src={foto.dataUrl} alt={foto.name} class="w-full h-full object-cover" />
						</button>
						<button
							onclick={() => removerFoto(foto.id)}
							class="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-red-500 text-white text-xs
								flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
							x
						</button>
					</div>
				{/each}
			</div>
		{:else}
			<p class="text-xs text-steel-4 mb-4 italic">Nenhuma foto adicionada. Faça upload abaixo.</p>
		{/if}

		<input bind:this={fileInput} type="file" accept="image/*" multiple onchange={handleFotos} class="hidden" />
		<button onclick={() => fileInput.click()}
			class="px-5 py-2.5 rounded-full text-sm font-medium border border-steel-3/30 text-steel-3 hover:bg-steel-0 transition-all cursor-pointer active:scale-[0.97]">
			Adicionar fotos
		</button>
	</div>

	<!-- Actions -->
	<div class="flex gap-3">
		<button onclick={salvar} disabled={salvando}
			class="flex-1 py-3 rounded-full font-medium text-white transition-all duration-300 cursor-pointer
				bg-gradient-to-r from-steel-4 via-steel-3 to-steel-2
				hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed">
			{salvando ? 'Salvando...' : salvo ? 'Salvo!' : 'Salvar configurações'}
		</button>
		<button onclick={resetar}
			class="px-6 py-3 rounded-full font-medium text-steel-4 border border-teal-4/30 hover:bg-teal-1 transition-all cursor-pointer">
			Resetar
		</button>
	</div>

	{#if erroSalvar}
		<div class="mt-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm text-center animate-fade-up">
			{erroSalvar}
		</div>
	{/if}

	{#if salvo}
		<div class="mt-4 p-3 rounded-xl bg-teal-1 border border-teal-4/30 text-teal-6 text-sm text-center animate-fade-up">
			Configurações salvas com sucesso!
		</div>
	{/if}
</div>
