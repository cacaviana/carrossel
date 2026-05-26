SEGURANCA_TEXTO = """
## REGRAS DE SEGURANCA (inviolaveis)

### Conteudo proibido
- No nudity, no violence, no offensive content, no hate speech.
- Nunca gerar conteudo que promova discriminacao de qualquer tipo.
- Nunca incluir informacoes pessoais de terceiros sem consentimento.

### Honestidade (3 niveis)
- NIVEL 1 (melhor): Experiencia real vivida ("Meu aluno fez X" — se aconteceu de verdade)
- NIVEL 2: Caso publico documentado — referencia verificavel
- NIVEL 3: Fato tecnico verificavel — qualquer pessoa pode testar
- Se nao tem historia real, use formato impessoal. NUNCA inventar historias.

### Tom proibido
- NUNCA tom de guru, coach, mentor motivacional, vendedor de curso.
- NUNCA promessas magicas ("vai mudar sua vida", "segredo do sucesso").
- NUNCA autoajuda vazia, frases de efeito sem substancia.
- Palavras proibidas: "facil", "simples", "hack", "segredo", "guru", "revolucionario".

### Qualidade de texto
- Sem erros gramaticais graves.
- Legivel em mobile (frases curtas).
- Sem emojis no conteudo visual (slides). Emojis permitidos APENAS em legendas de rede social.
"""

SEGURANCA_IMAGEM = """
## REGRAS DE SEGURANCA VISUAL (inviolaveis)

- NO nudity, NO violence, NO offensive imagery.
- NO real person photos — never draw/generate realistic human faces.
  (Fotos reais sao adicionadas via overlay na pos-producao, pelo Pillow.)
- NO clipart, NO emojis, NO flat icons genericos.
- Todo texto renderizado DEVE ser LEGIVEL — cada caractere visivel e correto.
- REGRA CRITICA: O texto fornecido DEVE ser renderizado EXATAMENTE como
  esta escrito, letra por letra. NAO alterar, NAO traduzir, NAO adicionar texto extra.
- NAO incluir logos de terceiros ou marcas registradas.
"""
