<script lang="ts">
	interface Props {
		variant?: 'steel' | 'teal' | 'green' | 'red';
		children: import('svelte').Snippet;
	}
	let { variant = 'steel', children }: Props = $props();

	const classes: Record<string, string> = {
		steel: 'bg-steel-0 text-steel-3',
		teal: 'bg-teal-3 text-teal-6',
		green: 'text-green-600 bg-green-50',
		red: 'text-red-500 bg-red-50'
	};
</script>

<span class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium {classes[variant]}">
	{@render children()}
</span>
