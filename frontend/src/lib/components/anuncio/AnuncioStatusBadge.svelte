<script lang="ts">
	import type { AnuncioStatus } from '$lib/dtos/AnuncioDTO';

	interface Props {
		status: AnuncioStatus;
		size?: 'sm' | 'md';
	}

	let { status, size = 'md' }: Props = $props();

	const cfg = $derived.by(() => {
		const base: Record<AnuncioStatus, { label: string; classes: string; iconPath: string }> = {
			rascunho: {
				label: 'RASCUNHO',
				classes: 'bg-bg-elevated text-text-secondary border-border-default',
				iconPath: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
			},
			em_andamento: {
				label: 'EM ANDAMENTO',
				classes: 'bg-purple/8 text-purple border-purple/20',
				iconPath: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15'
			},
			concluido: {
				label: 'CONCLUIDO',
				classes: 'bg-green/10 text-green border-green/25',
				iconPath: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
			},
			erro: {
				label: 'ERRO',
				classes: 'bg-red/9 text-red border-red/15',
				iconPath: 'M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z'
			},
			cancelado: {
				label: 'CANCELADO',
				classes: 'bg-bg-elevated text-text-muted border-border-default opacity-70',
				iconPath: 'M5 8a2 2 0 012-2h10a2 2 0 012 2v10a2 2 0 01-2 2H7a2 2 0 01-2-2V8zM9 12h6'
			}
		};
		return base[status];
	});
	const sizeClasses = $derived(size === 'sm' ? 'px-2 py-0.5 text-[10px]' : 'px-3 py-1 text-xs');
	const iconSize = $derived(size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5');
</script>

<span class="inline-flex items-center gap-1.5 rounded-full font-mono uppercase tracking-wide border {cfg.classes} {sizeClasses}">
	<svg
		class="{iconSize} shrink-0 {status === 'em_andamento' ? 'animate-spin' : ''}"
		fill="none"
		stroke="currentColor"
		viewBox="0 0 24 24"
	>
		<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={cfg.iconPath} />
	</svg>
	{cfg.label}
</span>
