from dtos.anuncio.base import AnuncioResponse


# O frontend espera um array direto (nao paginado). Mantemos flexibilidade:
# o router retorna a lista de anuncios completa (ate page_size=500 itens),
# igual ao mock.
ListarAnunciosResponse = list[AnuncioResponse]
