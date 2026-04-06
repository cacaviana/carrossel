<script lang="ts">
	interface Props {
		variant?: 'line' | 'block' | 'circle';
		width?: string;
		height?: string;
	}
	let { variant = 'line', width = 'w-full', height = '' }: Props = $props();

	const variantClasses: Record<string, string> = {
		line: 'h-4 rounded-lg',
		block: 'h-24 rounded-xl',
		circle: 'w-10 h-10 rounded-full'
	};
</script>

<div class="bg-bg-elevated animate-shimmer {variantClasses[variant]} {width} {height}"></div>
