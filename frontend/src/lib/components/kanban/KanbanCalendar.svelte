<script lang="ts">
	import type { CardDTO, CardFormato } from '$lib/dtos/CardDTO';

	let { cards = [], onCardClick }: { cards: CardDTO[]; onCardClick?: (cardId: string) => void } = $props();

	// Mes atual navegavel
	let currentDate = $state(new Date());
	const currentYear = $derived(currentDate.getFullYear());
	const currentMonth = $derived(currentDate.getMonth());

	const monthNames = ['Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
		'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
	const dayNames = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab'];

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

	// Cards com deadline agrupados por dia (YYYY-MM-DD)
	const cardsByDay = $derived.by(() => {
		const map = new Map<string, CardDTO[]>();
		for (const card of cards) {
			if (!card.hasDeadline) continue;
			const day = card.deadline.slice(0, 10); // YYYY-MM-DD
			if (!map.has(day)) map.set(day, []);
			map.get(day)!.push(card);
		}
		return map;
	});

	// Grid do calendario
	const calendarDays = $derived.by(() => {
		const firstDay = new Date(currentYear, currentMonth, 1).getDay();
		const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
		const days: ({ day: number; dateKey: string } | null)[] = [];

		// Dias vazios antes do primeiro dia
		for (let i = 0; i < firstDay; i++) days.push(null);

		// Dias do mes
		for (let d = 1; d <= daysInMonth; d++) {
			const dateKey = `${currentYear}-${String(currentMonth + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
			days.push({ day: d, dateKey });
		}

		return days;
	});

	const today = $derived(new Date().toISOString().slice(0, 10));

	function prevMonth() {
		currentDate = new Date(currentYear, currentMonth - 1, 1);
	}

	function nextMonth() {
		currentDate = new Date(currentYear, currentMonth + 1, 1);
	}

	function goToday() {
		currentDate = new Date();
	}
</script>

<div class="bg-bg-card rounded-2xl border border-border-default p-4">
	<!-- Header: navegacao -->
	<div class="flex items-center justify-between mb-4">
		<button onclick={prevMonth} class="p-2 rounded-lg hover:bg-bg-elevated transition-all cursor-pointer text-text-secondary">
			<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
			</svg>
		</button>

		<div class="flex items-center gap-3">
			<h3 class="text-lg font-semibold text-text-primary">
				{monthNames[currentMonth]} {currentYear}
			</h3>
			<button onclick={goToday} class="text-[11px] px-2 py-1 rounded-lg bg-purple/10 text-purple font-medium hover:bg-purple/20 transition-all cursor-pointer">
				Hoje
			</button>
		</div>

		<button onclick={nextMonth} class="p-2 rounded-lg hover:bg-bg-elevated transition-all cursor-pointer text-text-secondary">
			<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
			</svg>
		</button>
	</div>

	<!-- Legenda -->
	<div class="flex items-center gap-4 mb-4">
		{#each Object.entries(formatoColors) as [fmt, color]}
			<div class="flex items-center gap-1.5">
				<div class="w-3 h-3 rounded-sm {color}"></div>
				<span class="text-[11px] text-text-muted">{formatoLabels[fmt as CardFormato]}</span>
			</div>
		{/each}
	</div>

	<!-- Grid -->
	<div class="grid grid-cols-7 gap-px bg-border-default/30 rounded-lg overflow-hidden">
		<!-- Header dias da semana -->
		{#each dayNames as name}
			<div class="bg-bg-elevated px-2 py-2 text-center text-[11px] font-semibold text-text-muted uppercase tracking-wide">
				{name}
			</div>
		{/each}

		<!-- Dias -->
		{#each calendarDays as cell}
			{#if cell === null}
				<div class="bg-bg-card/50 min-h-[80px]"></div>
			{:else}
				{@const dayCards = cardsByDay.get(cell.dateKey) ?? []}
				{@const isToday = cell.dateKey === today}
				<div class="bg-bg-card min-h-[80px] p-1.5 flex flex-col
					{isToday ? 'ring-2 ring-purple/40 ring-inset' : ''}">
					<span class="text-[11px] font-medium mb-1
						{isToday ? 'text-purple font-bold' : 'text-text-secondary'}">
						{cell.day}
					</span>
					<div class="flex flex-col gap-0.5 flex-1">
						{#each dayCards as card}
							<button
								onclick={() => onCardClick?.(card.id)}
								class="h-2.5 w-full rounded-sm {formatoColors[card.formato]} opacity-80 hover:opacity-100 hover:scale-y-150 transition-all cursor-pointer"
								title="{card.title} ({formatoLabels[card.formato]})"
							></button>
						{/each}
					</div>
				</div>
			{/if}
		{/each}
	</div>
</div>
