<script lang="ts">
	import { ListarAnunciosFiltroDTO } from '$lib/dtos/ListarAnunciosFiltroDTO';
	import Button from '$lib/components/ui/Button.svelte';

	interface Props {
		filtro: ListarAnunciosFiltroDTO;
		onChange: (filtro: ListarAnunciosFiltroDTO) => void;
	}
	let { filtro, onChange }: Props = $props();

	// Estado local inicializado a partir do filtro recebido.
	// Svelte 5 warning "state_referenced_locally" e aceitavel aqui — queremos inicializar uma vez
	// e que o usuario digite livremente sem reset.
	let busca = $state<string>('');
	let status = $state<any>('todos');
	let etapa_funil = $state<any>('todas');
	let data_inicio = $state('');
	let data_fim = $state('');
	let incluir_excluidos = $state(false);

	// Sincroniza na primeira montagem (e quando store reseta vindo de fora)
	let ultimoFiltroAplicado = $state('');
	$effect(() => {
		const key = JSON.stringify(filtro.toPayload());
		if (key !== ultimoFiltroAplicado) {
			ultimoFiltroAplicado = key;
			busca = filtro.busca;
			status = filtro.status;
			etapa_funil = filtro.etapa_funil;
			data_inicio = filtro.data_inicio;
			data_fim = filtro.data_fim;
			incluir_excluidos = filtro.incluir_excluidos;
		}
	});

	// Debounce simples no campo de busca
	let timer: ReturnType<typeof setTimeout> | null = null;

	function aplicar(imediato = false) {
		if (timer) clearTimeout(timer);
		const novo = new ListarAnunciosFiltroDTO({ busca, status, etapa_funil, data_inicio, data_fim, incluir_excluidos });
		if (imediato) {
			onChange(novo);
		} else {
			timer = setTimeout(() => onChange(novo), 250);
		}
	}

	function limpar() {
		busca = '';
		status = 'todos';
		etapa_funil = 'todas';
		data_inicio = '';
		data_fim = '';
		incluir_excluidos = false;
		onChange(new ListarAnunciosFiltroDTO({}));
	}

	const temFiltroAtivo = $derived(
		busca !== '' || status !== 'todos' || etapa_funil !== 'todas' || data_inicio !== '' || data_fim !== '' || incluir_excluidos
	);
</script>

<div class="bg-bg-card rounded-xl border border-border-default p-4 flex flex-wrap items-end gap-3">
	<div class="flex-1 min-w-[200px]">
		<label class="text-[10px] font-mono uppercase tracking-wide text-text-muted block mb-1" for="f-busca">Buscar</label>
		<div class="relative">
			<svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
			</svg>
			<input
				id="f-busca"
				type="text"
				bind:value={busca}
				oninput={() => aplicar()}
				placeholder="Titulo ou headline..."
				class="w-full pl-9 pr-3 py-2 rounded-lg bg-bg-input border border-border-default text-sm text-text-primary focus:outline-none focus:border-purple transition-colors"
			/>
		</div>
	</div>

	<div class="min-w-[140px]">
		<label class="text-[10px] font-mono uppercase tracking-wide text-text-muted block mb-1" for="f-status">Status</label>
		<select
			id="f-status"
			bind:value={status}
			onchange={() => aplicar(true)}
			class="w-full px-3 py-2 rounded-lg bg-bg-input border border-border-default text-sm text-text-primary focus:outline-none focus:border-purple transition-colors"
		>
			<option value="todos">Todos</option>
			<option value="rascunho">Rascunho</option>
			<option value="em_andamento">Em andamento</option>
			<option value="concluido">Concluido</option>
			<option value="erro">Erro</option>
			<option value="cancelado">Cancelado</option>
		</select>
	</div>

	<div class="min-w-[140px]">
		<label class="text-[10px] font-mono uppercase tracking-wide text-text-muted block mb-1" for="f-funil">Funil</label>
		<select
			id="f-funil"
			bind:value={etapa_funil}
			onchange={() => aplicar(true)}
			class="w-full px-3 py-2 rounded-lg bg-bg-input border border-border-default text-sm text-text-primary focus:outline-none focus:border-purple transition-colors"
		>
			<option value="todas">Todas</option>
			<option value="topo">Topo</option>
			<option value="meio">Meio</option>
			<option value="fundo">Fundo</option>
			<option value="avulso">Avulso</option>
		</select>
	</div>

	<div>
		<label class="text-[10px] font-mono uppercase tracking-wide text-text-muted block mb-1" for="f-di">De</label>
		<input
			id="f-di"
			type="date"
			bind:value={data_inicio}
			onchange={() => aplicar(true)}
			class="px-3 py-2 rounded-lg bg-bg-input border border-border-default text-sm text-text-primary focus:outline-none focus:border-purple transition-colors"
		/>
	</div>

	<div>
		<label class="text-[10px] font-mono uppercase tracking-wide text-text-muted block mb-1" for="f-df">Ate</label>
		<input
			id="f-df"
			type="date"
			bind:value={data_fim}
			onchange={() => aplicar(true)}
			class="px-3 py-2 rounded-lg bg-bg-input border border-border-default text-sm text-text-primary focus:outline-none focus:border-purple transition-colors"
		/>
	</div>

	<label class="inline-flex items-center gap-2 cursor-pointer select-none text-sm text-text-secondary mb-1">
		<input
			type="checkbox"
			bind:checked={incluir_excluidos}
			onchange={() => aplicar(true)}
			class="w-4 h-4 rounded border-border-default text-purple focus:ring-purple/40"
		/>
		Incluir excluidos
	</label>

	{#if temFiltroAtivo}
		<Button variant="ghost" size="sm" onclick={limpar}>
			Limpar filtros
		</Button>
	{/if}
</div>
