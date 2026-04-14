<script lang="ts">
	import '../app.css';
	import { afterNavigate, goto } from '$app/navigation';
	import { page } from '$app/state';
	import { tick } from 'svelte';
	import { browser } from '$app/environment';
	import Sidebar from '$lib/components/layout/Sidebar.svelte';

	let { children } = $props();
	let sidebarCollapsed = $state(false);
	let mobileMenuOpen = $state(false);
	let mainEl: HTMLElement;

	const isHome = $derived(page.url.pathname === '/' && !page.url.searchParams.has('formato'));
	const isLoginPage = $derived(page.url.pathname === '/login');
	const isConvitePage = $derived(page.url.pathname === '/convite');
	const histTab = $derived(page.url.searchParams.get('tab'));
	const isKanbanPage = $derived(page.url.pathname === '/historico' && (histTab === 'kanban' || histTab === 'calendario' || histTab === 'usuarios'));
	const isProtectedPage = $derived(page.url.pathname === '/historico' || page.url.pathname.startsWith('/kanban'));

	// Auth — lazy load pra nao quebrar SSR
	let authReady = $state(false);
	let loggedIn = $state(false);
	let authData: any = $state(null);
	let NotificationBellComponent: any = $state(null);

	async function loadAuth() {
		if (!browser) return;
		try {
			const { isLoggedIn, getAuth } = await import('$lib/stores/auth.svelte');
			loggedIn = isLoggedIn();
			authData = getAuth();
			authReady = true;
			const mod = await import('$lib/components/notification/NotificationBell.svelte');
			NotificationBellComponent = mod.default;
		} catch {}
	}

	$effect(() => { if (browser) loadAuth(); });

	const showAuthHeader = $derived(authReady && loggedIn && !isLoginPage && !isConvitePage);

	afterNavigate(async () => {
		await tick();
		window.scrollTo({ top: 0, behavior: 'instant' });
		mainEl?.scrollTo({ top: 0, behavior: 'instant' });

		if (browser) await loadAuth();

		if (isProtectedPage && authReady && !loggedIn) {
			goto('/login');
		}
		if (isLoginPage && authReady && loggedIn) {
			goto('/historico');
		}
	});

	async function handleLogout() {
		if (!browser) return;
		const { clearAuth } = await import('$lib/stores/auth.svelte');
		clearAuth();
		loggedIn = false;
		authData = null;
		goto('/login');
	}
</script>

{#if isLoginPage || isConvitePage}
	{@render children()}
{:else}
<div class="min-h-screen flex bg-bg-global">
	<!-- Sidebar desktop -->
	<div class="hidden md:block shrink-0">
		<Sidebar collapsed={sidebarCollapsed} onToggle={() => sidebarCollapsed = !sidebarCollapsed} />
	</div>

	<!-- Mobile header + drawer -->
	<div class="md:hidden fixed top-0 left-0 right-0 z-40 bg-bg-card border-b border-border-default px-4 py-3 flex items-center justify-between">
		<div class="flex items-center gap-2">
			<div class="w-8 h-8 rounded-lg bg-gradient-to-br from-steel-3 to-steel-5 flex items-center justify-center text-white font-bold text-xs shadow-sm">
				CF
			</div>
			<span class="text-sm font-semibold text-text-primary">Content Factory</span>
		</div>
		<div class="flex items-center gap-2">
			{#if showAuthHeader && NotificationBellComponent}
				<NotificationBellComponent />
			{/if}
			<button
				onclick={() => mobileMenuOpen = !mobileMenuOpen}
				class="p-2 rounded-lg hover:bg-black/5 transition-all cursor-pointer text-text-secondary"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					{#if mobileMenuOpen}
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					{:else}
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
					{/if}
				</svg>
			</button>
		</div>
	</div>

	{#if mobileMenuOpen}
		<div class="md:hidden fixed inset-0 z-30">
			<button class="absolute inset-0 bg-black/60" onclick={() => mobileMenuOpen = false} tabindex="-1"></button>
			<div class="absolute left-0 top-0 bottom-0">
				<Sidebar collapsed={false} onToggle={() => mobileMenuOpen = false} />
			</div>
		</div>
	{/if}

	<!-- Content -->
	<main bind:this={mainEl} class="flex-1 min-h-screen overflow-y-auto md:pt-0 pt-14">
		<!-- Auth header (desktop) -->
		{#if showAuthHeader}
			<div class="hidden md:flex items-center justify-end gap-3 px-6 py-3 border-b border-border-default bg-bg-card">
				{#if NotificationBellComponent}
					<NotificationBellComponent />
				{/if}
				<div class="flex items-center gap-2">
					<div class="w-8 h-8 rounded-full bg-purple/10 text-[10px] font-bold text-purple flex items-center justify-center border border-purple/20">
						{authData?.iniciais ?? ''}
					</div>
					<div class="text-right">
						<p class="text-xs font-medium text-text-primary">{authData?.name ?? ''}</p>
						<p class="text-[10px] text-text-muted">{authData?.roleLabel ?? ''}</p>
					</div>
					<button
						onclick={handleLogout}
						class="ml-2 p-1.5 rounded-lg text-text-muted hover:text-red hover:bg-red/5 transition-all cursor-pointer"
						title="Sair"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
						</svg>
					</button>
				</div>
			</div>
		{/if}

		{#if isHome}
			{@render children()}
		{:else if isKanbanPage}
			<div class="mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
				{@render children()}
			</div>
		{:else}
			<div class="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
				{@render children()}
			</div>
		{/if}
	</main>
</div>
{/if}
