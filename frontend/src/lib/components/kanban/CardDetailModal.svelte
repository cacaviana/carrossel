<script lang="ts">
	import { goto } from '$app/navigation';
	import type { CardDTO } from '$lib/dtos/CardDTO';
	import type { UserDTO } from '$lib/dtos/UserDTO';
	import type { ColumnData } from '$lib/dtos/BoardDTO';
	import CardDetailTab from '$lib/components/kanban/CardDetailTab.svelte';
	import CardCommentsTab from '$lib/components/kanban/CardCommentsTab.svelte';
	import CardActivityTab from '$lib/components/kanban/CardActivityTab.svelte';

	let { card, users = [], columns = [], onClose }: {
		card: CardDTO | null;
		users: UserDTO[];
		columns: ColumnData[];
		onClose: () => void;
	} = $props();

	let activeTab = $state<'detalhes' | 'comentarios' | 'atividade'>('detalhes');

	const currentColumn = $derived(
		card ? columns.find(c => c.id === card.column_id) : null
	);

	const columnColorClasses: Record<string, string> = {
		'#3B82F6': 'bg-blue-500/10 text-blue-600',
		'#8B5CF6': 'bg-purple-500/10 text-purple-600',
		'#F59E0B': 'bg-amber-500/10 text-amber-600',
		'#10B981': 'bg-emerald-500/10 text-emerald-600',
		'#06B6D4': 'bg-cyan-500/10 text-cyan-600',
		'#EF4444': 'bg-red-500/10 text-red-500'
	};

	const priorityClasses: Record<string, string> = {
		alta: 'bg-red-500/10 text-red-600',
		media: 'bg-amber-500/10 text-amber-600',
		baixa: 'bg-gray-500/10 text-gray-500'
	};
</script>

{#if card}
	<div class="fixed inset-0 z-50 flex items-center justify-center">
		<!-- Overlay -->
		<button class="absolute inset-0 bg-black/60" onclick={onClose} tabindex={-1}></button>

		<!-- Modal -->
		<div class="relative w-full max-w-3xl mx-4 bg-bg-card rounded-2xl border border-border-default shadow-2xl animate-fade-up
			max-h-[85vh] flex flex-col">
			<!-- Header -->
			<div class="px-6 py-4 border-b border-border-default shrink-0">
				<div class="flex items-start justify-between">
					<div class="flex-1 min-w-0">
						<h2 class="text-lg font-semibold text-text-primary mb-2">{card.title}</h2>
						<div class="flex items-center gap-2">
							{#if currentColumn}
								<span class="{columnColorClasses[currentColumn.color ?? ''] ?? 'bg-gray-500/10 text-gray-500'} text-[10px] px-2 py-0.5 rounded-full font-medium">
									{currentColumn.name}
								</span>
							{/if}
							<span class="{priorityClasses[card.priority] ?? ''} text-[10px] px-2 py-0.5 rounded-full font-medium">
								{card.priorityLabel}
							</span>
							<button
								onclick={() => { onClose(); goto(card!.hasPipeline ? `/pipeline/${card!.pipeline_id}` : '/'); }}
								class="inline-flex items-center gap-1 text-[11px] px-2.5 py-0.5 rounded-full font-medium
									bg-purple/10 text-purple hover:bg-purple/20 transition-all cursor-pointer"
							>
								<svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
								</svg>
								{card.hasPipeline ? 'Abrir Pipeline' : 'Criar Pipeline'}
							</button>
						</div>
					</div>
					<button onclick={onClose} class="p-1 rounded-lg text-text-muted hover:text-text-primary hover:bg-black/5 transition-all cursor-pointer ml-4">
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>

				<!-- Tabs -->
				<div class="flex gap-1 mt-4">
					{#each [
						{ id: 'detalhes' as const, label: 'Detalhes' },
						{ id: 'comentarios' as const, label: `Comentarios (${card.comment_count})` },
						{ id: 'atividade' as const, label: 'Atividade' }
					] as tab}
						<button
							onclick={() => activeTab = tab.id}
							class="px-4 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer
								{activeTab === tab.id
									? 'bg-purple/8 text-purple'
									: 'text-text-secondary hover:text-text-primary hover:bg-black/5'}"
						>
							{tab.label}
						</button>
					{/each}
				</div>
			</div>

			<!-- Tab content -->
			<div class="flex-1 overflow-y-auto scrollbar-thin px-6 py-5">
				{#if activeTab === 'detalhes'}
					<CardDetailTab {card} {users} {columns} />
				{:else if activeTab === 'comentarios'}
					<CardCommentsTab cardId={card.id} />
				{:else}
					<CardActivityTab cardId={card.id} />
				{/if}
			</div>
		</div>
	</div>
{/if}
