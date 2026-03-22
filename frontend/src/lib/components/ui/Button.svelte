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
		primary: 'text-white bg-gradient-to-r from-steel-4 via-steel-3 to-steel-2 hover:-translate-y-0.5 hover:shadow-lg',
		secondary: 'text-white bg-gradient-to-r from-steel-6 via-steel-5 to-steel-4 hover:-translate-y-0.5 hover:shadow-lg',
		outline: 'border border-steel-3/30 text-steel-3 hover:bg-steel-0',
		ghost: 'text-steel-3 hover:bg-teal-1',
		danger: 'text-red-600 bg-red-50 hover:bg-red-100'
	};

	const sizeClasses: Record<string, string> = {
		sm: 'px-3 py-1 text-xs',
		md: 'px-5 py-2.5 text-sm',
		lg: 'px-6 py-3 text-sm'
	};
</script>

<button
	class="rounded-full font-medium transition-all duration-300 cursor-pointer
		disabled:opacity-50 disabled:cursor-not-allowed
		{variantClasses[variant]} {sizeClasses[size]}"
	disabled={loading || rest.disabled}
	{...rest}
>
	{#if loading}
		<span class="inline-flex items-center gap-2">
			<span class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
			{@render children()}
		</span>
	{:else}
		{@render children()}
	{/if}
</button>
