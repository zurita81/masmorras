"""Jogador: movimento, pulo e colisão com o cenário.

A posição é sempre em pixels inteiros e o movimento é feito pixel a pixel,
assim o personagem nunca "treme" nem atravessa um bloco.
"""
from dataclasses import dataclass

import pygame

import recursos

# ---------- ajustes de sensação (mexa aqui para mudar o jogo) ----------
VEL_MAX = 2.3          # velocidade máxima andando (pixels por quadro)
ACEL_CHAO = 0.28
ACEL_AR = 0.20
ATRITO_CHAO = 0.30
ATRITO_AR = 0.08
GRAVIDADE = 0.50
GRAVIDADE_PULO_CURTO = 1.10   # gravidade extra se soltar o botão subindo
VEL_QUEDA_MAX = 9.0
FORCA_PULO = 8.8
QUADROS_COYOTE = 6     # ainda pode pular logo depois de sair da borda
QUADROS_BUFFER = 6     # pulo apertado um pouco antes de pousar vale
QUADROS_DESCER = 12    # tempo atravessando plataforma ao descer


@dataclass
class Entrada:
    esquerda: bool = False
    direita: bool = False
    baixo: bool = False
    pulo_apertou: bool = False     # só no quadro em que apertou
    pulo_segurando: bool = False


class Jogador:
    LARG, ALT = 12, 34

    def __init__(self, x_centro, y_pes, personagem="cavaleiro"):
        self.x = int(x_centro - self.LARG // 2)
        self.y = int(y_pes - self.ALT)
        self.rx = 0.0  # resto fracionário do movimento
        self.ry = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.no_chao = False
        self.olhando_direita = True
        self.coyote = 0
        self.buffer = 0
        self.ignora_plataforma = 0
        self.tempo = 0
        self.quadros_dir, self.quadros_esq = recursos.carregar_quadros(personagem)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.LARG, self.ALT)

    # ---------- lógica ----------
    def atualizar(self, entrada, nivel):
        self.tempo += 1
        direcao = int(entrada.direita) - int(entrada.esquerda)

        # horizontal
        acel = ACEL_CHAO if self.no_chao else ACEL_AR
        atrito = ATRITO_CHAO if self.no_chao else ATRITO_AR
        if direcao:
            self.vx += direcao * acel
            self.vx = max(-VEL_MAX, min(VEL_MAX, self.vx))
            self.olhando_direita = direcao > 0
        elif self.vx > 0:
            self.vx = max(0.0, self.vx - atrito)
        elif self.vx < 0:
            self.vx = min(0.0, self.vx + atrito)

        # pulo (com "coyote time" e "jump buffer" para perdoar erros)
        self.buffer = QUADROS_BUFFER if entrada.pulo_apertou else max(0, self.buffer - 1)
        self.coyote = QUADROS_COYOTE if self.no_chao else max(0, self.coyote - 1)
        self.ignora_plataforma = max(0, self.ignora_plataforma - 1)

        if self.buffer and self.coyote:
            if entrada.baixo and self._em_plataforma(nivel):
                self.ignora_plataforma = QUADROS_DESCER  # desce atravessando
                self.y += 1
            else:
                self.vy = -FORCA_PULO
            self.buffer = 0
            self.coyote = 0

        # gravidade
        g = GRAVIDADE
        if self.vy < 0 and not entrada.pulo_segurando:
            g += GRAVIDADE_PULO_CURTO
        self.vy = min(VEL_QUEDA_MAX, self.vy + g)

        self._mover_x(nivel)
        self._mover_y(nivel)
        self.no_chao = self._tem_apoio(nivel)

    def _mover_x(self, nivel):
        self.rx += self.vx
        passos = int(self.rx)
        self.rx -= passos
        sinal = 1 if passos > 0 else -1
        for _ in range(abs(passos)):
            alvo = self.rect.move(sinal, 0)
            if any(alvo.colliderect(b) for b in nivel.solidos_em(alvo)):
                self.vx = 0.0
                self.rx = 0.0
                break
            self.x += sinal

    def _mover_y(self, nivel):
        self.ry += self.vy
        passos = int(self.ry)
        self.ry -= passos
        sinal = 1 if passos > 0 else -1
        for _ in range(abs(passos)):
            atual = self.rect
            alvo = atual.move(0, sinal)
            if any(alvo.colliderect(b) for b in nivel.solidos_em(alvo)):
                self.vy = 0.0
                self.ry = 0.0
                break
            if sinal > 0 and self.ignora_plataforma == 0:
                if any(alvo.colliderect(b) and atual.bottom <= b.top
                       for b in nivel.plataformas_em(alvo)):
                    self.vy = 0.0
                    self.ry = 0.0
                    break
            self.y += sinal

    def _tem_apoio(self, nivel):
        r = self.rect
        embaixo = r.move(0, 1)
        if any(embaixo.colliderect(b) for b in nivel.solidos_em(embaixo)):
            return True
        if self.ignora_plataforma == 0:
            return any(embaixo.colliderect(b) and r.bottom <= b.top
                       for b in nivel.plataformas_em(embaixo))
        return False

    def _em_plataforma(self, nivel):
        """True se está em cima de uma plataforma fina (e não de um bloco sólido)."""
        r = self.rect
        embaixo = r.move(0, 1)
        if any(embaixo.colliderect(b) for b in nivel.solidos_em(embaixo)):
            return False
        return any(embaixo.colliderect(b) and r.bottom <= b.top
                   for b in nivel.plataformas_em(embaixo))

    # ---------- desenho ----------
    def desenhar(self, tela, cam_x, cam_y):
        quadros = self.quadros_dir if self.olhando_direita else self.quadros_esq
        img = quadros[(self.tempo // 30) % len(quadros)]
        r = self.rect
        # o sprite tem 40x40 e os pés ficam na linha 38; o centro do corpo, perto da coluna 18/21
        esq = r.centerx - (18 if self.olhando_direita else 21)
        topo = r.bottom - 39
        tela.blit(img, (esq - cam_x, topo - cam_y))
