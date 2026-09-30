# -*- coding: utf-8 -*-
"""Kostuemutensilien — die kleinen Teile, die die Prüf-KI in jedem Bericht vermisst: Amulett, Fläschchen, Gürtelschnalle.

Die Prüf-KI (qwen3.8:27b) nannte am 30.09.2026 in jeder Runde „Fläschchen am Gürtel", „Amulett am Hals", „Nieten am
Ledergürtel" als fehlend (Bereich „Taschen und Utensilien": 1 von 10). Alle drei sind kleine Teile aus wenigen Ringen und
sitzen VOR dem Rumpf in der Öffnung des Mantels (dort sieht man sie): Ein Ring ohne Wertesatz-Maß, nur mit dem Schalter
`utensilien.an` — Form und Ort folgen den Körpermaßen (`Koerpermasse.ring`), nicht dem Optimierer.
"""

from effekte.blender.kostuem.rohr import Rohr

__all__ = ['Kostuemutensilien']


class Kostuemutensilien:
    #: Halbe Breite des Fläschchens (m) und seine Länge.
    FLASCHE = 0.022
    LAENGE = 0.10

    def __init__(self, masse, p, vorn_grad):
        self.m = masse
        self.p = p
        self.vorn = 1 if vorn_grad == 90 else -1

    def farbe(self, name):
        return tuple(float(self.p['farbe.%s.%s' % (name, k)]) for k in 'rgb')

    def _vorn(self, name, aufschlag=0.0):
        """(mitte_x, y der Vorderseite des Unterkleids auf Höhe `name`) — vor dem Unterkleid, unter dem Mantel."""
        mx, my, _, ht = self.m.ring(self.m.z(name))
        return mx, my + self.vorn * (ht * self.p['unterkleid.luft'] + 0.008 + aufschlag)

    def amulett(self):
        """Eine Scheibe an der Brust (die Kette verschwindet unter dem Kragen): Zylinder mit der Achse nach vorn."""
        x, y = self._vorn('brust', 0.006)
        z = (self.m.z('brust') + self.m.z('schulter')) / 2 - 0.02
        rohr = Rohr('Amulett', self.farbe('borte'))
        for dy in (0.008, 0.0):  # der vordere Ring zuerst: `deckel_oben` schließt den ersten Ring
            rohr.ring_auf_achse((x, y + self.vorn * dy, z), (0.0, 1.0, 0.0), 0.028, 0.028)
        return rohr.bauen(dicke=0.0, glaetten=0, deckel_oben=True)

    def flaeschchen(self):
        """Ein Glasfläschchen am Gürtel, rechts der Mitte (Vorlage: links im Bild von vorn), Hals und Bauch."""
        x, y = self._vorn('taille', 0.03)
        x += self.vorn * 0.10
        z0 = self.m.z('taille') - 0.03
        r = self.FLASCHE
        rohr = Rohr('Flaeschchen', self.farbe('kristall'))
        # der Korken zuerst: `deckel_oben` schließt den ersten Ring
        for dz, f in ((0.0, 0.32), (-0.025, 0.4), (-0.04, 1.0), (-0.09, 1.0), (-self.LAENGE, 0.55)):
            rohr.ring_waagerecht(x, y, r * f, r * f, z0 + dz)
        return rohr.bauen(dicke=0.002, glaetten=1, deckel_oben=True)

    def schnalle(self):
        """Die Gürtelschnalle vorn: ein flacher Zylinder (Achse nach vorn), gold."""
        x, y = self._vorn('taille', 0.014)
        rohr = Rohr('Schnalle', self.farbe('borte'))
        for dy in (0.006, 0.0):
            rohr.ring_auf_achse((x, y + self.vorn * dy, self.m.z('taille')), (0.0, 1.0, 0.0), 0.02, 0.016)
        return rohr.bauen(dicke=0.0, glaetten=0, deckel_oben=True)

    def bauen(self):
        if self.p['utensilien.an'] < 0.5:
            return []
        return [self.amulett(), self.flaeschchen(), self.schnalle()]
