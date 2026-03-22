<script lang="ts">
	interface Props {
		hover?: boolean;
		children: import('svelte').Snippet;
	}
	let { hover = false, children }: Props = $props();
</script>

<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-5
	{hover ? 'hover:-translate-y-1 hover:shadow-md transition-all' : ''}">
	{@render children()}
</div>
