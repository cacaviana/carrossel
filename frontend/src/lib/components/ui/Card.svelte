<script lang="ts">
	interface Props {
		hover?: boolean;
		glow?: boolean;
		padding?: 'sm' | 'md' | 'lg';
		children: import('svelte').Snippet;
	}
	let { hover = false, glow = false, padding = 'md', children }: Props = $props();

	const paddingClasses: Record<string, string> = {
		sm: 'p-3',
		md: 'p-5',
		lg: 'p-7'
	};
</script>

<div class="bg-bg-card rounded-xl border border-border-default {paddingClasses[padding]}
	{hover ? 'hover:-translate-y-1 hover:shadow-md hover:border-purple/30 transition-all cursor-pointer' : ''}
	{glow ? 'shadow-[0_0_20px_rgba(167,139,250,0.06)]' : ''}">
	{@render children()}
</div>
