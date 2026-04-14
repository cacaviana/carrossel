<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
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

	import KanbanBoard from '$lib/components/kanban/KanbanBoard.svelte';
	import KanbanCalendar from '$lib/components/kanban/KanbanCalendar.svelte';
	import KanbanFilters from '$lib/components/kanban/KanbanFilters.svelte';
	import CardDetailModal from '$lib/components/kanban/CardDetailModal.svelte';
	import CardCreateModal from '$lib/components/kanban/CardCreateModal.svelte';

	let showCreateModal = $state(false);
	let viewMode = $state<'board' | 'calendar'>('board');
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

	onMount(async () => {
		if (!isLoggedIn()) {
			goto('/login');
			return;
		}

		// Check for card query param
		const cardParam = page.url.searchParams.get('card');
		if (cardParam) selectedCardId = cardParam;

		await loadBoard();
	});

	async function loadBoard() {
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
		} catch {
			setErro('Erro ao carregar o board. Tente novamente.');
		} finally {
			setLoading(false);
		}
	}

	async function handleRefresh() {
		refreshing = true;
		await loadBoard();
		refreshing = false;
	}

	function handleCardClick(cardId: string) {
		selectedCardId = cardId;
		const url = new URL(window.location.href);
		url.searchParams.set('card', cardId);
		history.replaceState(null, '', url.toString());
	}

	function handleCloseDetail() {
		selectedCardId = null;
		const url = new URL(window.location.href);
		url.searchParams.delete('card');
		history.replaceState(null, '', url.toString());
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
</script>

<svelte:head>
	<title>Kanban - Content Factory</title>
</svelte:head>

<!-- Header bar -->
<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
	<h1 class="text-2xl font-bold text-steel-6">Kanban</h1>
	<div class="flex items-center gap-2">
		<!-- View toggle -->
		<div class="flex rounded-lg border border-border-default overflow-hidden">
			<button
				onclick={() => viewMode = 'board'}
				class="px-3 py-2 text-sm transition-all cursor-pointer
					{viewMode === 'board' ? 'bg-purple text-white' : 'text-text-secondary hover:bg-bg-elevated'}"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2" />
				</svg>
			</button>
			<button
				onclick={() => viewMode = 'calendar'}
				class="px-3 py-2 text-sm transition-all cursor-pointer
					{viewMode === 'calendar' ? 'bg-purple text-white' : 'text-text-secondary hover:bg-bg-elevated'}"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
				</svg>
			</button>
		</div>

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
</div>

<!-- Filters -->
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

<!-- Board states -->
{#if loading}
	<!-- Skeleton -->
	<div class="flex gap-4 overflow-x-auto pb-4">
		{#each Array(6) as _, i}
			<div class="min-w-[280px] w-[280px] bg-bg-elevated/50 rounded-xl">
				<div class="px-3 py-2.5 border-t-4 border-gray-300">
					<div class="h-4 w-16 animate-shimmer rounded"></div>
				</div>
				<div class="p-2 space-y-2">
					{#each Array(i < 3 ? 2 : 1) as _}
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
	{#if viewMode === 'board'}
		<KanbanBoard {board} {users} onCardClick={handleCardClick} onDrop={handleDrop} />
	{:else}
		<KanbanCalendar {cards} />
	{/if}
{/if}

<!-- Card detail modal -->
<CardDetailModal
	card={selectedCard}
	{users}
	columns={board?.columnsSorted ?? []}
	onClose={handleCloseDetail}
/>

<!-- Create card modal -->
<CardCreateModal
	open={showCreateModal}
	{users}
	onClose={() => showCreateModal = false}
	onCreate={handleCreateCard}
/>
