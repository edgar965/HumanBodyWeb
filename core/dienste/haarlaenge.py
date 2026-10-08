# -*- coding: utf-8 -*-
"""Haarlaenge — wie lang das Herrenhaar ist: unten (Schläfen, hinten unten) und oben (Kopfdecke), dazwischen interpoliert (07.10.2026).

Edgar: „mach beim eigen Herrenhaar regler, wie lange das Haar unten ist (an den Schläfen) bzw. hinten unten, und wie lange es oben ist. Dazwischen wird es interpoliert. Die Länge oben ist auch die Länge des Haars
an der Kopfdecke". Zwei Zahlen in cm — `unten` und `oben`; die Länge einer Strähne ist die Länge entlang des Kopfes (Bogenlänge ab der Wurzel, `Herrenhaar._strahlen`), je Wurzel nach ihrem Höhenwinkel am Kopf
(Grad über der Waagerechten durch den Kopfmittelpunkt): bis `HOEHEN[0]` gilt `unten` (Ohr, Schläfe und Nacken liegen darunter bzw. knapp darüber), ab `HOEHEN[1]` gilt `oben` (Kopfdecke, auch die Stirn vorn
liegt dort), dazwischen läuft es glatt (Hermite) von der einen zur anderen Länge.

Die Dicke des Haars (Strähnenhöhe über der Haut, Dicke der Haarkappe darunter) folgt der Länge: kurzes Haar liegt dicht an der Haut, ab `DICKE_AB_M` Länge gilt die Dicke der Hülle des Fotohaars; sie sinkt
nie unter `DICKE_MIN` davon. Längeres Haar wird also nicht dicker, es legt sich weiter an den Kopf.

Die Vorgaben sind die Länge, die `Herrenhaar` vor diesem Regler im Mittel hatte (damals `2,4 × Dicke der Hülle`, 6…40 mm): gemessen am Auftrag `2026.10.07.17.45.25` (`ProjektTemp/_wegwerf/edgar/haarlaenge_probe.py`,
30.278 Wurzeln) 12,1 mm im Mittel unter 15° Höhenwinkel (8,6 mm im Nacken, 16,2 mm über dem Ohr) und 21,2 mm über 65° (die Hülle des Fotohaars liegt dort nur 8 mm über der Haut, die Untergrenze der Dicke). `HOEHEN`,
`DICKE_AB_M` und `DICKE_MIN` sind Annahmen („normaler Herrenschnitt"), nicht am Foto gemessen.

    laenge = Haarlaenge(unten_cm=1.0, oben_cm=5.0)
    laenge.laenge(el_grad)          # Länge in m je Höhenwinkel (Feld)
    laenge.dickefaktor(el_grad)     # Faktor auf die Dicke des Fotohaars je Höhenwinkel
"""

import numpy as np

__all__ = ['Haarlaenge']


class Haarlaenge:
    #: Länge unten (Schläfen, Nacken) und oben (Kopfdecke) in cm, wenn nichts gewählt ist.
    UNTEN_CM = 1.2
    OBEN_CM = 2.0
    #: Grenzen der beiden Regler (cm). Oben 8 cm: eine Strähne hat `Herrenhaar.PUNKTE` Stützpunkte, bei mehr zerfiele ihre Rundung um den Kopf in Sehnen.
    GRENZE_CM = (0.5, 8.0)
    #: Höhenwinkel (Grad): ab hier nach unten gilt `unten`, ab hier nach oben `oben`. Das Ohr liegt bei −41…+15°, der Nackenrand bei −38°, der Haaransatz an der Stirn bei 45–55°.
    HOEHEN = (15.0, 65.0)
    #: Ab dieser Länge (m) gilt die Dicke der Hülle des Fotohaars voll; kürzer wird sie im Verhältnis kleiner, nie unter `DICKE_MIN` davon.
    DICKE_AB_M = 0.020
    DICKE_MIN = 0.30

    def __init__(self, unten_cm=None, oben_cm=None):
        self.unten_cm = self.begrenzen(self.UNTEN_CM if unten_cm is None else unten_cm)
        self.oben_cm = self.begrenzen(self.OBEN_CM if oben_cm is None else oben_cm)

    @classmethod
    def begrenzen(cls, cm):
        """Auf die Grenzen der Regler gekappt (cm), eine Zahl."""
        return float(np.clip(float(cm), *cls.GRENZE_CM))

    @classmethod
    def aus_werte(cls, werte):
        """Aus einem Wörterbuch `{'unten': cm, 'oben': cm}` (so steht es im Rezept, `m.haar_laenge`, in `haltung_werte['haarlaenge']`) — fehlende Werte gelten als Vorgabe."""
        werte = werte if isinstance(werte, dict) else {}
        return cls(werte.get('unten'), werte.get('oben'))

    @classmethod
    def aus_modell(cls, modell):
        """Die Länge, die das Rezept des Modells gewählt hat (`m.haar_laenge`); `default` wenn keine Zeile da ist."""
        return cls.aus_werte((getattr(modell, 'haltung_werte', None) or {}).get('haarlaenge'))

    def ist_vorgabe(self):
        """True, wenn beide Werte die Vorgabe sind (dann braucht es keine Rezeptzeile)."""
        return self.unten_cm == self.UNTEN_CM and self.oben_cm == self.OBEN_CM

    def werte(self):
        """`{'unten': cm, 'oben': cm}` — Form für `haltung_werte` und die Fassung."""
        return {'unten': self.unten_cm, 'oben': self.oben_cm}

    def gewicht(self, el):
        """0 (unten) … 1 (oben) je Höhenwinkel `el` (Grad): glatt zwischen `HOEHEN[0]` und `HOEHEN[1]`."""
        unten, oben = self.HOEHEN
        x = np.clip((np.asarray(el, dtype=np.float64) - unten) / (oben - unten), 0.0, 1.0)
        return x * x * (3.0 - 2.0 * x)

    def laenge(self, el):
        """Die Länge in m je Höhenwinkel `el` (Grad)."""
        w = self.gewicht(el)
        return 0.01 * (self.unten_cm + (self.oben_cm - self.unten_cm) * w)

    def dickefaktor(self, el):
        """Faktor (`DICKE_MIN` … 1) auf die Dicke der Hülle des Fotohaars je Höhenwinkel: die Länge geteilt durch `DICKE_AB_M`."""
        return np.clip(self.laenge(el) / self.DICKE_AB_M, self.DICKE_MIN, 1.0)

    def fingerabdruck(self):
        """Gehört in die Fassung des Standmodells (zusammen mit `Herrenhaar.VERSION`): alles, was die Länge bestimmt."""
        return [self.unten_cm, self.oben_cm, list(self.HOEHEN), self.DICKE_AB_M, self.DICKE_MIN]
