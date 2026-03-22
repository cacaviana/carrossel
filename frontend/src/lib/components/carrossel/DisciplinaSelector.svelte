<script lang="ts">
	import { disciplinas } from '$lib/data/disciplinas';

	interface Props {
		disciplinaSelecionada: string;
		techSelecionada: string;
		temaCustom: string;
		onSelectDisciplina: (id: string) => void;
		onSelectTech: (tech: string) => void;
		onChangeTema: (tema: string) => void;
	}

	let {
		disciplinaSelecionada,
		techSelecionada,
		temaCustom,
		onSelectDisciplina,
		onSelectTech,
		onChangeTema
	}: Props = $props();

	const disciplinaAtual = $derived(disciplinas.find((d) => d.id === disciplinaSelecionada));
</script>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
	{#each disciplinas as disc}
		<button
			onclick={() => { onSelectDisciplina(disc.id); }}
			class="text-left p-5 rounded-2xl border transition-all duration-300 cursor-pointer
				{disciplinaSelecionada === disc.id
					? 'bg-steel-6 text-white border-steel-3 shadow-lg scale-[1.02]'
					: 'bg-bg-card border-teal-4/30 hover:border-steel-3/40 hover:-translate-y-1 hover:shadow-md'}"
		>
			<div class="flex items-center gap-3 mb-2">
				<span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium
					{disciplinaSelecionada === disc.id ? 'bg-steel-3 text-white' : 'bg-steel-0 text-steel-3'}">
					{disc.id}
				</span>
				<h3 class="font-semibold text-sm">{disc.nome}</h3>
			</div>
			<p class="text-xs {disciplinaSelecionada === disc.id ? 'text-teal-4' : 'text-steel-4'} font-light">
				{disc.descricao}
			</p>
		</button>
	{/each}
</div>

{#if disciplinaAtual}
	<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-6 animate-fade-up">
		<h3 class="font-semibold text-steel-6 mb-4">{disciplinaAtual.id} — {disciplinaAtual.nome}</h3>

		<div class="mb-4">
			<label class="block text-sm font-medium text-steel-5 mb-2">Tecnologia</label>
			<div class="flex flex-wrap gap-2">
				{#each disciplinaAtual.techs as tech}
					<button
						onclick={() => onSelectTech(tech)}
						class="px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 cursor-pointer
							{techSelecionada === tech ? 'bg-steel-3 text-white shadow-md' : 'bg-teal-3 text-steel-5 hover:bg-teal-4'}"
					>
						{tech}
					</button>
				{/each}
			</div>
		</div>

		<div>
			<label for="tema" class="block text-sm font-medium text-steel-5 mb-2">Tema customizado (opcional)</label>
			<input id="tema" type="text" value={temaCustom}
				oninput={(e) => onChangeTema((e.target as HTMLInputElement).value)}
				placeholder="Ex: Como reduzir custo de inferencia com quantizacao..."
				class="w-full px-4 py-3 rounded-xl border border-teal-4/30 bg-bg-card text-steel-6 text-sm
					focus:border-steel-3 focus:ring-2 focus:ring-steel-3/20 outline-none transition-all" />
		</div>
	</div>
{/if}
