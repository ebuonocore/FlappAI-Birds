import random
from bird import Bird
from tuyau import *
from ia import lire_scores

# INDICE_MUTATION est un pourcentage (entre 0 et 100)
INDICE_MUTATION = 0
N_IA = 1
N_HUMAINS = 0
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
TUYAU_ESPACE_X = 800
N_TUYAUX = 3

for tour in range(30):
    print("tour numéro : ", tour)
    decalage = 0
    animation = 1
    birds_mort = []
    birds = []
    tuyaux = []
    delta_y_min, ttf_max = lire_scores()
    for i in range(N_TUYAUX):
        tuyaux.append(Tuyau())
        tuyaux[i].x += 848 * i // N_TUYAUX
    for j in range(N_HUMAINS):
        nom = "Player " + str(j + 1)
        birds.append(Bird(nom))
    for j in range(N_IA):
        nom = "IA " + str(j + 1)
        birds.append(Bird(nom, True))
        birds[-1].réseau.charger()
        birds[-1].réseau.mutation(INDICE_MUTATION)
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
                    animation += 1
            else:
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
                    birds_mort[j] = True
                if all(
                    element == True for element in birds_mort
                ):  # Vérifie si tous les oiseaux sont morts
                    running = False
                if birds[j].score > 250:
                    running = False

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
    meilleurs_birds = []
    meilleur_bird = None
    delta_ancien = delta_y_min
    delta_y_min = 600
    ttf_ancien = ttf_max
    print("Dernier ttf max et delta_y_min : ", ttf_ancien, delta_ancien)
    score_max_local = 0
    bird_plus_fort_local = None
    for bird in birds:
        if bird.score > score_max_local:
            bird_plus_fort_local = bird
    if bird_plus_fort_local is not None:
        print("Score local : ", bird_plus_fort_local.score)
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
            print("score : ", meilleur_bird.score)
            meilleur_bird.réseau.sauvegarde(
                meilleur_bird.ttf, abs(meilleur_bird.delta_y)
            )
    # Si son score ttf est égale au score enregistré mais avec un meilleur delta_y alors, on enregistre.
    elif ttf_max == ttf_ancien:
        if meilleur_bird is not None:
            if delta_y_min < delta_ancien:
                print(meilleur_bird.nom)
                print("score : ", meilleur_bird.score)
                meilleur_bird.réseau.sauvegarde(
                    meilleur_bird.ttf, abs(meilleur_bird.delta_y)
                )
