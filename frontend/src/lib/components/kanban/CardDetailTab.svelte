<script lang="ts">
	import type { CardDTO } from '$lib/dtos/CardDTO';
	import type { UserDTO } from '$lib/dtos/UserDTO';
	import type { ColumnData } from '$lib/dtos/BoardDTO';
	import { formatRelativeDate, formatAbsoluteDate } from '$lib/utils/date';

	let { card, users, columns }: {
		card: CardDTO;
		users: UserDTO[];
		columns: ColumnData[];
	} = $props();

	const assignedUsers = $derived(users.filter(u => card.assigned_user_ids.includes(u.id)));
	const createdByUser = $derived(users.find(u => u.id === card.created_by));
	const currentColumn = $derived(columns.find(c => c.id === card.column_id));
</script>

<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
	<!-- Left column: editable fields -->
	<div class="space-y-4">
		<div>
			<label class="label-upper mb-1.5 block">Titulo</label>
			<p class="text-sm text-text-primary font-medium">{card.title}</p>
		</div>

		<div>
			<label class="label-upper mb-1.5 block">Copy text</label>
			<p class="text-sm text-text-secondary whitespace-pre-wrap">{card.copy_text || '(vazio)'}</p>
		</div>

		<div class="grid grid-cols-2 gap-4">
			<div>
				<label class="label-upper mb-1.5 block">Disciplina</label>
				<p class="text-sm text-text-secondary">{card.disciplina || '-'}</p>
			</div>
			<div>
				<label class="label-upper mb-1.5 block">Tecnologia</label>
				<p class="text-sm text-text-secondary">{card.tecnologia || '-'}</p>
			</div>
		</div>

		<div>
			<label class="label-upper mb-1.5 block">Prioridade</label>
			<p class="text-sm text-text-secondary">{card.priorityLabel}</p>
		</div>

		<div>
			<label class="label-upper mb-1.5 block">Responsaveis</label>
			{#if assignedUsers.length > 0}
				<div class="flex flex-wrap gap-2">
					{#each assignedUsers as user}
						<div class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-bg-elevated border border-border-default">
							<div class="w-5 h-5 rounded-full bg-steel-3/20 text-[8px] font-bold text-steel-3 flex items-center justify-center">
								{user.iniciais}
							</div>
							<span class="text-xs text-text-secondary">{user.name}</span>
						</div>
					{/each}
				</div>
			{:else}
				<p class="text-sm text-text-muted">Nao atribuido</p>
			{/if}
		</div>
	</div>

	<!-- Right column: readonly fields -->
	<div class="space-y-4">
		<div>
			<label class="label-upper mb-1.5 block">Coluna atual</label>
			<p class="text-sm text-text-secondary">{currentColumn?.name ?? '-'}</p>
		</div>

		<div>
			<label class="label-upper mb-1.5 block">Criado por</label>
			<p class="text-sm text-text-secondary">{createdByUser?.name ?? '-'}</p>
		</div>

		<div>
			<label class="label-upper mb-1.5 block">Criado em</label>
			<p class="text-sm text-text-secondary" title={formatAbsoluteDate(card.created_at)}>
				{formatRelativeDate(card.created_at)}
			</p>
		</div>

		{#if card.updated_at}
			<div>
				<label class="label-upper mb-1.5 block">Atualizado em</label>
				<p class="text-sm text-text-secondary" title={formatAbsoluteDate(card.updated_at)}>
					{formatRelativeDate(card.updated_at)}
				</p>
			</div>
		{/if}

		{#if card.hasPipeline}
			<div>
				<label class="label-upper mb-1.5 block">Pipeline</label>
				<p class="text-sm text-purple">{card.pipeline_id}</p>
			</div>
		{/if}

		{#if card.hasDriveLink}
			<div>
				<label class="label-upper mb-1.5 block">Google Drive</label>
				<a href={card.drive_link} target="_blank" rel="noopener noreferrer"
					class="text-sm text-purple hover:underline inline-flex items-center gap-1">
					{card.drive_folder_name || 'Abrir no Drive'}
					<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
					</svg>
				</a>
			</div>
		{/if}

		{#if card.hasPdf}
			<div>
				<label class="label-upper mb-1.5 block">PDF</label>
				<p class="text-sm text-purple">{card.pdf_url}</p>
			</div>
		{/if}
	</div>
</div>

<!-- Images gallery -->
{#if card.hasImages}
	<div class="mt-6">
		<label class="label-upper mb-2 block">Imagens ({card.image_urls.length})</label>
		<div class="grid grid-cols-4 gap-2">
			{#each card.image_urls as url}
				<div class="w-20 h-20 rounded-lg bg-bg-elevated border border-border-default flex items-center justify-center">
					<svg class="w-6 h-6 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
					</svg>
				</div>
			{/each}
		</div>
	</div>
{/if}
