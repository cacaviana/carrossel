<script lang="ts">
	import { onMount } from 'svelte';
	import { ActivityService } from '$lib/services/ActivityService';
	import type { ActivityDTO } from '$lib/dtos/ActivityDTO';
	import { formatRelativeDate, formatAbsoluteDate } from '$lib/utils/date';

	let { cardId }: { cardId: string } = $props();

	let activities = $state<ActivityDTO[]>([]);
	let loading = $state(true);
	let error = $state('');

	onMount(() => loadActivities());

	async function loadActivities() {
		loading = true;
		error = '';
		try {
			activities = await ActivityService.listarPorCard(cardId);
		} catch {
			error = 'Erro ao carregar atividades.';
		} finally {
			loading = false;
		}
	}

	const iconColors: Record<string, string> = {
		plus: 'bg-emerald-500/10 text-emerald-600',
		arrow: 'bg-blue-500/10 text-blue-600',
		user: 'bg-purple-500/10 text-purple-600',
		pencil: 'bg-amber-500/10 text-amber-600',
		chat: 'bg-cyan-500/10 text-cyan-600',
		trash: 'bg-red-500/10 text-red-500',
		image: 'bg-pink-500/10 text-pink-600',
		link: 'bg-teal-6/10 text-teal-6',
		document: 'bg-orange-500/10 text-orange-600'
	};

	const iconPaths: Record<string, string> = {
		plus: 'M12 4v16m8-8H4',
		arrow: 'M14 5l7 7m0 0l-7 7m7-7H3',
		user: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
		pencil: 'M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z',
		chat: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z',
		trash: 'M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16',
		image: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z',
		link: 'M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1',
		document: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
	};
</script>

{#if loading}
	<div class="flex items-center justify-center py-12">
		<span class="w-6 h-6 border-2 border-purple/30 border-t-purple rounded-full animate-spin"></span>
	</div>
{:else if error}
	<div class="text-center py-8">
		<p class="text-sm text-red mb-3">{error}</p>
		<button onclick={loadActivities} class="text-sm text-purple hover:underline cursor-pointer">Tentar novamente</button>
	</div>
{:else if activities.length === 0}
	<p class="text-sm text-text-muted text-center py-8">Nenhuma atividade registrada.</p>
{:else}
	<div class="relative">
		<!-- Vertical line -->
		<div class="absolute left-4 top-0 bottom-0 w-0.5 bg-border-default"></div>

		<div class="space-y-4">
			{#each activities as activity (activity.id)}
				<div class="flex items-start gap-3 relative">
					<!-- Icon circle -->
					<div class="w-8 h-8 rounded-full {iconColors[activity.iconType] ?? 'bg-bg-elevated text-text-muted'} flex items-center justify-center relative z-10 shrink-0">
						<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={iconPaths[activity.iconType] ?? iconPaths.pencil} />
						</svg>
					</div>

					<!-- Content -->
					<div class="flex-1 pt-1">
						<p class="text-sm text-text-primary">{activity.descricao}</p>
						<span class="text-[11px] text-text-muted" title={formatAbsoluteDate(activity.created_at)}>
							{formatRelativeDate(activity.created_at)}
						</span>
					</div>
				</div>
			{/each}
		</div>
	</div>
{/if}
