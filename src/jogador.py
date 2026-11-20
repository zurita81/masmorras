"""Jogador visto de cima: movimento em 8 direções, colisão com paredes e animação.

A posição é sempre em pixels inteiros e o movimento é feito pixel a pixel,
assim o personagem nunca "treme" nem atravessa uma parede.
O corpo de colisão é só uma caixa pequena nos pés (como em Zelda/Soul Knight):
a cabeça pode passar "por trás" das paredes.
"""
import math
from dataclasses import dataclass

import pygame

import recursos

# ---------- ajustes de sensação (mexa aqui para mudar o jogo) ----------
VEL = 1.5       # velocidade andando (pixels por quadro, 60 quadros por segundo)
ACEL = 0.25     # quão rápido chega na velocidade máxima
ATRITO = 0.30   # quão rápido para ao soltar as teclas


@dataclass
class Entrada:
    esquerda: bool = False
    direita: bool = False
    cima: bool = False
    baixo: bool = False


def _aproximar(valor, alvo, passo):
    if valor < alvo:
        return min(alvo, valor + passo)
    return max(alvo, valor - passo)


class Jogador:
    LARG, ALT = 12, 8  # caixa de colisão nos pés

    def __init__(self, x_centro, y_pes, personagem="cavaleiro"):
        self.x = int(x_centro - self.LARG // 2)
        self.y = int(y_pes - self.ALT)
        self.rx = 0.0  # restos fracionários do movimento
        self.ry = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.direcao = "baixo"
        self.olhando_direita = True
        self.tempo = 0
        self.deu_passo = False  # vira True no quadro em que um pé toca o chão (para o som)
        self.quadros = recursos.carregar_topo(personagem)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.LARG, self.ALT)

    @property
    def andando(self):
        return math.hypot(self.vx, self.vy) > 0.3

    # ---------- lógica ----------
    def atualizar(self, entrada, nivel):
        self.tempo += 1
        dx = int(entrada.direita) - int(entrada.esquerda)
        dy = int(entrada.baixo) - int(entrada.cima)
        if dx or dy:
            n = math.hypot(dx, dy)  # na diagonal não anda mais rápido
            alvo_x, alvo_y, passo = dx / n * VEL, dy / n * VEL, ACEL
        else:
            alvo_x = alvo_y = 0.0
            passo = ATRITO
        self.vx = _aproximar(self.vx, alvo_x, passo)
        self.vy = _aproximar(self.vy, alvo_y, passo)

        if dx:
            self.direcao = "lado"
            self.olhando_direita = dx > 0
        elif dy > 0:
            self.direcao = "baixo"
        elif dy < 0:
            self.direcao = "cima"

        self._mover(nivel, 0)
        self._mover(nivel, 1)
        # um passo a cada 14 quadros (a cada 2 trocas de quadro da animação)
        self.deu_passo = self.andando and self.tempo % 14 == 0

    def _mover(self, nivel, eixo):
        if eixo == 0:
            self.rx += self.vx
            passos = int(self.rx)
            self.rx -= passos
        else:
            self.ry += self.vy
            passos = int(self.ry)
            self.ry -= passos
        sinal = 1 if passos > 0 else -1
        for _ in range(abs(passos)):
            alvo = self.rect.move(sinal if eixo == 0 else 0, sinal if eixo == 1 else 0)
            if any(alvo.colliderect(p) for p in nivel.paredes_em(alvo)):
                if eixo == 0:
                    self.vx, self.rx = 0.0, 0.0
                else:
                    self.vy, self.ry = 0.0, 0.0
                break
            if eixo == 0:
                self.x += sinal
            else:
                self.y += sinal

    # ---------- desenho ----------
    def desenhar(self, tela, cam_x, cam_y):
        nome = self.direcao
        if nome == "lado" and not self.olhando_direita:
            nome = "lado_esq"
        if self.andando:
            i = (self.tempo // 7) % 4          # 4 quadros de caminhada
        else:
            i = 4 + (self.tempo // 32) % 2     # 2 quadros respirando
        img = self.quadros[nome][i]
        r = self.rect
        # sprite 32x32: pés na linha 29 e corpo centrado na coluna 16
        tela.blit(img, (r.centerx - 16 - cam_x, r.bottom - 30 - cam_y))
