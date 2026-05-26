<script lang="ts">
	interface Props {
		size?: 'sm' | 'md';
	}
	let { size = 'sm' }: Props = $props();
	const sizeClasses = $derived(size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-3 py-1 text-xs');
</script>

<!-- Badge ciano especifico pra formato "Anuncio" (decisao do Designer) -->
<span class="inline-flex items-center gap-1 rounded-full font-mono uppercase tracking-wide border bg-cyan-400/10 text-cyan-600 border-cyan-400/30 {sizeClasses}">
	<svg class="w-3 h-3 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
		<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z" />
	</svg>
	Anuncio
</span>
