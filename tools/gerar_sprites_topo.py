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

    def imagem(self):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for y in range(27, 32):  # sombra no chão (elipse translúcida)
            for x in range(3, 29):
                dx, dy = (x - 15.5) / 10.5, (y - 29.5) / 2.4
                if dx * dx + dy * dy <= 1:
                    img.putpixel((x, y), (0, 0, 0, 90))
        cont = {}
        for (x, y) in self.p:
            for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                v = (x + ox, y + oy)
                if v not in self.p and 0 <= v[0] < W and 0 <= v[1] < H:
                    cont[v] = OUT
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


PERSONAGENS = [
    ("cavaleiro", "Cavaleiro", cavaleiro),
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
