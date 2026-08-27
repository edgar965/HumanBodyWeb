# -*- coding: utf-8 -*-
"""Testnetz — die Netzantwort der Testfassung fuer EINE Anfrage.

Aus `core/test_character_api.py` herausgelöst (17.08.2026). `test_character_mesh`
hatte 65 Zeilen mit zwei vollständigen Antwortzweigen (mit und ohne
Unterteilung); die stehen jetzt als zwei Methoden von `Testnetz` nebeneinander.

Die Endpunkte, die diese Klasse benutzen, stehen seit dem 27.08.2026 in
`testfigur/netzendpunkte.py` (Befunde `freie-funktionen`, `klassen-je-datei`).
"""

import logging

import numpy as np

from ...daten.netzantwort import Netzantwort
from .testkern import Testkern

logger = logging.getLogger(__name__)


class Testnetz:
    """Die Netzantwort der Testfassung für eine Anfrage."""

    #: Vorsilbe der Regler in der Abfragezeichenkette.
    REGLER = 'morph_'

    def __init__(self, anfrage):
        self.anfrage = anfrage

    def antwort(self):
        """Fertiges Wörterbuch für `JsonResponse` — oder None bei Rechenfehler."""
        zustand = Testkern.zustand(
            self.anfrage.GET.get('body_type', Testkern.koerpertyp()))
        self._regler_setzen(zustand)
        punkte = zustand.compute()
        if punkte is None:
            return None
        unterteiler = Testkern.unterteiler()
        if unterteiler is not None:
            return self._unterteilt(unterteiler, punkte)
        return self._grundnetz(punkte)

    def _regler_setzen(self, zustand):
        for schluessel, wert in self.anfrage.GET.items():
            if not schluessel.startswith(self.REGLER):
                continue
            name = schluessel[len(self.REGLER):]
            try:
                zustand.set_morph(name, float(wert))
            except ValueError:
                # Der Regler kommt aus der Abfragezeichenkette. Ein Wert, der
                # keine Zahl ist, heisst: Das Frontend schickt etwas anderes als
                # gedacht — der Charakter sieht dann nur „irgendwie falsch" aus.
                logger.warning('[test-charakter] Morph %r hat den unlesbaren '
                               'Wert %r', name, wert)

    def _unterteilt(self, unterteiler, rohpunkte):
        """Die gerechneten Punkte durch die Unterteilung — nicht neu rechnen.

        `rohpunkte` kommt aus `antwort()`: Dort stehen die Reglerwerte der
        Anfrage schon drin. Ein zweiter `compute()` hier hätte sie verloren.
        """
        punkte = unterteiler.subdivide(rohpunkte)
        normalen = unterteiler.compute_quad_normals(punkte)
        netz = Testkern.netzdaten()
        antwort = Netzantwort.aus(punkte, unterteiler.triangles, normalen,
                                  unterteiler.uvs)
        antwort['groups'] = unterteiler.groups
        antwort['material_names'] = netz.material_names or []
        return antwort

    def _grundnetz(self, punkte):
        """Ohne Unterteiler: Vierecke selbst in Dreiecke zerlegen."""
        netz = Testkern.netzdaten()
        dreiecke = self._dreiecke(netz.faces) if netz.faces is not None else None
        return Netzantwort.aus(punkte, dreiecke, None, netz.uvs)

    @staticmethod
    def _dreiecke(flaechen):
        """Vierecke -> zwei Dreiecke; Dreiecke nur umgedreht (Umlaufrichtung)."""
        if flaechen.ndim == 2 and flaechen.shape[1] == 4:
            return np.concatenate([flaechen[:, [0, 2, 1]],
                                   flaechen[:, [0, 3, 2]]], axis=0)
        if flaechen.shape[1] == 3:
            return flaechen[:, [0, 2, 1]]
        return flaechen
