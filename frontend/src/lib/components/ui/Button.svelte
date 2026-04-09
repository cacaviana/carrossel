<script lang="ts">
	import type { HTMLButtonAttributes } from 'svelte/elements';

	interface Props extends HTMLButtonAttributes {
		variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
		size?: 'sm' | 'md' | 'lg';
		loading?: boolean;
		children: import('svelte').Snippet;
	}

	let { variant = 'primary', size = 'md', loading = false, children, ...rest }: Props = $props();

	const variantClasses: Record<string, string> = {
		primary: 'text-bg-global bg-purple hover:shadow-[0_0_20px_rgba(53,120,176,0.2)] hover:opacity-90',
		secondary: 'text-bg-global bg-green hover:shadow-[0_0_20px_rgba(42,157,110,0.2)] hover:opacity-90',
		outline: 'border border-purple/20 text-purple hover:bg-purple/8',
		ghost: 'text-purple hover:bg-purple/8',
		danger: 'text-red bg-red/9 border border-red/15 hover:bg-red/15'
	};

	const sizeClasses: Record<string, string> = {
		sm: 'px-3 py-1.5 text-xs',
		md: 'px-5 py-2.5 text-sm',
		lg: 'px-6 py-3 text-base'
	};
</script>

<button
	class="rounded-full font-medium transition-all duration-250 cursor-pointer
		disabled:opacity-50 disabled:cursor-not-allowed
		{variantClasses[variant]} {sizeClasses[size]}"
	disabled={loading || rest.disabled}
	{...rest}
>
	{#if loading}
		<span class="inline-flex items-center gap-2">
			<span class="w-4 h-4 border-2 border-current/30 border-t-current rounded-full animate-spin"></span>
			{@render children()}
		</span>
	{:else}
		{@render children()}
	{/if}
</button>
