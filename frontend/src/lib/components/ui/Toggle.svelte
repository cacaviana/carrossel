<script lang="ts">
	interface Props {
		checked: boolean;
		label?: string;
		onchange: (checked: boolean) => void;
	}
	let { checked, label = '', onchange }: Props = $props();
</script>

<label class="inline-flex items-center gap-3 cursor-pointer">
	<button
		role="switch"
		aria-checked={checked}
		onclick={() => onchange(!checked)}
		class="relative w-11 h-6 rounded-full transition-colors duration-200 cursor-pointer
			{checked ? 'bg-purple' : 'bg-bg-elevated border border-border-default'}"
	>
		<span class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-sm transition-transform duration-200
			{checked ? 'translate-x-5' : 'translate-x-0'}"></span>
	</button>
	{#if label}
		<span class="text-sm text-text-secondary">{label}</span>
	{/if}
</label>
