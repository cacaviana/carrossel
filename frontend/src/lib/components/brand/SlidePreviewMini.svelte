<script lang="ts">
	interface Props {
		cores: Record<string, string>;
		fontes?: Record<string, string>;
		visual?: Record<string, string>;
		elementos?: Record<string, any>;
		nome: string;
	}

	let { cores, fontes, visual, elementos, nome }: Props = $props();

	const fundo = $derived(cores?.fundo || '#0A0A0F');
	const gradDe = $derived(cores?.gradiente_de || '#1a0a2e');
	const gradAte = $derived(cores?.gradiente_ate || '#0a1628');
	const card = $derived(cores?.card || '#12121A');
	const cardBorda = $derived(cores?.card_borda || 'rgba(167,139,250,0.2)');
	const acento = $derived(cores?.acento_principal || '#A78BFA');
	const acento2 = $derived(cores?.acento_secundario || '#34D399');
	const txtPrincipal = $derived(cores?.texto_principal || '#FFFFFF');
	const txtSecundario = $derived(cores?.texto_secundario || '#9896A3');
	const fontTitulo = $derived(fontes?.titulo || 'Outfit');
	const fontCorpo = $derived(fontes?.corpo || 'Outfit');
	const badge = $derived(elementos?.badge_topo || nome);
	const cta = $derived(elementos?.cta_texto || 'Saiba mais');
</script>

<div class="rounded-xl overflow-hidden border border-border-default shadow-sm" style="aspect-ratio: 4/5; max-width: 260px;">
	<!-- Simula slide de capa -->
	<div class="w-full h-full relative flex flex-col justify-between p-4"
		style="background: linear-gradient(160deg, {gradDe} 0%, {fundo} 40%, {gradAte} 100%);">

		<!-- Badge topo -->
		<div class="flex items-center gap-1.5">
			<span class="px-2 py-0.5 rounded-full text-[8px] font-semibold"
				style="background: {acento}20; color: {acento}; border: 1px solid {acento}30;">
				{badge}
			</span>
		</div>

		<!-- Conteudo central -->
		<div class="flex-1 flex flex-col justify-center gap-2">
			<p class="text-[10px] font-light leading-tight" style="color: {txtSecundario}; font-family: {fontCorpo};">
				Preview ao vivo
			</p>
			<p class="text-sm font-bold leading-tight" style="color: {txtPrincipal}; font-family: {fontTitulo};">
				7 Habitos para Conquistar sua Vaga
			</p>
			<p class="text-[9px] leading-relaxed" style="color: {txtSecundario}; font-family: {fontCorpo};">
				Descubra como devs brasileiros estao conseguindo vagas remotas no exterior.
			</p>
		</div>

		<!-- Card simulado -->
		<div class="rounded-lg p-2.5 mb-2" style="background: {card}; border: 1px solid {cardBorda};">
			<div class="flex items-center gap-1.5 mb-1">
				<span class="w-1.5 h-1.5 rounded-full" style="background: {acento2};"></span>
				<span class="text-[8px] font-medium" style="color: {acento2};">Dica #1</span>
			</div>
			<p class="text-[8px]" style="color: {txtSecundario};">Tenha portfolio no GitHub com projetos reais</p>
		</div>

		<!-- Rodape -->
		<div class="flex items-center justify-between">
			<span class="text-[8px]" style="color: {txtSecundario};">{elementos?.rodape_nome || nome}</span>
			<span class="px-2 py-0.5 rounded-full text-[7px] font-semibold" style="background: {acento}; color: {fundo};">
				{cta}
			</span>
		</div>

		<!-- Glow decorativo -->
		<div class="absolute top-2 right-2 w-16 h-16 rounded-full opacity-10 blur-xl" style="background: {acento};"></div>
	</div>
</div>
