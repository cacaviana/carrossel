<script lang="ts">
	interface Props {
		textoLivre: string;
		onChange: (texto: string) => void;
	}

	let { textoLivre, onChange }: Props = $props();
</script>

<div class="bg-bg-card rounded-2xl border border-teal-4/30 p-6 animate-fade-up">
	<h3 class="font-semibold text-steel-6 mb-2">Cole ou escreva seu conteúdo</h3>
	<p class="text-xs text-steel-4 font-light mb-4">
		O Claude vai formatar seu texto criando os slides automaticamente.
	</p>

	<textarea
		value={textoLivre}
		oninput={(e) => onChange((e.target as HTMLTextAreaElement).value)}
		placeholder="Ex: Hoje vou falar sobre como implementei detecção de objetos em tempo real com YOLO v8 e Python..."
		rows="8"
		class="w-full px-4 py-3 rounded-xl border border-teal-4/30 bg-white text-steel-6 text-sm
			focus:border-steel-3 focus:ring-2 focus:ring-steel-3/20 outline-none transition-all resize-y"
	></textarea>
</div>
