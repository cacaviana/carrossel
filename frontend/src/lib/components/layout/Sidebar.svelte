<script lang="ts">
	import { page } from '$app/state';

	interface NavItem {
		href: string;
		label: string;
		icon: string;
		badge?: string;
		badgeVariant?: string;
		disabled?: boolean;
	}

	let { collapsed = false, onToggle }: { collapsed: boolean; onToggle: () => void } = $props();

	const mainItems: NavItem[] = [
		{ href: '/', label: 'Home', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
		{ href: '#', label: 'Historico', icon: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z', badge: 'Em breve', disabled: true },
	];

	const formatItems: NavItem[] = [
		{ href: '/?formato=carrossel', label: 'Carrossel', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10' },
		{ href: '/?formato=post_unico', label: 'Post Unico', icon: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z' },
		{ href: '/?formato=thumbnail_youtube', label: 'YouTube', icon: 'M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z' },
		{ href: '/?formato=capa_reels', label: 'Reels', icon: 'M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z' },
		{ href: '#', label: 'Anuncio', icon: 'M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z', badge: 'Em breve', disabled: true },
		{ href: '#', label: 'Funil', icon: 'M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12', badge: 'Em breve', disabled: true },
	];

	const systemItems: NavItem[] = [
		{ href: '/agentes', label: 'Agentes', icon: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
		{ href: '/configuracoes', label: 'Config', icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z' },
	];

	function isActive(href: string): boolean {
		if (href === '/') return page.url.pathname === '/' && !page.url.searchParams.has('formato');
		if (href.startsWith('/?formato=')) {
			const fmt = href.split('=')[1];
			return page.url.pathname === '/' && page.url.searchParams.get('formato') === fmt;
		}
		return page.url.pathname.startsWith(href);
	}
</script>

<aside class="flex flex-col h-screen bg-bg-card border-r border-border-default transition-all duration-300
	{collapsed ? 'w-16' : 'w-60'}">

	<!-- Logo -->
	<div class="flex items-center gap-3 px-4 py-5 border-b border-steel-3/10">
		<div class="w-9 h-9 rounded-xl bg-gradient-to-br from-steel-3 to-steel-5 flex items-center justify-center text-white font-bold text-sm shrink-0 shadow-sm">
			CF
		</div>
		{#if !collapsed}
			<div>
				<p class="text-sm font-semibold text-text-primary tracking-tight">Content Factory</p>
				<p class="text-[10px] text-text-muted">IT Valley School</p>
			</div>
		{/if}
	</div>

	<!-- Nav -->
	<nav class="flex-1 overflow-y-auto py-3 px-2 space-y-4 scrollbar-hide">
		<!-- Principal -->
		<div>
			{#if !collapsed}<p class="label-upper px-3 mb-2">Principal</p>{/if}
			{#each mainItems as item}
				<a href={item.href}
					class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all no-underline mb-0.5
						{isActive(item.href)
							? 'bg-purple/8 text-purple border-l-[3px] border-purple'
							: 'text-text-secondary hover:text-text-primary hover:bg-black/5'}">
					<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d={item.icon} />
					</svg>
					{#if !collapsed}<span>{item.label}</span>{/if}
				</a>
			{/each}
		</div>

		<!-- Formatos -->
		<div>
			{#if !collapsed}<p class="label-upper px-3 mb-2">Formatos</p>{/if}
			{#each formatItems as item}
				{#if item.disabled}
					<div class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-text-muted opacity-50 mb-0.5">
						<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d={item.icon} />
						</svg>
						{#if !collapsed}
							<span>{item.label}</span>
							{#if item.badge}
								<span class="ml-auto text-[10px] px-1.5 py-0.5 rounded-full bg-purple/8 text-purple-soft border border-purple/20">{item.badge}</span>
							{/if}
						{/if}
					</div>
				{:else}
					<a href={item.href}
						class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all no-underline mb-0.5
							text-text-secondary hover:text-text-primary hover:bg-black/5">
						<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d={item.icon} />
						</svg>
						{#if !collapsed}<span>{item.label}</span>{/if}
					</a>
				{/if}
			{/each}
		</div>

		<!-- Sistema -->
		<div>
			{#if !collapsed}<p class="label-upper px-3 mb-2">Sistema</p>{/if}
			{#each systemItems as item}
				<a href={item.href}
					class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all no-underline mb-0.5
						{isActive(item.href)
							? 'bg-purple/8 text-purple border-l-[3px] border-purple'
							: 'text-text-secondary hover:text-text-primary hover:bg-black/5'}">
					<svg class="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d={item.icon} />
					</svg>
					{#if !collapsed}<span>{item.label}</span>{/if}
				</a>
			{/each}
		</div>

	</nav>

	<!-- Footer -->
	<div class="px-4 py-3 border-t border-steel-3/10 flex items-center justify-between">
		{#if !collapsed}
			<span class="text-[10px] text-text-muted font-mono">v3.0</span>
		{/if}
		<button onclick={onToggle} class="p-1.5 rounded-lg text-text-muted hover:text-text-primary hover:bg-black/5 transition-all cursor-pointer">
			<svg class="w-4 h-4 transition-transform {collapsed ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
			</svg>
		</button>
	</div>
</aside>
