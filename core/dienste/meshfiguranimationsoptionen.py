# -*- coding: utf-8 -*-
"""Meshfiguranimationsoptionen — die Option `animationspruefung` von „Mesh to 3D" und Mesh-3D (13.10.2026).

Edgar: „das Testscript für Animation brauche ich auch generisch, so dass ich das auswählen kann beim Bauen des Mesh to 3D, und das gleich korrigiert werden kann. Als extra Option im Job, default: An."
Was die Prüfung tut: `Meshfigurtanzpruefung` (Dehnung des Stoffs im Tanz messen, die Gewichte mit den wenigsten gerissenen Kanten nehmen).
"""

__all__ = ['Meshfiguranimationsoptionen']


class Meshfiguranimationsoptionen:
    KATALOG = [
        {
            'schluessel': 'animationspruefung',
            'titel': 'Animationsprüfung (Stoff im Tanz messen und korrigieren)',
            'art': 'wahl',
            'vorgabe': 'an',
            'werte': [
                ('an', 'An — Dehnung im Tanz messen, die besten Gewichte nehmen (Vorgabe)'),
                ('aus', 'Aus — die Gewichte der Käfig-Nachbarschaft, ungeprüft'),
            ],
            'hinweis': 'Im Schritt „vorschau“ wird eine Bewegung (A_Results/DanceKurz) auf die Figur gelegt und für jedes mitgehende Objekt (Kleidung, Bart, Tasche) die Dehnung jeder Kante gemessen, mit den alten Gewichten und mit weichen in drei Breiten. '
            'Die mit den wenigsten gerissenen Kanten (über 5× ihrer Länge) gewinnt; der Bericht steht unter „Animation“ im Ergebnis. Kostet rund 2–4 Minuten bei einem Netz wie dem Zauberer (1,4 Mio. Dreiecke). '
            'Gemessen am Zauberer: größte Dehnung 1.002× → 100×, p99,9 58× → 12×; an der Ballerina 182× → 28×.',
        },
    ]
