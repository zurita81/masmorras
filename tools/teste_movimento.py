"""Testes automáticos do movimento (rodam sem abrir janela).

Uso:  python tools/teste_movimento.py
"""
import math
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from config import ALTURA, LARGURA, TAM  # noqa: E402
from jogador import Entrada  # noqa: E402
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


def pos_pes(jog, x_tile, y_tile):
    """Coloca o jogador com os pés no centro de um bloco."""
    jog.x = x_tile * TAM + TAM // 2 - jog.LARG // 2
    jog.y = y_tile * TAM + TAM // 2 - jog.ALT // 2
    jog.vx = jog.vy = jog.rx = jog.ry = 0.0


print("Parado fica parado")
jogo, jog, niv = novo()
x0, y0 = jog.x, jog.y
rodar(jogo, 60)
confere("não se mexe sozinho", (jog.x, jog.y) == (x0, y0))

print("Andar nas 4 direções")
for nome, kw, eixo, sinal in (("direita", {"direita": True}, "x", 1), ("esquerda", {"esquerda": True}, "x", -1),
                              ("baixo", {"baixo": True}, "y", 1), ("cima", {"cima": True}, "y", -1)):
    jogo, jog, niv = novo()
    pos_pes(jog, 20, 4 if nome == "baixo" else 20)  # área livre
    ini = getattr(jog, eixo)
    rodar(jogo, 30, **kw)
    confere(f"anda para {nome}", (getattr(jog, eixo) - ini) * sinal > 20, f"{getattr(jog, eixo) - ini}px")

print("Diagonal não é mais rápida")
jogo, jog, niv = novo()
pos_pes(jog, 12, 4)
a = (jog.x, jog.y)
rodar(jogo, 40, direita=True)
reta = math.hypot(jog.x - a[0], jog.y - a[1])
jogo, jog, niv = novo()
pos_pes(jog, 12, 4)
a = (jog.x, jog.y)
rodar(jogo, 40, direita=True, baixo=True)
diag = math.hypot(jog.x - a[0], jog.y - a[1])
confere("distância na diagonal ≈ distância reta", abs(diag - reta) / reta < 0.06, f"reta={reta:.1f} diag={diag:.1f}")

print("Paredes")
jogo, jog, niv = novo()
pos_pes(jog, 20, 4)
rodar(jogo, 200, cima=True)
confere("para na parede de cima", jog.rect.top >= 2 * TAM and jog.rect.top <= 2 * TAM + 2,
        f"topo={jog.rect.top}")
y_antes = jog.y
rodar(jogo, 40, cima=True)
confere("empurrar a parede não faz tremer", jog.y == y_antes)

jogo, jog, niv = novo()
pos_pes(jog, 5, 8)  # à esquerda do pilar 2x2 em (8..9, 8..9)
rodar(jogo, 200, direita=True)
confere("pilar bloqueia", jog.rect.right <= 8 * TAM and jog.rect.right >= 8 * TAM - 2,
        f"direita={jog.rect.right}")

jogo, jog, niv = novo()
pos_pes(jog, 20, 4)
rodar(jogo, 100, cima=True)
x_antes = jog.x
rodar(jogo, 40, cima=True, direita=True)
confere("desliza ao longo da parede na diagonal", jog.x - x_antes > 20, f"{jog.x - x_antes}px")

jogo, jog, niv = novo()
pos_pes(jog, 20, 20)
rodar(jogo, 400, baixo=True)
confere("parede de baixo também segura", jog.rect.bottom <= (niv.lins - 2) * TAM, f"baixo={jog.rect.bottom}")

print("Direção do sprite")
jogo, jog, niv = novo()
pos_pes(jog, 20, 4)
rodar(jogo, 3, esquerda=True)
confere("esquerda -> lado, virado para a esquerda", jog.direcao == "lado" and not jog.olhando_direita)
rodar(jogo, 3, baixo=True)
confere("baixo -> frente", jog.direcao == "baixo")
rodar(jogo, 3, cima=True)
confere("cima -> costas", jog.direcao == "cima")

print("Personagens")
from jogo import PERSONAGENS_JOGAVEIS  # noqa: E402
import recursos  # noqa: E402

for slug in PERSONAGENS_JOGAVEIS + ("lobo",):
    folha = recursos.carregar_topo(slug)
    ok = all(len(folha[d]) == 6 and folha[d][0].get_size() == (32, 32) for d in ("baixo", "cima", "lado", "lado_esq"))
    confere(f"sprites de {slug} carregam (3 direções x 6 quadros)", ok)

jogo, jog, niv = novo()
desenhou = True
tela_teste = pygame.Surface((LARGURA, ALTURA))
for slug in PERSONAGENS_JOGAVEIS:
    jogo.trocar_personagem(slug)
    for kw in ({"direita": True}, {"esquerda": True}, {"baixo": True}, {"cima": True}, {}):
        pos_pes(jog, 20, 12)
        try:
            rodar(jogo, 12, **kw)
            jogo.desenhar(tela_teste)
        except Exception as e:  # noqa: BLE001
            desenhou = False
            print("   erro:", slug, kw, e)
confere("todos os 5 personagens andam e são desenhados em todas as direções", desenhou)


def distancia_em_40(slug):
    j, jg, _ = novo()
    jg.definir_personagem(slug)
    pos_pes(jg, 8, 12)
    x0 = jg.x
    rodar(j, 40, direita=True)
    return jg.x - x0


confere("lobo corre mais que o cavaleiro", distancia_em_40("lobo") > distancia_em_40("cavaleiro") * 1.2,
        f"lobo={distancia_em_40('lobo')}px cavaleiro={distancia_em_40('cavaleiro')}px")

jogo, jog, niv = novo()
jogo.trocar_personagem("mago")
jogo.transformar()
confere("T não transforma o mago", jog.personagem == "mago")
jogo.trocar_personagem("metamorfo")
jogo.transformar()
confere("T transforma o metamorfo em lobo", jog.personagem == "lobo")
jogo.transformar()
confere("T de novo volta a metamorfo", jog.personagem == "metamorfo")
jogo.trocar_personagem("lobo")
confere("o lobo não é escolhido direto pelas teclas", jog.personagem == "metamorfo")

print("Câmera")
jogo, jog, niv = novo()
rodar(jogo, 300, direita=True, baixo=True)
confere("câmera dentro dos limites",
        0 <= jogo.camera.x <= niv.largura_px - LARGURA and 0 <= jogo.camera.y <= niv.altura_px - ALTURA)

print("\n" + ("TUDO CERTO" if not falhas else f"{len(falhas)} FALHA(S): {falhas}"))
sys.exit(1 if falhas else 0)
