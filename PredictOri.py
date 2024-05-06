__author__ = "Joseph ARIAS, Arthur BORGES"
__copyright__ = "Copyright 2024, PredictOri"
__license__ = "GPL"
__maintainer__ = "Joseph ARIAS"
__email__ = "joseph.arias@ens.uvsq.fr"
__status__ = "Released"

import flet as ft
import sys
import matplotlib.pyplot as plt
from flet.matplotlib_chart import MatplotlibChart


class Interface:
    """Classe principale de l'interface."""

    def __init__(self, page):

        self.file_picker = ft.Ref[ft.FilePicker]()
        self.page = page  # Page principale de l'interface
        self.page.title = "PredictOri"  # Titre de la page
        self.page.window_maximized = True  # Maximise la fenêtre
        self.page.overlay.append(
            ft.FilePicker(on_result=lambda e: self.file_selected(e, self.file_picker), ref=self.file_picker))
        self.chart1 = MatplotlibChart()
        self.chart2 = MatplotlibChart()

        self.change_view("accueil")

    def change_view(self, view: str):
        """Fonction qui change la vue de l'interface."""
        file_picker = self.file_picker
        self.page.views.clear()
        if view == "analyse":
            self.page.views.append(
                ft.View(
                    route="analyse",
                    scroll=ft.ScrollMode.HIDDEN,
                    on_scroll_interval=0,
                    controls=[
                        ft.Column(
                            controls=[
                                self.chart1,
                                self.chart2,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0.1 * self.page.width), ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER), )
        elif view == "explication":
            self.page.views.append(
                ft.View(
                    route="explication",
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(
                                    value="Qu'est-ce qu'une origine de réplication ?",
                                    size=30,
                                    weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    value="L'origine de réplication est une séquence d'ADN à partir de laquelle la réplication"
                                          " de l'ADN commence. Elle est caractérisée par une région riche en AT et en séquences"
                                          " spécifiques qui permettent l'initiation de la réplication.",
                                    size=20),
                                ft.FilledButton(
                                    text="Retour",
                                    on_click=lambda _: self.change_view("accueil"), ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0.1 * self.page.width), ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER), )
        elif view == "aide":
            self.page.views.append(
                ft.View(
                    route="aide",
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(
                                    value="Comment utiliser PredictOri ?",
                                    size=30,
                                    weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    value="Pour utiliser PredictOri, il vous suffit de sélectionner le fichier FASTA contenant"
                                          " le génome de la bactérie dont vous souhaitez prédire l'origine de réplication.",
                                    size=20),
                                ft.FilledButton(
                                    text="Retour",
                                    on_click=lambda _: self.change_view("accueil"), ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0.1 * self.page.width), ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER), )
        elif view == "accueil":
            self.page.views.append(ft.View(
                route="accueil",
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(
                                value="Bienvenue sur PredictOri !",
                                size=30,
                                weight=ft.FontWeight.BOLD),
                            ft.Text(
                                value="Application pour prédire l'origine de réplication d'une bactérie à partir de son"
                                      " génome.",
                                size=20),
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
                        spacing=0.1 * self.page.width), ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER), )
        elif view == "attente":
            self.page.views.append(
                ft.View(
                    route="attente",
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(
                                    value="Analyse en cours...",
                                    size=30,
                                    weight=ft.FontWeight.BOLD),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0.1 * self.page.width), ],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER), )
        self.page.go(view)

    def file_selected(self, e, file_picker: ft.Ref[ft.FilePicker]):
        """Fonction appelée lorsqu'un fichier est sélectionné."""
        if e.files is not None:
            file = file_picker.current.result.files[0].path
            self.change_view("attente")
            self.analyze_genome(e, file)
            self.change_view("analyse")

    def analyze_genome(self, e, file, len_window=10_000, overlap=9_000):
        """Fonction qui analyse le génome pour déterminer l'origine de réplication."""
        if e.files is not None:
            with open(file, 'r') as f:
                lines = f.read()
            genome = '\n'.join(lines.splitlines()[1:])
            i = 0
            ratio = []
            while True:
                end_window = min(i + len_window, len(genome))
                window = genome[i:end_window]
                nb_G = window.count('G')
                nb_C = window.count('C')
                try:
                    ratio.append((nb_G - nb_C) / (nb_G + nb_C))
                except ZeroDivisionError:
                    print(window)
                    print("Division by zero while calculating ratio, must choose a greater window size.")
                    sys.exit()
                if min(i + len_window, len(genome)) == len(genome):
                    break
                i += overlap

            fig1, ax1 = plt.subplots(figsize=(15, 6))
            ax1.plot(ratio, linewidth=0.5)
            try:
                invert_point = self.find_inversion_point(ratio)
                print(
                    f"Le point d'inversion se trouve entre les nucléotides {overlap * invert_point} et {overlap * invert_point + len_window}.")
                ax1.axhline(y=0, color='r', label='Fenêtre contenant le point d\'inversion')
                ax1.scatter(invert_point, 0, color='red', zorder=5)
                ax1.axvline(invert_point, linestyle='--', color='r', ymax=0.5)
                ax1.annotate(f'Fenêtre du point d\'inversion: {invert_point}', xy=(invert_point, 0),
                             xytext=(invert_point, -0.25),
                             color='red', ha='center', va='top')
            except Exception:
                print("Point d'inversion non trouvé.")

            val_max_y = max(abs(min(ratio)), abs(max(ratio)))
            ax1.set_ylim(-val_max_y, val_max_y)
            ax1.set_title('Ratio (G-C) / (G+C) en fonction de la fenêtre')
            ax1.set_xlabel('Window')
            ax1.set_ylabel('Ratio (G-C) / (G+C)')
            self.chart1.figure = fig1

            SeqLength = len(genome)
            InitW = 0
            x_values = [0]  # La position initiale
            y_values = [0]  # La position initiale

            while InitW <= SeqLength:
                nbA = nbC = nbG = nbT = 0
                nb = 0
                for I in range(InitW, min(InitW + len_window, SeqLength)):
                    nb += 1
                    base = genome[I]  # Python utilise des indices 0-based

                    if base == 'A':
                        nbA += 1
                    elif base == 'C':
                        nbC += 1
                    elif base == 'G':
                        nbG += 1
                    elif base == 'T':
                        nbT += 1

                NbStepsRight = nbC - nbG
                NbStepsUp = nbA - nbT
                XEndSegment = NbStepsRight * nb
                YEndSegment = NbStepsUp * nb

                x_values.append(x_values[-1] + XEndSegment)
                y_values.append(y_values[-1] + YEndSegment)

                InitW += len_window

            fig2, ax2 = plt.subplots(figsize=(15, 6))
            try:
                cusp = self.find_cusp(x_values, y_values)
                ax2.annotate('Point de rebroussement', xy=(cusp[0], cusp[1]), xytext=(cusp[0], cusp[1]), color='red',
                            ha='center', va='top')
                ax2.scatter(cusp[0], cusp[1], color='red', zorder=5)
            except Exception:
                print("Pas de point de rebroussement trouvé.")
            ax2.plot(x_values, y_values, linestyle='-')
            ax2.set_xlabel('Horizontal Direction')
            ax2.set_ylabel('Vertical Direction')
            ax2.set_title('DNA Sequence Graph')
            ax2.grid()
            self.chart2.figure = fig2

    @staticmethod
    def find_inversion_point(ratios):
        """Fonction qui trouve le point d'inversion dans une liste de ratios (G-C) / (G+C)."""
        invert_point = -1
        if ratios[0] < 0:  # si le premier ratio est négatif
            sens = 1  # alors on veut que le ratio soit positif
        else:  # sinon
            sens = -1  # on veut que le ratio soit négatif
        for i in range(1, len(ratios)):
            nb_ratio_inversions = 0  # nombre de ratios qui respectent la condition d'être de signe opposé au ratio initial
            if sens == 1 and ratios[i] > 0:  # si on veut que le ratio soit positif et que le ratio est positif
                for j in range(i+1, i+11):  # on regarde les 10 ratios suivants
                    if ratios[j] > 0:  # si le ratio est positif
                        nb_ratio_inversions += 1 # on incrémente le nombre de ratios positifs
                if nb_ratio_inversions >= 8:  # si on a trouvé au moins 8 ratios positifs
                    invert_point = i  # on a trouvé le point d'inversion
                    return invert_point
            elif sens == -1 and ratios[i] < 0:  # si on veut que le ratio soit négatif et que le ratio est négatif
                for j in range(i+1, i+11):  # on regarde les 10 ratios suivants
                    if ratios[j] < 0:  # si le ratio est négatif
                        nb_ratio_inversions += 1  # on incrémente le nombre de ratios négatifs
                if nb_ratio_inversions >= 8:  # si on a trouvé au moins 8 ratios négatifs
                    invert_point = i  # on a trouvé le point d'inversion
                    return invert_point
        raise Exception("Point d'inversion non trouvé")  # si on n'a pas trouvé de point d'inversion

    @staticmethod
    def find_cusp(x_values, y_values):
        cusp = [-1, -1]
        for i in range(1, len(x_values)):
            count = 0
            for j in range(i+1, i+11):
                if x_values[i] > x_values[j] and y_values[i] >= y_values[j]:
                    count += 1
            if count >= 8:
                cusp = [x_values[i], y_values[i]]
                return cusp
        raise Exception("Cusp not found")


ft.app(Interface)
