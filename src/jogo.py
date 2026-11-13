"""Junta tudo: fase, jogador, câmera e interface."""
import pygame

import recursos
from camera import Camera
from config import ALTURA, LARGURA
from idiomas import t
from jogador import Jogador
from nivel import Nivel


class Jogo:
    def __init__(self, fase="1-1", personagem="cavaleiro"):
        self.fase = fase
        self.nivel = Nivel(recursos.caminho("niveis", f"{fase}.txt"))
        x, y = self.nivel.inicio
        self.jogador = Jogador(x, y, personagem)
        self.camera = Camera(self.nivel.largura_px, self.nivel.altura_px)
        self.camera.centralizar(self.jogador.rect)
        self.fonte = pygame.font.Font(None, 18)

    def atualizar(self, entrada):
        self.jogador.atualizar(entrada, self.nivel)
        self.camera.seguir(self.jogador.rect)

    def desenhar(self, tela):
        cx, cy = self.camera.ix, self.camera.iy
        tela.fill((10, 8, 12))
        self.nivel.desenhar(tela, cx, cy)
        self.jogador.desenhar(tela, cx, cy)
        self._interface(tela)

    def _texto(self, tela, texto, pos, cor=(232, 200, 120)):
        tela.blit(self.fonte.render(texto, False, (10, 6, 10)), (pos[0] + 1, pos[1] + 1))
        tela.blit(self.fonte.render(texto, False, cor), pos)

    def _interface(self, tela):
        self._texto(tela, t("fase", fase=self.fase), (8, 6))
        self._texto(tela, t("ajuda"), (8, ALTURA - 16), (170, 160, 150))
