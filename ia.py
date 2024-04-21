import random
import graphviz
import json
import os


class Neurone_entrée:
    """Une instance de la classe Neurone_entrée correspond à unpoint d'entrée du réseau de neurones : Le capteur d'un observable.
    Ces neurones n'ont ni seuil ni entrées.
    """

    def __init__(self, nom, valeur=None):
        self.valeur = valeur
        self.nom = nom

    def sortie(self):
        """Getter de la valeur produite par le neurone."""
        if self.valeur is not None:
            return self.valeur
        else:
            return 0


class Neurone:
    """Elément de base du réseau."""

    def __init__(self, nom, entrées_dict: dict):
        self.seuil = 2
        self.entrées = entrées_dict
        self.nom = nom

    def sortie(self):
        """Getter de la valeur produite par le neurone."""
        somme = 0
        for entrée, coef in self.entrées.items():
            valeur = entrée.sortie()
            somme += valeur * coef
        return int(somme > self.seuil)


class Réseau:
    """Le réseau reçoit les valuers des observables par ses Neurones_entrée listés par self.entrées_réseau.
    Les calculs en cascade se répercuttent jusqu'au neuron feuille self.feuille
    """

    def __init__(self):
        self.entrées_réseau = []
        self.neurones = []
        self.feuille = None
        self.construction()

    def construction(self):
        # 3 paramètres d'entrée au réseau: Delta_Y,Delta_X, Vy
        e1 = Neurone_entrée(12)
        self.entrées_réseau.append(e1)
        e2 = Neurone_entrée(13)
        self.entrées_réseau.append(e2)
        e3 = Neurone_entrée(14)
        self.entrées_réseau.append(e3)
        # 11 neurones intermédiaires
        n5 = Neurone(5, {e1: 1})
        self.neurones.append(n5)
        n6 = Neurone(6, {e2: 1})
        self.neurones.append(n6)
        n7 = Neurone(7, {e3: 1})
        self.neurones.append(n7)
        n8 = Neurone(8, {e1: 1, e2: 1})
        self.neurones.append(n8)
        n9 = Neurone(9, {e1: 1, e3: 1})
        self.neurones.append(n9)
        n10 = Neurone(10, {e2: 1, e3: 1})
        self.neurones.append(n10)
        n11 = Neurone(11, {e1: 1, e2: 1, e3: 1})
        self.neurones.append(n11)
        n1 = Neurone(1, {n5: 1, n8: 1, n11: 1})
        self.neurones.append(n1)
        n2 = Neurone(2, {n6: 1, n9: 1, n11: 1})
        self.neurones.append(n2)
        n3 = Neurone(3, {n7: 1, n10: 1, n11: 1})
        self.neurones.append(n3)
        n4 = Neurone(4, {n11: 1})
        self.neurones.append(n4)
        # n0 est la feuille
        n0 = Neurone(0, {n1: 1, n2: 1, n3: 1, n4: 1})
        self.feuille = n0
        self.neurones.append(n0)

    def résultat(self, entrées_réseau: list) -> float:
        """Place les valeurs listées dans entrées_réseau dans chacun des Neurone_entrée.
        Appelle la méthode sortie() de la feuille qui appelle en cascade la sortie de tous les neurons du réseau jusqu'aux entrées.
        """
        for i in range(len(entrées_réseau)):
            self.entrées_réseau[i].valeur = entrées_réseau[i]
        return self.feuille.sortie()

    def diagramme(self) -> str:
        """Produit le diagramme Graphviz (https://dreampuf.github.io/GraphvizOnline) du réseau de neurones."""
        dot = graphviz.Digraph(comment="Réseau de neurones")
        for entrée in self.entrées_réseau:
            dot.node(str(entrée.nom), label="E" + str(entrée.nom))
        for neurone in self.neurones:
            dot.node(
                str(neurone.nom),
                label=str(neurone.nom) + "_" + str(round(neurone.seuil, 2)),
            )
        for neurone in self.neurones:
            for n, c in neurone.entrées.items():
                dot.edge(str(n.nom), str(neurone.nom), label=str(round(c, 2)))
        return dot.source

    def sauvegarde(self, ttf: float, delta_y: float) -> None:
        """Enregistre la structure du réseau de neurone et ses dernières performances dans un fichier mut_xxx.json dans le répertoire /mutatek.
        Le fichier json contient une liste :
          * de dictionnaires de neurones décrits par leur nom, valeur de seuil, dictionnaire des antécédents (id du neurone : coefficient d'entrée)
          * valeur de ttf atteint
          * valeur de delta_min atteint
        """
        # Construction de la liste des neurones
        réseaux_neurones = []
        for neurone_actif in self.neurones:
            neurone = dict()
            neurone["nom"] = neurone_actif.nom
            neurone["seuil"] = neurone_actif.seuil
            entrées = dict()
            for n, c in neurone_actif.entrées.items():
                entrées[int(n.nom)] = c
            neurone["entrees"] = entrées
            réseaux_neurones.append(neurone)
        # ajout des performances
        réseaux_neurones.append(ttf)
        réseaux_neurones.append(delta_y)
        # Liste tous les fichiers dans le dossier spécifié mutatek
        dossier = "mutatek"
        fichiers = os.listdir(dossier)
        fichiers.sort()
        # S'il n'y a aucun fichier, amlors mut_000;son est créé, sinon, incrémente l'indice du fichier de sauvegarde
        if len(fichiers) == 0:
            fichier = dossier + "/mut_000.json"
        else:
            dernier_fichier = fichiers[-1][4:7]
            indice_fichier = str(int(dernier_fichier) + 1)
            indice_fichier = (3 - len(indice_fichier)) * "0" + indice_fichier
            fichier = dossier + "/mut_" + indice_fichier + ".json"
        # Sauvegarde le fichier
        with open(fichier, "w") as json_file:
            json.dump(réseaux_neurones, json_file)

    def charger(self):
        """Récupère les informations du dernier fichier json du dossier mutatek.
        Met à jour les liaisons du réseau de neurones (coefficients des liaisons)
        """
        fichiers = os.listdir("mutatek")
        fichiers.sort()
        ancien_fichier = "mutatek/" + fichiers[-1]
        with open(ancien_fichier) as json_data:
            données = json.load(json_data)
        delta_y = données.pop()
        ttf = données.pop()
        for dico in données:
            neurone_actif = self.trouver_neurone(dico["nom"])
            neurone_actif.seuil = dico["seuil"]
            entrées = dico["entrees"]
            neurone_actif.entrées = dict()
            for numéro, val in entrées.items():
                num = int(numéro)
                neurone_entrée = self.trouver_neurone(num)
                neurone_actif.entrées[neurone_entrée] = val
            if dico["nom"] == 0:
                self.feuille = neurone_actif

    def mutation(self, pourcentage: int):
        """Fais varié les valeurs des coefficients des liaisons et des seuils aléatoirement et fonction du paramètre pourcentage."""
        for neurone_actif in self.neurones:
            gamme = list(range(-pourcentage, pourcentage + 1))
            aléa = random.choice(gamme)
            neurone_actif.seuil = neurone_actif.seuil * (1 + aléa / 100) + (aléa / 10)
            for n, c in neurone_actif.entrées.items():
                aléa = random.choice(gamme)
                neurone_actif.entrées[n] = c * (1 + aléa / 100) + (aléa / 10)

    def trouver_neurone(self, numéro: int) -> Neurone | Neurone_entrée:
        """Prend en paramètre un entier et renvoie le neurone de la liste self.neurones ou self.entrées_neurone qui a un nom correspondant à numéro.
        Sinon, renvoie None
        """
        for neurone in self.neurones:
            if neurone.nom == numéro:
                return neurone
        for neurone in self.entrées_réseau:
            if neurone.nom == numéro:
                return neurone
        return None


def lire_scores(fichier=None) -> tuple:
    """Ouvre le fichier désigné par le paramètre fichier et renvoie les valeurs des performances associées : delta_y et ttf"""
    if fichier is None:
        fichiers = os.listdir("mutatek")
        if len(fichiers) == 0:
            return 600, 0
        fichiers.sort()
        fichier = "mutatek/" + fichiers[-1]
    with open(fichier) as json_data:
        données = json.load(json_data)
    delta_y = données.pop()
    ttf = données.pop()
    return delta_y, ttf
