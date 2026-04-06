<script lang="ts">
	let { pipelineId, aprovando, rejeitando, onaprovar, onrejeitar, aprovarLabel = 'Aprovar e Continuar', aprovandoLabel = 'Aprovando...', className = '' }: {
		pipelineId: string;
		aprovando: boolean;
		rejeitando: boolean;
		onaprovar: () => void;
		onrejeitar: () => void;
		aprovarLabel?: string;
		aprovandoLabel?: string;
		className?: string;
	} = $props();
</script>

<div class="flex items-center justify-end gap-3 sticky bottom-4 {className}">
	<a href="/pipeline/{pipelineId}" class="px-4 py-2.5 rounded-full text-sm text-text-secondary hover:text-text-primary transition-all no-underline cursor-pointer">Voltar</a>
	<button onclick={onrejeitar}
		class="px-5 py-2.5 rounded-full text-sm font-medium text-red bg-red/9 border border-red/15 hover:bg-red/15 transition-all cursor-pointer">
		Rejeitar e Regerar
	</button>
	<button onclick={onaprovar} disabled={aprovando}
		class="px-6 py-2.5 rounded-full text-sm font-medium text-bg-global bg-purple hover:opacity-90 transition-all cursor-pointer disabled:opacity-50">
		{aprovando ? aprovandoLabel : aprovarLabel}
	</button>
</div>
