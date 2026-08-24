# -*- coding: utf-8 -*-
"""Bereichsstoff — ein Kleidungsnetz aus einem Höhenbereich des Körpers.

Herausgelöst aus `api/schnittmuster.pattern_region_generate` (66 Zeilen). Der
Nutzer wählt am Regler eine Höhe von … bis (in Metern) und bekommt daraus ein
Stoffstück — die Grundlage für einen eigenen Schnitt.

WARUM AUF DEM UNTERTEILTEN KÖRPER GEBAUT WIRD
=============================================
Der angezeigte Körper ist Catmull-Clark-unterteilt (rund 70.000 Punkte statt
18.000). Wird der Stoff auf dem GROBEN Netz gebaut, hat er dessen Auflösung — und
liegt an den Rundungen sichtbar in der Haut, weil das feine Netz dort weiter
außen liegt. Deshalb: unterteilte Punkte und deren Vierecke.

DER ZWEITE ABSTAND IST ABSICHT
==============================
Nach dem Bauen wird noch einmal herausgeschoben, und zwar mit `0,006 + Weite ×
0,010` statt dem normalen Abstand: Die Laplace-Glättung zieht Punkte an konvexen
Stellen (Brust, Knie, Schulter) nach innen. Der zweite, größere Schub fängt genau
die ein.
"""

import numpy as np
from humanbody_core.cloth import generate_builder_custom, _push_outside_body

from ..dienste.charakterdaten import Charakterdaten


class Bereichsstoff:
    """Baut ein Stoffstück über einem Höhenbereich der Figur."""

    GRUNDABSTAND = 0.006
    WEITENANTEIL = 0.010

    def __init__(self, parameter):
        self.von = float(parameter.get('z_min', 0.0))
        self.bis = float(parameter.get('z_max', 1.0))
        self.mit_armen = parameter.get('include_arms', '0') == '1'
        self.wachsen = int(parameter.get('grow', 2))
        self.weite = float(parameter.get('looseness', 0.3))
        self.kategorie = parameter.get('category', None)

    # ------------------------------------------------------------------ Bauen

    def bauen(self, koerper):
        """`(ergebnis, fehlertext)` — genau eines von beiden ist gesetzt."""
        punkte = np.asarray(koerper.vertices, dtype=np.float64)
        flaechen = self._flaechen(koerper)
        if flaechen is None:
            return None, 'No face topology available'
        grundlage, grundflaechen = self._grundlage(koerper.geschlecht, punkte,
                                                  flaechen)
        ergebnis = generate_builder_custom(
            grundlage, grundflaechen, self.von, self.bis,
            include_arms=self.mit_armen, looseness=self.weite,
            grow=self.wachsen, category=self.kategorie)
        if ergebnis is None:
            return None, 'No body faces in region'
        ergebnis['vertices'] = self._herausschieben(ergebnis, grundlage)
        return ergebnis, None

    @staticmethod
    def _flaechen(koerper):
        """Die Vierecke der Figur — der Baumeister braucht die Topologie."""
        if koerper.faces is not None:
            return koerper.faces
        netz = Charakterdaten.netzdaten(koerper.geschlecht)
        if netz.faces is not None and netz.faces.ndim == 2:
            return netz.faces
        return None

    @staticmethod
    def _grundlage(geschlecht, punkte, flaechen):
        """Unterteilte Punkte und Vierecke — oder das grobe Netz."""
        unterteiler = Charakterdaten.unterteiler(geschlecht)
        if unterteiler is None:
            return punkte, flaechen
        return (unterteiler.subdivide(punkte).astype(np.float64),
                unterteiler._sub_quads)

    def _herausschieben(self, ergebnis, grundlage):
        """Zweiter Schub gegen die konvexen Stellen (siehe Modul-Docstring)."""
        abstand = self.GRUNDABSTAND + self.weite * self.WEITENANTEIL
        geschoben = _push_outside_body(ergebnis['vertices'].astype(np.float64),
                                       grundlage, min_dist=abstand)
        return geschoben.astype(np.float32)
