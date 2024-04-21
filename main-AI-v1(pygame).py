import pygame
import sys
import random
from bird import Bird
from tuyau import *
from ia import lire_scores

# INDICE_MUTATION est un pourcentage (entre 0 et 100)
INDICE_MUTATION = 0
N_IA = 1
N_HUMAINS = 2
if N_HUMAINS not in [0, 1, 2, 3]:
    N_HUMAINS = 0
N_BIRDS = N_IA + N_HUMAINS
# Accélération verticale descendante des birds
GRAVITE = 0.15
# Puissance de la poussée verticale ascendante
IMPULSION = -10
# Largeur de l'ouverture en pixel entre la partie basse et haute d'un tuyau
ESPACEMENT_Y = 100
# Les N_TUYAUX occupent TUYAU_ESPACE_X pixels en largeur
N_TUYAUX = 3
# Liste des touches de contrôle par défaut pour les joueurs humains
TOUCHE = [pygame.K_SPACE, pygame.K_RETURN, pygame.K_a]

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Flappy bird")
fond = pygame.image.load("assets/background.png")
ecriture_score = pygame.font.Font("assets/pixel_font.ttf", 17)
ecriture_player = pygame.font.Font("assets/pixel_font.ttf", 12)
decalage = 0
animation = 1
birds_mort = []
birds = []
tuyaux = []
delta_y_min, ttf_max = lire_scores()
for i in range(N_TUYAUX):
    tuyaux.append(Tuyau())
    tuyaux[i].x += 848 * i / N_TUYAUX
for j in range(N_HUMAINS):
    nom = "Player " + str(j + 1)
    birds.append(Bird(nom))
for j in range(N_IA):
    nom = "IA " + str(j + 1)
    birds.append(Bird(nom, True))
    birds[-1].réseau.charger()
    birds[-1].réseau.mutation(INDICE_MUTATION)
# Affiche le diagramme de la dernière IA si elle existe
if N_IA > 0:
    print(birds[-1].réseau.diagramme())
for l in range(N_BIRDS):
    birds_mort.append(False)

running = N_BIRDS > 0

