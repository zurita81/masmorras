"""Junta tudo: fase, jogador, câmera, fundo e interface."""
import pygame

import recursos
from camera import Camera
from config import ALTURA, LARGURA
from idiomas import t
from jogador import Jogador
from nivel import Nivel


def _fundo_degrade():
    s = pygame.Surface((LARGURA, ALTURA))
    topo, base = (12, 9, 18), (36, 26, 38)
    for y in range(ALTURA):
        k = y / (ALTURA - 1)
        cor = tuple(int(topo[i] + (base[i] - topo[i]) * k) for i in range(3))
        pygame.draw.line(s, cor, (0, y), (LARGURA, y))
    return s


def _pilares():
    """Faixa com colunas góticas ao fundo, que se repete (efeito de paralaxe)."""
    passo = 112
    s = pygame.Surface((passo, ALTURA), pygame.SRCALPHA)
    cor, clara = (24, 18, 30), (30, 23, 37)
    pygame.draw.rect(s, cor, (44, 30, 24, ALTURA))
    pygame.draw.rect(s, clara, (44, 30, 5, ALTURA))
    pygame.draw.rect(s, cor, (38, 22, 36, 10))
    pygame.draw.rect(s, cor, (38, ALTURA - 40, 36, 40))
    pygame.draw.polygon(s, cor, [(0, 0), (passo, 0), (passo // 2 + 26, 22), (passo // 2 - 26, 22)])
    return s, passo


class Jogo:
    def __init__(self, fase="1-1", personagem="cavaleiro"):
        self.fase = fase
        self.nivel = Nivel(recursos.caminho("niveis", f"{fase}.txt"))
        x, y = self.nivel.inicio
        self.jogador = Jogador(x, y, personagem)
        self.camera = Camera(self.nivel.largura_px, self.nivel.altura_px)
        self.camera.centralizar(self.jogador.rect)
        self.fundo = _fundo_degrade()
        self.pilares, self.passo_pilar = _pilares()
        self.fonte = pygame.font.Font(None, 18)

    def atualizar(self, entrada):
        self.jogador.atualizar(entrada, self.nivel)
        self.camera.seguir(self.jogador.rect)

    def desenhar(self, tela):
        cx, cy = self.camera.ix, self.camera.iy
        tela.blit(self.fundo, (0, 0))
        deslocamento = -int(cx * 0.35) % self.passo_pilar - self.passo_pilar
        for x in range(deslocamento, LARGURA, self.passo_pilar):
            tela.blit(self.pilares, (x, 0))
        self.nivel.desenhar(tela, cx, cy)
        self.jogador.desenhar(tela, cx, cy)
        self._interface(tela)

    def _texto(self, tela, texto, pos, cor=(232, 200, 120)):
        sombra = self.fonte.render(texto, False, (10, 6, 10))
        tela.blit(sombra, (pos[0] + 1, pos[1] + 1))
        tela.blit(self.fonte.render(texto, False, cor), pos)

    def _interface(self, tela):
        self._texto(tela, t("fase", fase=self.fase), (8, 6))
        self._texto(tela, t("ajuda"), (8, ALTURA - 16), (170, 160, 150))
