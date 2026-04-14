<script lang="ts">
	let { disabled = false }: { disabled: boolean } = $props();
</script>

<div class="space-y-3">
	<div class="flex items-center gap-3">
		<div class="flex-1 h-px bg-border-default"></div>
		<span class="text-xs text-text-muted">ou continue com</span>
		<div class="flex-1 h-px bg-border-default"></div>
	</div>

	<div class="grid grid-cols-2 gap-3">
		<button
			type="button"
			disabled={disabled}
			class="flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-border-default
				text-sm font-medium text-text-secondary hover:bg-bg-elevated hover:border-purple/30
				transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
		>
			<svg class="w-4 h-4" viewBox="0 0 24 24">
				<path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
				<path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
				<path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
				<path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
			</svg>
			Google
		</button>

		<button
			type="button"
			disabled={disabled}
			class="flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-border-default
				text-sm font-medium text-text-secondary hover:bg-bg-elevated hover:border-purple/30
				transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
		>
			<svg class="w-4 h-4" viewBox="0 0 23 23">
				<rect x="1" y="1" width="10" height="10" fill="#F25022"/>
				<rect x="12" y="1" width="10" height="10" fill="#7FBA00"/>
				<rect x="1" y="12" width="10" height="10" fill="#00A4EF"/>
				<rect x="12" y="12" width="10" height="10" fill="#FFB900"/>
			</svg>
			Microsoft
		</button>
	</div>
</div>
