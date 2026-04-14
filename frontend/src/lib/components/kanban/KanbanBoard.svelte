<script lang="ts">
	import type { BoardDTO } from '$lib/dtos/BoardDTO';
	import type { UserDTO } from '$lib/dtos/UserDTO';
	import KanbanColumn from '$lib/components/kanban/KanbanColumn.svelte';
	import { getCardsByColumn } from '$lib/stores/kanban.svelte';

	let { board, users, onCardClick, onDrop }: {
		board: BoardDTO;
		users: UserDTO[];
		onCardClick: (cardId: string) => void;
		onDrop: (cardId: string) => void;
	} = $props();
</script>

<div class="flex gap-4 overflow-x-auto pb-4 scrollbar-thin snap-x snap-mandatory md:snap-none">
	{#each board.columnsSorted as column (column.id)}
		<div class="snap-center">
			<KanbanColumn
				{column}
				cards={getCardsByColumn(column.id)}
				{users}
				isDropTarget={column.id === 'col-cancelado' || column.id === 'col-publicado'}
				{onCardClick}
				{onDrop}
			/>
		</div>
	{/each}
</div>
