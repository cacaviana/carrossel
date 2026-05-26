<script lang="ts">
	interface Props {
		variant?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'steel' | 'teal' | 'green' | 'red';
		size?: 'sm' | 'md';
		children: import('svelte').Snippet;
	}
	let { variant = 'primary', size = 'sm', children }: Props = $props();

	const classes: Record<string, string> = {
		primary: 'bg-purple/8 text-purple border border-purple/20',
		secondary: 'bg-bg-elevated text-text-secondary border border-border-default',
		success: 'bg-green/10 text-green border border-green/25',
		danger: 'bg-red/9 text-red border border-red/15',
		warning: 'bg-amber/10 text-amber border border-amber/25',
		// Legado
		steel: 'bg-steel-0 text-steel-3',
		teal: 'bg-teal-3 text-teal-6',
		green: 'text-green-600 bg-green-50',
		red: 'text-red-500 bg-red-50'
	};

	const sizeClasses: Record<string, string> = {
		sm: 'px-2 py-0.5 text-[10px]',
		md: 'px-3 py-1 text-xs'
	};
</script>

<span class="inline-flex rounded-full font-mono uppercase tracking-wide {classes[variant]} {sizeClasses[size]}">
	{@render children()}
</span>
