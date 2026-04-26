<script lang="ts">
	import type { AnuncioDTO, EtapaFunil } from '$lib/dtos/AnuncioDTO';
	import Button from '$lib/components/ui/Button.svelte';
	import AnuncioStatusBadge from './AnuncioStatusBadge.svelte';
	import AnuncioFormatoBadge from './AnuncioFormatoBadge.svelte';

	interface Props {
		anuncio: AnuncioDTO;
		onClick: (id: string) => void;
		onEditar: (id: string) => void;
		onExcluir: (anuncio: AnuncioDTO) => void;
		onAbrirDrive: (url: string) => void;
	}
	let { anuncio, onClick, onEditar, onExcluir, onAbrirDrive }: Props = $props();

	const etapaVariant: Record<EtapaFunil, string> = {
		topo: 'bg-purple/8 text-purple border-purple/20',
		meio: 'bg-green/10 text-green border-green/25',
		fundo: 'bg-amber/10 text-amber border-amber/25',
		avulso: 'bg-bg-elevated text-text-secondary border-border-default'
	};
</script>

<div
	class="group bg-bg-card rounded-xl border border-border-default transition-all cursor-pointer
		hover:-translate-y-0.5 hover:shadow-md hover:border-purple/30
		{anuncio.isDeletado ? 'opacity-60' : ''}"
	onclick={() => onClick(anuncio.id)}
	onkeydown={(e) => { if (e.key === 'Enter') onClick(anuncio.id); }}
	role="button"
	tabindex="0"
	data-testid="anuncio-card"
>
	<!-- Header -->
	<div class="p-4 pb-3 flex items-center justify-between gap-2">
		<div class="flex items-center gap-2 flex-wrap">
			<AnuncioFormatoBadge size="sm" />
			<AnuncioStatusBadge status={anuncio.status} size="sm" />
		</div>
		<span class="text-[10px] font-mono text-text-muted shrink-0">{anuncio.criadoHa}</span>
	</div>

	<!-- Thumbnail 1080x1350 (aspect 4:5) -->
	<div class="mx-4 mb-3 aspect-[4/5] rounded-lg overflow-hidden bg-bg-code border border-border-default">
		{#if anuncio.thumbnailUrl}
			<img src={anuncio.thumbnailUrl} alt={anuncio.titulo} class="w-full h-full object-cover" />
		{:else}
			<div class="w-full h-full flex items-center justify-center text-text-muted/40">
				<svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
				</svg>
			</div>
		{/if}
	</div>

	<!-- Titulo + headline -->
	<div class="px-4 pb-3">
		<p class="text-sm font-medium text-text-primary line-clamp-1">{anuncio.titulo}</p>
		<p class="text-xs text-text-secondary mt-1 line-clamp-2 leading-snug">
			{anuncio.copy.headline}
		</p>
		{#if anuncio.copy.cta}
			<span class="inline-flex items-center gap-1 mt-2 px-2 py-0.5 rounded-full text-[10px] font-mono uppercase tracking-wide border bg-purple/8 text-purple border-purple/20">
				CTA: {anuncio.copy.cta}
			</span>
		{/if}
	</div>

	<!-- Meta badges -->
	<div class="px-4 pb-3 flex flex-wrap gap-2">
		<span class="inline-flex items-center rounded-full text-[10px] font-mono uppercase tracking-wide border px-2 py-0.5 {etapaVariant[anuncio.etapa_funil]}">
			Funil: {anuncio.etapaFunilLabel}
		</span>
	</div>

	<!-- Acoes -->
	<div class="border-t border-border-default px-3 py-2 flex items-center justify-between gap-2">
		<div class="flex items-center gap-1">
			<Button variant="ghost" size="sm" onclick={(e) => { e.stopPropagation(); onEditar(anuncio.id); }}>
				Editar
			</Button>
			{#if anuncio.hasDriveLink}
				<Button variant="ghost" size="sm" onclick={(e) => { e.stopPropagation(); onAbrirDrive(anuncio.drive_folder_link); }}>
					Drive
				</Button>
			{/if}
		</div>
		<Button variant="ghost" size="sm" onclick={(e) => { e.stopPropagation(); onExcluir(anuncio); }}>
			<span class="text-red">Excluir</span>
		</Button>
	</div>
</div>
