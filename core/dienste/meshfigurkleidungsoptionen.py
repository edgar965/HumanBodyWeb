# -*- coding: utf-8 -*-
"""Meshfigurkleidungsoptionen — Option `kleidungsluft_mm` von „Mesh to 3D": die Haut darf nicht durch die Kleidung scheinen (07.10.2026).

Edgar am Ten24-Lauf („es sind noch Hautstellen sichtbar, kommen die vom Ten Modell oder von unserem Fit?"): Die Kleiderfläche des Scans ist an diesen Stellen
geschlossen — die Figur lag dort selbst außerhalb davon (gemessen: 359 Figurpunkte, davon 80 über 3 mm, 15 über 8 mm; Rücken, Hüfte, Ellbogen, Füße in den Schuhen). Der
Rest-Schritt (`Meshfigurregistrierung.ruhe_rest`) schob solche Punkte nur bis auf die Stoffoberfläche (r = 0), nicht darunter.

    kleidungsluft_mm   so tief mindestens unter der Stoffoberfläche — im Rest-Schritt; 0 = wie bisher (Vorgabe)

Die Zahl ist eine Untergrenze, kein Ziel: Punkte, die schon tiefer liegen, bleiben (die Stoffdicke und der Zug stehen in `kleidungsabstand_mm` und `kleidungszug`).
"""

__all__ = ['Meshfigurkleidungsoptionen']


class Meshfigurkleidungsoptionen:
    KATALOG = [
        {
            'schluessel': 'kleidungsluft_mm',
            'titel': 'Mindestluft unter dem Stoff (mm)',
            'art': 'zahl',
            'vorgabe': 0,
            'min': 0,
            'max': 20,
            'fein': True,
            'hinweis': 'Der Rest-Schritt schiebt Figurpunkte, die durch Stoff oder Haar ragen, mindestens so weit unter die Oberfläche. 0 = nur bis auf die '
            'Oberfläche (bisher): Die Haut kann dann an Stellen, wo der Stoff sie knapp berührt, durchscheinen (Ten24-Scan, 07.10.2026). Bei einem '
            'eng anliegenden Stoff macht ein hoher Wert die Figur dort schmaler als den Körper darunter.',
        },
    ]
