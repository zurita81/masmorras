"""Gera os efeitos sonoros retrô do jogo por código (sem direitos autorais).

Cada som é sintetizado com ondas quadradas, ruído e varreduras de frequência,
no estilo dos jogos de 8 bits. Saída: assets/sons/<nome>.ogg

Uso:  python tools/gerar_sons.py        (precisa de numpy e ffmpeg)
"""
import os
import subprocess
import tempfile
import wave

import numpy as np

TAXA = 22050
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "assets", "sons")
rng = np.random.default_rng(7)  # semente fixa: os sons saem sempre iguais


def tempo(dur):
    return np.arange(int(TAXA * dur)) / TAXA


def quadrada(freq, duty=0.5):
    fase = np.cumsum(freq / TAXA)
    return np.where((fase % 1.0) < duty, 1.0, -1.0)


def triangular(freq):
    fase = np.cumsum(freq / TAXA)
    return 2 * np.abs(2 * (fase % 1.0) - 1) - 1


def ruido(n):
    return rng.uniform(-1, 1, n)


def varredura(f0, f1, dur, curva=1.0):
    k = (tempo(dur) / dur) ** curva
    return f0 + (f1 - f0) * k


def envelope(n, ataque=0.005, queda=3.0):
    t = np.arange(n) / TAXA
    a = np.minimum(1.0, t / max(ataque, 1e-4))
    return a * np.exp(-queda * t / (n / TAXA))


def passa_baixa(x, k):
    """Filtro simples (k de 0 a 1: quanto menor, mais abafado)."""
    y = np.zeros_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc += k * (v - acc)
        y[i] = acc
    return y


def notas(lista, onda=quadrada, dur_nota=0.09, queda=4.0):
    pedacos = []
    for f in lista:
        n = int(TAXA * dur_nota)
        som = onda(np.full(n, f)) if f else np.zeros(n)
        pedacos.append(som * envelope(n, queda=queda))
    return np.concatenate(pedacos)


# ---------------- os sons ----------------
def passo():
    n = int(TAXA * 0.07)
    return passa_baixa(ruido(n), 0.18) * envelope(n, queda=9) * 1.6


def espada():
    d = 0.16
    n = int(TAXA * d)
    chiado = passa_baixa(ruido(n), 0.5) * np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
    tom = quadrada(varredura(900, 300, d)) * 0.25 * envelope(n, queda=6)
    return chiado * 0.9 + tom


def acerto():
    d = 0.12
    n = int(TAXA * d)
    return (ruido(n) * 0.7 + quadrada(varredura(260, 70, d)) * 0.6) * envelope(n, 0.002, 7)


def dano():
    d = 0.30
    n = int(TAXA * d)
    vibrato = varredura(420, 90, d) * (1 + 0.04 * np.sin(2 * np.pi * 30 * tempo(d)))
    return (quadrada(vibrato, 0.35) * 0.7 + ruido(n) * 0.25) * envelope(n, 0.002, 4)


def moeda():
    return np.concatenate([quadrada(np.full(int(TAXA * 0.06), 988)) * 0.6,
                           quadrada(np.full(int(TAXA * 0.22), 1319)) * 0.6
                           * envelope(int(TAXA * 0.22), queda=5)])


def flecha():
    d = 0.18
    n = int(TAXA * d)
    return (passa_baixa(ruido(n), 0.35) * 0.6 * envelope(n, 0.01, 6)
            + triangular(varredura(1200, 500, d)) * 0.35 * envelope(n, queda=7))


def magia():
    d = 0.35
    n = int(TAXA * d)
    base = triangular(varredura(300, 1100, d, 1.4)) * (1 + 0.3 * np.sin(2 * np.pi * 18 * tempo(d)))
    brilho = quadrada(varredura(600, 2200, d, 1.4)) * 0.18
    return (base * 0.6 + brilho) * envelope(n, 0.02, 3.5)


def uivo():
    d = 0.9
    n = int(TAXA * d)
    f = np.interp(np.linspace(0, 1, n), [0, 0.25, 0.7, 1], [330, 620, 600, 300])
    f = f * (1 + 0.012 * np.sin(2 * np.pi * 6 * tempo(d)))
    onda = triangular(f) * 0.7 + quadrada(f * 2, 0.25) * 0.12
    return onda * np.sin(np.pi * np.linspace(0, 1, n)) ** 0.7


def sala_fecha():
    d = 0.55
    n = int(TAXA * d)
    grave = quadrada(varredura(110, 45, d, 0.6), 0.5) * 0.8 * envelope(n, 0.003, 5)
    rangido = passa_baixa(ruido(n), 0.08) * 1.4 * np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return grave + rangido * 0.5


def sala_abre():
    d = 0.5
    n = int(TAXA * d)
    rangido = passa_baixa(ruido(n), 0.10) * 1.3 * np.sin(np.pi * np.linspace(0, 1, n))
    campainha = np.concatenate([np.zeros(int(n * 0.45)), notas([659, 988], dur_nota=0.11, queda=3)])
    campainha = np.pad(campainha, (0, max(0, n - len(campainha))))[:n]
    return rangido * 0.6 + campainha * 0.5


def clique():
    n = int(TAXA * 0.05)
    return quadrada(np.full(n, 740)) * 0.5 * envelope(n, 0.001, 8)


def vitoria():
    return notas([523, 659, 784, 1047, 0, 784, 1047], dur_nota=0.13, queda=2.5) * 0.6


def derrota():
    return notas([392, 370, 330, 262], onda=triangular, dur_nota=0.22, queda=1.8) * 0.9


def chefe():
    d = 1.1
    n = int(TAXA * d)
    f = varredura(90, 45, d, 0.8) * (1 + 0.06 * np.sin(2 * np.pi * 22 * tempo(d)))
    return (quadrada(f, 0.3) * 0.7 + passa_baixa(ruido(n), 0.12) * 0.7) * np.sin(np.pi * np.linspace(0, 1, n)) ** 0.5


SONS = {
    "passo": passo, "espada": espada, "acerto": acerto, "dano": dano, "moeda": moeda,
    "flecha": flecha, "magia": magia, "uivo": uivo, "sala_fecha": sala_fecha,
    "sala_abre": sala_abre, "clique": clique, "vitoria": vitoria, "derrota": derrota,
    "chefe": chefe,
}


def salvar_ogg(nome, onda):
    onda = np.asarray(onda, dtype=float)
    pico = np.max(np.abs(onda)) or 1.0
    dados = (onda / pico * 0.70 * 32767).astype("<i2")  # margem para o ogg não saturar
    os.makedirs(SAIDA, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, nome + ".wav")
        with wave.open(wav, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(TAXA)
            w.writeframes(dados.tobytes())
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis",
                        "-q:a", "4", os.path.join(SAIDA, nome + ".ogg")], check=True)
    return len(dados) / TAXA


def main():
    for nome, fn in SONS.items():
        dur = salvar_ogg(nome, fn())
        print(f"  {nome:<11} {dur:4.2f}s")
    print("ok:", SAIDA)


if __name__ == "__main__":
    main()
