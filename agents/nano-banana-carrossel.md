# Skill Geracao de Slides Visuais — Carlos Viana / IT Valley School

## DESIGN SYSTEM: Dark Mode Premium — Carrossel Tech IT Valley

### Paleta de Cores & Atmosfera

| Elemento | Cor Hex | Uso |
|----------|---------|-----|
| Fundo Global | #0A0A0F | Base de tudo. Nunca 100% preto. |
| Fundo de Card | #12121A | Cards e elementos destacados |
| Fundo Codigo | #0D0D18 | Corpo da janela de terminal |
| Barra titulo terminal | #1a1a2a | Title bar da janela macOS |
| Gradiente Base | #1a0a2e → #0a1628 | Gradiente sutil diagonal |
| Texto Principal | #FFFFFF | Titulos e informacoes cruciais |
| Texto Secundario | #9896A3 | Corpo, legendas, detalhes |
| Texto Muted | #5A5A66 | Paginacao, elementos terciarios |
| Acento Principal | #A78BFA (Roxo Lilas) | Keywords, bordas ativas, pontos focais |
| Acento Soft | #C4B5FD (Roxo Claro) | Citacoes, italicos |
| Acento Secundario | #34D399 (Verde Neon) | Badges codigo, numeros positivos |
| Acento Terciario | #FBBF24 (Amber) | Metricas de impacto, atencao |
| Acento Negativo | #F87171 (Vermelho) | Limitacoes, alertas |
| Bordas Sutis | rgba(167,139,250,0.2) | Bordas finas de 1px para cards |

### Tipografia

| Fonte | Uso | Peso |
|-------|-----|------|
| Outfit | Titulos grandes | Light (300) |
| Outfit | Destaques em titulos | Semibold (600) |
| Outfit | Corpo de texto | Regular (400) ou Light (300) |
| JetBrains Mono | Badges pill | Uppercase, letter-spacing, 12px |
| JetBrains Mono | Codigo Python | Verde #34D399 sobre fundo #0D0D18 |
| JetBrains Mono | Metricas | Numeros de impacto, 28px+ |

