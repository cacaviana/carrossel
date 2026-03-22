<script lang="ts">
	import type { Slide } from '$lib/stores/carrossel';

	interface Props {
		slide: Slide | undefined;
		slideIndex: number;
		totalSlides: number;
	}

	let { slide, slideIndex, totalSlides }: Props = $props();
</script>

<div class="aspect-[4/5] bg-steel-6 rounded-xl overflow-hidden flex items-center justify-center">
	{#if slide?.imageBase64}
		<img src={slide.imageBase64} alt="Slide {slideIndex + 1}" class="w-full h-full object-contain" />
	{:else}
		<div class="text-center p-8">
			<p class="text-teal-4 text-sm font-light mb-2">Slide {slideIndex + 1} / {totalSlides}</p>
			<p class="text-white font-semibold text-lg mb-1">{slide?.headline || slide?.title || slide?.type || ''}</p>
			{#if slide?.subline}<p class="text-teal-5 text-sm">{slide.subline}</p>{/if}
			{#if slide?.bullets}
				<ul class="text-left text-teal-4 text-sm mt-4 space-y-1.5">
					{#each slide.bullets as bullet}<li>→ {bullet}</li>{/each}
				</ul>
			{/if}
			{#if slide?.code}
				<pre class="text-left text-green-400 text-xs mt-4 p-3 bg-black/50 rounded-lg overflow-auto font-mono">{slide.code}</pre>
			{/if}
			<p class="text-steel-4 text-xs mt-4 italic">Clique "Editar slides" para ajustar o texto</p>
		</div>
	{/if}
</div>
