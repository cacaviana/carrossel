<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { HistoricoService } from '$lib/services/HistoricoService';
	import { HistoricoItemDTO } from '$lib/dtos/HistoricoItemDTO';
	import { BoardService } from '$lib/services/BoardService';
	import { CardService } from '$lib/services/CardService';
	import { UserService } from '$lib/services/UserService';
	import { CriarCardDTO } from '$lib/dtos/CriarCardDTO';
	import { isLoggedIn, getAuth } from '$lib/stores/auth.svelte';
	import {
		getBoard, setBoard,
		getCards, setCards,
		getUsers, setUsers,
		getSearchQuery, setSearchQuery,
		getFilterResponsavel, setFilterResponsavel,
		getFilterPrioridade, setFilterPrioridade,
		getFilterColuna, setFilterColuna,
		getLoading, setLoading,
		getErro, setErro,
		clearFilters, hasActiveFilters
	} from '$lib/stores/kanban.svelte';
	import Spinner from '$lib/components/ui/Spinner.svelte';
	import Banner from '$lib/components/ui/Banner.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import KanbanBoard from '$lib/components/kanban/KanbanBoard.svelte';
	import KanbanCalendar from '$lib/components/kanban/KanbanCalendar.svelte';
	import KanbanFilters from '$lib/components/kanban/KanbanFilters.svelte';
	import CardDetailModal from '$lib/components/kanban/CardDetailModal.svelte';
	import CardCreateModal from '$lib/components/kanban/CardCreateModal.svelte';
	import { scoreCor } from '$lib/dtos/ScoreDTO';
	import { AuthService } from '$lib/services/AuthService';
	import { UserDTO } from '$lib/dtos/UserDTO';
	import { CriarUsuarioDTO } from '$lib/dtos/CriarUsuarioDTO';
	import { EditarUsuarioDTO } from '$lib/dtos/EditarUsuarioDTO';
	import UserTable from '$lib/components/user/UserTable.svelte';
	import UserFormModal from '$lib/components/user/UserFormModal.svelte';
	import InviteModal from '$lib/components/user/InviteModal.svelte';

	// === TABS ===
	let activeTab = $state<'historico' | 'kanban' | 'calendario' | 'usuarios'>('historico');

	// === HISTORICO STATE ===
	let historico = $state<HistoricoItemDTO[]>([]);
	let filtroTexto = $state('');
	let filtroFormato = $state('');
	let filtroStatus = $state('');
	let carregando = $state(true);
	let erroHistorico = $state('');
	let showRemoveModal = $state(false);
	let itemToRemove = $state<HistoricoItemDTO | null>(null);

	const historicoFiltrado = $derived(
		historico.filter(h => {
			if (filtroTexto && !h.titulo.toLowerCase().includes(filtroTexto.toLowerCase()) &&
				!h.disciplina.toLowerCase().includes(filtroTexto.toLowerCase()) &&
				!h.tecnologia_principal.toLowerCase().includes(filtroTexto.toLowerCase())) return false;
			if (filtroFormato && h.formato !== filtroFormato) return false;
			if (filtroStatus && h.status !== filtroStatus) return false;
			return true;
		})
	);

	function statusBadge(status: string): string {
		switch (status) {
			case 'completo': return 'bg-green/10 text-green border-green/25';
			case 'em_andamento': return 'bg-purple/8 text-purple border-purple/20';
			case 'erro': return 'bg-red/9 text-red border-red/15';
			case 'cancelado': return 'bg-bg-elevated text-text-muted border-border-default';
			default: return 'bg-bg-elevated text-text-muted border-border-default';
		}
	}

	async function confirmarRemover() {
		if (!itemToRemove) return;
		try {
			await HistoricoService.remover(itemToRemove.id);
			historico = historico.filter(h => h.id !== itemToRemove!.id);
		} catch {}
		showRemoveModal = false;
		itemToRemove = null;
	}

	// === KANBAN STATE ===
	let showCreateModal = $state(false);
	let selectedCardId = $state<string | null>(null);
	let refreshing = $state(false);

	const board = $derived(getBoard());
	const users = $derived(getUsers());
	const cards = $derived(getCards());
	const loading = $derived(getLoading());
	const erro = $derived(getErro());
	const searchQuery = $derived(getSearchQuery());
	const filterResponsavel = $derived(getFilterResponsavel());
	const filterPrioridade = $derived(getFilterPrioridade());
	const filterColuna = $derived(getFilterColuna());
	const filtersActive = $derived(hasActiveFilters());
	const auth = $derived(getAuth());

	const selectedCard = $derived(
		selectedCardId ? cards.find(c => c.id === selectedCardId) ?? null : null
	);

	// === USUARIOS STATE ===
	let allUsers = $state<UserDTO[]>([]);
	let loadingUsers = $state(false);
	let erroUsers = $state('');
	let showUserFormModal = $state(false);
	let showInviteModal = $state(false);
	let editingUser = $state<UserDTO | null>(null);
	let successMsg = $state('');
	let inviteUrl = $state('');

	async function loadUsers() {
		loadingUsers = true;
		erroUsers = '';
		try {
			allUsers = await AuthService.listarUsuarios();
		} catch {
			erroUsers = 'Erro ao carregar usuarios.';
		} finally {
			loadingUsers = false;
		}
	}

	function handleEditUser(user: UserDTO) {
		editingUser = user;
		showUserFormModal = true;
	}

	async function handleToggleStatus(user: UserDTO) {
		try {
			if (user.isActive) {
				await AuthService.desativarUsuario(user.id);
			} else {
				await AuthService.reativarUsuario(user.id);
			}
			await loadUsers();
			successMsg = user.isActive ? 'Usuario desativado.' : 'Usuario reativado.';
			setTimeout(() => successMsg = '', 3000);
		} catch (err: any) {
			erroUsers = err.message ?? 'Erro ao alterar status.';
		}
	}

	async function handleSaveUser(data: Record<string, any>) {
		try {
			if (data.user_id) {
				const dto = new EditarUsuarioDTO(data);
				await AuthService.editarUsuario(dto);
				successMsg = 'Usuario atualizado.';
			} else {
				const dto = new CriarUsuarioDTO(data);
				await AuthService.criarUsuario(dto);
				successMsg = 'Usuario criado.';
			}
			showUserFormModal = false;
			editingUser = null;
			await loadUsers();
			setTimeout(() => successMsg = '', 3000);
		} catch (err: any) {
			erroUsers = err.message ?? 'Erro ao salvar usuario.';
		}
	}

	async function handleInvite(data: { email: string; name: string; role: string }) {
		try {
			const result = await AuthService.convidarUsuario(data);
			inviteUrl = result.invite_url;
			showInviteModal = false;
			successMsg = 'Convite gerado com sucesso!';
			setTimeout(() => { successMsg = ''; inviteUrl = ''; }, 10000);
		} catch (err: any) {
			erroUsers = err.message ?? 'Erro ao convidar usuario.';
		}
	}

	let kanbanLoaded = false;

	async function loadKanban() {
		if (kanbanLoaded) return;
		setLoading(true);
		setErro('');
		try {
			const [boardData, cardsData, usersData] = await Promise.all([
				BoardService.carregar(),
				CardService.listarTodos(),
				UserService.listarTodos()
			]);
			setBoard(boardData);
			setCards(cardsData);
			setUsers(usersData);
			kanbanLoaded = true;
		} catch {
			setErro('Erro ao carregar o board. Tente novamente.');
		} finally {
			setLoading(false);
		}
	}

	async function handleRefresh() {
		refreshing = true;
		kanbanLoaded = false;
		await loadKanban();
		refreshing = false;
	}

	function handleCardClick(cardId: string) {
		selectedCardId = cardId;
	}

	function handleCloseDetail() {
		selectedCardId = null;
	}

	async function handleDrop(cardId: string) {
		if (!board) return;
		try {
			await CardService.moverParaCancelado(cardId, board.canceladoColumnId);
			const updatedCards = await CardService.listarTodos();
			setCards(updatedCards);
		} catch {
			setErro('Erro ao cancelar carrossel. Tente novamente.');
		}
	}

	async function handleCreateCard(data: Record<string, any>) {
		const dto = new CriarCardDTO(data);
		if (!dto.isValid()) return;
		await CardService.criar(dto);
		const updatedCards = await CardService.listarTodos();
		setCards(updatedCards);
		showCreateModal = false;
	}

	// Quando troca pra aba kanban ou calendario, carrega os dados
	$effect(() => {
		if (activeTab === 'kanban' || activeTab === 'calendario') {
			loadKanban();
		}
		if (activeTab === 'usuarios') {
			loadUsers();
		}
	});

	onMount(async () => {
		try {
			historico = await HistoricoService.listar();
		} catch {
			erroHistorico = 'Nao foi possivel carregar o historico.';
		} finally {
			carregando = false;
		}

		// Check tab from URL
		const tab = page.url.searchParams.get('tab');
		if (tab === 'kanban' || tab === 'calendario' || tab === 'usuarios') activeTab = tab;

		const cardParam = page.url.searchParams.get('card');
		if (cardParam) {
			selectedCardId = cardParam;
			activeTab = 'kanban';
		}
	});

	function setTab(tab: 'historico' | 'kanban' | 'calendario' | 'usuarios') {
		activeTab = tab;
		const url = new URL(window.location.href);
		if (tab === 'historico') url.searchParams.delete('tab');
		else url.searchParams.set('tab', tab);
		history.replaceState(null, '', url.toString());
	}
