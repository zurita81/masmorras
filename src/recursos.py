"""Carrega imagens e outros arquivos da pasta assets/."""
import os

import pygame

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(RAIZ, "assets")


def caminho(*partes):
    return os.path.join(ASSETS, *partes)


def carregar_quadros(slug, largura=40):
    """Lê assets/sprites/<slug>_idle.png e devolve (quadros_direita, quadros_esquerda)."""
    folha = pygame.image.load(caminho("sprites", f"{slug}_idle.png")).convert_alpha()
    direita = []
    for x in range(0, folha.get_width(), largura):
        direita.append(folha.subsurface((x, 0, largura, folha.get_height())).copy())
    esquerda = [pygame.transform.flip(q, True, False) for q in direita]
    return direita, esquerda
