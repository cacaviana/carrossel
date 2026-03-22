<script lang="ts">
	interface Props {
		currentSlide: number;
		totalSlides: number;
		onPrev: () => void;
		onNext: () => void;
		onGoto: (index: number) => void;
	}

	let { currentSlide, totalSlides, onPrev, onNext, onGoto }: Props = $props();
</script>

<div class="flex items-center justify-between mt-4">
	<button onclick={onPrev} disabled={currentSlide === 0}
		class="px-4 py-2 rounded-full text-sm font-medium bg-teal-3 text-steel-5 hover:bg-teal-4 transition-all cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed">
		Anterior
	</button>
	<div class="flex gap-1.5">
		{#each Array(totalSlides) as _, i}
			<button onclick={() => onGoto(i)}
				class="w-2.5 h-2.5 rounded-full transition-all cursor-pointer
					{i === currentSlide ? 'bg-steel-3 scale-125' : 'bg-teal-4 hover:bg-teal-5'}">
			</button>
		{/each}
	</div>
	<button onclick={onNext} disabled={currentSlide === totalSlides - 1}
		class="px-4 py-2 rounded-full text-sm font-medium bg-teal-3 text-steel-5 hover:bg-teal-4 transition-all cursor-pointer disabled:opacity-30 disabled:cursor-not-allowed">
		Próximo
	</button>
</div>
