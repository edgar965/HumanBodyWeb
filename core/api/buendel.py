# -*- coding: utf-8 -*-
"""Das gebündelte Seitenskript ausliefern (Szene, BVH Studio).

Eine eigene Route, weil das Bündel bewusst NICHT unter `static/` liegt:
Die Fassung ist die jüngste Änderungszeit im Statik-Baum, ein Bündel dort
würde sie also bei jedem Bau weiterdrehen und den nächsten Bau auslösen
(gemessen: zwei Bündel für eine Änderung). Die Begründung steht in
`core/dienste/modulbuendel.py`.

Die Fassung steht trotzdem im Pfad — genau wie bei der übrigen Statik. Damit
gilt dasselbe: Ändert sich eine Datei, ändert sich die Adresse, und der
Browser kann nichts Altes liefern. Ändert sich nichts, liegt die Datei ein
Jahr im Zwischenspeicher, ohne eine einzige Rückfrage.
"""

import os

from django.http import FileResponse, Http404

from ..dienste.modulbuendel import Modulbuendel

__all__ = ['buendel_datei']


def buendel_datei(request, fassung, seite):
    """`/buendel/<fassung>/<seite>.js` — `seite` eines von `Modulbuendel.EINSTIEGE`."""
    # Nur Ziffern: Die Fassung kommt aus dem Pfad, und `os.path.join` mit
    # „..“ darin läge sonst außerhalb der Ablage.
    if not fassung.isdigit() or seite not in Modulbuendel.EINSTIEGE:
        raise Http404('unbekannte Fassung oder Seite')
    pfad = Modulbuendel.pfad(seite, fassung)
    if not os.path.isfile(pfad):
        # Nicht heimlich neu bauen: Wer hier landet, hat eine Adresse aus
        # einer alten Seite. Ein 404 lässt ihn neu laden und die aktuelle
        # Adresse holen; ein Neubau lieferte ihm dagegen Code, der nicht zu
        # seiner Seite gehört.
        raise Http404('Bündel nicht vorhanden')
    antwort = FileResponse(open(pfad, 'rb'), content_type='application/javascript')
    antwort['Cache-Control'] = 'public, max-age=31536000, immutable'
    return antwort
