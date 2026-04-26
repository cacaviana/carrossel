<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	// Este wizard foi unificado com os demais formatos na Home.
	// Mantemos este arquivo como redirecionamento para nao quebrar links antigos.
	onMount(() => {
		goto('/?formato=anuncio', { replaceState: true });
	});
</script>

<div class="min-h-[40vh] flex items-center justify-center text-text-muted">
	Redirecionando...
</div>
