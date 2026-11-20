"""Textos do jogo. Para adicionar um idioma, copie o bloco "pt" e traduza.

Uso:
    from idiomas import t
    t("fase", fase="1-1")  ->  "Fase 1-1"
"""

TEXTOS = {
    "pt": {
        "titulo": "Masmorra",
        "fase": "Fase {fase}",
        "ajuda": "Setas ou WASD: mover   M: som   F11: tela cheia   Esc: sair",
    },
    # "es": {...},
    # "en": {...},
}

_idioma = "pt"


def definir_idioma(codigo):
    global _idioma
    if codigo in TEXTOS:
        _idioma = codigo


def t(chave, **dados):
    texto = TEXTOS[_idioma].get(chave) or TEXTOS["pt"].get(chave, chave)
    return texto.format(**dados) if dados else texto
