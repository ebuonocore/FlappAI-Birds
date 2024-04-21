import pygame
import random


class Tuyau:
    def __init__(self):
        self.y = random.randint(300, 600)
        self.x = 800
        self.vx = 2
        image_bas = pygame.image.load("assets/tuyau.png")
        image = pygame.image.load("assets/tuyau.png")
        image_haut = pygame.transform.flip(image, False, True)
        # Redimensionner l'image du tuyau
        largeur_actuelle, hauteur_actuelle = image_bas.get_size()
        self.nouvelle_largeur = largeur_actuelle * 1.5
        self.nouvelle_hauteur = hauteur_actuelle * 1.5
        self.image_bas = pygame.transform.scale(
            image_bas, (self.nouvelle_largeur, self.nouvelle_hauteur)
        )
        self.image_haut = pygame.transform.scale(
            image_haut, (self.nouvelle_largeur, self.nouvelle_hauteur)
        )
        self.point_droit = self.x + self.nouvelle_largeur
