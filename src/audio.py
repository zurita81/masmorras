"""Efeitos sonoros. Se o computador não tiver áudio, o jogo continua sem som (sem erro)."""
import pygame

import recursos

NOMES = ("passo", "espada", "acerto", "dano", "moeda", "flecha", "magia", "uivo",
         "sala_fecha", "sala_abre", "clique", "vitoria", "derrota", "chefe")

# volume de cada som (0 a 1); passos bem baixinhos para não cansar
VOLUMES = {"passo": 0.25, "clique": 0.5}


class Audio:
    def __init__(self):
        self.sons = {}
        self.ativo = False
        self.mudo = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, channels=1)
            for nome in NOMES:
                som = pygame.mixer.Sound(recursos.caminho("sons", f"{nome}.ogg"))
                som.set_volume(VOLUMES.get(nome, 0.6))
                self.sons[nome] = som
            self.ativo = True
        except (pygame.error, FileNotFoundError, NotImplementedError):
            self.ativo = False

    def tocar(self, nome):
        if self.ativo and not self.mudo and nome in self.sons:
            self.sons[nome].play()

    def alternar_mudo(self):
        self.mudo = not self.mudo
        if self.mudo and self.ativo:
            pygame.mixer.stop()
