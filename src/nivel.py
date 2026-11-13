"""Cenário: lê o mapa em texto, desenha os blocos e responde sobre colisões."""
import random

import pygame

from config import TAM

# Paleta de pedra sombria
PEDRA = (62, 52, 60)
PEDRA_CLARA = (86, 74, 82)
PEDRA_ESCURA = (44, 36, 46)
MASSA = (34, 27, 35)
MUSGO = (70, 108, 62)
MUSGO_ESCURO = (42, 70, 46)
MADEIRA = (116, 76, 44)
MADEIRA_ESCURA = (70, 44, 28)
FERRO = (112, 114, 128)


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
        self.solidos = set()
        self.plataformas = set()
        self.inicio = (TAM * 2, TAM * 2)  # (x do centro, y dos pés)
        for y, linha in enumerate(linhas):
            for x, c in enumerate(linha):
                if c == "#":
                    self.solidos.add((x, y))
                elif c == "=":
                    self.plataformas.add((x, y))
                elif c == "P":
                    self.inicio = (x * TAM + TAM // 2, (y + 1) * TAM)
        self.imagem = self._pre_desenhar()

    # ---------- colisões ----------
    def _tiles_em(self, rect, conjunto):
        x0, x1 = rect.left // TAM, (rect.right - 1) // TAM
        y0, y1 = rect.top // TAM, (rect.bottom - 1) // TAM
        for ty in range(y0, y1 + 1):
            for tx in range(x0, x1 + 1):
                if (tx, ty) in conjunto:
                    yield pygame.Rect(tx * TAM, ty * TAM, TAM, TAM)

    def solidos_em(self, rect):
        return self._tiles_em(rect, self.solidos)

    def plataformas_em(self, rect):
        return self._tiles_em(rect, self.plataformas)

    # ---------- desenho ----------
    def _pre_desenhar(self):
        img = pygame.Surface((self.largura_px, self.altura_px), pygame.SRCALPHA)
        for (x, y) in self.solidos:
            livre_em_cima = (x, y - 1) not in self.solidos
            img.blit(self._bloco(x, y, livre_em_cima), (x * TAM, y * TAM))
        for (x, y) in self.plataformas:
            img.blit(self._tabua(x, y), (x * TAM, y * TAM))
        return img

    def _bloco(self, x, y, com_musgo):
        rng = random.Random(x * 7919 + y * 104729)
        s = pygame.Surface((TAM, TAM))
        s.fill(PEDRA)
        for px in range(TAM):  # ruído leve para a pedra não ficar chapada
            for py in range(TAM):
                if rng.random() < 0.12:
                    s.set_at((px, py), PEDRA_CLARA if rng.random() < 0.5 else PEDRA_ESCURA)
        for ly in (7, 15):  # argamassa horizontal e vertical alternada
            pygame.draw.line(s, MASSA, (0, ly), (TAM - 1, ly))
        pygame.draw.line(s, MASSA, (7, 0), (7, 6))
        pygame.draw.line(s, MASSA, (3 if (y % 2) else 12, 8), (3 if (y % 2) else 12, 14))
        if com_musgo:
            pygame.draw.line(s, PEDRA_CLARA, (0, 0), (TAM - 1, 0))
            pygame.draw.rect(s, MUSGO_ESCURO, (0, 0, TAM, 3))
            pygame.draw.rect(s, MUSGO, (0, 0, TAM, 2))
            for px in range(TAM):
                if rng.random() < 0.35:
                    s.set_at((px, 3), MUSGO_ESCURO)
                if rng.random() < 0.15:
                    s.set_at((px, 4), MUSGO_ESCURO)
        return s

    def _tabua(self, x, y):
        s = pygame.Surface((TAM, TAM), pygame.SRCALPHA)
        pygame.draw.rect(s, MADEIRA, (0, 0, TAM, 5))
        pygame.draw.rect(s, MADEIRA_ESCURA, (0, 4, TAM, 1))
        pygame.draw.line(s, (150, 104, 62), (0, 0), (TAM - 1, 0))
        if (x, y) and (x - 1, y) not in self.plataformas:
            pygame.draw.rect(s, FERRO, (0, 0, 2, 5))
        if (x + 1, y) not in self.plataformas:
            pygame.draw.rect(s, FERRO, (TAM - 2, 0, 2, 5))
        return s

    def desenhar(self, tela, cam_x, cam_y):
        tela.blit(self.imagem, (-cam_x, -cam_y))
