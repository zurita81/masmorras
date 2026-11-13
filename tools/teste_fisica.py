"""Testes automáticos da física (rodam sem abrir janela).

Uso:  python tools/teste_fisica.py
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from config import TAM  # noqa: E402
from jogador import Entrada, Jogador  # noqa: E402
from jogo import Jogo  # noqa: E402

falhas = []


def confere(nome, condicao, detalhe=""):
    print(("  OK   " if condicao else "  FALHOU ") + nome + (f"  [{detalhe}]" if detalhe else ""))
    if not condicao:
        falhas.append(nome)


def novo():
    j = Jogo()
    return j, j.jogador, j.nivel


def rodar(jogo, n, **kw):
    for _ in range(n):
        jogo.atualizar(Entrada(**kw))


print("Fase carrega e jogador pousa no chão")
jogo, jog, niv = novo()
rodar(jogo, 60)
chao_y = max(y for (_, y) in niv.solidos) - 1  # primeira linha de chão = topo do piso
topo_piso = min(y for (x, y) in niv.solidos if x == 10 and y > 10) * TAM
confere("está no chão", jog.no_chao)
confere("pés exatamente em cima do piso", jog.rect.bottom == topo_piso, f"{jog.rect.bottom} vs {topo_piso}")

print("Andar e bater na parede/bloco")
rodar(jogo, 400, direita=True)
bloco_x = min(x for (x, y) in niv.solidos if 5 < y < 15 and 5 < x < 55) * TAM
confere("parou antes do bloco", jog.rect.right <= bloco_x and jog.rect.right > bloco_x - 4,
        f"direita={jog.rect.right} bloco={bloco_x}")
x_antes = jog.x
rodar(jogo, 60, direita=True)
confere("empurrando o bloco não atravessa nem treme", jog.x == x_antes, f"{x_antes} -> {jog.x}")

print("Altura do pulo")
jogo, jog, niv = novo()
rodar(jogo, 30)
base = jog.rect.bottom
alt_max = 0
jogo.atualizar(Entrada(pulo_apertou=True, pulo_segurando=True))
for _ in range(70):
    jogo.atualizar(Entrada(pulo_segurando=True))
    alt_max = max(alt_max, base - jog.rect.bottom)
confere("pulo completo entre 65 e 90 px", 65 <= alt_max <= 90, f"{alt_max}px")

jogo, jog, niv = novo()
rodar(jogo, 30)
base = jog.rect.bottom
jogo.atualizar(Entrada(pulo_apertou=True, pulo_segurando=True))
curto = 0
for _ in range(70):
    jogo.atualizar(Entrada(pulo_segurando=False))
    curto = max(curto, base - jog.rect.bottom)
confere("pulo curto é menor que o completo", curto < alt_max - 15, f"{curto}px")

print("Plataforma fina (atravessa por baixo, pousa em cima, desce com baixo+pulo)")
plat = sorted((x, y) for (x, y) in niv.plataformas if y == 11)
px_centro = (plat[len(plat) // 2][0]) * TAM + TAM // 2
topo_plat = 11 * TAM
jogo, jog, niv = novo()
jog.x = px_centro - jog.LARG // 2
jog.y = topo_piso - jog.ALT
rodar(jogo, 10)
jogo.atualizar(Entrada(pulo_apertou=True, pulo_segurando=True))
rodar(jogo, 80, pulo_segurando=True)
confere("subiu e pousou em cima da plataforma", jog.no_chao and jog.rect.bottom == topo_plat,
        f"pés={jog.rect.bottom} topo={topo_plat}")
jogo.atualizar(Entrada(baixo=True, pulo_apertou=True, pulo_segurando=True))
rodar(jogo, 80)
confere("desceu atravessando e voltou ao piso", jog.rect.bottom == topo_piso, f"pés={jog.rect.bottom}")

print("Coyote time (pular logo depois de sair da borda)")
jogo, jog, niv = novo()
jog.x = plat[-1][0] * TAM + TAM - jog.LARG - 2
jog.y = topo_plat - jog.ALT
rodar(jogo, 5)
rodar(jogo, 30, direita=True)
for _ in range(60):
    jogo.atualizar(Entrada(direita=True))
    if not jog.no_chao:
        break
jogo.atualizar(Entrada(direita=True))
jogo.atualizar(Entrada(direita=True, pulo_apertou=True, pulo_segurando=True))
confere("pulou no ar logo depois da borda", jog.vy < 0, f"vy={jog.vy}")

print("Câmera fica dentro da fase")
jogo, jog, niv = novo()
rodar(jogo, 600, direita=True)
confere("câmera dentro dos limites", 0 <= jogo.camera.x <= niv.largura_px - 480 and 0 <= jogo.camera.y)

print("\n" + ("TUDO CERTO" if not falhas else f"{len(falhas)} FALHA(S): {falhas}"))
sys.exit(1 if falhas else 0)
