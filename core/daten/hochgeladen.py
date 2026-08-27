# -*- coding: utf-8 -*-
"""Hochgeladen — eine Datei aus dem Formular auf die Platte schreiben.

Vier Zeilen, die in `api/studio.py` und `api/studio_video.py` je einmal
standen (Befund `doppelrumpf`, 27.08.2026):

    with open(ziel, 'wb') as datei:
        for stueck in hochgeladen.chunks():
            datei.write(stueck)

`chunks()` und nicht `.read()`: Eine Bildfolge aus dem Theatre-Export ist
mehrere hundert Megabyte gross. `read()` haelt sie vollstaendig im Speicher,
`chunks()` gibt sie stueckweise weiter — Django liest sie ohnehin so ein.
"""


class Hochgeladen:
    """Der Weg von `request.FILES[...]` auf die Platte."""

    @staticmethod
    def ablegen(ziel, datei):
        """Schreibt `datei` nach `ziel` und gibt den Zielpfad zurueck."""
        with open(ziel, 'wb') as offen:
            for stueck in datei.chunks():
                offen.write(stueck)
        return ziel