while running:
    decalage -= 0.5

    for i in range(len(tuyaux)):
        tuyaux[i].x -= tuyaux[i].vx

    for i in range(len(tuyaux)):
        tuyaux[i].point_droit = tuyaux[i].x + tuyaux[i].nouvelle_largeur

    for j in range(N_BIRDS):
        for i in range(len(tuyaux)):
            if birds[j].x > tuyaux[i].point_droit:
                if i != birds[j].id_tuyau_passé:
                    birds[j].score += 1
                    birds[j].id_tuyau_passé = i

    for j in range(N_BIRDS):
        birds[j].vy += GRAVITE

    for i in range(len(tuyaux)):
        if tuyaux[i].x < -48:
            tuyaux[i].x = 800
            tuyaux[i].y = random.randint(100, 500)

    for j in range(N_BIRDS):
        if birds[j].sens == 1:
            birds[j].sens = 0
            birds[j].vy = IMPULSION

        birds[j].y += birds[j].vy

    for j in range(N_BIRDS):
        if birds[j].vivant:
            if birds[j].vy < 0:
                birds[j].vy -= IMPULSION // 80
                birds[j]._image = pygame.transform.rotate(
                    birds[j].images[(animation // 4) % 3], -birds[j].angle
                )
                animation += 1
            else:
                birds[j]._image = pygame.transform.rotate(
                    birds[j].images[0], -birds[j].angle
                )
            birds[j].angle = min(birds[j].vy * 3, 90)
        else:
            birds[j]._image = pygame.transform.rotate(birds[j].images[0], 180)
            birds[j].x -= tuyaux[0].vx

    # condition de mort du bird
    for i in range(len(tuyaux)):
        for j in range(N_BIRDS):
            if birds[j].x > tuyaux[i].x or birds[j].x + 32 > tuyaux[i].x:
                if (
                    birds[j].x < tuyaux[i].point_droit
                    or birds[j].x + 32 < tuyaux[i].point_droit
                ):
                    if (
                        birds[j].y + 32 > tuyaux[i].y
                        or birds[j].y < tuyaux[i].y - ESPACEMENT_Y
                    ):
                        birds[j].vivant = False

            if (birds[j].y + 32) < 0 or birds[j].y > 600:
                birds[j].vivant = False

            if not birds[j].vivant:
                if (
                    birds[j].y > 600
                ):  # Vérifie si l'oiseau est mort et est sorti de l'écran
                    birds_mort[j] = True
            if all(
                element == True for element in birds_mort
            ):  # Vérifie si tous les oiseaux sont morts
                running = False
            if birds[j].score > 200:
                running = False

    screen.blit(fond, (decalage % 800, 0))
    screen.blit(fond, (decalage % 800 - 800, 0))
    for i in range(len(tuyaux)):
        screen.blit(tuyaux[i].image_bas, (tuyaux[i].x, tuyaux[i].y))
        screen.blit(
            tuyaux[i].image_haut, (tuyaux[i].x, tuyaux[i].y - 768 - ESPACEMENT_Y)
        )
    for j in range(N_BIRDS):
        screen.blit(birds[j]._image, (birds[j].x, birds[j].y))
        player = ecriture_player.render(birds[j].nom, True, (0, 0, 0))
        if birds[j].ia == False and N_HUMAINS > 1:
            if birds[j].vivant:
                screen.blit(
                    player, (200, (birds[j].y - 30))
                )  # affichage du nom du joueur au dessu de l'oiseaux
        if birds[j].vivant:
            affichage_score = ecriture_score.render(
                "score : " + str(birds[j].score), True, (0, 0, 0)
            )
            screen.blit(affichage_score, (10, 0))  # affichage du score

    keys = pygame.key.get_pressed()

    tuyau_min = 800
    tuyau_y = 600
    for tuyau in tuyaux:
        if tuyau.point_droit < tuyau_min and tuyau.point_droit > 200:
            tuyau_min = tuyau.point_droit
            tuyau_y = tuyau.y

    for bird in birds:
        if bird.ia and bird.vivant:
            bird.ttf += 1
            bird.delta_y = bird.y - tuyau_y
            if bird.réseau.résultat(
                [(tuyau_min - bird.x) / 200, (-bird.delta_y) / 250]
            ):
                bird.sens = 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        for j in range(N_HUMAINS):
            if keys[TOUCHE[j]] and birds[j].vivant:
                birds[j].sens = 1
        if event.type == pygame.KEYDOWN:
            # touche "x" tue le deuxième bird en plein vol
            if event.key == pygame.K_x and N_BIRDS > 0:
                birds[1].vivant = False
            # touche "m" tue le premier bird en plein vol
            if event.key == pygame.K_m:
                birds[0].vivant = False
    pygame.display.update()

meilleurs_birds = []
meilleur_bird = None
delta_ancien = delta_y_min
delta_y_min = 600
ttf_ancien = ttf_max
print("Dernier ttf max et delta_y_min : ", ttf_ancien, delta_ancien)
# Sélectionne le ou les Birds qui sont allés le plus loin
for j in range(N_HUMAINS, N_BIRDS):
    if birds[j].ttf > ttf_max:
        print("  Nouveau max trouvé: ", birds[j].ttf)
        ttf_max = birds[j].ttf
        meilleurs_birds = [birds[j]]
    elif birds[j].ttf == ttf_max:
        meilleurs_birds.append(birds[j])
print("  Nombre de candidats : ", len(meilleurs_birds))
# Parmi les plus aventureux, sélectionne celui qui se rapproche le plus du point bas d el'entrée du prochain tuyau
for bird in meilleurs_birds:
    print("    Delta_y du prétendant : ", abs(bird.delta_y))
    if abs(bird.delta_y) < delta_y_min:
        delta_y_min = abs(bird.delta_y)
        meilleur_bird = bird
# Si son score ttf bat le record enregistré, alors cette mutation est sauvegardée
if ttf_max > ttf_ancien:
    if meilleur_bird is not None:
        print(meilleur_bird.nom)
        meilleur_bird.réseau.sauvegarde(meilleur_bird.ttf, abs(meilleur_bird.delta_y))
# Si son score ttf est égale au score enregistré mais avec un meilleur delta_y alors, on enregistre.
elif ttf_max == ttf_ancien:
    if meilleur_bird is not None:
        if delta_y_min < delta_ancien:
            print(meilleur_bird.nom)
            meilleur_bird.réseau.sauvegarde(
                meilleur_bird.ttf, abs(meilleur_bird.delta_y)
            )
