# -*- coding: utf-8 -*-
"""Hautknoten — Grundklasse eines Knotens im lokalen Backer.

Ein Knoten bekommt seinen Eintrag aus dem Export (`blendmaterialgraph.py`: `typ`, `eig`, `ein`, `ein_art`, `aus_art`) und rechnet für einen Stapel Texel (`Hautkontext`):
`auswerten(graph, ctx, modus)` → `{Ausgang-Identifier: Hautwert}`. `modus` = `(0, 0.0)` (Mitte) oder `(1|2, Filterbreite)` — der Bump-Knoten wertet die Höhe an den um dx/dy
versetzten Koordinaten aus; nur Knoten, die Koordinaten oder Attribute lesen (`KOORDINATE = True`), antworten darauf verschieden.
`pruefen(genutzt)` nennt, was dieser Knoten in diesem Material nicht kann (Texte, kein Raten); `genutzt`: die Ausgänge, die jemand liest.
"""

__all__ = ['Hautknoten']


class Hautknoten:
    #: Blenders `node.type`, den die Klasse rechnet.
    TYPEN = ()
    #: Liest der Knoten Koordinaten/Attribute (ändert sich bei Bump-Versatz)?
    KOORDINATE = False

    def __init__(self, schluessel, eintrag):
        self.schluessel = schluessel
        self.eintrag = eintrag
        self.typ = eintrag['typ']
        self.eig = eintrag['eig']

    def pruefen(self, genutzt):
        """Liste von Gründen, warum der lokale Backer diesen Knoten nicht so rechnen kann, wie Cycles es täte (leer = in Ordnung)."""
        return []

    def auswerten(self, graph, ctx, modus):
        raise NotImplementedError(self.typ)

    # ---- Hilfen

    def hat(self, name):
        """Ist die Buchse im Export (verfügbar)?"""
        return name in self.eintrag['ein']

    def ein(self, graph, ctx, modus, name, art):
        """Der Wert der Eingangsbuchse `name` als Art `art`."""
        return graph.eingang(self, name, ctx, modus, art)

    def ein_oder(self, graph, ctx, modus, name, art, standard):
        """Wie `ein`; fehlt die Buchse im Export (sie ist bei dieser Einstellung nicht verfügbar und wird nicht gelesen), der feste Wert `standard`."""
        if self.hat(name):
            return graph.eingang(self, name, ctx, modus, art)
        return ctx.konstante(art, standard)
