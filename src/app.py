"""Laço principal do jogo (quem inicia é o main.py da raiz do projeto).

O laço é "async" de propósito: é o que a ferramenta pygbag exige
para publicar o jogo no navegador (PC e celular).
"""
import asyncio

import pygame

from config import (ALTURA, ESCALA_JANELA, FPS, LARGURA, TECLAS_BAIXO, TECLAS_CIMA,
                    TECLAS_DIREITA, TECLAS_ESQUERDA, TECLAS_PERSONAGEM)
from idiomas import t
from jogador import Entrada
from jogo import Jogo


def _apresentar(janela, tela):
    """Amplia a tela interna para a janela, mantendo a proporção (barras pretas)."""
    jw, jh = janela.get_size()
    esc = min(jw / LARGURA, jh / ALTURA)
    if esc >= 1:
        esc = int(esc)  # escala inteira = pixels nítidos
    tam = (max(1, int(LARGURA * esc)), max(1, int(ALTURA * esc)))
    janela.fill((0, 0, 0))
    janela.blit(pygame.transform.scale(tela, tam), ((jw - tam[0]) // 2, (jh - tam[1]) // 2))


async def principal(max_quadros=None):
    pygame.init()
    janela = pygame.display.set_mode((LARGURA * ESCALA_JANELA, ALTURA * ESCALA_JANELA),
                                     pygame.RESIZABLE)
    pygame.display.set_caption(t("titulo"))
    tela = pygame.Surface((LARGURA, ALTURA))
    relogio = pygame.time.Clock()
    jogo = Jogo()

    quadros = 0
    rodando = True
    while rodando:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                rodando = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    rodando = False
                elif ev.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
                elif ev.key == pygame.K_m:
                    jogo.audio.alternar_mudo()
                elif ev.key == pygame.K_t:
                    jogo.transformar()
                elif ev.key in TECLAS_PERSONAGEM:
                    jogo.trocar_personagem(TECLAS_PERSONAGEM[ev.key])

        teclas = pygame.key.get_pressed()
        entrada = Entrada(
            esquerda=any(teclas[k] for k in TECLAS_ESQUERDA),
            direita=any(teclas[k] for k in TECLAS_DIREITA),
            cima=any(teclas[k] for k in TECLAS_CIMA),
            baixo=any(teclas[k] for k in TECLAS_BAIXO),
        )
        jogo.atualizar(entrada)
        jogo.desenhar(tela)
        _apresentar(janela, tela)
        pygame.display.flip()
        relogio.tick(FPS)
        await asyncio.sleep(0)

        quadros += 1
        if max_quadros and quadros >= max_quadros:
            break
    pygame.quit()
