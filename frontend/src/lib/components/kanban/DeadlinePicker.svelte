<script lang="ts">
	import { onMount } from 'svelte';
	import { CardService } from '$lib/services/CardService';
	import { CardDTO } from '$lib/dtos/CardDTO';
	import type { CardFormato } from '$lib/dtos/CardDTO';

	let { value = '', onchange }: { value: string; onchange: (date: string) => void } = $props();

	let cards = $state<CardDTO[]>([]);
	let expanded = $state(false);
	let currentDate = $state(new Date());

	const currentYear = $derived(currentDate.getFullYear());
	const currentMonth = $derived(currentDate.getMonth());

	const monthNames = ['Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
		'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
	const dayNames = ['D', 'S', 'T', 'Q', 'Q', 'S', 'S'];

	const formatoColors: Record<CardFormato, string> = {
		carrossel: 'bg-purple-500',
		post_unico: 'bg-blue-500',
		thumbnail_youtube: 'bg-red-500',
		capa_reels: 'bg-pink-500',
		anuncio: 'bg-cyan-500'
	};

	const formatoLabels: Record<CardFormato, string> = {
		carrossel: 'Carrossel',
		post_unico: 'Post unico',
		thumbnail_youtube: 'YouTube',
		capa_reels: 'Capa Reels',
		anuncio: 'Anuncio'
	};

	const cardsByDay = $derived.by(() => {
		const map = new Map<string, CardDTO[]>();
		for (const card of cards) {
			if (!card.hasDeadline) continue;
			const day = card.deadline.slice(0, 10);
			if (!map.has(day)) map.set(day, []);
			map.get(day)!.push(card);
		}
		return map;
	});

	const calendarDays = $derived.by(() => {
		const firstDay = new Date(currentYear, currentMonth, 1).getDay();
		const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
		const days: ({ day: number; dateKey: string } | null)[] = [];
		for (let i = 0; i < firstDay; i++) days.push(null);
		for (let d = 1; d <= daysInMonth; d++) {
			const dateKey = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
			days.push({ day: d, dateKey });
		}
		return days;
	});

	const today = $derived(new Date().toISOString().slice(0, 10));
	const isPast = (dateKey: string) => dateKey < today;
	const selectedLabel = $derived(value ? new Date(value + 'T12:00:00').toLocaleDateString('pt-BR') : '');

	function selectDate(dateKey: string) {
		if (isPast(dateKey)) return;
		onchange(value === dateKey ? '' : dateKey);
	}

	function prevMonth() { currentDate = new Date(currentYear, currentMonth - 1, 1); }
	function nextMonth() { currentDate = new Date(currentYear, currentMonth + 1, 1); }

	onMount(async () => {
		try {
			const all = await CardService.listarTodos();
			cards = all;
		} catch {}
	});
</script>

<div>
	<!-- Botao fechado -->
	<button
		onclick={() => expanded = !expanded}
		class="w-full flex items-center justify-between px-4 py-2.5 rounded-lg border border-border-default bg-bg-input
			text-sm transition-all cursor-pointer hover:border-purple/30
			{expanded ? 'border-purple ring-3 ring-purple/12' : ''}"
	>
		<div class="flex items-center gap-2">
			<svg class="w-4 h-4 text-text-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
			</svg>
			{#if value}
				<span class="text-text-primary font-medium">Prazo: {selectedLabel}</span>
			{:else}
				<span class="text-text-muted">Prazo de publicacao (opcional)</span>
			{/if}
		</div>
		<svg class="w-4 h-4 text-text-muted transition-transform {expanded ? 'rotate-180' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
		</svg>
	</button>

	<!-- Calendario expandido -->
	{#if expanded}
		<div class="mt-2 bg-bg-card rounded-xl border border-border-default p-3 animate-fade-up">
			<!-- Nav -->
			<div class="flex items-center justify-between mb-2">
				<button onclick={prevMonth} class="p-1 rounded hover:bg-bg-elevated transition-all cursor-pointer text-text-muted">
					<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
					</svg>
				</button>
				<span class="text-xs font-semibold text-text-primary">{monthNames[currentMonth]} {currentYear}</span>
				<button onclick={nextMonth} class="p-1 rounded hover:bg-bg-elevated transition-all cursor-pointer text-text-muted">
					<svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
					</svg>
				</button>
			</div>

			<!-- Legenda -->
			<div class="flex flex-wrap items-center gap-x-3 gap-y-1 mb-2">
				{#each Object.entries(formatoColors) as [fmt, color]}
					<div class="flex items-center gap-1">
						<div class="w-2 h-2 rounded-sm {color}"></div>
						<span class="text-[9px] text-text-muted">{formatoLabels[fmt as CardFormato]}</span>
					</div>
				{/each}
			</div>

			<!-- Grid -->
			<div class="grid grid-cols-7 gap-px">
				{#each dayNames as name}
					<div class="text-center text-[9px] font-semibold text-text-muted py-1">{name}</div>
				{/each}

				{#each calendarDays as cell}
					{#if cell === null}
						<div class="h-10"></div>
					{:else}
						{@const dayCards = cardsByDay.get(cell.dateKey) ?? []}
						{@const isToday = cell.dateKey === today}
						{@const isSelected = cell.dateKey === value}
						{@const past = isPast(cell.dateKey)}
						<button
							onclick={() => selectDate(cell.dateKey)}
							disabled={past}
							class="h-10 rounded-lg flex flex-col items-center justify-start pt-0.5 gap-0.5 transition-all
								{isSelected ? 'bg-purple/20 ring-2 ring-purple' : ''}
								{isToday && !isSelected ? 'bg-purple/5' : ''}
								{past ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer hover:bg-bg-elevated'}
								{dayCards.length === 0 && !past && !isSelected ? 'hover:ring-1 hover:ring-purple/30' : ''}"
						>
							<span class="text-[10px] font-medium {isToday ? 'text-purple font-bold' : 'text-text-secondary'}">
								{cell.day}
							</span>
							{#if dayCards.length > 0}
								<div class="flex gap-px">
									{#each dayCards.slice(0, 3) as card}
										<div class="w-1.5 h-1.5 rounded-sm {formatoColors[card.formato]}" title={card.title}></div>
									{/each}
								</div>
							{/if}
						</button>
					{/if}
				{/each}
			</div>

			{#if value}
				<div class="mt-2 flex items-center justify-end">
					<button onclick={() => { onchange(''); }} class="text-[10px] text-red hover:underline cursor-pointer">Limpar prazo</button>
				</div>
			{/if}
		</div>
	{/if}
</div>
