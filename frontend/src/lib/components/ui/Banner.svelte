<script lang="ts">
	interface Props {
		type?: 'success' | 'error' | 'warning' | 'info';
		dismissible?: boolean;
		ondismiss?: () => void;
		children: import('svelte').Snippet;
	}
	let { type = 'info', dismissible = true, ondismiss, children }: Props = $props();

	const typeClasses: Record<string, string> = {
		success: 'bg-green/10 border-green/25 text-green',
		error: 'bg-red/9 border-red/15 text-red',
		warning: 'bg-amber/10 border-amber/25 text-amber',
		info: 'bg-purple/8 border-purple/20 text-purple'
	};

	let visible = $state(true);
</script>

{#if visible}
	<div class="flex items-start gap-3 px-4 py-3 rounded-lg border {typeClasses[type]}">
		<div class="flex-1 text-sm">
			{@render children()}
		</div>
		{#if dismissible}
			<button
				onclick={() => { visible = false; ondismiss?.(); }}
				class="opacity-60 hover:opacity-100 transition-opacity cursor-pointer"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</button>
		{/if}
	</div>
{/if}
