<script lang="ts">
	import type { CardDTO } from '$lib/dtos/CardDTO';
	import type { UserDTO } from '$lib/dtos/UserDTO';
	let { card, users = [], onclick }: {
		card: CardDTO;
		users: UserDTO[];
		onclick: () => void;
	} = $props();

	const assignedUsers = $derived(
		users.filter(u => card.assigned_user_ids.includes(u.id))
	);

	const priorityClasses: Record<string, string> = {
		alta: 'bg-red-500/10 text-red-600',
		media: 'bg-amber-500/10 text-amber-600',
		baixa: 'bg-gray-500/10 text-gray-500'
	};

	const pipelineTagLabels: Record<string, string> = {
		'col-copy': 'Copy',
		'col-design': 'Diretor de Arte',
		'col-aprovado': 'Aprovado',
		'col-publicado': 'Publicado',
		'col-cancelado': 'Cancelado'
	};

	const pipelineTagClasses: Record<string, string> = {
		'col-copy': 'bg-blue-500/10 text-blue-500 border-blue-500/20',
		'col-design': 'bg-purple-500/10 text-purple-500 border-purple-500/20',
		'col-aprovado': 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
		'col-publicado': 'bg-cyan-500/10 text-cyan-500 border-cyan-500/20',
		'col-cancelado': 'bg-red-500/10 text-red-500 border-red-500/20'
	};
</script>

<button
	{onclick}
	draggable="true"
	ondragstart={(e) => {
		e.dataTransfer?.setData('text/plain', card.id);
		const el = e.currentTarget as HTMLElement;
		el.classList.add('opacity-50', 'rotate-2', 'scale-105');
	}}
	ondragend={(e) => {
		const el = e.currentTarget as HTMLElement;
		el.classList.remove('opacity-50', 'rotate-2', 'scale-105');
	}}
	class="w-full text-left p-3 rounded-xl bg-bg-card border border-border-default
		hover:shadow-md hover:border-purple/30 transition-all cursor-pointer"
>
	<!-- Top row: priority + avatars -->
	<div class="flex items-center justify-between mb-1.5">
		<span class="{priorityClasses[card.priority] ?? ''} text-[10px] px-1.5 py-0.5 rounded-full font-medium">
			{card.priorityLabel}
		</span>
		<div class="flex items-center gap-2">
			{#if assignedUsers.length > 0}
				<div class="flex -space-x-1.5">
					{#each assignedUsers.slice(0, 3) as user}
						<div class="w-6 h-6 rounded-full bg-steel-3/20 text-[9px] font-bold text-steel-3 flex items-center justify-center border border-bg-card"
							title={user.name}>
							{user.iniciais}
						</div>
					{/each}
					{#if assignedUsers.length > 3}
						<div class="w-6 h-6 rounded-full bg-bg-elevated text-[9px] font-medium text-text-muted flex items-center justify-center border border-bg-card">
							+{assignedUsers.length - 3}
						</div>
					{/if}
				</div>
			{/if}
		</div>
	</div>

	<!-- Title -->
	<p class="text-sm font-medium text-text-primary line-clamp-2 mb-2">{card.title}</p>

	<!-- Deadline -->
	{#if card.hasDeadline}
		<div class="flex items-center gap-1 mb-2 text-[11px] {card.isOverdue ? 'text-red-500' : card.isDueSoon ? 'text-amber-500' : 'text-text-muted'}">
			<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
			</svg>
			<span class="font-medium">{card.isOverdue ? 'Atrasado' : card.isDueSoon ? 'Vence em breve' : 'Prazo'}: {card.deadlineLabel}</span>
		</div>
	{/if}

	<!-- Bottom row: pipeline tag + comments -->
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-2">
			<span class="text-[10px] px-1.5 py-0.5 rounded-full font-medium border {pipelineTagClasses[card.column_id] ?? 'bg-gray-500/10 text-gray-500 border-gray-500/20'}">
				{pipelineTagLabels[card.column_id] ?? card.column_id}
			</span>
		</div>

		{#if card.comment_count > 0}
			<div class="flex items-center gap-0.5 text-[11px] text-text-muted">
				<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
				</svg>
				{card.comment_count}
			</div>
		{/if}
	</div>
</button>
