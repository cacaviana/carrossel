<script lang="ts">
	import type { CommentDTO } from '$lib/dtos/CommentDTO';
	import { formatRelativeDate, formatAbsoluteDate } from '$lib/utils/date';

	let { comment, currentUserId, isAdmin, onDelete }: {
		comment: CommentDTO;
		currentUserId: string;
		isAdmin: boolean;
		onDelete: () => void;
	} = $props();

	let confirmDelete = $state(false);

	const canDelete = $derived(comment.isOwnedBy(currentUserId) || isAdmin);
</script>

<div class="flex gap-3 p-3 rounded-lg hover:bg-bg-elevated/50 transition-all">
	<!-- Avatar -->
	<div class="w-8 h-8 rounded-full bg-steel-3/20 text-[10px] font-bold text-steel-3 flex items-center justify-center shrink-0">
		{comment.userIniciais}
	</div>

	<div class="flex-1 min-w-0">
		<div class="flex items-center gap-2 mb-1">
			<span class="text-sm font-medium text-text-primary">{comment.user_name}</span>
			<span class="text-[11px] text-text-muted" title={formatAbsoluteDate(comment.created_at)}>
				{formatRelativeDate(comment.created_at)}
			</span>
			{#if comment.isEdited}
				<span class="text-[10px] text-text-muted">(editado)</span>
			{/if}
		</div>
		<p class="text-sm text-text-secondary">{comment.text}</p>

		<!-- Actions -->
		{#if canDelete}
			<div class="flex items-center gap-2 mt-1.5">
				{#if confirmDelete}
					<span class="text-[11px] text-red">Excluir?</span>
					<button onclick={onDelete} class="text-[11px] text-red font-medium hover:underline cursor-pointer">Sim</button>
					<button onclick={() => confirmDelete = false} class="text-[11px] text-text-muted hover:underline cursor-pointer">Nao</button>
				{:else}
					<button onclick={() => confirmDelete = true}
						class="text-[11px] text-text-muted hover:text-red transition-colors cursor-pointer">
						Excluir
					</button>
				{/if}
			</div>
		{/if}
	</div>
</div>
