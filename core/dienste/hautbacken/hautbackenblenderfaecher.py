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

import torch
from KoerperKI_alle.torchfeld import Torchfeld

__all__ = ['Hautbackenblenderfaecher']


class Hautbackenblenderfaecher:
    def __init__(self, e, ecke_kante, scharf_kante=None, scharf_flaeche=None):
        succ, pred = self._verbindungen(e, ecke_kante, scharf_kante, scharf_flaeche)
        self.fan, self.pos = self._nummerieren(e, succ, pred)
        self.reihe = Torchfeld.lexsort((self.pos, self.fan))
        self.groesse = Torchfeld.bincount(self.fan)
        self.anfang = Torchfeld.cat([[0], Torchfeld.cumsum(self.groesse)])

    @staticmethod
    def _verbindungen(e, ecke_kante, scharf_kante, scharf_flaeche):
        """`(succ, pred)`: je Eintrag der Eintrag dahinter bzw. davor im Fächer oder -1."""
        n = len(e.punkt)
        j = Torchfeld.arange(2 * n)
        eintrag, art = j // 2, j % 2                      # art 0: prev-Kante (zum Punkt hin), art 1: next-Kante (vom Punkt weg)
        andere = torch.where(art == 0, e.punkt_vor[eintrag], e.punkt_nach[eintrag])
        schluessel = e.punkt[eintrag] * (int(e.punkt.max()) + 1 if n else 1) + andere
        ordnung = torch.argsort(schluessel, stable=True)   # stabil: Antreffreihenfolge bleibt
        s = schluessel[ordnung]
        neu = torch.ones(len(s), dtype=torch.bool, device='cuda')
        neu[1:] = s[1:] != s[:-1]
        anfaenge = torch.flatten(neu).nonzero()[:, 0]
        zwei = anfaenge[Torchfeld.diff(Torchfeld.append(anfaenge, len(s))) == 2]   # nur Kanten mit genau zwei benutzenden Ecken können verbinden
        a, b = ordnung[zwei], ordnung[zwei + 1]            # a zuerst angetroffen, b danach
        gut = art[a] != art[b]
        if scharf_flaeche is not None:
            gut &= ~scharf_flaeche[e.flaeche[eintrag[a]]] & ~scharf_flaeche[e.flaeche[eintrag[b]]]
        if scharf_kante is not None:
            kante_a = torch.where(art[a] == 0, ecke_kante[e.ecke_vor[eintrag[a]]], ecke_kante[e.ecke[eintrag[a]]])
            gut &= ~scharf_kante[kante_a]
        a, b = a[gut], b[gut]
        weg = torch.where(art[a] == 1, eintrag[a], eintrag[b])   # die Ecke, für die es die next-Kante ist
        hin = torch.where(art[a] == 1, eintrag[b], eintrag[a])   # die Ecke, für die es die prev-Kante ist
        succ = Torchfeld.full(n, -1, dtype=torch.int64)
        pred = Torchfeld.full(n, -1, dtype=torch.int64)
        succ[weg] = hin
        pred[hin] = weg
        return succ, pred

    @staticmethod
    def _nummerieren(e, succ, pred):
        n = len(succ)
        fan = Torchfeld.full(n, -1, dtype=torch.int64)
        pos = torch.zeros(n, dtype=torch.int64, device='cuda')
        kopf = torch.flatten(succ < 0).nonzero()[:, 0]                    # offene Fächer beginnen bei der Ecke ohne Nachfolger
        fan[kopf] = Torchfeld.arange(len(kopf))
        Hautbackenblenderfaecher._laufen(kopf, fan, pos, pred)
        rest = torch.flatten(fan < 0).nonzero()[:, 0]                     # nur noch Ringe: Anfang = kleinste Eckennummer
        if len(rest):
            schluessel = e.ecke * n + Torchfeld.arange(n)
            kleinste = torch.where(fan < 0, schluessel, torch.iinfo(torch.int64).max)
            p = torch.where(fan < 0, pred, Torchfeld.arange(n))
            for _ in range(int(Torchfeld.ceil(Torchfeld.log2(max(int(e.anzahl.max()), 2)))) + 1):    # ein Ring hat höchstens so viele Ecken wie der Punkt Polygone
                kleinste = Torchfeld.minimum(kleinste, kleinste[p])
                p = p[p]
            kopf2 = rest[kleinste[rest] == schluessel[rest]]
            fan[kopf2] = len(kopf) + Torchfeld.arange(len(kopf2))
            Hautbackenblenderfaecher._laufen(kopf2, fan, pos, pred)
        return fan, pos

    @staticmethod
    def _laufen(kopf, fan, pos, pred):
        """Von den Köpfen aus entlang `pred`: Fächernummer und Platz weitergeben, bis es nicht weitergeht oder der Ring sich schließt."""
        aktuell, platz = kopf, 0
        while len(aktuell):
            nach = pred[aktuell]
            weiter = (nach >= 0)
            maske = weiter.clone()                       # torch: Maske und Ziel dürfen sich den Speicher nicht teilen
            weiter[maske] = fan[nach[maske]] < 0
            aktuell, nach = aktuell[weiter], nach[weiter]
            platz += 1
            fan[nach] = fan[aktuell]
            pos[nach] = platz
            aktuell = nach
