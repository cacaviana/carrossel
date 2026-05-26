# Skill Geracao de Slides Visuais — Carrossel LinkedIn

NOTA: Este skill e generico. Cores, fontes, badges, rodape e elementos de marca sao injetados em runtime pelo PromptComposer via brand profile. Placeholders entre {chaves} indicam dados que vem do brand profile.

## DESIGN SYSTEM: Dark Mode Premium — Carrossel Tech

### Paleta de Cores & Atmosfera

| Elemento | Placeholder | Uso |
|----------|-------------|-----|
| Fundo Global | {cor_fundo_global} | Base de tudo. Nunca 100% preto. |
| Fundo de Card | {cor_fundo_card} | Cards e elementos destacados |
| Fundo Codigo | {cor_fundo_codigo} | Corpo da janela de terminal |
| Barra titulo terminal | {cor_barra_terminal} | Title bar da janela macOS |
| Gradiente Base | {cor_gradiente_inicio} a {cor_gradiente_fim} | Gradiente sutil diagonal |
| Texto Principal | {cor_texto_principal} | Titulos e informacoes cruciais |
| Texto Secundario | {cor_texto_secundario} | Corpo, legendas, detalhes |
| Texto Muted | {cor_texto_muted} | Paginacao, elementos terciarios |
| Acento Principal | {cor_acento_principal} | Keywords, bordas ativas, pontos focais |
| Acento Soft | {cor_acento_soft} | Citacoes, italicos |
| Acento Secundario | {cor_acento_secundario} | Badges codigo, numeros positivos |
| Acento Terciario | {cor_acento_terciario} | Metricas de impacto, atencao |
| Acento Negativo | {cor_acento_negativo} | Limitacoes, alertas |
| Bordas Sutis | {cor_bordas_sutis} | Bordas finas de 1px para cards |

### Tipografia

| Placeholder | Uso | Peso |
|-------------|-----|------|
| {fonte_titulo} | Titulos grandes | Light (300) |
| {fonte_titulo} | Destaques em titulos | Semibold (600) |
| {fonte_titulo} | Corpo de texto | Regular (400) ou Light (300) |
| {fonte_mono} | Badges pill | Uppercase, letter-spacing, 12px |
| {fonte_mono} | Codigo | {cor_acento_secundario} sobre {cor_fundo_codigo} |
| {fonte_mono} | Metricas | Numeros de impacto, 28px+ |

### Hierarquia de Destaques no Texto
Dentro de texto {cor_texto_secundario}, palavras-chave ganham cor e peso:

| Tipo | Cor | Peso | Quando usar |
|------|-----|------|-------------|
| Keyword principal | {cor_acento_principal} | Semibold (600) | Tecnologias, conceitos centrais |
| Numero de impacto | {cor_acento_terciario} | Semibold (600) | Metricas, percentuais |
| Positivo | {cor_acento_secundario} | Semibold (600) | Resultados bons, badges codigo |
| Negativo | {cor_acento_negativo} | Semibold (600) | Limitacoes, problemas |
| Riscado | {cor_texto_muted} | Regular + strikethrough | Conceito obsoleto |

## BADGES NOS SLIDES

| Tipo | Borda | Fundo | Texto |
|------|-------|-------|-------|
| Codigo / Noticia | 1px {cor_acento_secundario} | {cor_acento_secundario} 10% opacidade | "CODIGO REAL" ou "NOTICIA REAL" em {cor_acento_secundario} |
| Categoria | 1px {cor_acento_principal} 20% opacidade | {cor_acento_principal} 10% opacidade | {cor_acento_principal} |
| Alerta | 1px {cor_acento_negativo} 15% opacidade | {cor_acento_negativo} 9% opacidade | {cor_acento_negativo} |

Forma: Pill (cantos arredondados). Fonte: {fonte_mono}, Uppercase, ~12px.

- Slide de CAPA: badge {badge_topo} (definido no brand profile)
- TODO slide de CODIGO: badge "CODIGO REAL" em {cor_acento_secundario}
- Slide CTA: rodape {rodape_nome} — {rodape_instituicao} — {rodape_curso} (definidos no brand profile)
- NUNCA: nomes de ferramentas internas, nomes de metodos internos

## REGRA OBRIGATORIA: SLIDE DE CODIGO
Todo slide do tipo "code" DEVE ter:
1. Badge "CODIGO REAL" no topo ({cor_acento_secundario}, pill)
2. Codigo dentro de JANELA DE TERMINAL estilo macOS/Apple:
   - Container: largura 90-95%, borda 1px {cor_borda_terminal}, radius 10px
   - Barra titulo: altura 28px, fundo {cor_barra_terminal}, radius superior 10px
   - 3 botoes: {cor_botao_fechar}, {cor_botao_minimizar}, {cor_botao_maximizar}, 10px cada, gap 6px (definidos no brand profile)
   - Nome arquivo: em {fonte_mono} 10px {cor_texto_secundario}, centralizado
   - Corpo: fundo {cor_fundo_codigo}, radius inferior 10px, padding 24-32px
   - Codigo: {fonte_mono}, 9.5px, {cor_acento_secundario}, line-height 1.55