</script>

<svelte:head>
	<title>Historico — Content Factory</title>
</svelte:head>

<div class="animate-fade-up">
	<!-- Header com tabs -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
		<div>
			<h1 class="text-2xl font-light text-text-primary mb-2">Historico</h1>
			<!-- Tabs -->
			<div class="flex gap-1 bg-bg-elevated rounded-lg p-1">
				<button
					onclick={() => setTab('historico')}
					class="px-4 py-1.5 rounded-md text-sm font-medium transition-all cursor-pointer
						{activeTab === 'historico' ? 'bg-bg-card text-text-primary shadow-sm' : 'text-text-muted hover:text-text-secondary'}"
				>
					Lista
				</button>
				<button
					onclick={() => setTab('kanban')}
					class="px-4 py-1.5 rounded-md text-sm font-medium transition-all cursor-pointer
						{activeTab === 'kanban' ? 'bg-bg-card text-text-primary shadow-sm' : 'text-text-muted hover:text-text-secondary'}"
				>
					Kanban
				</button>
				<button
					onclick={() => setTab('calendario')}
					class="px-4 py-1.5 rounded-md text-sm font-medium transition-all cursor-pointer
						{activeTab === 'calendario' ? 'bg-bg-card text-text-primary shadow-sm' : 'text-text-muted hover:text-text-secondary'}"
				>
					Calendario
				</button>
				{#if auth?.isAdmin}
					<button
						data-testid="tab-usuarios"
						onclick={() => setTab('usuarios')}
						class="px-4 py-1.5 rounded-md text-sm font-medium transition-all cursor-pointer
							{activeTab === 'usuarios' ? 'bg-bg-card text-text-primary shadow-sm' : 'text-text-muted hover:text-text-secondary'}"
					>
						Usuarios
					</button>
				{/if}
			</div>
		</div>

		<!-- Actions (kanban only) -->
		{#if activeTab === 'kanban' || activeTab === 'calendario'}
			<div class="flex items-center gap-2">
				{#if auth?.canCreateCard}
					<button
						onclick={() => showCreateModal = true}
						class="px-4 py-2 rounded-lg font-medium text-sm text-white
							bg-purple hover:opacity-90 transition-all cursor-pointer
							inline-flex items-center gap-1.5"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
						</svg>
						Novo Card
					</button>
				{/if}

				<button
					onclick={handleRefresh}
					disabled={refreshing}
					class="p-2 rounded-lg border border-border-default text-text-secondary
						hover:bg-bg-elevated transition-all cursor-pointer disabled:opacity-50"
				>
					<svg class="w-5 h-5 {refreshing ? 'animate-spin' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
					</svg>
				</button>
			</div>
		{/if}
	</div>

	<!-- ========== TAB: HISTORICO ========== -->
	{#if activeTab === 'historico'}
		<!-- Filtros -->
		<div class="flex flex-wrap gap-3 mb-6">
			<input data-testid="campo-busca-historico" type="text" bind:value={filtroTexto} placeholder="Buscar por titulo..."
				class="flex-1 min-w-[200px] max-w-sm px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
					focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all placeholder:text-text-muted" />
			<select bind:value={filtroFormato}
				class="px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
					focus:border-purple outline-none cursor-pointer">
				<option value="">Todos os formatos</option>
				<option value="carrossel">Carrossel</option>
				<option value="post_unico">Post Unico</option>
				<option value="thumbnail_youtube">Thumbnail YouTube</option>
			</select>
			<select bind:value={filtroStatus}
				class="px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
					focus:border-purple outline-none cursor-pointer">
				<option value="">Todos os status</option>
				<option value="completo">Completo</option>
				<option value="em_andamento">Em andamento</option>
				<option value="erro">Erro</option>
				<option value="cancelado">Cancelado</option>
			</select>
		</div>

		{#if erroHistorico}
			<Banner type="error">{erroHistorico}</Banner>
		{:else if carregando}
			<div class="text-center py-16">
				<Spinner size="lg" />
				<p class="text-text-secondary mt-3 text-sm">Carregando historico...</p>
			</div>
		{:else if historicoFiltrado.length === 0}
			<div class="text-center py-16">
				<p class="text-text-secondary text-lg mb-2">
					{filtroTexto || filtroFormato || filtroStatus ? 'Nenhum resultado encontrado.' : 'Nenhum conteudo salvo ainda.'}
				</p>
				{#if filtroTexto || filtroFormato || filtroStatus}
					<button onclick={() => { filtroTexto = ''; filtroFormato = ''; filtroStatus = ''; }}
						class="text-sm text-purple hover:text-purple-soft cursor-pointer">Limpar filtros</button>
				{:else}
					<p class="text-text-muted text-sm mb-4">Crie conteudo e salve no Google Drive para ve-lo aqui.</p>
					<a href="/" class="inline-flex px-6 py-3 rounded-full bg-purple text-bg-global font-medium text-sm no-underline hover:opacity-90 transition-all">Criar Conteudo</a>
				{/if}
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each historicoFiltrado as item}
					<div
						onclick={() => { if (item.isPipelineV3 && item.pipeline_id) window.open(`/pipeline/${item.pipeline_id}`, '_blank', 'noopener'); }}
						role={item.isPipelineV3 ? 'link' : undefined}
						class="bg-bg-card rounded-xl border border-border-default p-5 hover:-translate-y-1 hover:shadow-md hover:border-purple/30 transition-all
							{item.isPipelineV3 ? 'cursor-pointer' : ''}"
					>
						<div class="flex items-center gap-2 mb-3 flex-wrap">
							<span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-purple/8 text-purple border border-purple/20">{item.formato || 'carrossel'}</span>
							<span class="px-2 py-0.5 rounded-full text-[10px] font-mono border {statusBadge(item.status)}">{item.status}</span>
							{#if !item.isPipelineV3}
								<span class="px-2 py-0.5 rounded-full text-[10px] font-mono bg-amber/10 text-amber border border-amber/25">legado</span>
							{/if}
						</div>
						<h3 class="text-sm font-medium text-text-primary mb-1 line-clamp-2">{item.titulo}</h3>
						{#if item.disciplina}
							<p class="text-xs text-text-secondary mb-2">{item.disciplina} — {item.tecnologia_principal}</p>
						{/if}
						<div class="flex items-center justify-between mt-3">
							<span class="text-xs text-text-muted font-mono">
								{item.total_slides} slide{item.total_slides !== 1 ? 's' : ''}
								{#if item.criado_em} — {item.dataFormatada}{/if}
							</span>
							{#if item.temScore && item.final_score !== null}
								<span class="text-lg font-bold font-mono {scoreCor(item.final_score)}">{item.final_score.toFixed(1)}</span>
							{/if}
						</div>
						<div class="flex items-center gap-2 mt-3 pt-3 border-t border-border-default">
							{#if item.temDriveLink}
								<a href={item.google_drive_link} target="_blank" rel="noopener"
									class="text-xs text-purple hover:text-purple-soft no-underline cursor-pointer">Drive</a>
							{/if}
							{#if item.isPipelineV3}
								<a href="/pipeline/{item.pipeline_id}" target="_blank" rel="noopener" class="text-xs text-purple hover:text-purple-soft no-underline cursor-pointer">Reabrir</a>
							{/if}
							<button onclick={() => { itemToRemove = item; showRemoveModal = true; }}
								class="text-xs text-text-muted hover:text-red transition-colors cursor-pointer ml-auto">Remover</button>
						</div>
					</div>
				{/each}
			</div>
		{/if}

		<Modal open={showRemoveModal} size="sm" title="Remover conteudo?" onclose={() => showRemoveModal = false}>
			<p class="text-sm text-text-secondary">A acao nao pode ser desfeita.</p>
			{#snippet footer()}
				<button onclick={() => showRemoveModal = false}
					class="px-4 py-2 rounded-full text-sm text-text-secondary cursor-pointer">Cancelar</button>
				<button onclick={confirmarRemover}
					class="px-4 py-2 rounded-full text-sm font-medium text-red bg-red/9 border border-red/15 hover:bg-red/15 transition-all cursor-pointer">Remover</button>
			{/snippet}
		</Modal>

	<!-- ========== TAB: KANBAN ========== -->
	{:else if activeTab === 'kanban'}
		{#if board}
			<div class="mb-6">
				<KanbanFilters
					{users}
					columns={board.columnsSorted}
					{searchQuery}
					{filterResponsavel}
					{filterPrioridade}
					{filterColuna}
					onSearchChange={setSearchQuery}
					onResponsavelChange={setFilterResponsavel}
					onPrioridadeChange={setFilterPrioridade}
					onColunaChange={setFilterColuna}
					onClear={clearFilters}
					hasFilters={filtersActive}
				/>
			</div>
		{/if}

		{#if loading}
			<div class="flex gap-4 overflow-x-auto pb-4">
				{#each Array(5) as _, i}
					<div class="min-w-[280px] w-[280px] bg-bg-elevated/50 rounded-xl">
						<div class="px-3 py-2.5 border-t-4 border-gray-300">
							<div class="h-4 w-16 animate-shimmer rounded"></div>
						</div>
						<div class="p-2 space-y-2">
							{#each Array(i < 2 ? 2 : 1) as _}
								<div class="h-24 animate-shimmer rounded-xl border border-border-default"></div>
							{/each}
						</div>
					</div>
				{/each}
			</div>
		{:else if erro}
			<div class="bg-red/10 border border-red/20 rounded-xl p-4 flex items-center justify-between">
				<p class="text-sm text-red">{erro}</p>
				<button onclick={handleRefresh} class="text-sm text-purple hover:underline cursor-pointer">Tentar novamente</button>
			</div>
		{:else if board}
			<KanbanBoard {board} {users} onCardClick={handleCardClick} onDrop={handleDrop} />
		{/if}

	<!-- ========== TAB: CALENDARIO ========== -->
	{:else if activeTab === 'calendario'}
		{#if loading}
			<div class="text-center py-16">
				<Spinner size="lg" />
				<p class="text-text-secondary mt-3 text-sm">Carregando calendario...</p>
			</div>
		{:else}
			<KanbanCalendar {cards} onCardClick={handleCardClick} />
		{/if}

	<!-- ========== TAB: USUARIOS ========== -->
	{:else if activeTab === 'usuarios'}
		{#if successMsg}
			<Banner type="success" dismissible ondismiss={() => successMsg = ''}>{successMsg}</Banner>
			{#if inviteUrl}
				<div class="mt-3 p-3 rounded-lg bg-purple/8 border border-purple/20">
					<p class="text-xs text-text-secondary mb-1">Link de convite (copie e envie):</p>
					<div class="flex items-center gap-2">
						<code class="flex-1 text-xs text-purple font-mono break-all">{inviteUrl}</code>
						<button
							data-testid="btn-copiar-link"
							onclick={() => navigator.clipboard.writeText(inviteUrl)}
							class="px-3 py-1.5 rounded-lg text-xs font-medium text-purple bg-purple/10 hover:bg-purple/20 transition-all cursor-pointer"
						>
							Copiar
						</button>
					</div>
				</div>
			{/if}
		{/if}

		{#if erroUsers}
			<div class="mt-3">
				<Banner type="error" dismissible ondismiss={() => erroUsers = ''}>{erroUsers}</Banner>
			</div>
		{/if}

		{#if loadingUsers}
			<div class="text-center py-16">
				<Spinner size="lg" />
				<p class="text-text-secondary mt-3 text-sm">Carregando usuarios...</p>
			</div>
		{:else}
			<div class="mt-4">
				<UserTable
					users={allUsers}
					onEdit={handleEditUser}
					onToggleStatus={handleToggleStatus}
					onInvite={() => showInviteModal = true}
				/>
			</div>
		{/if}

		<UserFormModal
			open={showUserFormModal}
			user={editingUser}
			onClose={() => { showUserFormModal = false; editingUser = null; }}
			onSave={handleSaveUser}
		/>

		<InviteModal
			open={showInviteModal}
			onClose={() => showInviteModal = false}
			onInvite={handleInvite}
		/>
	{/if}

	<!-- Card detail modal (kanban + calendario) -->
	{#if activeTab === 'kanban' || activeTab === 'calendario'}
		<CardDetailModal
			card={selectedCard}
			{users}
			columns={board?.columnsSorted ?? []}
			onClose={handleCloseDetail}
		/>

		<CardCreateModal
			open={showCreateModal}
			{users}
			onClose={() => showCreateModal = false}
			onCreate={handleCreateCard}
		/>
	{/if}
</div>
