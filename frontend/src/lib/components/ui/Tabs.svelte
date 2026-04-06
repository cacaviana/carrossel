<script lang="ts">
	interface TabItem {
		id: string;
		label: string;
		count?: number;
	}
	interface Props {
		tabs: TabItem[];
		active: string;
		onchange: (id: string) => void;
	}
	let { tabs, active, onchange }: Props = $props();
</script>

<div class="flex border-b border-border-default gap-1">
	{#each tabs as tab}
		<button
			onclick={() => onchange(tab.id)}
			class="px-4 py-2.5 text-sm font-medium transition-all cursor-pointer
				{active === tab.id
					? 'text-purple bg-purple/8 border-b-2 border-purple'
					: 'text-text-secondary hover:text-text-primary'}"
		>
			{tab.label}
			{#if tab.count !== undefined}
				<span class="ml-1.5 text-xs text-text-muted">({tab.count})</span>
			{/if}
		</button>
	{/each}
</div>
