<script lang="ts">
	import { goto } from '$app/navigation';
	import { NotificationService } from '$lib/services/NotificationService';
	import { getNotifications, setNotifications, getUnreadCount } from '$lib/stores/notifications.svelte';
	import { formatRelativeDate } from '$lib/utils/date';

	let { onClose }: { onClose: () => void } = $props();

	const notifications = $derived(getNotifications());
	const unreadCount = $derived(getUnreadCount());

	async function markAllRead() {
		await NotificationService.marcarTodasComoLidas();
		const updated = await NotificationService.listar();
		setNotifications(updated);
	}

	async function handleClick(notifId: string, cardId: string) {
		await NotificationService.marcarComoLida(notifId);
		const updated = await NotificationService.listar();
		setNotifications(updated);
		onClose();
		goto(`/kanban?card=${cardId}`);
	}

	const typeIcons: Record<string, string> = {
		assigned: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
		column_changed: 'M14 5l7 7m0 0l-7 7m7-7H3',
		mentioned: 'M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207'
	};

	const typeColors: Record<string, string> = {
		assigned: 'bg-purple-500/10 text-purple-600',
		column_changed: 'bg-blue-500/10 text-blue-600',
		mentioned: 'bg-cyan-500/10 text-cyan-600'
	};
</script>

<!-- Backdrop -->
<button class="fixed inset-0 z-40" onclick={onClose} tabindex={-1}></button>

<!-- Dropdown -->
<div class="absolute right-0 top-full mt-2 w-[360px] bg-bg-card rounded-xl border border-border-default shadow-lg z-50 max-h-[480px] overflow-hidden flex flex-col animate-fade-up">
	<!-- Header -->
	<div class="px-4 py-3 border-b border-border-default flex items-center justify-between shrink-0">
		<span class="text-sm font-semibold text-text-primary">Notificacoes</span>
		{#if unreadCount > 0}
			<button
				onclick={markAllRead}
				class="text-[11px] text-purple hover:underline cursor-pointer"
			>
				Marcar todas como lidas
			</button>
		{/if}
	</div>

	<!-- List -->
	<div class="overflow-y-auto scrollbar-thin flex-1">
		{#if notifications.length === 0}
			<p class="text-sm text-text-muted text-center py-8">Nenhuma notificacao.</p>
		{:else}
			{#each notifications as notif (notif.id)}
				<button
					onclick={() => handleClick(notif.id, notif.card_id)}
					class="w-full px-4 py-3 flex gap-3 hover:bg-bg-elevated transition-all text-left cursor-pointer
						{!notif.is_read ? 'bg-purple/3' : ''}"
				>
					<!-- Icon -->
					<div class="w-8 h-8 rounded-full {typeColors[notif.type] ?? 'bg-bg-elevated text-text-muted'} flex items-center justify-center shrink-0">
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={typeIcons[notif.type] ?? typeIcons.assigned} />
						</svg>
					</div>

					<!-- Content -->
					<div class="flex-1 min-w-0">
						<p class="text-sm {!notif.is_read ? 'font-medium text-text-primary' : 'font-normal text-text-secondary'} line-clamp-2">
							{notif.message}
						</p>
						<span class="text-[11px] text-text-muted">{formatRelativeDate(notif.created_at)}</span>
					</div>

					<!-- Unread dot -->
					{#if !notif.is_read}
						<div class="w-2 h-2 rounded-full bg-purple shrink-0 mt-1.5"></div>
					{/if}
				</button>
			{/each}
		{/if}
	</div>
</div>
