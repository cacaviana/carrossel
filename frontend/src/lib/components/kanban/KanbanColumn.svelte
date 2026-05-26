<script lang="ts">
	import type { ColumnData } from '$lib/dtos/BoardDTO';
	import type { CardDTO } from '$lib/dtos/CardDTO';
	import type { UserDTO } from '$lib/dtos/UserDTO';
	import KanbanCard from '$lib/components/kanban/KanbanCard.svelte';

	let { column, cards, users, isDropTarget = false, onCardClick, onDrop }: {
		column: ColumnData;
		cards: CardDTO[];
		users: UserDTO[];
		isDropTarget: boolean;
		onCardClick: (cardId: string) => void;
		onDrop: (cardId: string) => void;
	} = $props();

	let dragOver = $state(false);

	function handleDragOver(e: DragEvent) {
		if (!isDropTarget) return;
		e.preventDefault();
		dragOver = true;
	}

	function handleDragLeave() {
		dragOver = false;
	}

	function handleDrop(e: DragEvent) {
		if (!isDropTarget) return;
		e.preventDefault();
		dragOver = false;
		const cardId = e.dataTransfer?.getData('text/plain');
		if (cardId) onDrop(cardId);
	}

	const columnBorderColors: Record<string, string> = {
		'#3B82F6': 'border-t-blue-500',
		'#8B5CF6': 'border-t-purple-500',
		'#F59E0B': 'border-t-amber-500',
		'#10B981': 'border-t-emerald-500',
		'#06B6D4': 'border-t-cyan-500',
		'#EF4444': 'border-t-red-500'
	};

	const columnTextColors: Record<string, string> = {
		'#3B82F6': 'text-blue-600',
		'#8B5CF6': 'text-purple-600',
		'#F59E0B': 'text-amber-600',
		'#10B981': 'text-emerald-600',
		'#06B6D4': 'text-cyan-600',
		'#EF4444': 'text-red-500'
	};

	const borderClass = $derived(columnBorderColors[column.color ?? ''] ?? 'border-t-gray-400');
	const textClass = $derived(columnTextColors[column.color ?? ''] ?? 'text-gray-600');
</script>

<div
	class="min-w-[280px] w-[280px] flex flex-col bg-bg-elevated/50 rounded-xl border-t-4 {borderClass}
		{dragOver && column.id === 'col-cancelado' ? 'border-2 border-dashed border-red-500/50 bg-red-500/5' : ''}
		{dragOver && column.id === 'col-publicado' ? 'border-2 border-dashed border-cyan-500/50 bg-cyan-500/5' : ''}"
	role="region"
	aria-label="Coluna {column.name}"
	ondragover={handleDragOver}
	ondragleave={handleDragLeave}
	ondrop={handleDrop}
>
	<!-- Header -->
	<div class="px-3 py-2.5 flex items-center justify-between">
		<span class="text-xs font-semibold uppercase tracking-wide {textClass}">
			{column.name}
		</span>
		<span class="text-[11px] text-text-muted bg-bg-card rounded-full px-2 py-0.5">
			{cards.length}
		</span>
	</div>

	<!-- Cards -->
	<div class="flex flex-col gap-2 p-2 flex-1 overflow-y-auto scrollbar-thin min-h-[100px]">
		{#each cards as card (card.id)}
			<KanbanCard {card} {users} onclick={() => onCardClick(card.id)} />
		{:else}
			{#if dragOver && isDropTarget}
				<p class="text-xs {column.id === 'col-cancelado' ? 'text-red-500' : 'text-cyan-500'} text-center py-4">
					{column.id === 'col-cancelado' ? 'Solte aqui para cancelar' : 'Solte aqui para publicar'}
				</p>
			{/if}
		{/each}
	</div>
</div>
