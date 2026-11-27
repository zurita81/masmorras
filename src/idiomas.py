"""Textos do jogo. Para adicionar um idioma, copie o bloco "pt" e traduza.

Uso:
    from idiomas import t
    t("fase", fase="1-1")  ->  "Fase 1-1"
"""

TEXTOS = {
    "pt": {
        "titulo": "Masmorra",
        "fase": "Fase {fase}",
        "ajuda": "WASD/setas: mover  1-5: personagem  T: lobo  M: som  F11  Esc",
        "personagem": "Personagem: {nome}",
        "p_cavaleiro": "Cavaleiro",
        "p_mago": "Mago",
        "p_druida": "Druida",
        "p_arqueiro": "Arqueiro",
        "p_metamorfo": "Metamorfo",
        "p_lobo": "Lobo",
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
