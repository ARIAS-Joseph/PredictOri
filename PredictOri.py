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


# PARTIE INTERFACE GRAPHIQUE


class Interface:
    """Classe principale de l'interface."""

    def __init__(self, page):

        self.file_picker = ft.Ref[ft.FilePicker]()
        self.progress_ring = ft.Ref[ft.ProgressRing]()
        self.page = page  # Page principale de l'interface
        self.page.title = "PredictOri"  # Titre de la page
        self.page.window_maximized = True  # Maximise la fenêtre
        self.window_ori = 0
        self.ori_start = 0
        self.ori_end = 0
        self.page.overlay.append(
            ft.FilePicker(on_result=lambda e: self.file_selected(e, self.file_picker), ref=self.file_picker))
        self.chart1 = MatplotlibChart()
        self.chart2 = MatplotlibChart()

        self.change_view("accueil")

    def change_view(self, view: str, err_mess : str = None):
        """Fonction qui change la vue de l'interface."""
        file_picker = self.file_picker
        self.page.views.clear()
        appbar = None
        scroll = None
        controls = []
        on_scroll_interval = None
        vertical_alignment = ft.MainAxisAlignment.CENTER
        horizontal_alignment = ft.CrossAxisAlignment.CENTER
        if view == "analyse":
            scroll = ft.ScrollMode.HIDDEN
            on_scroll_interval = 0
            controls = [
                ft.Column(
                    controls=[
                        self.chart1,
                        ft.Text(f"L'origine de réplication se trouve entre les nucléotides {self.ori_start} "
                                f"et {self.ori_end} dans la fenêtre {self.window_ori}.",
                                size=20),
                        self.chart2,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0.01 * self.page.width), ]
            vertical_alignment = ft.MainAxisAlignment.CENTER
            appbar = ft.AppBar(leading=ft.IconButton(icon=ft.icons.ARROW_CIRCLE_LEFT,
                                                     on_click=lambda _: self.change_view("accueil"),
                                                     tooltip="Retour à l'accueil"))
        elif view == "explication":
            controls = [ft.Row(
                controls=[
                    ft.Text(
                        value="Qu'est-ce qu'une origine de réplication ?",
                        size=30,
                        weight=ft.FontWeight.BOLD)],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
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
        elif view == "attente":
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
        elif view == "erreur":
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
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0.1 * self.page.width), ]
            vertical_alignment = ft.MainAxisAlignment.CENTER
            horizontal_alignment = ft.CrossAxisAlignment.CENTER

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
            file = file_picker.current.result.files[0].path
            self.change_view("attente")
            self.analyze_genome(e, file)
            if self.page.views[-1].route != "erreur":
                self.change_view("analyse")

    # PARTIE BIOLOGIE

    def analyze_genome(self, e, file, len_window=10_000, overlap=9_000):
        """Fonction qui analyse le génome pour déterminer l'origine de réplication."""
        if e.files is not None:
            with open(file, 'r') as f:
                lines = f.read().strip()
            genome = "".join(lines.splitlines()[1:]).upper()
            non_adn = re.compile(r'[^ATCGU]')
            cherche_non_nucl = non_adn.search(genome)
            print(cherche_non_nucl)
            if cherche_non_nucl:
                self.change_view("erreur", "Le fichier FASTA contient des caractères non nucléotidiques.")
                return
            elif "U" in genome:
                self.change_view("erreur", "Le fichier FASTA est une séquence d'ARN. Une séquence d'ADN est requise.")
                return
            i = 0
            ratio = []
            self.progress_ring.current.value = 0
            self.page.update()
            while True:
                end_window = min(i + len_window, len(genome))
                window = genome[i:end_window]
                nb_g = window.count('G')
                nb_c = window.count('C')
                try:
                    ratio.append((nb_g - nb_c) / (nb_g + nb_c))
                except ZeroDivisionError:
                    self.change_view("erreur", "Division par zéro. Vérifiez que le fichier FASTA contient des G et C. "
                                               "Si c'est le cas, veuillez modifier la taille de la fenêtre ou du "
                                               "chevauchement.")
                    return
                if min(i + len_window, len(genome)) == len(genome):
                    break
                i += overlap
                self.progress_ring.current.value = (i / len(genome)) / 2
                self.page.update()

            self.progress_ring.current.value = None
            self.page.update()
            fig1, ax1 = plt.subplots(figsize=(15, 6))
            ax1.plot(ratio, linewidth=0.5)
            try:
                invert_point = self.find_inversion_point(ratio)
                self.window_ori = invert_point
                self.ori_start = overlap * invert_point
                self.ori_end = overlap * invert_point + len_window
                ax1.axhline(y=0, color='r', label='Fenêtre contenant le point d\'inversion')
                ax1.scatter(invert_point, 0, color='red', zorder=5)
                ax1.axvline(invert_point, linestyle='--', color='r', ymax=0.5)
                ax1.annotate(f'Fenêtre du point d\'inversion: {invert_point}', xy=(invert_point, 0),
                             xytext=(invert_point, -0.25),
                             color='red', ha='center', va='top')
            except Exception:
                self.change_view("erreur", "Point d'inversion non trouvé.")
                return

            val_max_y = max(abs(min(ratio)), abs(max(ratio)))
            ax1.set_ylim(-val_max_y, val_max_y)
            ax1.set_title('Ratio (G-C) / (G+C) en fonction de la fenêtre')
            ax1.set_xlabel('Window')
            ax1.set_ylabel('Ratio (G-C) / (G+C)')
            self.chart1.figure = fig1

            seqlength = len(genome)
            initw = 0
            x_values = [0]  # La position initiale
            y_values = [0]  # La position initiale

            self.progress_ring.current.value = 0.5
            self.page.update()
            while initw <= seqlength:
                nba = nbc = nbg = nbt = 0
                nb = 0
                for i in range(initw, min(initw + len_window, seqlength)):
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

                initw += len_window
                self.progress_ring.current.value = 0.5 + (initw / seqlength) / 2
                self.page.update()

            self.progress_ring.current.value = None
            self.page.update()
            fig2, ax2 = plt.subplots(figsize=(15, 6))
            try:
                cusp = self.find_cusp(x_values, y_values)
                ax2.annotate('Point de rebroussement', xy=(cusp[0], cusp[1]), xytext=(cusp[0], cusp[1]), color='red',
                             ha='center', va='top')
                ax2.scatter(cusp[0], cusp[1], color='red', zorder=5)
            except Exception:
                self.change_view("erreur", "Point de rebroussement non trouvé.")
                return
            ax2.plot(x_values, y_values, linestyle='-')
            ax2.set_xlabel('Horizontal Direction')
            ax2.set_ylabel('Vertical Direction')
            ax2.set_title('DNA Sequence Graph')
            ax2.grid()
            self.chart2.figure = fig2

    @staticmethod
    def find_inversion_point(ratios):
        """Fonction qui trouve le point d'inversion dans une liste de ratios (G-C) / (G+C)."""
        if ratios[0] < 0:  # si le premier ratio est négatif
            sens = 1  # on veut que le ratio soit positif
        else:  # sinon
            sens = -1  # on veut que le ratio soit négatif
        for i in range(1, len(ratios)):
            nb_ratio_inversions = 0  # nombre de ratios qui respectent la condition d'être de signe opposé au ratio
            # initial
            if sens == 1 and ratios[i] > 0:  # si on veut que le ratio soit positif et que le ratio est positif
                for j in range(i + 1, i + 11):  # on regarde les 10 ratios suivants
                    if ratios[j] > 0:  # si le ratio est positif
                        nb_ratio_inversions += 1  # on incrémente le nombre de ratios positifs
                if nb_ratio_inversions >= 8:  # si on a trouvé au moins 8 ratios positifs
                    invert_point = i  # on a trouvé le point d'inversion
                    return invert_point
            elif sens == -1 and ratios[i] < 0:  # si on veut que le ratio soit négatif et que le ratio est négatif
                for j in range(i + 1, i + 11):  # on regarde les 10 ratios suivants
                    if ratios[j] < 0:  # si le ratio est négatif
                        nb_ratio_inversions += 1  # on incrémente le nombre de ratios négatifs
                if nb_ratio_inversions >= 8:  # si on a trouvé au moins 8 ratios négatifs
                    invert_point = i  # on a trouvé le point d'inversion
                    return invert_point
        raise Exception("Point d'inversion non trouvé")  # si on n'a pas trouvé de point d'inversion

    @staticmethod
    def find_cusp(x_values, y_values):
        for i in range(1, len(x_values)):
            count = 0
            for j in range(i + 1, i + 11):
                if x_values[i] > x_values[j] and y_values[i] >= y_values[j]:
                    count += 1
            if count == 10:
                cusp = [x_values[i], y_values[i]]
                return cusp
        raise Exception("Cusp not found")


ft.app(Interface)
