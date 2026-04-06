<script lang="ts">
	let { title, subtitle }: { title: string; subtitle?: string } = $props();
</script>

<div class="mb-6">
	<h1 class="text-2xl font-light text-text-primary mb-1">{title}</h1>
	{#if subtitle}
		<p class="text-sm text-text-secondary">{subtitle}</p>
	{/if}
</div>
