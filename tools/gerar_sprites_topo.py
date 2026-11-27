"""Gera os sprites em pixel art em vista de cima (3/4), 32x32 pixels.

Cada personagem vira uma folha com 3 linhas (baixo, cima, lado-direita) e 6 colunas:
  colunas 0-3 = andando (4 quadros)   colunas 4-5 = parado (respirando)
O lado esquerdo é feito espelhando o direito dentro do jogo.

Luz vinda de cima à esquerda: cada peça tem um tom claro à esquerda/em cima
e um tom escuro à direita/embaixo, o que dá volume.

Uso:  python tools/gerar_sprites_topo.py
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 32
COLS = 6
DIRECOES = ["baixo", "cima", "lado"]
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "assets", "sprites")

# ---------- paleta sombria ----------
OUT = (14, 10, 12, 255)
AÇO_L, AÇO, AÇO_D, AÇO_DD = (176, 178, 192, 255), (112, 114, 130, 255), (66, 68, 84, 255), (44, 46, 60, 255)
BRILHO = (236, 238, 246, 255)
RUBI_L, RUBI, RUBI_D = (200, 56, 64, 255), (156, 30, 40, 255), (98, 16, 28, 255)
OURO_L, OURO, OURO_D = (250, 222, 128, 255), (222, 176, 72, 255), (150, 108, 40, 255)
COURO, MARROM, MARROM_D = (138, 92, 54, 255), (112, 72, 42, 255), (68, 42, 28, 255)
VISOR = (22, 16, 24, 255)
ÂMBAR = (244, 196, 64, 255)


class Tela:
    def __init__(self):
        self.p = {}

    def px(self, x, y, cor):
        if 0 <= x < W and 0 <= y < H:
            self.p[(x, y)] = cor

    def ret(self, x0, y0, x1, y1, cor):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, cor)

    def apagar(self, x, y):
        self.p.pop((x, y), None)

    def linha(self, x0, y0, x1, y1, cor):
        passos = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(passos + 1):
            self.px(round(x0 + (x1 - x0) * i / passos), round(y0 + (y1 - y0) * i / passos), cor)

    def imagem(self):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for y in range(27, 32):  # sombra no chão (elipse translúcida)
            for x in range(3, 29):
                dx, dy = (x - 15.5) / 10.5, (y - 29.5) / 2.4
                if dx * dx + dy * dy <= 1:
                    img.putpixel((x, y), (0, 0, 0, 90))
        # contorno "colorido": em vez de preto chapado, usa uma versão bem escura da cor vizinha
        # (técnica "selout"), o que deixa o desenho mais suave e profissional
        vizinhas = {}
        for (x, y), cor in self.p.items():
            for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                v = (x + ox, y + oy)
                if v not in self.p and 0 <= v[0] < W and 0 <= v[1] < H:
                    vizinhas.setdefault(v, []).append((cor, oy))
        cont = {}
        for v, lista in vizinhas.items():
            media = [sum(c[i] for c, _ in lista) / len(lista) for i in range(3)]
            fator = 0.20 if any(oy == -1 for _, oy in lista) else 0.30  # embaixo fica mais escuro
            cont[v] = tuple(int(media[i] * fator + OUT[i] * 0.55) for i in range(3)) + (255,)
        for pos, cor in {**cont, **self.p}.items():
            img.putpixel(pos, cor)
        return img


def caixa(t, x0, y0, x1, y1, base, luz=None, sombra=None, cantos=()):
    """Retângulo com tom claro (esq/cima) e escuro (dir/baixo) para dar volume."""
    t.ret(x0, y0, x1, y1, base)
    if luz:
        t.ret(x0, y0, x1, y0, luz)
        t.ret(x0, y0, x0, y1, luz)
    if sombra:
        t.ret(x0, y1, x1, y1, sombra)
        t.ret(x1, y0, x1, y1, sombra)
    for c in cantos:
        t.apagar(*c)


# ======================= CAVALEIRO =======================
def _elmo(t, u):
    linhas = [(4, 13, 18), (5, 11, 20)] + [(y, 10, 21) for y in range(6, 14)] + [(14, 11, 20)]
    for y, a, b in linhas:
        for x in range(a, b + 1):
            cor = AÇO
            if x <= a + 1:
                cor = AÇO_L
            elif x >= b - 1:
                cor = AÇO_D
            t.px(x, y + u, cor)
    t.px(12, 5 + u, BRILHO)
    t.px(11, 6 + u, BRILHO)


def _ombreiras(t, u):
    for x0 in (8, 20):
        caixa(t, x0, 16 + u, x0 + 3, 19 + u, AÇO, AÇO_L, AÇO_D)
        t.px(x0 + 1, 17 + u, OURO)


def _pernas_frente(t, fase, andando):
    lev = {0: (2, 0), 2: (0, 2)}.get(fase, (0, 0)) if andando else (0, 0)
    for x0, l, bx in ((12, lev[0], 11), (17, lev[1], 17)):
        caixa(t, x0, 25 - l, x0 + 2, 27 - l, AÇO_D, AÇO, AÇO_DD)
        caixa(t, bx, 28 - l, bx + 3, 29 - l, MARROM_D, COURO, (38, 24, 18, 255))


def _frente(t, fase, andando, u):
    _pernas_frente(t, fase, andando)
    caixa(t, 11, 16 + u, 20, 24, AÇO, AÇO_L, AÇO_D)
    caixa(t, 14, 17 + u, 17, 24, RUBI, RUBI_L, RUBI_D)
    t.ret(11, 22, 20, 22, OURO)
    t.ret(11, 23, 20, 23, OURO_D)
    t.ret(15, 22, 16, 23, OURO_L)
    # escudo (direita do desenho)
    caixa(t, 21, 18 + u, 26, 25, OURO_D, OURO, OURO_D, cantos=((21, 25), (26, 25)))
    caixa(t, 22, 19 + u, 25, 24, AÇO, AÇO_L, AÇO_D)
    t.ret(23, 20 + u, 24, 23, OURO)
    t.ret(22, 21 + u, 25, 21 + u, OURO)
    # espada (esquerda do desenho)
    caixa(t, 7, 20 + u, 9, 23, AÇO_D, AÇO, AÇO_DD)
    t.ret(5, 8 + u, 6, 20 + u, AÇO_L)
    t.ret(6, 8 + u, 6, 20 + u, AÇO)
    t.px(5, 7 + u, AÇO_L)
    t.ret(3, 21 + u, 8, 21 + u, OURO)
    t.ret(5, 22 + u, 6, 24 + u, MARROM)
    t.ret(5, 25 + u, 6, 25 + u, OURO_D)
    _ombreiras(t, u)
    t.ret(12, 15 + u, 19, 16 + u, AÇO_D)
    _elmo(t, u)
    t.ret(11, 9 + u, 20, 10 + u, VISOR)
    t.ret(13, 10 + u, 14, 10 + u, ÂMBAR)
    t.ret(17, 10 + u, 18, 10 + u, ÂMBAR)
    t.ret(15, 4 + u, 16, 8 + u, AÇO_L)
    t.ret(15, 11 + u, 16, 14 + u, AÇO_L)
    t.ret(14, 12 + u, 17, 12 + u, AÇO_D)
    # pluma vermelha
    t.px(15, 1 + u, RUBI_L)
    t.px(16, 1 + u, RUBI)
    caixa(t, 14, 2 + u, 17, 3 + u, RUBI, RUBI_L, RUBI_D)


def _costas(t, fase, andando, u):
    _pernas_frente(t, fase, andando)
    caixa(t, 5, 18 + u, 9, 25, OURO_D, OURO, OURO_D, cantos=((5, 25),))
    caixa(t, 6, 19 + u, 9, 24, AÇO_D, AÇO, AÇO_DD)
    caixa(t, 22, 20 + u, 24, 23, AÇO_D, AÇO, AÇO_DD)
    caixa(t, 10, 16 + u, 21, 26, RUBI, RUBI_L, RUBI_D, cantos=((10, 26), (21, 26)))
    for x in (13, 16, 19):
        t.ret(x, 18 + u, x, 25, RUBI_D)
    t.ret(11, 26, 20, 26, OURO_D)
    t.ret(25, 8 + u, 26, 20 + u, AÇO_L)
    t.ret(26, 8 + u, 26, 20 + u, AÇO)
    t.px(25, 7 + u, AÇO_L)
    t.ret(23, 21 + u, 28, 21 + u, OURO)
    t.ret(25, 22 + u, 26, 24 + u, MARROM)
    t.ret(25, 25 + u, 26, 25 + u, OURO_D)
    _ombreiras(t, u)
    t.ret(12, 15 + u, 19, 16 + u, AÇO_D)
    _elmo(t, u)
    t.ret(10, 10 + u, 21, 10 + u, AÇO_D)
    t.px(12, 8 + u, AÇO_D)
    t.px(19, 8 + u, AÇO_D)
    caixa(t, 14, 1 + u, 17, 13 + u, RUBI, RUBI_L, RUBI_D)


def _perna_lado(t, x0, lev, tras):
    cor, luz, som = (AÇO_DD, AÇO_D, OUT) if tras else (AÇO_D, AÇO, AÇO_DD)
    bota = (50, 32, 22, 255) if tras else MARROM_D
    caixa(t, x0, 25 - lev, x0 + 2, 27 - lev, cor, luz, som)
    caixa(t, x0, 28 - lev, x0 + 3, 29 - lev, bota, MARROM if tras else COURO, (30, 18, 14, 255))


def _lado(t, fase, andando, u):
    caixa(t, 7, 16 + u, 12, 27, RUBI, RUBI_L, RUBI_D, cantos=((7, 27),))
    t.ret(8, 27, 12, 27, OURO_D)
    if andando:
        xt, xf = {0: (11, 17), 1: (14, 15), 2: (17, 11), 3: (15, 14)}[fase]
    else:
        xt, xf = 13, 16
    lev = 1 if (andando and fase in (1, 3)) else 0
    _perna_lado(t, xt, 0, True)
    _perna_lado(t, xf, lev, False)
    caixa(t, 12, 16 + u, 19, 24, AÇO, AÇO_L, AÇO_D)
    t.ret(12, 22, 19, 22, OURO)
    t.ret(12, 23, 19, 23, OURO_D)
    # escudo no braço de perto
    caixa(t, 11, 18 + u, 16, 26, OURO_D, OURO, OURO_D, cantos=((11, 26), (16, 26)))
    caixa(t, 12, 19 + u, 15, 25, AÇO, AÇO_L, AÇO_D)
    t.ret(13, 20 + u, 14, 24, OURO)
    caixa(t, 13, 16 + u, 17, 19 + u, AÇO, AÇO_L, AÇO_D)
    t.px(15, 17 + u, OURO)
    # espada para a frente
    caixa(t, 17, 20 + u, 20, 22 + u, AÇO_D, AÇO, AÇO_DD)
    t.ret(19, 20 + u, 20, 21 + u, MARROM)
    t.ret(22, 19 + u, 30, 19 + u, AÇO_L)
    t.ret(22, 20 + u, 30, 20 + u, AÇO)
    t.ret(21, 17 + u, 21, 22 + u, OURO)
    t.ret(13, 15 + u, 18, 16 + u, AÇO_D)
    _elmo(t, u)
    t.ret(15, 9 + u, 21, 10 + u, VISOR)
    t.px(19, 10 + u, ÂMBAR)
    t.ret(19, 12 + u, 20, 12 + u, AÇO_D)
    t.px(11, 10 + u, AÇO_D)
    t.ret(13, 2 + u, 17, 3 + u, RUBI)
    t.ret(13, 2 + u, 17, 2 + u, RUBI_L)
    t.ret(7, 3 + u, 12, 4 + u, RUBI)
    t.ret(4, 4 + u, 8, 5 + u, RUBI_D)


def cavaleiro(direcao, q):
    t = Tela()
    andando = q < 4
    fase = q if andando else 0
    u = -1 if ((andando and q in (1, 3)) or q == 5) else 0
    {"baixo": _frente, "cima": _costas, "lado": _lado}[direcao](t, fase, andando, u)
    return t.imagem()


# ======================= PALETAS E PEÇAS COMUNS =======================
BRANCO = (240, 236, 228, 255)
PELE_L, PELE, PELE_D = (246, 212, 178, 255), (226, 184, 146, 255), (170, 122, 98, 255)
OSSO, OSSO_D = (228, 220, 196, 255), (162, 152, 132, 255)
ROXO_L, ROXO, ROXO_D, ROXO_DD = (148, 108, 190, 255), (104, 64, 140, 255), (66, 40, 96, 255), (40, 24, 64, 255)
VERDE_L, VERDE, VERDE_D, VERDE_DD = (128, 170, 86, 255), (76, 118, 64, 255), (44, 76, 48, 255), (26, 48, 32, 255)
FOLHA = (160, 224, 104, 255)
CIANO, CIANO_D = (130, 232, 240, 255), (60, 170, 190, 255)
PELO_L, PELO, PELO_D, PELO_DD = (196, 196, 208, 255), (144, 144, 158, 255), (92, 92, 108, 255), (58, 58, 72, 255)
TEAL_L, TEAL, TEAL_D = (96, 150, 146, 255), (62, 104, 104, 255), (34, 62, 66, 255)
COURO_L = (170, 118, 72, 255)
BOTA = (MARROM_D, COURO, (38, 24, 18, 255))
BOTA_TRAS = ((50, 32, 22, 255), MARROM, (30, 18, 14, 255))
CALCA_COURO = (MARROM_D, MARROM, (38, 24, 18, 255))
CABECA = [(4, 13, 18), (5, 11, 20)] + [(y, 10, 21) for y in range(6, 14)] + [(14, 11, 20)]


def forma(t, linhas, u, base, luz, som):
    """Desenha uma forma dada por linhas (y, x_inicio, x_fim), com luz à esquerda e sombra à direita."""
    for y, a, b in linhas:
        for x in range(a, b + 1):
            t.px(x, y + u, luz if x <= a + 1 else som if x >= b - 1 else base)


def pernas(t, fase, andando, calca, bota):
    lev = {0: (2, 0), 2: (0, 2)}.get(fase, (0, 0)) if andando else (0, 0)
    for x0, l, bx in ((12, lev[0], 11), (17, lev[1], 17)):
        caixa(t, x0, 25 - l, x0 + 2, 27 - l, *calca)
        caixa(t, bx, 28 - l, bx + 3, 29 - l, *bota)


def pernas_lado(t, fase, andando, calca, bota):
    xt, xf = {0: (11, 17), 1: (14, 15), 2: (17, 11), 3: (15, 14)}[fase] if andando else (13, 16)
    lev = 1 if (andando and fase in (1, 3)) else 0
    caixa(t, xt, 25, xt + 2, 27, calca[2], calca[2], OUT)
    caixa(t, xt, 28, xt + 3, 29, *BOTA_TRAS)
    caixa(t, xf, 25 - lev, xf + 2, 27 - lev, *calca)
    caixa(t, xf, 28 - lev, xf + 3, 29 - lev, *bota)


def tunica(t, direcao, fase, andando, u, pal, barra):
    """Túnica/manto comprido (mago, druida). A barra balança ao andar."""
    base, luz, som = pal
    d = {1: 1, 3: -1}.get(fase, 0) if andando else 0
    for y in range(16, 29):
        if direcao == "lado":
            a, b = (9, 21) if y >= 25 else (10, 20) if y >= 23 else (11, 19)
        else:
            a, b = (8, 23) if y >= 27 else (9, 22) if y >= 25 else (10, 21) if y >= 23 else (11, 20)
        if y >= 27:
            a, b = a + d, b + d
        yy = y + u if y <= 22 else y
        for x in range(a, b + 1):
            c = luz if x <= a + 1 else som if x >= b - 1 else base
            if y == 27:
                c = barra[0]
            elif y == 28:
                c = barra[1]
            t.px(x, yy, c)
    if direcao == "lado":
        t.ret(12 + d, 29, 15 + d, 29, BOTA[0])
    else:
        t.ret(12 + d, 29, 14 + d, 29, BOTA[0])
        t.ret(17 + d, 29, 19 + d, 29, BOTA[0])


def arco(t, x_corda, sentido, u, y0=7, y1=27):
    for y in range(y0 + u, y1 + 1):
        k = (y - (y0 + u)) / (y1 - (y0 + u))
        x = x_corda + sentido * round(3 * math.sin(math.pi * k))
        t.px(x, y, MARROM)
        if x != x_corda:
            t.px(x - sentido, y, COURO)
    t.ret(x_corda, y0 + 2 + u, x_corda, y1 - 2, BRANCO)


# ======================= MAGO =======================
def _chapeu(t, u):
    cone = [(9, 10, 21), (8, 11, 20), (7, 11, 20), (6, 12, 19), (5, 12, 19), (4, 13, 18), (3, 13, 18), (2, 14, 17)]
    forma(t, cone, u, ROXO, ROXO_L, ROXO_D)
    forma(t, [(1, 15, 19)], u, ROXO, ROXO_L, ROXO_D)
    t.ret(10, 9 + u, 21, 9 + u, OURO_D)
    caixa(t, 7, 10 + u, 24, 11 + u, ROXO_D, ROXO, ROXO_DD)


def _bastao_mago(t, x, u):
    t.ret(x, 8 + u, x + 1, 29, MARROM)
    t.ret(x, 8 + u, x, 29, COURO)
    caixa(t, x - 1, 3 + u, x + 2, 6 + u, CIANO, BRANCO, CIANO_D,
          cantos=((x - 1, 3 + u), (x + 2, 3 + u), (x - 1, 6 + u), (x + 2, 6 + u)))
    t.ret(x - 1, 7 + u, x + 2, 7 + u, MARROM_D)


def _braco_manga(t, x0, x1, u, pal, mao_x0, mao_x1):
    caixa(t, x0, 17 + u, x1, 23, *pal)
    t.ret(mao_x0, 24, mao_x1, 25, PELE)


def _mago_frente(t, fase, andando, u):
    pal = (ROXO, ROXO_L, ROXO_D)
    _bastao_mago(t, 23, u)
    tunica(t, "baixo", fase, andando, u, pal, (OURO, OURO_D))
    t.ret(11, 21, 20, 21, OURO)
    t.ret(11, 22, 20, 22, OURO_D)
    t.ret(15, 21, 16, 22, OURO_L)
    _braco_manga(t, 8, 10, u, pal, 8, 10)
    _braco_manga(t, 21, 23, u, pal, 22, 24)
    t.ret(12, 12 + u, 19, 14 + u, PELE)
    t.ret(18, 12 + u, 19, 14 + u, PELE_D)
    t.ret(15, 12 + u, 16, 13 + u, PELE_L)
    for x in (13, 14, 17, 18):
        t.px(x, 12 + u, CIANO)
    for y, a, b in [(14, 12, 19), (15, 12, 19), (16, 13, 18), (17, 13, 18), (18, 14, 17), (19, 14, 17), (20, 15, 16)]:
        for x in range(a, b + 1):
            t.px(x, y + u, BRANCO if x < (a + b) / 2 else OSSO)
    _chapeu(t, u)


def _mago_costas(t, fase, andando, u):
    pal = (ROXO, ROXO_L, ROXO_D)
    _bastao_mago(t, 23, u)
    tunica(t, "cima", fase, andando, u, pal, (OURO, OURO_D))
    t.ret(15, 18 + u, 16, 22 + u, OURO)
    t.ret(13, 20 + u, 18, 20 + u, OURO)
    t.px(15, 19 + u, OURO_L)
    _braco_manga(t, 8, 10, u, pal, 8, 10)
    _braco_manga(t, 21, 23, u, pal, 22, 24)
    for y, a, b in [(12, 11, 20), (13, 11, 20), (14, 11, 20), (15, 11, 20), (16, 12, 19), (17, 12, 19),
                    (18, 13, 18), (19, 13, 18)]:
        for x in range(a, b + 1):
            t.px(x, y + u, OSSO_D if x >= b - 1 else BRANCO)
    _chapeu(t, u)


def _mago_lado(t, fase, andando, u):
    pal = (ROXO, ROXO_L, ROXO_D)
    tunica(t, "lado", fase, andando, u, pal, (OURO, OURO_D))
    t.ret(11, 21, 19, 21, OURO)
    t.ret(11, 22, 19, 22, OURO_D)
    for y in range(12, 19):
        t.ret(11, y + u, 15, y + u, BRANCO)
        t.px(11, y + u, OSSO_D)
    _bastao_mago(t, 24, u)
    caixa(t, 15, 19 + u, 21, 21 + u, *pal)
    t.ret(21, 19 + u, 24, 21 + u, PELE)
    t.ret(16, 12 + u, 20, 14 + u, PELE)
    t.px(21, 13 + u, PELE_L)
    t.px(19, 12 + u, CIANO)
    for y, a, b in [(14, 17, 21), (15, 17, 21), (16, 17, 20), (17, 18, 20), (18, 18, 19)]:
        t.ret(a, y + u, b, y + u, BRANCO)
    _chapeu(t, u)


# ======================= DRUIDA =======================
def _chifres(t, u, direcao):
    if direcao == "lado":
        pts = [[(15, 5), (14, 4), (14, 3), (13, 2), (13, 1)], [(14, 3), (16, 2), (17, 1)], [(13, 4), (11, 3)]]
        for pol in pts:
            for (x0, y0), (x1, y1) in zip(pol, pol[1:]):
                t.linha(x0, y0 + u, x1, y1 + u, OSSO)
        t.px(15, 5 + u, OSSO_D)
        return
    for esp in (False, True):
        f = (lambda x: 31 - x) if esp else (lambda x: x)
        main = [(12, 5), (11, 4), (10, 3), (10, 2), (10, 1)]
        ramo1 = [(10, 3), (8, 2)]
        ramo2 = [(11, 4), (9, 4)]
        for pol in (main, ramo1, ramo2):
            for (x0, y0), (x1, y1) in zip(pol, pol[1:]):
                t.linha(f(x0), y0 + u, f(x1), y1 + u, OSSO)
        t.px(f(12), 5 + u, OSSO_D)


def _capuz_druida(t, u, direcao):
    forma(t, CABECA, u, VERDE, VERDE_L, VERDE_D)
    if direcao == "baixo":
        t.ret(12, 7 + u, 19, 13 + u, VERDE_DD)
        t.ret(13, 9 + u, 18, 13 + u, PELE_D)
        t.px(14, 10 + u, FOLHA)
        t.px(17, 10 + u, FOLHA)
        t.ret(14, 12 + u, 17, 14 + u, OSSO_D)
        t.ret(15, 14 + u, 16, 15 + u, OSSO_D)
    elif direcao == "cima":
        t.ret(15, 7 + u, 16, 13 + u, VERDE_D)
        for (x, y) in ((13, 9), (18, 9), (14, 11), (17, 11)):
            t.px(x, y + u, VERDE_L)
    else:
        t.ret(15, 7 + u, 20, 13 + u, VERDE_DD)
        t.ret(16, 9 + u, 20, 13 + u, PELE_D)
        t.px(19, 10 + u, FOLHA)
        t.ret(17, 12 + u, 20, 14 + u, OSSO_D)
    _chifres(t, u, direcao)


def _bastao_druida(t, x, u):
    for y in range(9 + u, 30):
        t.px(x + (1 if (y // 4) % 2 else 0), y, MARROM)
    t.ret(x - 1, 5 + u, x + 2, 7 + u, VERDE)
    t.ret(x, 3 + u, x + 1, 5 + u, FOLHA)
    t.px(x - 2, 6 + u, FOLHA)
    t.px(x + 3, 6 + u, FOLHA)
    t.px(x, 6 + u, FOLHA)
    t.ret(x, 8 + u, x + 1, 8 + u, MARROM_D)


def _druida_frente(t, fase, andando, u):
    pal = (VERDE, VERDE_L, VERDE_D)
    _bastao_druida(t, 23, u)
    tunica(t, "baixo", fase, andando, u, pal, (MARROM, MARROM_D))
    t.ret(11, 21, 20, 21, MARROM)
    t.ret(11, 22, 20, 22, MARROM_D)
    t.px(14, 21, FOLHA)
    t.px(17, 22, FOLHA)
    for (x, y) in ((15, 17), (16, 18), (14, 18), (15, 19), (17, 17)):
        t.px(x, y + u, FOLHA)
    _braco_manga(t, 8, 10, u, pal, 8, 10)
    _braco_manga(t, 21, 23, u, pal, 22, 24)
    t.ret(8, 17 + u, 10, 18 + u, VERDE_L)
    _capuz_druida(t, u, "baixo")


def _druida_costas(t, fase, andando, u):
    pal = (VERDE, VERDE_L, VERDE_D)
    _bastao_druida(t, 23, u)
    tunica(t, "cima", fase, andando, u, pal, (MARROM, MARROM_D))
    for (x, y) in ((15, 18), (16, 19), (15, 20), (16, 21), (14, 19), (17, 20)):
        t.px(x, y + u, FOLHA)
    t.ret(11, 21, 20, 21, MARROM)
    _braco_manga(t, 8, 10, u, pal, 8, 10)
    _braco_manga(t, 21, 23, u, pal, 22, 24)
    _capuz_druida(t, u, "cima")


def _druida_lado(t, fase, andando, u):
    pal = (VERDE, VERDE_L, VERDE_D)
    tunica(t, "lado", fase, andando, u, pal, (MARROM, MARROM_D))
    t.ret(11, 21, 19, 21, MARROM)
    t.px(14, 21, FOLHA)
    for (x, y) in ((16, 17), (17, 18), (15, 18)):
        t.px(x, y + u, FOLHA)
    _bastao_druida(t, 24, u)
    caixa(t, 15, 19 + u, 21, 21 + u, *pal)
    t.ret(21, 19 + u, 24, 21 + u, PELE)
    _capuz_druida(t, u, "lado")


# ======================= ARQUEIRO =======================
def _capuz_arq(t, u, direcao):
    forma(t, CABECA, u, VERDE_D, VERDE, VERDE_DD)
    forma(t, [(3, 14, 17), (2, 15, 16)], u, VERDE_D, VERDE, VERDE_DD)
    if direcao == "baixo":
        t.ret(12, 7 + u, 19, 13 + u, VISOR)
        for x in (13, 14, 17, 18):
            t.px(x, 10 + u, ÂMBAR)
        caixa(t, 12, 12 + u, 19, 14 + u, RUBI, RUBI_L, RUBI_D)
        t.ret(12, 15 + u, 19, 16 + u, RUBI_D)
        t.ret(18, 16 + u, 19, 18 + u, RUBI)
    elif direcao == "cima":
        t.ret(15, 6 + u, 16, 13 + u, VERDE_DD)
        t.ret(12, 15 + u, 19, 16 + u, RUBI_D)
    else:
        t.ret(15, 7 + u, 20, 13 + u, VISOR)
        t.px(19, 10 + u, ÂMBAR)
        t.px(18, 10 + u, ÂMBAR)
        caixa(t, 15, 12 + u, 21, 14 + u, RUBI, RUBI_L, RUBI_D)
        t.ret(8, 15 + u, 14, 17 + u, RUBI_D)
        t.ret(7, 16 + u, 10, 18 + u, RUBI)


def _flechas(t, xs, u, y0=9):
    for x in xs:
        t.ret(x, y0 + 1 + u, x, y0 + 5 + u, BRANCO)
        t.px(x, y0 + u, RUBI_L)
        t.px(x - 1, y0 + 1 + u, RUBI)


def _arqueiro_frente(t, fase, andando, u):
    pernas(t, fase, andando, CALCA_COURO, BOTA)
    caixa(t, 19, 13 + u, 22, 21 + u, MARROM_D, MARROM, OUT)
    _flechas(t, (20, 22), u, 9)
    caixa(t, 11, 16 + u, 20, 24, COURO, COURO_L, MARROM_D)
    t.linha(11, 16 + u, 20, 23, MARROM_D)
    t.ret(11, 23, 20, 24, MARROM_D)
    t.ret(15, 23, 16, 24, OURO)
    caixa(t, 8, 17 + u, 10, 23, VERDE_D, VERDE, VERDE_DD)
    caixa(t, 21, 17 + u, 23, 23, VERDE_D, VERDE, VERDE_DD)
    t.ret(8, 24, 10, 25, PELE)
    t.ret(21, 24, 23, 25, PELE)
    arco(t, 7, -1, u)
    t.ret(7, 19, 9, 21, PELE)
    _capuz_arq(t, u, "baixo")


def _arqueiro_costas(t, fase, andando, u):
    pernas(t, fase, andando, CALCA_COURO, BOTA)
    caixa(t, 11, 16 + u, 20, 24, COURO, COURO_L, MARROM_D)
    t.ret(11, 23, 20, 24, MARROM_D)
    _flechas(t, (13, 16, 18), u, 9)
    caixa(t, 11, 14 + u, 19, 25, MARROM, COURO, MARROM_D, cantos=((11, 25), (19, 25)))
    t.linha(11, 15 + u, 19, 24, MARROM_D)
    t.ret(11, 14 + u, 19, 15 + u, MARROM_D)
    caixa(t, 8, 17 + u, 10, 23, VERDE_D, VERDE, VERDE_DD)
    caixa(t, 21, 17 + u, 23, 23, VERDE_D, VERDE, VERDE_DD)
    t.ret(8, 24, 10, 25, PELE)
    t.ret(21, 24, 23, 25, PELE)
    arco(t, 7, -1, u)
    t.ret(7, 19, 9, 21, PELE)
    _capuz_arq(t, u, "cima")


def _arqueiro_lado(t, fase, andando, u):
    pernas_lado(t, fase, andando, CALCA_COURO, BOTA)
    caixa(t, 7, 14 + u, 11, 23, MARROM_D, MARROM, OUT)
    _flechas(t, (9, 11), u, 9)
    caixa(t, 12, 16 + u, 19, 24, COURO, COURO_L, MARROM_D)
    t.ret(12, 23, 19, 24, MARROM_D)
    t.ret(15, 23, 16, 24, OURO)
    arco(t, 24, 1, u)
    caixa(t, 16, 18 + u, 22, 20 + u, VERDE_D, VERDE, VERDE_DD)
    t.ret(22, 18 + u, 24, 20 + u, PELE)
    _capuz_arq(t, u, "lado")


# ======================= METAMORFO =======================
def _capuz_lobo(t, u, direcao):
    forma(t, CABECA, u, PELO_D, PELO, PELO_DD)
    if direcao == "lado":
        forma(t, [(1, 13, 14), (2, 12, 15), (3, 12, 15), (4, 12, 15)], u, PELO_D, PELO, PELO_DD)
        forma(t, [(2, 17, 18), (3, 17, 19), (4, 17, 19)], u, PELO_D, PELO, PELO_DD)
        t.px(14, 3 + u, RUBI_D)
        t.px(14, 2 + u, RUBI_D)
        t.ret(15, 7 + u, 20, 13 + u, VISOR)
        caixa(t, 17, 10 + u, 22, 13 + u, OSSO, BRANCO, OSSO_D)
        t.px(22, 10 + u, OUT)
        t.px(18, 9 + u, ÂMBAR)
        t.px(19, 9 + u, ÂMBAR)
        t.px(18, 11 + u, RUBI)
        return
    forma(t, [(1, 11, 12), (2, 10, 13), (3, 10, 13), (4, 10, 13)], u, PELO_D, PELO, PELO_DD)
    forma(t, [(1, 19, 20), (2, 18, 21), (3, 18, 21), (4, 18, 21)], u, PELO_D, PELO, PELO_DD)
    t.px(11, 3 + u, RUBI_D)
    t.px(11, 2 + u, RUBI_D)
    t.px(20, 3 + u, RUBI_D)
    t.px(20, 2 + u, RUBI_D)
    if direcao == "baixo":
        t.ret(12, 7 + u, 19, 13 + u, VISOR)
        t.ret(13, 8 + u, 15, 13 + u, PELE_D)
        caixa(t, 16, 8 + u, 19, 13 + u, OSSO, BRANCO, OSSO_D)
        t.px(13, 10 + u, ÂMBAR)
        t.px(14, 10 + u, ÂMBAR)
        t.px(17, 10 + u, ÂMBAR)
        t.px(18, 10 + u, ÂMBAR)
        t.px(17, 12 + u, RUBI)
        t.px(15, 12 + u, OUT)
        t.px(14, 13 + u, BRANCO)
        t.px(17, 13 + u, BRANCO)
    else:
        t.ret(15, 6 + u, 16, 13 + u, PELO_DD)
        for (x, y) in ((12, 8), (19, 8), (13, 12), (18, 12)):
            t.px(x, y + u, PELO_L)


def _pelos_ombro(t, u):
    caixa(t, 8, 16 + u, 10, 18 + u, PELO, PELO_L, PELO_D)
    caixa(t, 21, 16 + u, 23, 18 + u, PELO, PELO_L, PELO_D)
    caixa(t, 10, 15 + u, 21, 17 + u, PELO, PELO_L, PELO_D)
    for x in (11, 13, 15, 17, 19):
        t.px(x, 18 + u, PELO_D)


def _garras(t, x0, x1):
    t.ret(x0, 24, x1, 25, PELE)
    t.ret(x0, 26, x1, 26, BRANCO)
    t.px(x0 + 1, 26, OUT)


def _metamorfo_frente(t, fase, andando, u):
    pernas(t, fase, andando, (TEAL_D, TEAL, OUT), BOTA)
    caixa(t, 11, 16 + u, 20, 24, TEAL, TEAL_L, TEAL_D)
    t.ret(11, 22, 20, 23, MARROM_D)
    t.ret(15, 22, 16, 23, OSSO)
    caixa(t, 8, 19 + u, 10, 23, TEAL, TEAL_L, TEAL_D)
    caixa(t, 21, 19 + u, 23, 23, TEAL, TEAL_L, TEAL_D)
    _garras(t, 8, 10)
    _garras(t, 21, 23)
    _pelos_ombro(t, u)
    t.px(15, 19 + u, OSSO)
    t.px(16, 20 + u, OSSO)
    _capuz_lobo(t, u, "baixo")


def _metamorfo_costas(t, fase, andando, u):
    pernas(t, fase, andando, (TEAL_D, TEAL, OUT), BOTA)
    caixa(t, 8, 19 + u, 10, 23, TEAL, TEAL_L, TEAL_D)
    caixa(t, 21, 19 + u, 23, 23, TEAL, TEAL_L, TEAL_D)
    _garras(t, 8, 10)
    _garras(t, 21, 23)
    manto = [(y, 10, 21) for y in range(16, 22)] + [(y, 9, 22) for y in range(22, 25)]
    forma(t, manto, u, PELO, PELO_L, PELO_D)
    for x, y in ((10, 25), (12, 26), (14, 25), (16, 26), (18, 25), (20, 26), (21, 25)):
        t.px(x, y, PELO_D)
    t.px(12, 25, PELO)
    t.px(18, 24, PELO_D)
    t.ret(15, 17 + u, 16, 24, PELO_D)
    for x, y in ((12, 18), (13, 21), (18, 19), (19, 22), (11, 23), (20, 23)):
        t.px(x, y + (u if y < 23 else 0), PELO_L)
    _capuz_lobo(t, u, "cima")


def _metamorfo_lado(t, fase, andando, u):
    pernas_lado(t, fase, andando, (TEAL_D, TEAL, OUT), BOTA)
    forma(t, [(17, 9, 12), (18, 8, 12), (19, 7, 12), (20, 7, 12), (21, 6, 12), (22, 6, 12), (23, 6, 12), (24, 7, 12), (25, 8, 12), (26, 10, 12)], u, PELO, PELO_L, PELO_D)
    caixa(t, 12, 16 + u, 19, 24, TEAL, TEAL_L, TEAL_D)
    t.ret(12, 22, 19, 23, MARROM_D)
    caixa(t, 11, 15 + u, 20, 18 + u, PELO, PELO_L, PELO_D)
    caixa(t, 15, 19 + u, 21, 21 + u, TEAL, TEAL_L, TEAL_D)
    t.ret(21, 19 + u, 23, 21 + u, PELE)
    t.px(24, 19 + u, BRANCO)
    t.px(24, 20 + u, BRANCO)
    t.px(24, 21 + u, BRANCO)
    _capuz_lobo(t, u, "lado")


# ======================= LOBO =======================
def _lobo_lado(t, fase, andando, u):
    offs = {0: (-2, 2), 1: (0, 0), 2: (2, -2), 3: (0, 0)}[fase] if andando else (0, 0)
    lev = 1 if (andando and fase in (1, 3)) else 0
    for x, off, longe in ((8, offs[0], True), (12, offs[1], False), (20, offs[1], True), (23, offs[0], False)):
        cor = (PELO_DD, PELO_D, OUT) if longe else (PELO_D, PELO, PELO_DD)
        caixa(t, x + off, 23, x + off + 1, 28 - lev, *cor)
        t.ret(x + off, 28 - lev, x + off + 2, 29 - lev, PELO_L if not longe else PELO)
    ty = [0, 1, 0, -1][fase] if andando else 0
    t.ret(5, 16 + u, 7, 18 + u, PELO_D)
    t.ret(3, 13 + u + ty, 5, 16 + u, PELO_D)
    t.ret(2, 10 + u + ty, 4, 13 + u + ty, PELO)
    t.px(2, 9 + u + ty, PELO_L)
    t.px(3, 9 + u + ty, PELO_L)
    caixa(t, 7, 15 + u, 23, 24 + u, PELO, PELO_L, PELO_D,
          cantos=((7, 15 + u), (23, 15 + u), (7, 24 + u), (23, 24 + u)))
    t.ret(10, 22 + u, 21, 23 + u, PELO_L)
    t.ret(10, 15 + u, 22, 16 + u, PELO_D)
    caixa(t, 21, 12 + u, 26, 22 + u, PELO, PELO_L, PELO_D)
    caixa(t, 24, 11 + u, 29, 19 + u, PELO, PELO_L, PELO_D)
    caixa(t, 28, 14 + u, 31, 18 + u, PELO_L, BRANCO, PELO)
    t.px(31, 14 + u, OUT)
    t.px(30, 19 + u, BRANCO)
    caixa(t, 24, 8 + u, 26, 11 + u, PELO_D, PELO, PELO_DD)
    t.px(25, 10 + u, RUBI_D)
    caixa(t, 27, 9 + u, 28, 11 + u, PELO_D, PELO, PELO_DD)
    t.px(27, 13 + u, ÂMBAR)
    t.px(28, 13 + u, ÂMBAR)
    t.linha(25, 12 + u, 27, 16 + u, RUBI_D)


def contorno(t, linhas, u):
    """Contorno escuro em volta de uma forma, para separá-la do que está atrás (ex.: cabeça sobre o corpo)."""
    ys = [y for y, _, _ in linhas]
    for y, a, b in linhas:
        t.ret(a - 1, y + u, b + 1, y + u, OUT)
    ya, yb = min(ys), max(ys)
    a0, b0 = [(a, b) for y, a, b in linhas if y == ya][0]
    a1, b1 = [(a, b) for y, a, b in linhas if y == yb][0]
    t.ret(a0, ya - 1 + u, b0, ya - 1 + u, OUT)
    t.ret(a1, yb + 1 + u, b1, yb + 1 + u, OUT)


def _orelhas(t, u, esq, dir_):
    for linhas in (esq, dir_):
        contorno(t, linhas, u)
        forma(t, linhas, u, PELO, PELO_L, PELO_D)


def _lobo_frente(t, fase, andando, u):
    a = 1 if (andando and fase in (0, 1)) else 0
    b = 1 if (andando and fase in (2, 3)) else 0
    # corpo atrás da cabeça: afunila para o lombo e alarga nos ombros
    corpo = ([(8, 13, 18), (9, 12, 19)] + [(y, 11, 20) for y in range(10, 14)]
             + [(y, 9, 22) for y in range(14, 22)])
    forma(t, corpo, u, PELO_D, PELO, PELO_DD)
    t.ret(15, 8 + u, 16, 16 + u, PELO_DD)            # espinha
    for x, y in ((12, 11), (19, 12), (11, 15), (20, 16), (13, 17), (18, 18)):
        t.px(x, y + u, PELO)                            # tufos de pelo
    # patas dianteiras
    for x0, lev in ((9, a), (20, b)):
        caixa(t, x0, 22, x0 + 2, 28 - lev, PELO, PELO_L, PELO_D)
        t.ret(x0 - 1, 28 - lev, x0 + 3, 29 - lev, PELO_L)
        t.px(x0, 29 - lev, PELO_D)
        t.px(x0 + 2, 29 - lev, PELO_D)
    # peito claro
    peito = [(20, 10, 21), (21, 10, 21), (22, 11, 20), (23, 11, 20), (24, 12, 19)]
    forma(t, peito, u, PELO_L, BRANCO, PELO)
    # orelhas
    orelha_e = [(6, 11, 12), (7, 10, 12), (8, 10, 13), (9, 10, 13), (10, 10, 13), (11, 11, 13)]
    orelha_d = [(6, 19, 20), (7, 19, 21), (8, 18, 21), (9, 18, 21), (10, 18, 21), (11, 18, 20)]
    _orelhas(t, u, orelha_e, orelha_d)
    for y in (8, 9, 10):
        t.ret(11, y + u, 12, y + u, RUBI_D)
        t.ret(19, y + u, 20, y + u, RUBI_D)
    # cabeça redonda com bochechas e focinho claro
    cabeca = [(11, 12, 19), (12, 11, 20), (13, 11, 20), (14, 10, 21), (15, 10, 21), (16, 10, 21),
              (17, 11, 20), (18, 12, 19)]
    focinho = [(19, 13, 18), (20, 13, 18), (21, 13, 18), (22, 14, 17), (23, 14, 17)]
    contorno(t, cabeca + focinho, u)
    forma(t, cabeca, u, PELO, PELO_L, PELO_D)
    forma(t, focinho, u, PELO_L, BRANCO, PELO)
    t.ret(15, 11 + u, 16, 14 + u, PELO_D)            # listra na testa
    t.px(11, 17 + u, PELO_L)
    t.px(20, 17 + u, PELO_D)
    # olhos amarelos com pupila e sobrancelha brava
    t.ret(11, 14 + u, 14, 14 + u, PELO_DD)
    t.ret(17, 14 + u, 20, 14 + u, PELO_DD)
    t.px(12, 15 + u, ÂMBAR)
    t.px(13, 15 + u, OUT)
    t.px(18, 15 + u, OUT)
    t.px(19, 15 + u, ÂMBAR)
    # nariz, boca e presas
    t.ret(15, 21 + u, 16, 22 + u, OUT)
    t.px(15, 21 + u, PELO_DD)
    t.px(14, 23 + u, PELO_DD)
    t.px(17, 23 + u, PELO_DD)
    t.px(14, 24 + u, BRANCO)
    t.px(17, 24 + u, BRANCO)
    t.linha(11, 12 + u, 12, 16 + u, RUBI_D)         # cicatriz


def _lobo_costas(t, fase, andando, u):
    a = 1 if (andando and fase in (0, 1)) else 0
    b = 1 if (andando and fase in (2, 3)) else 0
    ty = {1: 1, 3: -1}.get(fase, 0) if andando else 0
    # patas traseiras (aparecem embaixo do quadril)
    for x0, lev in ((9, b), (20, a)):
        caixa(t, x0, 22, x0 + 2, 28 - lev, PELO, PELO_L, PELO_D)
        t.ret(x0 - 1, 28 - lev, x0 + 3, 29 - lev, PELO_L)
        t.px(x0, 29 - lev, PELO_D)
        t.px(x0 + 2, 29 - lev, PELO_D)
    # tronco: ombros estreitos, costelas largas, quadril arredondado
    tronco = ([(11, 12, 19), (12, 11, 20)] + [(y, 10, 21) for y in range(13, 16)]
              + [(y, 9, 22) for y in range(16, 23)] + [(23, 10, 21), (24, 12, 19)])
    forma(t, tronco, u, PELO, PELO_L, PELO_D)
    t.ret(15, 12 + u, 16, 23, PELO_D)                   # espinha
    for y in range(12, 17):                              # crina escura nos ombros
        t.ret(11, y + u, 20, y + u, PELO_D if y % 2 else PELO_DD)
    t.ret(15, 12 + u, 16, 16 + u, PELO_DD)
    for x0 in (10, 19):                                  # brilho nos quadris
        t.ret(x0, 18, x0 + 2, 18, PELO_L)
        t.ret(x0, 19, x0 + 1, 21, PELO_L)
    # cauda peluda caindo do quadril: mais clara que o corpo para destacar
    cauda = [(20, 15, 16), (21, 14, 17), (22, 14, 17), (23, 14, 17), (24, 14, 17), (25, 14, 17),
             (26, 14, 17), (27, 15, 16), (28, 15, 16)]
    for y, a0, b0 in cauda:
        a0, b0 = a0 + ty, b0 + ty
        t.ret(a0, y, b0, y, PELO_L)
        t.px(a0, y, PELO)
        t.px(b0, y, PELO_D)
        t.px(a0 - 1, y, PELO_DD) if y < 27 else None
    t.ret(15 + ty, 27, 16 + ty, 28, BRANCO)
    # cabeça vista por trás, com orelhas
    orelha_e = [(1, 11, 12), (2, 11, 13), (3, 10, 13), (4, 10, 13), (5, 11, 13)]
    orelha_d = [(1, 19, 20), (2, 18, 20), (3, 18, 21), (4, 18, 21), (5, 18, 20)]
    _orelhas(t, u, orelha_e, orelha_d)
    cabeca = [(4, 13, 18), (5, 12, 19), (6, 12, 19), (7, 12, 19), (8, 12, 19), (9, 12, 19), (10, 13, 18)]
    contorno(t, cabeca, u)
    forma(t, cabeca, u, PELO, PELO_L, PELO_D)
    t.ret(15, 4 + u, 16, 9 + u, PELO_D)
    t.px(11, 3 + u, PELO_DD)
    t.px(20, 3 + u, PELO_DD)


def _fabrica(frente, costas, lado):
    def fn(direcao, q):
        t = Tela()
        andando = q < 4
        fase = q if andando else 0
        u = -1 if ((andando and q in (1, 3)) or q == 5) else 0
        {"baixo": frente, "cima": costas, "lado": lado}[direcao](t, fase, andando, u)
        return t.imagem()
    return fn


PERSONAGENS = [
    ("cavaleiro", "Cavaleiro", cavaleiro),
    ("mago", "Mago", _fabrica(_mago_frente, _mago_costas, _mago_lado)),
    ("druida", "Druida", _fabrica(_druida_frente, _druida_costas, _druida_lado)),
    ("arqueiro", "Arqueiro", _fabrica(_arqueiro_frente, _arqueiro_costas, _arqueiro_lado)),
    ("metamorfo", "Metamorfo", _fabrica(_metamorfo_frente, _metamorfo_costas, _metamorfo_lado)),
    ("lobo", "Lobo (forma do metamorfo)", _fabrica(_lobo_frente, _lobo_costas, _lobo_lado)),
]


def montar_folha(fn):
    folha = Image.new("RGBA", (W * COLS, H * len(DIRECOES)), (0, 0, 0, 0))
    for r, d in enumerate(DIRECOES):
        for q in range(COLS):
            folha.paste(fn(d, q), (q * W, r * H))
    return folha


def main():
    os.makedirs(SAIDA, exist_ok=True)
    esc = 5
    try:
        fonte = ImageFont.load_default(size=20)
    except TypeError:
        fonte = ImageFont.load_default()
    folhas = []
    for slug, nome, fn in PERSONAGENS:
        folha = montar_folha(fn)
        folha.save(os.path.join(SAIDA, f"{slug}_topo.png"))
        folhas.append((nome, folha))

    margem, topo = 14, 40
    larg = W * COLS * esc + margem * 2
    alt = (H * len(DIRECOES) * esc + topo + margem) * len(folhas)
    prev = Image.new("RGBA", (larg, alt), (26, 20, 24, 255))
    dr = ImageDraw.Draw(prev)
    for i, (nome, folha) in enumerate(folhas):
        oy = i * (H * len(DIRECOES) * esc + topo + margem)
        dr.text((margem, oy + 8), nome + "  -  frente / costas / lado  (andando x4, parado x2)",
                fill=(232, 200, 120, 255), font=fonte)
        for r in range(len(DIRECOES)):
            for c in range(COLS):
                x, y = margem + c * W * esc, oy + topo + r * H * esc
                cor = (40, 32, 38, 255) if (r + c) % 2 == 0 else (46, 38, 44, 255)
                dr.rectangle([x, y, x + W * esc - 1, y + H * esc - 1], fill=cor)
        big = folha.resize((folha.width * esc, folha.height * esc), Image.NEAREST)
        prev.alpha_composite(big, (margem, oy + topo))
    prev.convert("RGB").save(os.path.join(SAIDA, "preview_topo.png"))
    print("ok:", SAIDA)


if __name__ == "__main__":
    main()
