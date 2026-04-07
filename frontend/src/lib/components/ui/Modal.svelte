<script lang="ts">
	interface Props {
		open: boolean;
		size?: 'sm' | 'md' | 'lg';
		title?: string;
		onclose: () => void;
		children: import('svelte').Snippet;
		footer?: import('svelte').Snippet;
	}
	let { open, size = 'md', title = '', onclose, children, footer }: Props = $props();

	const sizeClasses: Record<string, string> = {
		sm: 'max-w-sm',
		md: 'max-w-lg',
		lg: 'max-w-2xl'
	};
</script>

{#if open}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto">
		<!-- Overlay -->
		<button
			class="fixed inset-0 bg-black/60 backdrop-blur-sm cursor-default"
			onclick={onclose}
			tabindex="-1"
		></button>

		<!-- Container -->
		<div class="relative bg-bg-card border border-border-default rounded-xl shadow-lg {sizeClasses[size]} w-full animate-fade-up">
			{#if title}
				<div class="px-6 pt-6 flex items-center justify-between">
					<h3 class="text-lg font-semibold text-text-primary">{title}</h3>
					<button
						onclick={onclose}
						class="text-text-muted hover:text-text-primary transition-colors cursor-pointer p-1"
					>
						<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>
			{/if}

			<div class="px-6 py-4">
				{@render children()}
			</div>

			{#if footer}
				<div class="px-6 pb-6 flex justify-end gap-3">
					{@render footer()}
				</div>
			{/if}
		</div>
	</div>
{/if}
