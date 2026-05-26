<script lang="ts">
	import type { UserDTO } from '$lib/dtos/UserDTO';
	import type { ColumnData } from '$lib/dtos/BoardDTO';

	let { users, columns, searchQuery, filterResponsavel, filterPrioridade, filterColuna,
		onSearchChange, onResponsavelChange, onPrioridadeChange, onColunaChange, onClear, hasFilters
	}: {
		users: UserDTO[];
		columns: ColumnData[];
		searchQuery: string;
		filterResponsavel: string;
		filterPrioridade: string;
		filterColuna: string;
		onSearchChange: (v: string) => void;
		onResponsavelChange: (v: string) => void;
		onPrioridadeChange: (v: string) => void;
		onColunaChange: (v: string) => void;
		onClear: () => void;
		hasFilters: boolean;
	} = $props();
</script>

<div class="flex flex-wrap items-center gap-3">
	<!-- Search -->
	<div class="relative">
		<svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
		</svg>
		<input
			type="text"
			value={searchQuery}
			oninput={(e) => onSearchChange((e.target as HTMLInputElement).value)}
			placeholder="Buscar por titulo..."
			class="w-64 pl-9 pr-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
				focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all placeholder:text-text-muted"
		/>
	</div>

	<!-- Responsavel -->
	<select
		value={filterResponsavel}
		onchange={(e) => onResponsavelChange((e.target as HTMLSelectElement).value)}
		class="px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-secondary text-sm outline-none cursor-pointer"
	>
		<option value="">Responsavel</option>
		{#each users as user}
			<option value={user.id}>{user.name}</option>
		{/each}
	</select>

	<!-- Prioridade -->
	<select
		value={filterPrioridade}
		onchange={(e) => onPrioridadeChange((e.target as HTMLSelectElement).value)}
		class="px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-secondary text-sm outline-none cursor-pointer"
	>
		<option value="">Prioridade</option>
		<option value="alta">Alta</option>
		<option value="media">Media</option>
		<option value="baixa">Baixa</option>
	</select>

	<!-- Coluna -->
	<select
		value={filterColuna}
		onchange={(e) => onColunaChange((e.target as HTMLSelectElement).value)}
		class="px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-secondary text-sm outline-none cursor-pointer"
	>
		<option value="">Coluna</option>
		{#each columns as col}
			<option value={col.id}>{col.name}</option>
		{/each}
	</select>

	<!-- Clear -->
	{#if hasFilters}
		<button
			onclick={onClear}
			class="px-3 py-2 rounded-lg border border-border-default text-sm text-text-secondary
				hover:bg-bg-elevated transition-all cursor-pointer"
		>
			Limpar filtros
		</button>
	{/if}
</div>
