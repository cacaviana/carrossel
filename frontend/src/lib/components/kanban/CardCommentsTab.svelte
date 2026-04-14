<script lang="ts">
	import { onMount } from 'svelte';
	import { CommentService } from '$lib/services/CommentService';
	import type { CommentDTO } from '$lib/dtos/CommentDTO';
	import CommentItem from '$lib/components/kanban/CommentItem.svelte';
	import { getAuth } from '$lib/stores/auth.svelte';

	let { cardId }: { cardId: string } = $props();

	let comments = $state<CommentDTO[]>([]);
	let loading = $state(true);
	let error = $state('');
	let newComment = $state('');
	let sending = $state(false);

	const auth = getAuth();

	onMount(() => loadComments());

	async function loadComments() {
		loading = true;
		error = '';
		try {
			comments = await CommentService.listarPorCard(cardId);
		} catch {
			error = 'Erro ao carregar comentarios.';
		} finally {
			loading = false;
		}
	}

	async function sendComment() {
		if (!newComment.trim() || sending) return;
		sending = true;
		try {
			const comment = await CommentService.criar(cardId, newComment.trim());
			comments = [...comments, comment];
			newComment = '';
		} catch {
			error = 'Erro ao enviar comentario.';
		} finally {
			sending = false;
		}
	}

	async function deleteComment(commentId: string) {
		try {
			await CommentService.deletar(commentId);
			comments = comments.filter(c => c.id !== commentId);
		} catch {
			error = 'Erro ao excluir comentario.';
		}
	}
</script>

<div class="flex flex-col h-full">
	{#if loading}
		<div class="flex items-center justify-center py-12">
			<span class="w-6 h-6 border-2 border-purple/30 border-t-purple rounded-full animate-spin"></span>
		</div>
	{:else if error}
		<div class="text-center py-8">
			<p class="text-sm text-red mb-3">{error}</p>
			<button onclick={loadComments} class="text-sm text-purple hover:underline cursor-pointer">Tentar novamente</button>
		</div>
	{:else if comments.length === 0}
		<div class="text-center py-12">
			<svg class="w-12 h-12 mx-auto text-text-muted/30 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
			</svg>
			<p class="text-sm text-text-muted">Nenhum comentario ainda. Seja o primeiro a comentar.</p>
		</div>
	{:else}
		<div class="space-y-3 mb-4 max-h-[50vh] overflow-y-auto scrollbar-thin">
			{#each comments as comment (comment.id)}
				<CommentItem
					{comment}
					currentUserId={auth?.user_id ?? ''}
					isAdmin={auth?.isAdmin ?? false}
					onDelete={() => deleteComment(comment.id)}
				/>
			{/each}
		</div>
	{/if}

	<!-- New comment -->
	{#if auth?.canComment}
		<div class="mt-auto pt-4 border-t border-border-default">
			<textarea
				bind:value={newComment}
				placeholder="Escreva um comentario..."
				rows={2}
				disabled={sending}
				class="w-full px-3 py-2 rounded-lg border border-border-default bg-bg-input text-text-primary text-sm
					focus:border-purple focus:ring-3 focus:ring-purple/12 outline-none transition-all resize-y
					placeholder:text-text-muted disabled:opacity-50"
			></textarea>
			<div class="flex justify-end mt-2">
				<button
					onclick={sendComment}
					disabled={!newComment.trim() || sending}
					class="px-4 py-2 rounded-lg font-medium text-sm text-white
						bg-purple hover:opacity-90 transition-all cursor-pointer
						disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{#if sending}
						<span class="inline-flex items-center gap-1.5">
							<span class="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
							Enviando...
						</span>
					{:else}
						Enviar
					{/if}
				</button>
			</div>
		</div>
	{/if}
</div>
