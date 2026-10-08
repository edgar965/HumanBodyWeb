# -*- coding: utf-8 -*-
"""Meshfigurtexturoptionen — die Optionen der Textur von „Mesh to 3D" (aus `Meshfiguroptionen` herausgelöst, 07.10.2026).

`meshfiguroptionen.py` stand bei 312 Zeilen (Grenze 300, `struktur.md`); die Einträge zur Textur wohnen jetzt hier und
stehen in `Meshfiguroptionen.KATALOG` an derselben Stelle wie vorher (nach „Eigenmorph symmetrisch", vor „Kleidung im Netz").

    textur       Farbe des Netzes auf die Genesis-Haut backen, nur den Hautton, oder keine
    kopfhaut     unter dem Haar: die Haarfarbe des Netzes aufmalen oder Haut lassen
    entlichten   das Licht der Netzfarbe herausrechnen (`Meshfigurentlichtung`, 0 = aus)
"""

__all__ = ['Meshfigurtexturoptionen']


class Meshfigurtexturoptionen:
    KATALOG = [
        {
            'schluessel': 'textur',
            'titel': 'Textur',
            'art': 'wahl',
            'vorgabe': 'mesh',
            'werte': [
                ('mesh', 'Farbe des Netzes auf die Genesis-Haut'),
                ('hautton', 'Nur den Hautton übernehmen'),
                ('aus', 'Daz-Haut unverändert'),
            ],
        },
        {
            'schluessel': 'kopfhaut',
            'titel': 'Kopfhaut',
            'art': 'wahl',
            'vorgabe': 'haar',
            'werte': [
                ('haar', 'Haarfarbe des Netzes aufmalen'),
                ('haut', 'Haut lassen (für eigenes Haar)'),
            ],
            'hinweis': 'Unter dem Haar: „Haarfarbe des Netzes“ malt die Farbe, die das Netz dort trägt, auf die Genesis-Kopfhaut (die graue „Kappe“, solange kein Haar darüber sitzt); „Haut lassen“ '
                       'nimmt dort keine Farbe aus dem Netz, die Daz-Haut bleibt — für Haar als eigenes Objekt (Frisur, Iterationen). Wirkt mit dem Schritt „Körper“ (Quelle „rechnen“).',
        },
        {
            'schluessel': 'entlichten',
            'titel': 'Licht aus der Netzfarbe (%)',
            'art': 'zahl',
            'vorgabe': 0,
            'min': 0,
            'max': 100,
            'fein': True,
            'hinweis': 'Nur bei „Farbe des Netzes auf die Genesis-Haut“: teilt das geschätzte Licht der Netzfarbe heraus — '
            'je Blickrichtung (vorn, hinten, links, rechts) ein Polynom ersten Grades der Helligkeit in Normale und Lage, '
            'wie „Licht herausrechnen“ in 2D3D Kleider. 0 = aus (Vorgabe), 85 = die dortige Stärke. Gemessen an drei Aufträgen '
            '(07.10.2026): nimmt den ständigen Links-rechts-Unterschied der Hautfarbe zurück, nicht aber den Unterschied je Stelle.',
        },
    ]