### Hierarquia de Destaques no Texto
Dentro de texto cinza (#9896A3), palavras-chave ganham cor e peso:

| Tipo | Cor | Peso | Quando usar |
|------|-----|------|-------------|
| Keyword principal | #A78BFA (roxo) | Semibold (600) | Tecnologias, conceitos centrais |
| Numero de impacto | #FBBF24 (amber) | Semibold (600) | Metricas, percentuais |
| Positivo | #34D399 (verde) | Semibold (600) | Resultados bons, badges codigo |
| Negativo | #F87171 (vermelho) | Semibold (600) | Limitacoes, problemas |
| Riscado | #5C5A6B (cinza) | Regular + strikethrough | Conceito obsoleto |

## BADGES NOS SLIDES

| Tipo | Borda | Fundo | Texto |
|------|-------|-------|-------|
| Codigo / Noticia | 1px #34D399 | rgba(52,211,153,0.1) | "CODIGO REAL" ou "NOTICIA REAL" verde #34D399 |
| Categoria | 1px rgba(167,139,250,0.2) | rgba(167,139,250,0.1) | Roxo #A78BFA |
| Alerta | 1px rgba(248,113,113,0.15) | rgba(248,113,113,0.09) | Vermelho #F87171 |

Forma: Pill (cantos arredondados). Fonte: JetBrains Mono, Uppercase, ~12px.

- Slide de CAPA: badge "Carlos Viana" (verde #34D399)
- TODO slide de CODIGO: badge "CODIGO REAL" (verde #34D399)
- Slide CTA: rodape "Carlos Viana — IT Valley School — Pos IA & ML"
- NUNCA: nomes de ferramentas internas, nomes de metodos internos

## REGRA OBRIGATORIA: SLIDE DE CODIGO
Todo slide do tipo "code" DEVE ter:
1. Badge "CODIGO REAL" no topo (verde #34D399, pill)
2. Codigo dentro de JANELA DE TERMINAL estilo macOS/Apple:
   - Container: largura 90-95%, borda 1px #1E1E35, radius 10px
   - Barra titulo: altura 28px, fundo #1a1a2a, radius superior 10px
   - 3 botoes: vermelho #FF5F57, amarelo #FEBC2E, verde #28C840, 10px cada, gap 6px
   - Nome arquivo: "agent.py" em monospace 10px cinza #9896A3, centralizado
   - Corpo: fundo #0D0D18, radius inferior 10px, padding 24-32px
   - Codigo: JetBrains Mono, 9.5px, verde #34D399, line-height 1.55

## RODAPE PADRAO (todo slide)

| Posicao | Elemento | Detalhes |
|---------|----------|----------|
| Inferior Esquerdo | Foto + Nome | Circulo (40-48px) com borda roxa #A78BFA, "Carlos Viana" em Outfit Medium branco |
| Inferior Centro | Navegacao | "DESLIZA →" em monospace pequena, roxo #A78BFA |
| Inferior Direito | Paginacao | "XX / 10" em monospace, cinza #5A5A66 |

## COMPONENTES VISUAIS

### Quote Blocks
- Borda esquerda: 3px, #A78BFA
- Fundo: rgba(167,139,250,0.06)
- Texto: italico, #C4B5FD, 13px
- Fonte citacao: monospace, 10px, cinza

### Metric Cards
- Fundo: cor do acento com 10% opacidade
- Borda: cor do acento com 25% opacidade
- Radius: 10px
- Numero: 28px, peso 600, cor do acento
- Label: 10px, cinza monospace

### Glows (Atmosfera)
- Circulos com blur extremo (80px+) e 6-10% opacidade
- Cores: roxo #A78BFA, verde #34D399
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
| Capa | Gradiente + glows | Atmosfera + headline + badge Carlos Viana |
| Metricas | Card #12121A | Quote box + metric cards + destaques |
| Flow | Card #12121A | Steps verticais com linha conectora roxa |
| Respiro | Gradiente sem card | Frase GRANDE centralizada |
| Codigo | Card #12121A | Janela macOS + badge CODIGO REAL |
| Limitacoes | Card borda vermelha | Cards de alerta + metrica |
| Comparativo | Card #12121A | Duas colunas: vermelho vs roxo |
| Espelho | Gradiente + linha roxa | Frase de impacto + riscado |
| CTA | Gradiente + linha roxa | Card convite + tags + IT Valley |

## API
POST https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent
Header: x-goog-api-key: {GEMINI_API_KEY}
Config: { responseModalities: ["IMAGE", "TEXT"] }
Extrair imagem: data.candidates[0].content.parts → find part.inlineData → part.inlineData.data (base64)

## REGRAS DE OURO
1. Nunca muro de texto. Quebrar com cor, metrica ou bloco visual.
2. Palavras-chave SEMPRE em roxo (#A78BFA) dentro de texto cinza.
3. Numeros SEMPRE grandes — card proprio ou 28px+.
4. Alternar denso / respiro apos 2-3 slides densos.
5. Fundo nunca 100% preto. Sempre #0A0A0F com gradiente ou card #12121A.
6. Glows criam atmosfera. Blur extremo, 6-10% opacidade.
7. Rodape consistente: Carlos Viana + foto com borda roxa em TODO slide.
8. Codigo na janela macOS. Sempre com bolinhas, barra de titulo, nome do arquivo.
9. Sem icones genericos. Outline limpo dentro de caixa #16162A.
10. Sem stock vibes. Nada de clipart, robos, cerebros digitais.

## BANCO DE IMAGENS PRA CAPA
1. Terminal/IDE com codigo desfocado, dark mode
2. Dashboard com graficos, tons escuros
3. Dev de costas olhando pra tela com codigo
4. Rede de conexoes, pontos luminosos
5. GPU/hardware close-up, iluminacao dramatica
6. Fundo quase preto com spotlight sutil
7. Notebook com codigo + cafe, low key lighting
NUNCA: cerebro digital, robo, circuito brilhante generico
