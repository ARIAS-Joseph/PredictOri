__author__ = "Joseph ARIAS, Arthur BORGES"
__copyright__ = "Copyright 2024, PredictOri"
__license__ = "GPL"
__maintainer__ = "Joseph ARIAS"
__email__ = "joseph.arias@ens.uvsq.fr"
__status__ = "Released"

import flet as ft
import matplotlib.pyplot as plt
from flet.matplotlib_chart import MatplotlibChart
import regex as re
import threading


# PARTIE INTERFACE GRAPHIQUE


class Interface:
    """Classe de l'interface."""

    def __init__(self, page):

        self.file_picker = ft.Ref[ft.FilePicker]()  # Sélecteur de fichier
        self.progress_ring = ft.Ref[ft.ProgressRing]()  # Anneau de progression pour visualiser le temps d'attente
        # restant
        self.page = page  # Page de l'interface qui contiendra les différentes fenêtres (views)
        self.page.title = "PredictOri"  # Titre de la page
        self.page.window_maximized = True  # Maximise la fenêtre
        self.window_ori = 0  # Fenêtre contenant le point d'inversion
        self.ori_start = 0  # Nucléotide du début de la fenêtre contenant l'origine de réplication
        self.ori_end = 0  # Nucléotide de la fin de la fenêtre contenant de l'origine de réplication
        # Ajout du sélecteur de fichier
        self.page.overlay.append(
            ft.FilePicker(on_result=lambda e: self.file_selected(e, self.file_picker), ref=self.file_picker))
        self.chart1 = MatplotlibChart()  # Graphique pour afficher le ratio (G-C) / (G+C) en fonction de la fenêtre
        self.chart2 = MatplotlibChart()  # Graphique pour afficher le chemin de la séquence d'ADN
        self.wait_graph = threading.Condition()  # Condition pour attendre la fin de la création des graphiques

        # Création de la vue d'accueil
        self.change_view("accueil")

    def change_view(self, view: str, err_mess: str = None):
        """Fonction qui change la vue de l'interface."""
        file_picker = self.file_picker
        self.page.views.clear()  # On supprime les vues précédentes
        appbar = None  # Barre d'application qui apparait en haut de la page
        scroll = None  # Mode de défilement
        controls = []  # Contrôles de la page
        on_scroll_interval = None  # Intervalle de défilement
        vertical_alignment = ft.MainAxisAlignment.CENTER  # Alignement vertical
        horizontal_alignment = ft.CrossAxisAlignment.CENTER  # Alignement horizontal
        # Vérification de la vue à afficher
        if view == "analyse":  # Vue d'analyse
            scroll = ft.ScrollMode.HIDDEN  # On cache la barre de défilement
            on_scroll_interval = 0
            controls = [
                ft.Column(
                    controls=[
                        # On affiche le graphique du ratio (G-C) / (G+C) en fonction de la fenêtre
                        self.chart1,
                        # On affiche où se trouve l'origine de réplication
                        ft.Text(f"L'origine de réplication se trouve entre les nucléotides "
                                f"{format(self.ori_start, ',')} "
                                f"et {format(self.ori_end, ',')} dans la fenêtre {self.window_ori}.",
                                size=20),
                        # On affiche le graphique du chemin de la séquence d'ADN
                        self.chart2,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0.01 * self.page.width), ]
            vertical_alignment = ft.MainAxisAlignment.CENTER
            appbar = ft.AppBar(leading=ft.IconButton(icon=ft.icons.ARROW_CIRCLE_LEFT,
                                                     on_click=lambda _: self.change_view("accueil"),
                                                     tooltip="Retour à l'accueil"))
        elif view == "explication":  # Vue d'explication
            controls = [ft.Row(
                controls=[
                    ft.Text(
                        value="Qu'est-ce qu'une origine de réplication ?",
                        size=30,
                        weight=ft.FontWeight.BOLD)],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
                # On affiche le texte d'explication qui est contenu dans le fichier explications_ori.txt
                ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Text(
                            value=open("./assets/text/explications_ori.txt", "r", encoding="UTF-8").read(),
                            size=20, ), ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                )]
            appbar = ft.AppBar(leading=ft.IconButton(icon=ft.icons.ARROW_CIRCLE_LEFT,
                                                     on_click=lambda _: self.change_view("accueil"),
                                                     tooltip="Retour à l'accueil"),
                               title=ft.Text("Qu'est ce que l'origine de réplication ?", size=20),
                               title_spacing=0.0)
            vertical_alignment = ft.MainAxisAlignment.CENTER
            scroll = ft.ScrollMode.AUTO
            on_scroll_interval = 0
        elif view == "aide":
            controls = [
                ft.Column(
                    controls=[
                        ft.Text(
                            value="Comment utiliser PredictOri ?",
                            size=30,
                            weight=ft.FontWeight.BOLD),
                        ft.Text(
                            value="Pour utiliser PredictOri, il vous suffit de sélectionner le fichier FASTA "
                                  "contenant le génome de la bactérie dont vous souhaitez prédire l'origine "
                                  "de réplication.",
                            size=20),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0.1 * self.page.width), ]
            vertical_alignment = ft.MainAxisAlignment.CENTER
            horizontal_alignment = ft.CrossAxisAlignment.CENTER
            appbar = ft.AppBar(leading=ft.IconButton(icon=ft.icons.ARROW_CIRCLE_LEFT,
                                                     on_click=lambda _: self.change_view("accueil"),
                                                     tooltip="Retour à l'accueil"))
        elif view == "accueil":
            controls = [ft.Column(
                controls=[
                    ft.Text(
                        value="Bienvenue sur PredictOri !",
                        size=30,
                        weight=ft.FontWeight.BOLD),
                    ft.Text(
                        value="Application pour prédire l'origine de réplication d'une bactérie à partir de son"
                              " génome.",
                        size=20),
                    # Bouton pour commencer l'analyse et qui permet la sélection du fichier FASTA
                    ft.FilledButton(
                        text="Commencer",
                        on_click=lambda _: file_picker.current.pick_files(
                            dialog_title="Sélectionnez le fichier FASTA contenant le génome de la bactérie",
                            file_type=ft.FilePickerFileType.CUSTOM,
                            allowed_extensions=["fasta"],
                            allow_multiple=False), ),
                    ft.FilledButton(
                        text="Qu'est-ce qu'une origine de réplication ?",
                        on_click=lambda _: self.change_view("explication"), ),
                    ft.FilledButton(
                        text="Comment utiliser PredictOri ?",
                        on_click=lambda _: self.change_view("aide"), ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0.1 * self.page.width), ]
        elif view == "attente":  # Vue d'attente
            controls = [ft.Column(
                controls=[
                    ft.Text(
                        value="Analyse en cours...",
                        size=30,
                        weight=ft.FontWeight.BOLD),
                    ft.ProgressRing(ref=self.progress_ring),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0.1 * self.page.width), ]
            vertical_alignment = ft.MainAxisAlignment.CENTER
            horizontal_alignment = ft.CrossAxisAlignment.CENTER
        elif view == "erreur":  # Vue d'erreur
            button = ft.FilledButton(
                text="Voir les résultats malgré tout",
                on_click=lambda _: self.change_view("analyse"), )
            controls = [ft.Column(
                controls=[
                    ft.Text(
                        value="Erreur",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.RED),
                    ft.Text(
                        value=err_mess,
                        size=20),
                    ft.FilledButton(
                        text="Revenir à l'accueil",
                        on_click=lambda _: self.change_view("accueil"), ),
                    button,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0.1 * self.page.width), ]
            vertical_alignment = ft.MainAxisAlignment.CENTER
            horizontal_alignment = ft.CrossAxisAlignment.CENTER

        # Ajout de la vue à la page principale
        self.page.views.append(ft.View(
            route=view,
            appbar=appbar,
            controls=controls,
            horizontal_alignment=horizontal_alignment,
            vertical_alignment=vertical_alignment,
            scroll=scroll,
            on_scroll_interval=on_scroll_interval,
        ))
        self.page.go(view)

    def file_selected(self, e, file_picker: ft.Ref[ft.FilePicker]):
        """Fonction appelée lorsqu'un fichier est sélectionné."""
        if e.files is not None:
            file = file_picker.current.result.files[0].path  # On récupère le chemin du fichier
            self.change_view("attente")  # On affiche la vue d'attente
            thread = threading.Thread(target=self.analyze_genome, args=(e, file))  # On crée un thread pour l'analyse
            thread.start()  # On démarre le thread
            with self.wait_graph:
                self.wait_graph.wait()  # On attend la fin de la création des graphiques
                thread.join()
            if self.page.views[-1].route != "erreur":  # Si aucune erreur n'est survenue
                self.change_view("analyse")  # On affiche la vue d'analyse

    # PARTIE BIOLOGIE

    def analyze_genome(self, e, file):
        """Fonction qui analyse le génome pour déterminer l'origine de réplication."""
        if e.files is not None:
            with open(file, 'r') as f:
                lines = f.read().strip()  # On lit le fichier FASTA en enlevant les espaces et les retours à la ligne
            genome = "".join(lines.splitlines()[1:]).upper()  # On récupère la séquence d'ADN à partir de la 2ème ligne
            len_window = len(genome) // 175  # on crée 175 fenêtres
            overlap = (len_window // 10) * 9  # on chevauche les fenêtres de 90%
            non_dna = re.compile(r'[^ATCGU]')  # on crée une regex pour trouver les caractères non nucléotidiques
            search_non_nucl = non_dna.search(genome)  # on cherche les caractères non nucléotidiques
            if search_non_nucl:  # si on trouve des caractères non nucléotidiques
                # on affiche un message d'erreur
                self.change_view("erreur", "Le fichier FASTA contient des caractères non nucléotidiques"
                                           f" (le premier est {genome[search_non_nucl.span()[0]]} au nucléotide "
                                           f"{search_non_nucl.span()[0]}).")
                self.wait_graph.notify()  # on notifie la fin de la création des graphiques
                return  # on arrête la fonction
            elif "U" in genome:  # si on trouve des uraciles dans la séquence
                self.change_view("erreur", "Le fichier FASTA est une séquence d'ARN. Une séquence d'ADN est requise.")
                self.wait_graph.notify()  # on notifie la fin de la création des graphiques
                return  # on arrête la fonction

            i = 0  # on initialise l'indice de la fenêtre
            ratio = []  # on crée une liste pour stocker les ratios (G-C) / (G+C)
            self.progress_ring.current.value = 0
            self.page.update()
            while True:
                end_window = min(i + len_window, len(genome))  # on détermine la fin de la fenêtre
                window = genome[i:end_window]  # on récupère la fenêtre
                nb_g = window.count('G')  # on compte le nombre de G
                nb_c = window.count('C')   # on compte le nombre de C
                try:
                    ratio.append((nb_g - nb_c) / (nb_g + nb_c))  # on ajoute le ratio (G-C)/(G+C) à la liste
                except ZeroDivisionError:  # s'il y a une division par zéro
                    self.change_view("erreur", "Division par zéro. Vérifiez que le fichier FASTA contient des G et C. "
                                               "Si c'est le cas, veuillez modifier la taille de la fenêtre ou du "
                                               "chevauchement.")
                    self.wait_graph.notify()  # on notifie la fin de la création des graphiques
                    return  # on arrête la fonction
                if min(i + len_window, len(genome)) == len(genome):  # si on est à la fin de la séquence
                    break  # on arrête la boucle
                i += overlap  # on avance la fenêtre
                self.progress_ring.current.value = (i / len(genome)) / 2  # on met à jour la barre de progression
                self.page.update()  # on met à jour la page

            self.progress_ring.current.value = None
            self.page.update()
            fig1, ax1 = plt.subplots(figsize=(15, 6))  # on crée une figure pour le graphique affichant les ratios en
            # fonction de la fenêtre
            ax1.plot(ratio, linewidth=0.5)  # on affiche les ratios
            invert_point = self.find_inversion_point(ratio)  # on cherche le point d'inversion
            if len(invert_point) > 1:  # si on trouve plusieurs points d'inversion
                # on affiche un message d'erreur
                self.change_view("erreur", "Plusieurs points d'inversion trouvés. Veuillez modifier la taille "
                                           "de la fenêtre ou du chevauchement. Si le problème persiste, "
                                           "le point d'inversion ne peut être trouvé par l'algorithme utilisé.")
            elif len(invert_point) == 0:  # si on ne trouve pas de point d'inversion
                # on affiche un message d'erreur
                self.change_view("erreur", "Aucun point d'inversion trouvé. Veuillez modifier la taille de la fenêtre "
                                           "ou du chevauchement. Si le problème persiste, le point d'inversion ne peut "
                                           "être trouvé par l'algorithme utilisé.", )

            for invert_point in self.find_inversion_point(ratio):  # on affiche le point d'inversion
                self.window_ori = invert_point
                self.ori_start = overlap * invert_point
                self.ori_end = overlap * invert_point + len_window
                ax1.axhline(y=0, color='r', label='Fenêtre contenant le point d\'inversion')
                ax1.scatter(invert_point, 0, color='red', zorder=5)
                ax1.axvline(invert_point, linestyle='--', color='r', ymax=0.5)
                ax1.annotate(f'Fenêtre du point d\'inversion: {invert_point}', xy=(invert_point, 0),
                             xytext=(invert_point, -0.25),
                             color='red', ha='center', va='top')

            val_max_y = max(abs(min(ratio)), abs(max(ratio)))
            ax1.set_ylim(-val_max_y, val_max_y)
            ax1.set_title('Ratio (G-C) / (G+C) en fonction de la fenêtre')
            ax1.set_xlabel('Window')
            ax1.set_ylabel('Ratio (G-C) / (G+C)')
            self.chart1.figure = fig1

            seq_length = len(genome)
            window = 0
            x_values = [0]  # La position initiale
            y_values = [0]  # La position initiale

            self.progress_ring.current.value = 0.5
            self.page.update()
            while window <= seq_length:
                nba = nbc = nbg = nbt = 0
                nb = 0
                for i in range(window, min(window + len_window, seq_length)):
                    nb += 1
                    base = genome[i]  # Python utilise des indices 0-based

                    if base == 'A':
                        nba += 1
                    elif base == 'C':
                        nbc += 1
                    elif base == 'G':
                        nbg += 1
                    elif base == 'T':
                        nbt += 1

                nb_steps_right = nbc - nbg
                nb_steps_up = nba - nbt
                x_end_segment = nb_steps_right * nb
                y_end_segment = nb_steps_up * nb

                x_values.append(x_values[-1] + x_end_segment)
                y_values.append(y_values[-1] + y_end_segment)

                window += len_window
                self.progress_ring.current.value = 0.5 + (window / seq_length) / 2
                self.page.update()

            self.progress_ring.current.value = None
            self.page.update()
            fig2, ax2 = plt.subplots(figsize=(15, 6))
            cusps = self.find_cusp(x_values, y_values)
            if len(cusps) == 0:
                self.change_view("erreur", "Aucun point d'inversion trouvé. Veuillez modifier la taille "
                                           "de la fenêtre ou du chevauchement. Si le problème persiste, "
                                           "le point d'inversion ne peut être trouvé par l'algorithme utilisé.")
            elif len(cusps) > 1:
                self.change_view("erreur", "Plusieurs points d'inversions trouvés. Veuillez modifier la taille "
                                           "de la fenêtre ou du chevauchement. Si le problème persiste, "
                                           "le point d'inversion ne peut être trouvé par l'algorithme utilisé.")
            for cusp in cusps:
                ax2.scatter(cusp[0], cusp[1], color='red', zorder=5)
            ax2.plot(x_values, y_values, linestyle='-')
            ax2.set_xlabel('Horizontal Direction')
            ax2.set_ylabel('Vertical Direction')
            ax2.set_title('DNA Sequence Graph')
            ax2.grid()
            self.chart2.figure = fig2
            with self.wait_graph:
                self.wait_graph.notify()

    @staticmethod
    def find_inversion_point(ratios):
        """Fonction qui trouve le point d'inversion dans une liste de ratios (G-C) / (G+C)."""
        invert_point = []
        if ratios[0] < 0:  # si le premier ratio est négatif
            sens = 1  # on veut que le ratio soit positif
        else:  # sinon
            sens = -1  # on veut que le ratio soit négatif
        for i in range(1, len(ratios)):
            nb_ratio_inversions = 0  # nombre de ratios qui respectent la condition d'être de signe opposé au ratio
            # initial
            if sens == 1 and ratios[i] > 0:  # si on veut que le ratio soit positif et que le ratio est positif
                for j in range(i + 1, min(i + 11, len(ratios))):  # on regarde les 10 ratios suivants
                    if ratios[j] > 0:  # si le ratio est positif
                        nb_ratio_inversions += 1  # on incrémente le nombre de ratios positifs
                if nb_ratio_inversions >= 8:  # si on a trouvé au moins 8 ratios positifs
                    invert_point.append(i)  # on a trouvé le point d'inversion
                    sens = -1  # on veut que le ratio soit négatif

            elif sens == -1 and ratios[i] < 0:  # si on veut que le ratio soit négatif et que le ratio est négatif
                for j in range(i + 1, min(i + 11, len(ratios))):  # on regarde les 10 ratios suivants
                    if ratios[j] < 0:  # si le ratio est négatif
                        nb_ratio_inversions += 1  # on incrémente le nombre de ratios négatifs
                if nb_ratio_inversions >= 8:  # si on a trouvé au moins 8 ratios négatifs
                    invert_point.append(i)  # on a trouvé le point d'inversion
                    sens = 1  # on veut que le ratio soit positif
        return invert_point

    @staticmethod
    def find_cusp(x_values, y_values):
        """Fonction qui trouve le point de rebroussement dans une liste de coordonnées."""
        cusp = []
        # on se base sur les 100 premiers nucléotides pour déterminer la direction initiale
        if x_values[100] < 0 and y_values[100] < 0:
            direction = "sud-ouest"
        elif x_values[100] < 0 < y_values[100]:
            direction = "nord-ouest"
        elif x_values[100] > 0 > y_values[100]:
            direction = "sud-est"
        else:
            direction = "nord-est"
        for i in range(1, len(x_values)):  # on parcourt les coordonnées
            count = 0  # compteur pour les 10 prochaines coordonnées
            for j in range(i + 1, min(i + 11, len(x_values))):  # on regarde les 10 coordonnées suivantes
                if direction == "sud-ouest":  # si la direction est sud-ouest
                    if x_values[j] > x_values[i] and y_values[j] > y_values[i]:  # si les coordonnées suivantes sont
                        # dans le sens opposé à la direction
                        count += 1  # on incrémente le compteur
                elif direction == "nord-ouest":
                    if x_values[j] > x_values[i] and y_values[j] < y_values[i]:
                        count += 1
                elif direction == "sud-est":
                    if x_values[j] < x_values[i] and y_values[j] > y_values[i]:
                        count += 1
                else:
                    if x_values[j] < x_values[i] and y_values[j] < y_values[i]:
                        count += 1
            if count == 10:  # si les 10 coordonnées suivantes sont dans le sens opposé à la direction
                cusp.append((x_values[i], y_values[i]))  # on a trouvé un point de rebroussement
                try:  # on détermine la nouvelle direction à partir des 10 prochaines coordonnées
                    if x_values[i+10] < x_values[i] and y_values[i+10] < y_values[i]:
                        direction = "sud-ouest"
                    elif x_values[i+10] < x_values[i] and y_values[i+10] > y_values[i]:
                        direction = "nord-ouest"
                    elif x_values[i+10] > x_values[i] and y_values[i+10] < y_values[i]:
                        direction = "sud-est"
                    else:
                        direction = "nord-est"
                except IndexError:
                    break
        return cusp  # on retourne la liste des points de rebroussement


ft.app(Interface)
