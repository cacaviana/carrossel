<script lang="ts">
	import '../app.css';

	let { children } = $props();
	let menuAberto = $state(false);

	const navItems = [
		{ href: '/', label: 'Home' },
		{ href: '/carrossel', label: 'Carrossel' },
		{ href: '/historico', label: 'Historico' },
		{ href: '/agentes', label: 'Agentes' },
		{ href: '/configuracoes', label: 'Config' }
	];
</script>

<div class="min-h-screen flex flex-col">
	<header class="bg-steel-6 text-white px-4 sm:px-6 py-3 sm:py-4 shadow-lg">
		<div class="max-w-7xl mx-auto flex items-center justify-between">
			<a href="/" class="flex items-center gap-2 sm:gap-3 no-underline">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-xl sm:rounded-2xl bg-gradient-to-br from-steel-3 to-steel-2 flex items-center justify-center text-white font-bold text-sm sm:text-lg">
					C
				</div>
				<div>
					<h1 class="text-base sm:text-lg font-semibold tracking-tight text-white">Carrossel System</h1>
					<p class="text-[10px] sm:text-xs text-steel-2 font-light">IT Valley School</p>
				</div>
			</a>

			<!-- Hamburger mobile -->
			<button
				onclick={() => menuAberto = !menuAberto}
				class="sm:hidden p-2 rounded-lg hover:bg-steel-5 transition-all cursor-pointer"
				aria-label="Menu"
			>
				<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					{#if menuAberto}
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					{:else}
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
					{/if}
				</svg>
			</button>

			<!-- Nav desktop -->
			<nav class="hidden sm:flex gap-1">
				{#each navItems as item}
					<a
						href={item.href}
						class="px-4 py-2 rounded-full text-sm font-medium text-teal-4 hover:bg-steel-5 hover:text-white transition-all duration-200 no-underline"
					>
						{item.label}
					</a>
				{/each}
			</nav>
		</div>

		<!-- Nav mobile -->
		{#if menuAberto}
			<nav class="sm:hidden mt-3 pt-3 border-t border-steel-5 flex flex-col gap-1">
				{#each navItems as item}
					<a
						href={item.href}
						onclick={() => menuAberto = false}
						class="px-4 py-2.5 rounded-xl text-sm font-medium text-teal-4 hover:bg-steel-5 hover:text-white transition-all duration-200 no-underline"
					>
						{item.label}
					</a>
				{/each}
			</nav>
		{/if}
	</header>

	<main class="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 py-6 sm:py-8">
		{@render children()}
	</main>

	<footer class="bg-steel-6 text-teal-5 text-center py-4 text-xs font-light px-4">
		IT Valley School — Pos IA & ML — Carrossel System v1.0
	</footer>
</div>
