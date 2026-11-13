"""Gera os sprites em pixel art do jogo (desenhados por código).

Cada personagem tem 2 quadros de "idle" (respirando), virado para a direita,
numa tela de 40x40 pixels. Saída:
  assets/sprites/<nome>_idle.png   -> folha com os 2 quadros lado a lado (80x40)
  assets/sprites/preview.png       -> imagem ampliada para ver todos juntos

Uso:  python tools/gerar_sprites.py
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 40, 40
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "assets", "sprites")

# ---------- paleta sombria (gótico) ----------
OUT = (14, 10, 12, 255)
AÇO_L, AÇO, AÇO_D = (170, 172, 184, 255), (108, 110, 124, 255), (62, 64, 78, 255)
RUBI, RUBI_D = (156, 30, 40, 255), (96, 16, 26, 255)
OURO, OURO_D = (222, 176, 72, 255), (150, 108, 40, 255)
PELE, PELE_D = (226, 184, 146, 255), (170, 122, 98, 255)
OSSO, OSSO_D = (228, 220, 196, 255), (162, 152, 132, 255)
ROXO, ROXO_D, ROXO_L = (104, 64, 140, 255), (60, 36, 88, 255), (148, 108, 190, 255)
VERDE, VERDE_D, VERDE_L = (76, 118, 64, 255), (40, 72, 44, 255), (128, 170, 86, 255)
MARROM, MARROM_D, COURO = (112, 72, 42, 255), (68, 42, 28, 255), (138, 92, 54, 255)
CIANO = (130, 232, 240, 255)
PELO, PELO_D, PELO_L = (124, 124, 136, 255), (72, 72, 86, 255), (186, 186, 198, 255)
ÂMBAR = (244, 196, 64, 255)
BRANCO = (240, 236, 228, 255)
TEAL, TEAL_D = (62, 104, 104, 255), (34, 62, 66, 255)


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

    def linha(self, x0, y0, x1, y1, cor):
        passos = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(passos + 1):
            self.px(round(x0 + (x1 - x0) * i / passos),
                    round(y0 + (y1 - y0) * i / passos), cor)

    def imagem(self):
        # contorno escuro de 1 pixel em volta de tudo
        cont = {}
        for (x, y) in self.p:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                v = (x + dx, y + dy)
                if v not in self.p and 0 <= v[0] < W and 0 <= v[1] < H:
                    cont[v] = OUT
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for pos, cor in {**cont, **self.p}.items():
            img.putpixel(pos, cor)
        return img


def pernas(t, calça, bota, bota_d):
    t.ret(14, 31, 17, 37, calça)
    t.ret(19, 31, 22, 37, calça)
    t.ret(14, 36, 18, 37, bota_d)
    t.ret(19, 36, 23, 37, bota)


def olho(t, x, y, cor=BRANCO):
    t.px(x, y, cor)


# ---------- CAVALEIRO ----------
def cavaleiro(f):
    t, d = Tela(), f
    # capa rubra atrás
    t.ret(10, 19 + d, 13, 34, RUBI_D)
    t.ret(11, 19 + d, 13, 33, RUBI)
    pernas(t, AÇO_D, AÇO, AÇO_D)
    # torso de armadura + tabardo
    t.ret(13, 18 + d, 23, 31, AÇO)
    t.ret(13, 18 + d, 15, 31, AÇO_D)
    t.ret(16, 20 + d, 21, 33, RUBI)
    t.ret(18, 20 + d, 19, 33, RUBI_D)
    t.ret(13, 29 + d, 23, 30 + d, OURO_D)
    t.ret(17, 29 + d, 20, 30 + d, OURO)
    # ombreira
    t.ret(11, 18 + d, 15, 21 + d, AÇO_L)
    t.ret(11, 21 + d, 15, 21 + d, AÇO_D)
    # elmo alto com visor em fenda e pluma
    t.ret(14, 7 + d, 23, 17 + d, AÇO)
    t.ret(14, 7 + d, 16, 17 + d, AÇO_D)
    t.ret(17, 5 + d, 21, 7 + d, AÇO_L)
    t.ret(12, 3 + d, 19, 5 + d, RUBI)
    t.ret(9, 5 + d, 14, 7 + d, RUBI_D)
    t.ret(19, 12 + d, 23, 13 + d, OUT)
    t.px(22, 12 + d, ÂMBAR)
    t.ret(21, 15 + d, 23, 15 + d, AÇO_D)
    # escudo
    t.ret(19, 21 + d, 24, 29 + d, AÇO_D)
    t.ret(20, 22 + d, 23, 28 + d, AÇO)
    t.ret(21, 22 + d, 22, 28 + d, OURO)
    t.ret(20, 24 + d, 23, 25 + d, OURO)
    # espada erguida
    t.ret(27, 6 + d, 28, 25 + d, AÇO_L)
    t.ret(28, 6 + d, 28, 25 + d, AÇO)
    t.ret(25, 26 + d, 30, 27 + d, OURO)
    t.ret(27, 28 + d, 28, 30 + d, MARROM)
    t.px(27, 5 + d, AÇO_L)
    return t.imagem()


# ---------- MAGO ----------
def mago(f):
    t, d = Tela(), f
    # bainha da túnica (cobre as pernas)
    t.ret(12, 31, 25, 37, ROXO_D)
    t.ret(11, 35, 26, 37, ROXO_D)
    t.ret(12, 31, 14, 37, (44, 26, 66, 255))
    t.ret(16, 33, 21, 37, ROXO)
    t.ret(14, 37, 15, 37, MARROM_D)
    t.ret(21, 37, 23, 37, MARROM_D)
    # corpo
    t.ret(13, 18 + d, 24, 31, ROXO)
    t.ret(13, 18 + d, 15, 31, ROXO_D)
    t.ret(13, 29 + d, 24, 30 + d, OURO)
    t.ret(19, 20 + d, 20, 28 + d, ROXO_L)
    # barba branca
    t.ret(19, 15 + d, 23, 19 + d, OSSO)
    t.ret(20, 20 + d, 22, 21 + d, OSSO_D)
    # rosto
    t.ret(15, 10 + d, 23, 15 + d, PELE)
    t.ret(21, 12 + d, 22, 12 + d, CIANO)
    # chapéu pontudo e curvado
    t.ret(12, 9 + d, 26, 10 + d, ROXO_D)
    t.ret(15, 8 + d, 23, 8 + d, ROXO)
    t.ret(16, 7 + d, 22, 7 + d, ROXO)
    t.ret(17, 6 + d, 21, 6 + d, ROXO)
    t.ret(18, 5 + d, 21, 5 + d, ROXO)
    t.ret(19, 4 + d, 22, 4 + d, ROXO_D)
    t.ret(20, 3 + d, 23, 3 + d, ROXO_D)
    t.ret(22, 2 + d, 24, 2 + d, ROXO_D)
    t.ret(15, 8 + d, 23, 8 + d, OURO)
    # cajado com orbe brilhante
    t.ret(28, 8 + d, 28, 37, MARROM)
    t.ret(27, 6 + d, 29, 6 + d, MARROM_D)
    t.ret(27, 3 + d, 29, 5 + d, CIANO)
    t.px(28, 4 + d, BRANCO)
    t.px(26, 4 + d, (130, 232, 240, 140))
    t.ret(24, 25 + d, 28, 26 + d, ROXO)
    t.ret(26, 25 + d, 27, 26 + d, PELE)
    return t.imagem()


# ---------- DRUIDA ----------
def druida(f):
    t, d = Tela(), f
    # manto verde comprido
    t.ret(11, 31, 25, 37, VERDE_D)
    t.ret(12, 31, 14, 37, (28, 52, 32, 255))
    t.ret(16, 34, 21, 37, VERDE)
    t.ret(15, 37, 16, 37, MARROM_D)
    t.ret(20, 37, 22, 37, MARROM_D)
    t.ret(13, 18 + d, 24, 31, VERDE)
    t.ret(13, 18 + d, 15, 31, VERDE_D)
    # folhas no peito e cinto de cipó
    t.ret(13, 28 + d, 24, 28 + d, MARROM)
    t.ret(18, 21 + d, 19, 23 + d, VERDE_L)
    t.ret(20, 23 + d, 21, 25 + d, VERDE_L)
    t.px(17, 24 + d, VERDE_L)
    # capuz
    t.ret(13, 9 + d, 23, 17 + d, VERDE_D)
    t.ret(14, 8 + d, 22, 8 + d, VERDE_D)
    t.ret(17, 11 + d, 23, 16 + d, PELE_D)
    t.ret(19, 12 + d, 23, 15 + d, PELE)
    t.px(22, 13 + d, VERDE_L)
    t.ret(20, 15 + d, 23, 17 + d, OSSO_D)
    # chifres de veado
    for (x0, y0, x1, y1) in [(15, 8, 13, 3), (13, 3, 11, 1), (14, 5, 11, 4),
                              (20, 8, 22, 3), (22, 3, 24, 1), (21, 5, 24, 4)]:
        t.linha(x0, y0 + d, x1, y1 + d, OSSO)
    # cajado de madeira torta
    t.ret(28, 10 + d, 28, 37, MARROM)
    t.ret(29, 9 + d, 29, 11 + d, MARROM)
    t.ret(30, 7 + d, 30, 9 + d, MARROM)
    t.ret(27, 7 + d, 28, 9 + d, MARROM)
    t.ret(30, 5 + d, 32, 7 + d, VERDE_L)
    t.px(31, 6 + d, VERDE)
    t.ret(25, 25 + d, 28, 26 + d, VERDE)
    t.ret(27, 25 + d, 28, 26 + d, PELE)
    return t.imagem()


# ---------- ARQUEIRO ----------
def arqueiro(f):
    t, d = Tela(), f
    # aljava com flechas nas costas
    t.ret(10, 17 + d, 13, 28 + d, MARROM)
    t.ret(10, 17 + d, 11, 28 + d, MARROM_D)
    for x in (10, 12):
        t.ret(x, 13 + d, x, 16 + d, BRANCO)
        t.px(x, 12 + d, RUBI)
    pernas(t, MARROM_D, COURO, MARROM_D)
    # colete de couro
    t.ret(13, 18 + d, 23, 31, COURO)
    t.ret(13, 18 + d, 15, 31, MARROM)
    t.ret(13, 29 + d, 23, 30 + d, MARROM_D)
    t.ret(17, 29 + d, 19, 30 + d, OURO)
    t.ret(16, 18 + d, 17, 28 + d, MARROM)
    # capuz com máscara
    t.ret(13, 8 + d, 23, 17 + d, VERDE_D)
    t.ret(15, 6 + d, 21, 7 + d, VERDE_D)
    t.ret(17, 4 + d, 20, 5 + d, VERDE_D)
    t.ret(18, 2 + d, 19, 3 + d, VERDE_D)
    t.ret(18, 11 + d, 23, 14 + d, PELE_D)
    t.ret(19, 12 + d, 23, 13 + d, (20, 14, 16, 255))
    t.px(22, 12 + d, ÂMBAR)
    t.ret(18, 14 + d, 23, 17 + d, RUBI)  # lenço no rosto
    t.ret(12, 17 + d, 24, 18 + d, RUBI_D)
    # arco
    for y in range(8 + d, 32 + d):
        k = (y - (8 + d)) / 23
        t.px(26 + round(4 * math.sin(math.pi * k)), y, MARROM)
        t.px(25 + round(4 * math.sin(math.pi * k)), y, COURO)
    t.ret(26, 9 + d, 26, 30 + d, BRANCO)
    t.ret(23, 24 + d, 26, 25 + d, COURO)
    t.ret(25, 24 + d, 26, 25 + d, PELE)
    return t.imagem()


# ---------- METAMORFO (forma humana) ----------
def metamorfo(f):
    t, d = Tela(), f
    # manto de pelo esfarrapado
    t.ret(10, 19 + d, 13, 35, PELO_D)
    for i, y in enumerate(range(33, 37)):
        if i % 2 == 0:
            t.px(10, y, PELO_D)
    pernas(t, TEAL_D, MARROM, MARROM_D)
    t.ret(13, 18 + d, 23, 31, TEAL)
    t.ret(13, 18 + d, 15, 31, TEAL_D)
    t.ret(13, 29 + d, 23, 30 + d, MARROM_D)
    # gola de pelo
    t.ret(12, 17 + d, 24, 20 + d, PELO)
    t.ret(12, 19 + d, 24, 20 + d, PELO_L)
    # capuz de lobo com orelhas
    t.ret(14, 8 + d, 23, 17 + d, PELO_D)
    t.ret(15, 7 + d, 22, 7 + d, PELO_D)
    t.ret(15, 3 + d, 17, 6 + d, PELO_D)
    t.ret(20, 3 + d, 22, 6 + d, PELO_D)
    t.px(16, 4 + d, RUBI_D)
    t.px(21, 4 + d, RUBI_D)
    t.px(16, 3 + d, PELO)
    t.px(21, 3 + d, PELO)
    # meia máscara de osso e pintura tribal
    t.ret(18, 10 + d, 23, 16 + d, PELE_D)
    t.ret(20, 10 + d, 23, 15 + d, OSSO)
    t.ret(20, 14 + d, 23, 16 + d, OSSO_D)
    t.ret(21, 12 + d, 22, 12 + d, ÂMBAR)
    t.px(19, 13 + d, RUBI)
    t.px(19, 15 + d, RUBI)
    # garras
    t.ret(24, 24 + d, 26, 25 + d, PELE)
    for x in (27, 28, 29):
        t.px(x, 24 + d, BRANCO)
    t.px(27, 26 + d, BRANCO)
    t.px(29, 26 + d, BRANCO)
    # amuleto de presa
    t.ret(19, 22 + d, 19, 23 + d, OSSO)
    return t.imagem()


# ---------- LOBO (forma animal do metamorfo) ----------
def lobo(f):
    t, d = Tela(), f
    cau = [(8, 21), (6, 19), (4, 16), (3, 13)] if f == 0 else [(8, 21), (6, 20), (4, 18), (3, 15)]
    for (x, y) in cau:
        t.ret(x, y, x + 2, y + 2, PELO_D)
    t.px(cau[-1][0], cau[-1][1], PELO_L)
    # patas (traseira e dianteira)
    for x0 in (11, 16, 24, 29):
        t.ret(x0, 30, x0 + 2, 37, PELO_D)
        t.ret(x0, 36, x0 + 3, 37, PELO)
    # corpo
    t.ret(9, 20 + d, 31, 31, PELO)
    t.ret(9, 20 + d, 31, 22 + d, PELO_D)
    t.ret(11, 28, 29, 31, PELO_L)
    t.ret(24, 19 + d, 30, 23 + d, PELO_D)  # crina
    t.ret(24, 18 + d, 28, 19 + d, PELO_D)
    # pescoço e cabeça
    t.ret(29, 18 + d, 33, 26, PELO)
    t.ret(31, 17 + d, 36, 24 + d, PELO)
    t.ret(36, 20 + d, 39, 24 + d, PELO_L)  # focinho
    t.px(39, 20 + d, OUT)
    t.ret(36, 25 + d, 38, 25 + d, BRANCO)  # presas
    t.px(36, 25 + d, BRANCO)
    t.px(38, 25 + d, BRANCO)
    # orelhas
    t.ret(31, 14 + d, 33, 16 + d, PELO_D)
    t.ret(34, 15 + d, 35, 16 + d, PELO_D)
    t.px(32, 15 + d, RUBI_D)
    # olho âmbar e cicatriz
    t.ret(34, 19 + d, 35, 19 + d, ÂMBAR)
    t.px(35, 19 + d, OUT)
    t.linha(31, 20 + d, 33, 23 + d, RUBI_D)
    return t.imagem()


PERSONAGENS = [
    ("cavaleiro", "Cavaleiro", cavaleiro),
    ("mago", "Mago", mago),
    ("druida", "Druida", druida),
    ("arqueiro", "Arqueiro", arqueiro),
    ("metamorfo", "Metamorfo", metamorfo),
    ("lobo", "Lobo", lobo),
]


def main():
    os.makedirs(SAIDA, exist_ok=True)
    folhas = []
    for slug, nome, fn in PERSONAGENS:
        folha = Image.new("RGBA", (W * 2, H), (0, 0, 0, 0))
        for i in range(2):
            folha.paste(fn(i), (W * i, 0))
        folha.save(os.path.join(SAIDA, f"{slug}_idle.png"))
        folhas.append((nome, folha))

    # ---------- imagem de vista previa (ampliada) ----------
    esc = 5
    cel_w, cel_h = W * 2 * esc + 24, H * esc + 52
    cols = 3
    linhas = math.ceil(len(folhas) / cols)
    prev = Image.new("RGBA", (cols * cel_w, linhas * cel_h), (26, 20, 24, 255))
    dr = ImageDraw.Draw(prev)
    try:
        fonte = ImageFont.load_default(size=22)
    except TypeError:
        fonte = ImageFont.load_default()
    for i, (nome, folha) in enumerate(folhas):
        cx, cy = (i % cols) * cel_w, (i // cols) * cel_h
        dr.rectangle([cx + 6, cy + 6, cx + cel_w - 6, cy + cel_h - 6],
                     fill=(40, 32, 38, 255), outline=(90, 70, 60, 255), width=2)
        dr.line([cx + 14, cy + 6 + 44 + H * esc - 6, cx + cel_w - 14, cy + 6 + 44 + H * esc - 6],
                fill=(70, 56, 50, 255), width=2)
        big = folha.resize((W * 2 * esc, H * esc), Image.NEAREST)
        prev.alpha_composite(big, (cx + 12, cy + 40))
        dr.text((cx + 16, cy + 12), nome, fill=(232, 200, 120, 255), font=fonte)
    prev.convert("RGB").save(os.path.join(SAIDA, "preview.png"))
    print("ok:", SAIDA)


if __name__ == "__main__":
    main()
