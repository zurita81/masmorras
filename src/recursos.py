"""Carrega imagens e outros arquivos da pasta assets/."""
import os

import pygame

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "assets")

DIRECOES = ("baixo", "cima", "lado")


def caminho(*partes):
    return os.path.join(ASSETS, *partes)


def carregar_topo(slug, tam=32, colunas=6):
    """Lê assets/sprites/<slug>_topo.png (3 linhas: baixo, cima, lado).

    Devolve {"baixo": [6 quadros], "cima": [...], "lado": [...], "lado_esq": [...]}.
    Quadros 0-3 = andando, 4-5 = parado.
    """
    folha = pygame.image.load(caminho("sprites", f"{slug}_topo.png")).convert_alpha()
    quadros = {}
    for linha, nome in enumerate(DIRECOES):
        quadros[nome] = [folha.subsurface((c * tam, linha * tam, tam, tam)).copy()
                         for c in range(colunas)]
    quadros["lado_esq"] = [pygame.transform.flip(q, True, False) for q in quadros["lado"]]
    return quadros
