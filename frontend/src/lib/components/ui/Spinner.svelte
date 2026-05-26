<script lang="ts">
	interface Props {
		size?: 'sm' | 'md' | 'lg';
	}
	let { size = 'md' }: Props = $props();

	const sizeClasses: Record<string, string> = {
		sm: 'w-4 h-4',
		md: 'w-6 h-6',
		lg: 'w-8 h-8'
	};
</script>

<span class="inline-block {sizeClasses[size]} border-2 border-purple/30 border-t-purple rounded-full animate-spin"></span>