## RODAPE PADRAO (todo slide)

| Posicao | Elemento | Detalhes |
|---------|----------|----------|
| Inferior Esquerdo | Foto + Nome | Circulo (40-48px) com borda {cor_acento_principal}, {rodape_nome} em {fonte_titulo} Medium branco |
| Inferior Centro | Navegacao | {texto_navegacao} em {fonte_mono} pequena, {cor_acento_principal} (definido no brand profile) |
| Inferior Direito | Paginacao | "XX / NN" em {fonte_mono}, {cor_texto_muted} |

## COMPONENTES VISUAIS

### Quote Blocks
- Borda esquerda: 3px, {cor_acento_principal}
- Fundo: {cor_acento_principal} 6% opacidade
- Texto: italico, {cor_acento_soft}, 13px
- Fonte citacao: {fonte_mono}, 10px, cinza

### Metric Cards
- Fundo: cor do acento com 10% opacidade
- Borda: cor do acento com 25% opacidade
- Radius: 10px
- Numero: 28px, peso 600, cor do acento
- Label: 10px, cinza {fonte_mono}

### Glows (Atmosfera)
- Circulos com blur extremo (80px+) e 6-10% opacidade
- Cores: {cor_acento_principal}, {cor_acento_secundario}
- Posicao: cantos dos slides, capa e CTA

## MODELOS E CUSTOS

| Modelo | Uso | Custo | Free tier |
|--------|-----|-------|-----------|
| gemini-3-pro-image-preview | Capa + Codigo + CTA | $0.134/imagem | Nao |
| gemini-2.5-flash-image | Slides do meio | FREE | 500 img/dia |

## ESTRATEGIA MIX — Suporta 3, 7 e 10 slides

### 10 slides (padrao)
- SLIDE 1 (CAPA): Pro
- SLIDES 2-5 (MEIO): Flash (gratis)
- SLIDE 6 (CODIGO): Pro
- SLIDES 7-9 (MEIO): Flash (gratis)
- SLIDE 10 (CTA): Pro
- Custo: 3 x $0.134 = $0.402 ≈ R$2,25

### 7 slides
- SLIDE 1 (CAPA): Pro
- SLIDES 2-3 (MEIO): Flash (gratis)
- SLIDE 4 (CODIGO): Pro
- SLIDES 5-6 (MEIO): Flash (gratis)
- SLIDE 7 (CTA): Pro
- Custo: 3 x $0.134 ≈ R$2,25

### 3 slides (micro)
- SLIDE 1 (CAPA): Pro
- SLIDE 2 (CODIGO): Pro
- SLIDE 3 (CTA): Pro
- Custo: 3 x $0.134 ≈ R$2,25

## TIPOS VISUAIS DE SLIDE

| Tipo | Fundo | Elementos |
|------|-------|-----------|
| Capa | Gradiente + glows | Atmosfera + headline + badge {badge_topo} |
| Metricas | Card {cor_fundo_card} | Quote box + metric cards + destaques |
| Flow | Card {cor_fundo_card} | Steps verticais com linha conectora {cor_acento_principal} |
| Respiro | Gradiente sem card | Frase GRANDE centralizada |
| Codigo | Card {cor_fundo_card} | Janela macOS + badge CODIGO REAL |
| Limitacoes | Card borda {cor_acento_negativo} | Cards de alerta + metrica |
| Comparativo | Card {cor_fundo_card} | Duas colunas: {cor_acento_negativo} vs {cor_acento_principal} |
| Espelho | Gradiente + linha {cor_acento_principal} | Frase de impacto + riscado |
| CTA | Gradiente + linha {cor_acento_principal} | Card convite + tags + {rodape_instituicao} |

## API
POST https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent
Header: x-goog-api-key: {GEMINI_API_KEY}
Config: { responseModalities: ["IMAGE", "TEXT"] }
Extrair imagem: data.candidates[0].content.parts → find part.inlineData → part.inlineData.data (base64)

## REGRAS DE OURO
1. Nunca muro de texto. Quebrar com cor, metrica ou bloco visual.
2. Palavras-chave SEMPRE em {cor_acento_principal} dentro de texto {cor_texto_secundario}.
3. Numeros SEMPRE grandes — card proprio ou 28px+.
4. Alternar denso / respiro apos 2-3 slides densos.
5. Fundo nunca 100% preto. Sempre {cor_fundo_global} com gradiente ou card {cor_fundo_card}.
6. Glows criam atmosfera. Blur extremo, 6-10% opacidade.
7. Rodape consistente: {rodape_nome} + foto com borda {cor_acento_principal} em TODO slide.
8. Codigo na janela macOS. Sempre com bolinhas, barra de titulo, nome do arquivo.
9. Sem icones genericos. Outline limpo dentro de caixa {cor_fundo_icone} (definido no brand profile).
10. Sem stock vibes. Nada de clipart, robos, cerebros digitais.

## FORMATO DE IMAGEM
- Tamanho: 1080x1350px (formato LinkedIn carrossel)
- Orientacao: Vertical (portrait)
