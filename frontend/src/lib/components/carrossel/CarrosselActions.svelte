<script lang="ts">
	interface Props {
		modoEdicao: boolean;
		gerandoImagens: boolean;
		salvandoDrive: boolean;
		onToggleEdicao: () => void;
		onGerarImagens: () => void;
		onExportarPdf: () => void;
		onSalvarDrive: () => void;
	}

	let {
		modoEdicao,
		gerandoImagens,
		salvandoDrive,
		onToggleEdicao,
		onGerarImagens,
		onExportarPdf,
		onSalvarDrive
	}: Props = $props();
</script>

<div class="flex flex-wrap gap-2">
	<button
		onclick={onToggleEdicao}
		class="px-5 py-2.5 rounded-full text-sm font-medium transition-all cursor-pointer
			{modoEdicao ? 'bg-steel-6 text-white' : 'border border-steel-3/30 text-steel-3 hover:bg-steel-0'}"
	>
		{modoEdicao ? 'Visualizar' : 'Editar slides'}
	</button>
	<button onclick={onGerarImagens} disabled={gerandoImagens}
		class="px-5 py-2.5 rounded-full text-sm font-medium text-white cursor-pointer
			bg-gradient-to-r from-steel-4 via-steel-3 to-steel-2
			hover:-translate-y-0.5 hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed">
		{gerandoImagens ? 'Gerando...' : 'Gerar Imagens'}
	</button>
	<button onclick={onExportarPdf}
		class="px-5 py-2.5 rounded-full text-sm font-medium border border-steel-3/30 text-steel-3 hover:bg-steel-0 transition-all cursor-pointer">
		Exportar PDF
	</button>
	<button onclick={onSalvarDrive} disabled={salvandoDrive}
		class="px-5 py-2.5 rounded-full text-sm font-medium border border-steel-3/30 text-steel-3 hover:bg-steel-0 transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed">
		{salvandoDrive ? 'Salvando...' : 'Salvar no Drive'}
	</button>
</div>
