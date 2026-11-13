"""Masmorra vista de cima: lê o mapa em texto, desenha chão/paredes e responde colisões.

Visão 3/4: paredes que têm chão logo abaixo mostram a "frente" de tijolos;
as demais mostram só o "topo" escuro.
"""
import random

import pygame

from config import TAM

# paleta de pedra sombria
CHAO_A, CHAO_B = (50, 42, 52), (45, 37, 47)
JUNTA = (34, 28, 36)
MUSGO = (62, 98, 56)
FRENTE = (84, 70, 80)
FRENTE_LUZ = (118, 101, 112)
FRENTE_SOMBRA = (54, 43, 54)
MASSA = (46, 36, 47)
TOPO = (28, 22, 31)
TOPO_BORDA = (56, 46, 58)


class Nivel:
    def __init__(self, caminho):
        with open(caminho, encoding="utf-8") as f:
            linhas = [l.rstrip("\r\n") for l in f if l.strip() and not l.startswith(";")]
        self.cols = len(linhas[0])
        self.lins = len(linhas)
        for i, l in enumerate(linhas):
            if len(l) != self.cols:
                raise ValueError(f"{caminho}: a linha {i + 1} tem {len(l)} colunas "
                                 f"(esperado {self.cols})")
        self.largura_px = self.cols * TAM
        self.altura_px = self.lins * TAM
        self.paredes = set()
        self.inicio = (TAM * 2, TAM * 3)  # (x do centro, y dos pés)
        for y, linha in enumerate(linhas):
            for x, c in enumerate(linha):
                if c == "#":
                    self.paredes.add((x, y))
                elif c == "P":
                    self.inicio = (x * TAM + TAM // 2, y * TAM + TAM // 2 + 6)
        self.imagem = self._pre_desenhar()

    # ---------- colisões ----------
    def paredes_em(self, rect):
        x0, x1 = rect.left // TAM, (rect.right - 1) // TAM
        y0, y1 = rect.top // TAM, (rect.bottom - 1) // TAM
        for ty in range(y0, y1 + 1):
            for tx in range(x0, x1 + 1):
                if (tx, ty) in self.paredes:
                    yield pygame.Rect(tx * TAM, ty * TAM, TAM, TAM)

    # ---------- desenho ----------
    def _tem_frente(self, x, y):
        """Parede com chão logo abaixo (dentro do mapa) mostra a face de tijolos."""
        return ((x, y + 1) not in self.paredes) and (y + 1 < self.lins)

    def _pre_desenhar(self):
        img = pygame.Surface((self.largura_px, self.altura_px))
        for y in range(self.lins):
            for x in range(self.cols):
                if (x, y) in self.paredes:
                    tile = self._frente(x, y) if self._tem_frente(x, y) else self._topo(x, y)
                else:
                    tile = self._chao(x, y)
                img.blit(tile, (x * TAM, y * TAM))
        return img

    def _chao(self, x, y):
        rng = random.Random(x * 7919 + y * 104729)
        s = pygame.Surface((TAM, TAM))
        s.fill(CHAO_A if (x + y) % 2 == 0 else CHAO_B)
        for px in range(TAM):
            for py in range(TAM):
                if rng.random() < 0.10:
                    base = s.get_at((px, py))
                    d = rng.choice((-6, 6))
                    s.set_at((px, py), (base.r + d, base.g + d, base.b + d))
        pygame.draw.line(s, JUNTA, (0, TAM - 1), (TAM - 1, TAM - 1))
        pygame.draw.line(s, JUNTA, (TAM - 1, 0), (TAM - 1, TAM - 1))
        if rng.random() < 0.06:  # rachadura
            x0, y0 = rng.randint(3, 9), rng.randint(3, 9)
            pygame.draw.lines(s, JUNTA, False, [(x0, y0), (x0 + 3, y0 + 2), (x0 + 4, y0 + 5)])
        if rng.random() < 0.05:  # musgo
            for _ in range(7):
                s.set_at((rng.randint(2, 13), rng.randint(2, 13)), MUSGO)
        if (x, y - 1) in self.paredes and self._tem_frente(x, y - 1):  # sombra da parede
            sombra = pygame.Surface((TAM, 1), pygame.SRCALPHA)
            for i, alfa in enumerate((110, 85, 60, 40, 22)):
                sombra.fill((0, 0, 0, alfa))
                s.blit(sombra, (0, i))
        return s

    def _frente(self, x, y):
        rng = random.Random(x * 31337 + y * 7)
        s = pygame.Surface((TAM, TAM))
        s.fill(FRENTE)
        for px in range(TAM):
            for py in range(TAM):
                if rng.random() < 0.12:
                    base = s.get_at((px, py))
                    d = rng.choice((-8, 8))
                    s.set_at((px, py), (base.r + d, base.g + d, base.b + d))
        for ly in (7, 15):
            pygame.draw.line(s, MASSA, (0, ly), (TAM - 1, ly))
        pygame.draw.line(s, MASSA, (7, 0), (7, 6))
        pygame.draw.line(s, MASSA, (3 if y % 2 else 12, 8), (3 if y % 2 else 12, 14))
        pygame.draw.line(s, FRENTE_LUZ, (0, 0), (TAM - 1, 0))
        pygame.draw.line(s, FRENTE_SOMBRA, (0, 14), (TAM - 1, 14))
        return s

    def _topo(self, x, y):
        rng = random.Random(x * 4241 + y * 99991)
        s = pygame.Surface((TAM, TAM))
        s.fill(TOPO)
        for px in range(TAM):
            for py in range(TAM):
                if rng.random() < 0.08:
                    s.set_at((px, py), (36, 29, 39))
        if (x, y - 1) not in self.paredes:  # borda de luz onde a pedra encontra o fundo
            pygame.draw.line(s, TOPO_BORDA, (0, 0), (TAM - 1, 0))
        return s

    def desenhar(self, tela, cam_x, cam_y):
        tela.blit(self.imagem, (-cam_x, -cam_y))
