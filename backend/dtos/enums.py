from enum import Enum


class ContentFormat(str, Enum):
    CARROSSEL = "carrossel"
    POST_UNICO = "post_unico"
    THUMBNAIL_YOUTUBE = "thumbnail_youtube"
    CAPA_REELS = "capa_reels"
    ANUNCIO = "anuncio"
