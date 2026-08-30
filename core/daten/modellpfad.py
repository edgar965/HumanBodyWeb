# -*- coding: utf-8 -*-
"""Modellpfad — ein Dateiname aus der Adresse, gegen die Wurzel geprueft.

Die Endpunkte fuer Modelle, Szenen und Frisuren bekommen den Dateinamen aus
der URL (`/api/character/model/<str:name>/`). Sechsmal stand dafuer im Projekt
derselbe Block:

    if '/' in name or '\\\\' in name or '..' in name:
        return JsonResponse({'error': 'Invalid name'}, status=400)
    pfad = os.path.normpath(os.path.join(wurzel, f'{name}.json'))
    if not pfad.startswith(os.path.normpath(wurzel)):
        return JsonResponse({'error': 'Invalid path'}, status=400)

Sechs Kopien einer Sicherheitspruefung sind sechs Gelegenheiten, eine davon
beim naechsten Umbau zu vergessen — und das faellt nicht auf, weil der
Endpunkt danach freundlich antwortet.

`SafePath` (core/safe_paths.py) beantwortet dieselbe Frage fuer BELIEBIGE
Pfade aus einem Anfragerumpf und kennt dabei Windows-Geraetenamen, UNC-Pfade
und NTFS-Datenstroeme. Hier geht es um den engeren Fall: EIN Name, EINE
Wurzel, EINE Endung.
"""

import os

from .pfadvergleich import Pfadvergleich


class Modellpfad:
    """`<wurzel>/<name><endung>` — oder nichts."""

    #: Zeichen, die in einem Namen aus der Adresse nichts zu suchen haben.
    VERBOTEN = ('/', '\\', '..')

    @classmethod
    def geprueft(cls, wurzel, name, endung):
        """Der volle Pfad, oder None wenn der Name die Wurzel verlassen will.

        Zwei Pruefungen, weil jede allein zu wenig ist: die Zeichenliste
        faengt den offensichtlichen Fall, `Pfadvergleich` den Rest (etwa einen
        absoluten Pfad, der `join` die Wurzel wegnimmt). Bis zum 27.08.2026
        stand hier ein `startswith` — genau der Zeichenvergleich, den das
        Werkzeug `pfadpraefix` seitdem meldet.
        """
        if not name or any(z in name for z in cls.VERBOTEN):
            return None
        pfad = os.path.normpath(os.path.join(str(wurzel),
                                             '%s%s' % (name, endung)))
        if not Pfadvergleich.liegt_unter(pfad, wurzel):
            return None
        return pfad
