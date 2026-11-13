"""Constantes gerais do jogo."""

# Resolução interna (pixel art). A janela é só uma ampliação disso.
LARGURA, ALTURA = 480, 270
ESCALA_JANELA = 2
FPS = 60

# Tamanho de cada bloco do cenário, em pixels
TAM = 16

# Teclas
import pygame  # noqa: E402

TECLAS_ESQUERDA = (pygame.K_LEFT, pygame.K_a)
TECLAS_DIREITA = (pygame.K_RIGHT, pygame.K_d)
TECLAS_BAIXO = (pygame.K_DOWN, pygame.K_s)
TECLAS_PULO = (pygame.K_SPACE, pygame.K_UP, pygame.K_w, pygame.K_z)
