<script lang="ts">
	let { total, current, onSelect, activeClass = 'bg-purple scale-125', inactiveClass = 'bg-text-muted/30 hover:bg-text-muted/50' }: {
		total: number;
		current: number;
		onSelect: (i: number) => void;
		activeClass?: string;
		inactiveClass?: string;
	} = $props();
</script>

<div class="flex gap-1.5">
	{#each Array(total) as _, i}
		<button
			onclick={() => onSelect(i)}
			class="w-2.5 h-2.5 rounded-full transition-all cursor-pointer
				{i === current ? activeClass : inactiveClass}"
		></button>
	{/each}
</div>
