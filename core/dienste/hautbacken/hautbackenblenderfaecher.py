# -*- coding: utf-8 -*-
"""Hautbackenblenderfaecher — die Fächer um jeden Punkt: Blenders `calc_connecting_edge_info` + `traverse_fan_local_corners`, für alle Punkte zugleich.

Blender v5.2.2, `mesh_normals.cc` (gelesen 10.10.2026). Ein „Fächer" ist die Gruppe von Polygonecken um einen Punkt, die über glatte Kanten zusammenhängen. Je Punkt und
Nachbarpunkt (= Kante) sammelt Blender, welche Ecken sie benutzen (`add_corner_to_edge`); die Kante verbindet zwei Ecken (`EdgeTwoCorners`) genau dann, wenn
  * genau zwei Ecken sie benutzen, die eine in Laufrichtung zum Punkt hin (ihre „prev"-Kante), die andere vom Punkt weg (ihre „next"-Kante) — gleicher Umlaufsinn
    oder eine dritte Ecke machen sie scharf,
  * keine der benutzenden Ecken zu einem scharfen Polygon (`sharp_face`) gehört (das macht beide Kanten der Ecke scharf),
  * die Kante der ZUERST angetroffenen Ecke nicht `sharp_edge` ist (angetroffen wird in Eintragsreihenfolge, bei einer Ecke erst „prev", dann „next").
Daraus folgt je Ecke höchstens ein Nachfolger (`succ`: über die next-Kante) und ein Vorgänger (`pred`: über die prev-Kante) — Wege und Ringe.
Die Reihenfolge im Fächer (wirkt auf die Gleitkomma-Summen): Blender reiht den Fächer vom Ende der `succ`-Kette an gegen die `succ`-Richtung, also entlang `pred`:
  offener Fächer: beginnt bei der Ecke ohne Nachfolger;  Ring: beginnt bei der Ecke mit der kleinsten Eckennummer (`std::rotate` auf `min_element`).

Felder: `fan` (E,) Fächernummer je Eintrag, `pos` (E,) Platz im Fächer, `reihe` (E,) Einträge nach (Fächer, Platz), `anfang` (F+1) Offsets in `reihe`, `groesse` (F,).
"""

import numpy as np

__all__ = ['Hautbackenblenderfaecher']


class Hautbackenblenderfaecher:
    def __init__(self, e, ecke_kante, scharf_kante=None, scharf_flaeche=None):
        succ, pred = self._verbindungen(e, ecke_kante, scharf_kante, scharf_flaeche)
        self.fan, self.pos = self._nummerieren(e, succ, pred)
        self.reihe = np.lexsort((self.pos, self.fan))
        self.groesse = np.bincount(self.fan)
        self.anfang = np.concatenate([[0], np.cumsum(self.groesse)])

    @staticmethod
    def _verbindungen(e, ecke_kante, scharf_kante, scharf_flaeche):
        """`(succ, pred)`: je Eintrag der Eintrag dahinter bzw. davor im Fächer oder -1."""
        n = len(e.punkt)
        j = np.arange(2 * n)
        eintrag, art = j // 2, j % 2                      # art 0: prev-Kante (zum Punkt hin), art 1: next-Kante (vom Punkt weg)
        andere = np.where(art == 0, e.punkt_vor[eintrag], e.punkt_nach[eintrag])
        schluessel = e.punkt[eintrag] * (int(e.punkt.max()) + 1 if n else 1) + andere
        ordnung = np.argsort(schluessel, kind='stable')   # stabil: Antreffreihenfolge bleibt
        s = schluessel[ordnung]
        neu = np.ones(len(s), dtype=bool)
        neu[1:] = s[1:] != s[:-1]
        anfaenge = np.flatnonzero(neu)
        zwei = anfaenge[np.diff(np.append(anfaenge, len(s))) == 2]   # nur Kanten mit genau zwei benutzenden Ecken können verbinden
        a, b = ordnung[zwei], ordnung[zwei + 1]            # a zuerst angetroffen, b danach
        gut = art[a] != art[b]
        if scharf_flaeche is not None:
            gut &= ~scharf_flaeche[e.flaeche[eintrag[a]]] & ~scharf_flaeche[e.flaeche[eintrag[b]]]
        if scharf_kante is not None:
            kante_a = np.where(art[a] == 0, ecke_kante[e.ecke_vor[eintrag[a]]], ecke_kante[e.ecke[eintrag[a]]])
            gut &= ~scharf_kante[kante_a]
        a, b = a[gut], b[gut]
        weg = np.where(art[a] == 1, eintrag[a], eintrag[b])   # die Ecke, für die es die next-Kante ist
        hin = np.where(art[a] == 1, eintrag[b], eintrag[a])   # die Ecke, für die es die prev-Kante ist
        succ = np.full(n, -1, dtype=np.int64)
        pred = np.full(n, -1, dtype=np.int64)
        succ[weg] = hin
        pred[hin] = weg
        return succ, pred

    @staticmethod
    def _nummerieren(e, succ, pred):
        n = len(succ)
        fan = np.full(n, -1, dtype=np.int64)
        pos = np.zeros(n, dtype=np.int64)
        kopf = np.flatnonzero(succ < 0)                    # offene Fächer beginnen bei der Ecke ohne Nachfolger
        fan[kopf] = np.arange(len(kopf))
        Hautbackenblenderfaecher._laufen(kopf, fan, pos, pred)
        rest = np.flatnonzero(fan < 0)                     # nur noch Ringe: Anfang = kleinste Eckennummer
        if len(rest):
            schluessel = e.ecke * n + np.arange(n)
            kleinste = np.where(fan < 0, schluessel, np.iinfo(np.int64).max)
            p = np.where(fan < 0, pred, np.arange(n))
            for _ in range(int(np.ceil(np.log2(max(int(e.anzahl.max()), 2)))) + 1):    # ein Ring hat höchstens so viele Ecken wie der Punkt Polygone
                kleinste = np.minimum(kleinste, kleinste[p])
                p = p[p]
            kopf2 = rest[kleinste[rest] == schluessel[rest]]
            fan[kopf2] = len(kopf) + np.arange(len(kopf2))
            Hautbackenblenderfaecher._laufen(kopf2, fan, pos, pred)
        return fan, pos

    @staticmethod
    def _laufen(kopf, fan, pos, pred):
        """Von den Köpfen aus entlang `pred`: Fächernummer und Platz weitergeben, bis es nicht weitergeht oder der Ring sich schließt."""
        aktuell, platz = kopf, 0
        while len(aktuell):
            nach = pred[aktuell]
            weiter = (nach >= 0)
            weiter[weiter] = fan[nach[weiter]] < 0
            aktuell, nach = aktuell[weiter], nach[weiter]
            platz += 1
            fan[nach] = fan[aktuell]
            pos[nach] = platz
            aktuell = nach
