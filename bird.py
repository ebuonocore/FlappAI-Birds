import pygame
from tuyau import *
from ia import *


class Bird:
    def __init__(self, nom, type=False):
        self.nom = nom
        self.ia = type
        self.ttf = 0
        self.delta_y = 0
        self.score = 0
        self.vivant = True
        self.x = 200
        self.y = 300
        self.vy = 0
        self.vx = 0
        self.sens = 0
        self.angle = 0
        self.id_tuyau_passé = -1
        self.réseau = Réseau()
        self.images = [
            pygame.image.load("assets/oiseaux/B1.png"),
            pygame.image.load("assets/oiseaux/B2.png"),
            pygame.image.load("assets/oiseaux/B3.png"),
        ]
