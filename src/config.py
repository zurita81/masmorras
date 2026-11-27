"""Constantes gerais do jogo."""
import pygame

# Resolução interna (pixel art). A janela é só uma ampliação disso.
LARGURA, ALTURA = 480, 270
ESCALA_JANELA = 2
FPS = 60

# Tamanho de cada bloco do cenário, em pixels
TAM = 16

# Teclas
TECLAS_ESQUERDA = (pygame.K_LEFT, pygame.K_a)
TECLAS_DIREITA = (pygame.K_RIGHT, pygame.K_d)
TECLAS_CIMA = (pygame.K_UP, pygame.K_w)
TECLAS_BAIXO = (pygame.K_DOWN, pygame.K_s)

# Teclas 1-5 escolhem o personagem
TECLAS_PERSONAGEM = {
    pygame.K_1: "cavaleiro",
    pygame.K_2: "mago",
    pygame.K_3: "druida",
    pygame.K_4: "arqueiro",
    pygame.K_5: "metamorfo",
}
