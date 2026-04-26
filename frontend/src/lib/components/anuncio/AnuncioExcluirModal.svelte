<script lang="ts">
	import type { AnuncioDTO } from '$lib/dtos/AnuncioDTO';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		anuncio: AnuncioDTO | null;
		aberto: boolean;
		excluindo?: boolean;
		erro?: string;
		onConfirmar: () => void;
		onCancelar: () => void;
	}
	let { anuncio, aberto, excluindo = false, erro = '', onConfirmar, onCancelar }: Props = $props();
</script>

<Modal open={aberto} size="sm" onclose={onCancelar}>
	<div class="text-center py-2">
		<div class="w-12 h-12 rounded-full bg-red/10 text-red mx-auto flex items-center justify-center mb-4">
			<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
			</svg>
		</div>

		<h3 class="text-lg font-semibold text-text-primary mb-2">Excluir anuncio?</h3>

		<p class="text-sm text-text-secondary mb-4">
			<span class="font-medium text-text-primary">"{anuncio?.titulo ?? ''}"</span>
			sera removido do modulo Anuncios.
		</p>

		<ul class="text-xs text-text-muted space-y-1 mb-4 text-left max-w-xs mx-auto">
			<li class="flex items-start gap-2">
				<span class="text-text-muted">•</span>
				<span>Os arquivos no Google Drive permanecem intactos</span>
			</li>
			<li class="flex items-start gap-2">
				<span class="text-text-muted">•</span>
				<span>O anuncio pode ser recuperado via filtro "Incluir excluidos"</span>
			</li>
		</ul>

		{#if erro}
			<div class="mb-4 p-2 rounded-lg bg-red/9 text-red text-xs border border-red/15">
				{erro}
			</div>
		{/if}

		<div class="flex items-center justify-center gap-3 mt-6">
			<Button variant="ghost" size="md" onclick={onCancelar} disabled={excluindo}>
				Cancelar
			</Button>
			<Button variant="danger" size="md" onclick={onConfirmar} loading={excluindo}>
				Sim, excluir
			</Button>
		</div>
	</div>
</Modal>
