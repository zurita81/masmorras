"""Câmera que segue o jogador suavemente e não sai dos limites da fase."""
from config import ALTURA, LARGURA


class Camera:
    def __init__(self, largura_nivel, altura_nivel):
        self.lw, self.lh = largura_nivel, altura_nivel
        self.x = 0.0
        self.y = 0.0

    def centralizar(self, alvo):
        """Posiciona direto no alvo (usar ao começar a fase)."""
        self.x = alvo.centerx - LARGURA / 2
        self.y = alvo.centery - ALTURA / 2
        self._limitar()

    def seguir(self, alvo, suavidade=0.12):
        tx = alvo.centerx - LARGURA / 2
        ty = alvo.centery - ALTURA / 2 - 16
        self.x += (tx - self.x) * suavidade
        self.y += (ty - self.y) * suavidade
        self._limitar()

    def _limitar(self):
        self.x = max(0, min(self.x, max(0, self.lw - LARGURA)))
        self.y = max(0, min(self.y, max(0, self.lh - ALTURA)))

    @property
    def ix(self):
        return int(round(self.x))

    @property
    def iy(self):
        return int(round(self.y))
