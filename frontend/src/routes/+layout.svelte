<script lang="ts">
	import '../app.css';
	import { afterNavigate } from '$app/navigation';
	import { page } from '$app/state';
	import { tick } from 'svelte';
	import Sidebar from '$lib/components/layout/Sidebar.svelte';

	let { children } = $props();
	let sidebarCollapsed = $state(false);
	let mobileMenuOpen = $state(false);
	let mainEl: HTMLElement;

	const isHome = $derived(page.url.pathname === '/' && !page.url.searchParams.has('formato'));

	afterNavigate(async () => {
		await tick();
		window.scrollTo({ top: 0, behavior: 'instant' });
		mainEl?.scrollTo({ top: 0, behavior: 'instant' });
	});
</script>

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
		{#if isHome}
			{@render children()}
		{:else}
			<div class="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
				{@render children()}
			</div>
		{/if}
	</main>
</div>
