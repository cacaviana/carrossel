<script lang="ts">
	import { onMount } from 'svelte';
	import { NotificationService } from '$lib/services/NotificationService';
	import { getNotifications, setNotifications, getUnreadCount } from '$lib/stores/notifications.svelte';
	import NotificationDropdown from '$lib/components/notification/NotificationDropdown.svelte';

	let open = $state(false);

	onMount(async () => {
		try {
			const notifs = await NotificationService.listar();
			setNotifications(notifs);
		} catch { /* silently fail */ }
	});

	const unreadCount = $derived(getUnreadCount());

	function toggle() {
		open = !open;
	}

	function close() {
		open = false;
	}
</script>

<div class="relative">
	<button
		onclick={toggle}
		class="p-2 rounded-lg hover:bg-black/5 transition-all cursor-pointer relative text-text-secondary"
	>
		<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
		</svg>

		{#if unreadCount > 0}
			<div class="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-red text-white text-[10px] font-bold flex items-center justify-center">
				{unreadCount > 9 ? '9+' : unreadCount}
			</div>
		{/if}
	</button>

	{#if open}
		<NotificationDropdown onClose={close} />
	{/if}
</div>
