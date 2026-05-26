<script lang="ts">
	let { pipelineId, etapaLabel }: { pipelineId: string; etapaLabel: string } = $props();
</script>

<div class="text-xs text-text-muted mb-4">
	<a href="/pipeline/{pipelineId}" class="text-purple hover:text-purple-soft no-underline">Pipeline</a>
	<span class="mx-2">></span>
	<span>{etapaLabel}</span>
</div>
