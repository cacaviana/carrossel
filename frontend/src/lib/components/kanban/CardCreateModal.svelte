<script lang="ts">
	import { disciplinas } from '$lib/data/disciplinas';
	import type { UserDTO } from '$lib/dtos/UserDTO';

	let { open = false, users = [], onClose, onCreate }: {
		open: boolean;
		users: UserDTO[];
		onClose: () => void;
		onCreate: (data: Record<string, any>) => void;
	} = $props();

	let title = $state('');
	let copyText = $state('');
	let disciplina = $state('');
	let tecnologia = $state('');
	let priority = $state('media');
	let deadline = $state('');
	let responsavel = $state('');
	let creating = $state(false);
	let error = $state('');

	const disciplinaAtual = $derived(disciplinas.find(d => d.id === disciplina));
	const techs = $derived(disciplinaAtual?.techs ?? []);
	const canCreate = $derived(title.trim().length >= 3 && !creating);

	async function handleCreate() {
		if (!canCreate) return;
		creating = true;
		error = '';
		try {
			await onCreate({
				title: title.trim(),
				copy_text: copyText,
				disciplina,
				tecnologia,
				priority,
				deadline,
				assigned_user_ids: responsavel ? [responsavel] : []
			});
			// Reset
			title = '';
			copyText = '';
			disciplina = '';
			tecnologia = '';
			priority = 'media';
			deadline = '';
			responsavel = '';
		} catch (e) {
			error = 'Erro ao criar carrossel. Tente novamente.';
		} finally {
			creating = false;
		}
	}
</script>

{#if open}
	<div class="fixed inset-0 z-50 flex items-center justify-center">
		<!-- Overlay -->
		<button class="absolute inset-0 bg-black/60" onclick={onClose} tabindex={-1}></button>

		<!-- Modal -->
		<div class="relative w-full max-w-lg mx-4 bg-bg-card rounded-2xl border border-border-default shadow-2xl animate-fade-up">
			<!-- Header -->
			<div class="flex items-center justify-between px-6 py-4 border-b border-border-default">
				<h2 class="text-lg font-semibold text-text-primary">Novo carrossel</h2>
				<button onclick={onClose} class="p-1 rounded-lg text-text-muted hover:text-text-primary hover:bg-black/5 transition-all cursor-pointer">
					<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
			</div>

			<!-- Body -->
			<div class="px-6 py-5 space-y-4 max-h-[60vh] overflow-y-auto scrollbar-thin">
				<div>
					<label class="block text-xs font-medium text-text-secondary mb-1.5">Titulo *</label>
					<input
						type="text"
						bind:value={title}
						placeholder="Ex: Transfer Learning na pratica com PyTorch"
						disabled={creating}
						class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
							focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all placeholder:text-text-muted"
					/>
					{#if title.length > 0 && title.trim().length < 3}
						<p class="text-xs text-red mt-1">Titulo deve ter no minimo 3 caracteres.</p>
					{/if}
				</div>

				<div>
					<label class="block text-xs font-medium text-text-secondary mb-1.5">Copy text</label>
					<textarea
						bind:value={copyText}
						placeholder="Texto do conteudo (opcional)"
						rows={3}
						disabled={creating}
						class="w-full px-4 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
							focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all resize-y placeholder:text-text-muted"
					></textarea>
				</div>

				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="block text-xs font-medium text-text-secondary mb-1.5">Disciplina</label>
						<select
							bind:value={disciplina}
							disabled={creating}
							class="w-full px-3 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-secondary text-sm outline-none cursor-pointer"
						>
							<option value="">Selecione</option>
							{#each disciplinas as d}
								<option value={d.id}>{d.id} - {d.nome}</option>
							{/each}
						</select>
					</div>

					<div>
						<label class="block text-xs font-medium text-text-secondary mb-1.5">Tecnologia</label>
						<select
							bind:value={tecnologia}
							disabled={creating || !disciplina}
							class="w-full px-3 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-secondary text-sm outline-none cursor-pointer
								disabled:opacity-50"
						>
							<option value="">Selecione</option>
							{#each techs as t}
								<option value={t}>{t}</option>
							{/each}
						</select>
					</div>
				</div>

				<div class="grid grid-cols-3 gap-4">
					<div>
						<label class="block text-xs font-medium text-text-secondary mb-1.5">Prioridade</label>
						<select
							bind:value={priority}
							disabled={creating}
							class="w-full px-3 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-secondary text-sm outline-none cursor-pointer"
						>
							<option value="alta">Alta</option>
							<option value="media">Media</option>
							<option value="baixa">Baixa</option>
						</select>
					</div>

					<div>
						<label class="block text-xs font-medium text-text-secondary mb-1.5">Prazo de publicacao</label>
						<input
							type="date"
							bind:value={deadline}
							disabled={creating}
							class="w-full px-3 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-secondary text-sm outline-none
								focus:border-purple focus:ring-3 focus:ring-purple/12 transition-all"
						/>
					</div>

					<div>
						<label class="block text-xs font-medium text-text-secondary mb-1.5">Responsavel</label>
						<select
							bind:value={responsavel}
							disabled={creating}
							class="w-full px-3 py-2.5 rounded-lg border border-border-default bg-bg-input text-text-secondary text-sm outline-none cursor-pointer"
						>
							<option value="">Nenhum</option>
							{#each users as u}
								<option value={u.id}>{u.name}</option>
							{/each}
						</select>
					</div>
				</div>

				{#if error}
					<div class="p-3 rounded-lg bg-red/10 border border-red/20 text-sm text-red">
						{error}
					</div>
				{/if}
			</div>

			<!-- Footer -->
			<div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-border-default">
				<button
					onclick={onClose}
					disabled={creating}
					class="px-4 py-2 rounded-lg border border-border-default text-sm font-medium text-text-secondary
						hover:bg-bg-elevated transition-all cursor-pointer disabled:opacity-50"
				>
					Cancelar
				</button>
				<button
					onclick={handleCreate}
					disabled={!canCreate}
					class="px-4 py-2 rounded-lg font-medium text-sm text-white
						bg-purple hover:opacity-90 transition-all cursor-pointer
						disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{#if creating}
						<span class="inline-flex items-center gap-2">
							<span class="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
							Criando...
						</span>
					{:else}
						Criar
					{/if}
				</button>
			</div>
		</div>
	</div>
{/if}
