# -*- coding: utf-8 -*-
"""Kostuemrumpf — was am Rumpf hängt: Unterkleid, Mantel, Ärmel, Gürtel, Gürteltaschen.

Jedes Maß ist ein Vielfaches eines Körpermaßes (`Koerpermasse`) mal einem Wert aus dem Wertesatz `p`
(Schlüssel `teil.name`, Schema und Startwerte: `core/dienste/kostuemparameter.py`). Die Startwerte sind die
von Hand gefundenen Faktoren der Kostüm-Runde 9 — ohne Wertesatz sieht das Kostüm aus wie damals.
"""

import numpy as np

from effekte.blender.kostuem.kostuemfrontborte import Kostuemfrontborte
from effekte.blender.kostuem.rohr import Rohr

__all__ = ['Kostuemrumpf']


class Kostuemrumpf:
    #: Wie weit die Umriss-Hülle (`Kostuemhuelle`) die Ringe des Mantels bewegen darf — (unten, oben) als Vielfaches der Weite
    #: aus dem Wertesatz. Am Rumpf sitzen die Ärmel: Dort zeigt der Umriss Mantel UND Ärmel, der Mantel darf nur wenig
    #: nachgeben; im Rock ist der Umriss der Mantel.
    HUELLE_RUMPF = (0.85, 1.25)
    HUELLE_ROCK = (0.85, 1.3)
    #: Zwischenringe im Rock, wenn eine Hülle da ist (Anteile zwischen Knie und Saum) — mehr Stellen, die dem Umriss folgen.
    ROCK_ZWISCHEN = (0.25, 0.5, 0.75)

    def __init__(self, masse, p, vorn_grad, huelle=None):
        self.m = masse
        self.p = p
        self.vorn_grad = vorn_grad
        self.vorn = 1 if vorn_grad == 90 else -1
        self.huelle = huelle

    def farbe(self, name):
        return tuple(float(self.p['farbe.%s.%s' % (name, k)]) for k in 'rgb')

    def _rumpfringe(self, rohr, namen, luft, anpassen=None):
        for name in namen:
            mx, my, hb, ht = self.m.ring(self.m.z(name))
            rohr.ring_waagerecht(mx, my, hb * luft, ht * luft, self.m.z(name), anpassen=anpassen)

    def _rockringe(self, rohr, mitte_weite, saum_hoehe, saum_weite, welle, wellen, anpassen=None):
        """Zwei Ringe unter der Hüfte: Kniehöhe (0,29 × Höhe) und Saum — der Saum liegt laut Schema immer
        tiefer. Mit Hülle (`anpassen`) dazwischen weitere Ringe, die dem Umriss folgen."""
        mx, my, hb, ht = self.m.ring(self.m.z('huefte'))
        stufen = [(0.29, mitte_weite)]
        if anpassen is not None and self.huelle is not None:
            stufen += [
                (0.29 + (saum_hoehe - 0.29) * t, mitte_weite + (saum_weite - mitte_weite) * t)
                for t in self.ROCK_ZWISCHEN
            ]
        stufen.append((saum_hoehe, saum_weite))
        for anteil, f in stufen:
            rohr.ring_waagerecht(
                mx, my, hb * f, ht * f, self.m.boden + anteil * self.m.hoehe, welle=welle, wellen=wellen,
                anpassen=anpassen,
            )

    def unterkleid(self):
        p = self.p
        rohr = Rohr('Unterkleid', self.farbe('unterkleid'))
        self._rumpfringe(rohr, ('hals', 'schulter', 'brust', 'taille', 'huefte'), p['unterkleid.luft'])
        self._rockringe(
            rohr,
            p['unterkleid.mitte_weite'],
            p['unterkleid.saum_hoehe'],
            p['unterkleid.saum_weite'],
            p['unterkleid.welle'],
            12,
        )
        return rohr.bauen(dicke=0.004, deckel_oben=True)

    def mantel(self):
        p = self.p
        rohr = Rohr(
            'Mantel',
            self.farbe('mantel'),
            offen_grad=p['mantel.offen_grad'],
            offen_richtung=self.vorn_grad,
            huelle=self.huelle,
        )
        mx, my, hb, ht = self.m.ring(self.m.z('hals'))
        rohr.ring_waagerecht(
            mx, my, hb * p['mantel.hals_weite'], ht * p['mantel.hals_weite'] * 0.9, self.m.z('hals') + 0.01
        )
        mx, my, hb, ht = self.m.ring(self.m.z('schulter'))
        rohr.ring_waagerecht(
            mx,
            my,
            hb * p['mantel.schulter_weite'],
            ht * p['mantel.schulter_tiefe'],
            self.m.z('schulter') - 0.02,
        )
        self._rumpfringe(rohr, ('brust', 'taille', 'huefte'), p['mantel.luft'], anpassen=self.HUELLE_RUMPF)
        self._rockringe(
            rohr,
            p['mantel.mitte_weite'],
            p['mantel.saum_hoehe'],
            p['mantel.saum_weite'],
            p['mantel.welle'],
            9,
            anpassen=self.HUELLE_ROCK,
        )
        self.mantelringe = rohr.ringe  # für den Besatz an der Öffnung (`Kostuemfrontborte`)
        return rohr.bauen(dicke=0.008)

    @staticmethod
    def _auf_pfad(punkte, t):
        """(Ort, Richtung) bei Anteil `t` der Länge des Streckenzugs — über die Enden hinaus in Richtung des
        ersten bzw. letzten Stücks verlängert."""
        punkte = [np.asarray(v, float) for v in punkte]
        stuecke = [punkte[i + 1] - punkte[i] for i in range(len(punkte) - 1)]
        laengen = [float(np.linalg.norm(s)) for s in stuecke]
        s = t * sum(laengen)
        if s <= 0:
            return punkte[0] + stuecke[0] / max(laengen[0], 1e-9) * s, stuecke[0] / max(laengen[0], 1e-9)
        for i, laenge in enumerate(laengen):
            if s <= laenge or i == len(laengen) - 1:
                richtung = stuecke[i] / max(laenge, 1e-9)
                return punkte[i] + richtung * s, richtung
            s -= laenge
        return punkte[-1], stuecke[-1]

    def _aermelpfad(self, seite):
        """Schulter → (Ellbogen →) Handgelenk. Ein gebeugter Arm (Stabarm) liegt nicht auf der Geraden."""
        schulter, hand, radius = self.m.arm(seite)
        ellbogen = self.m.ellbogen.get(seite)
        pfad = [schulter, ellbogen, hand] if ellbogen is not None else [schulter, hand]
        return pfad, radius

    #: Ringe des Schlauchs am Arm: (Anteil der Pfadlänge, Weite als Mischung aus oben/mitte/saum).
    AERMEL = ((-0.05, (1, 0, 0)), (0.3, (0.5, 0.5, 0)), (0.65, (0, 1, 0)), (1.0, (0, 1, 0)))

    @staticmethod
    def _pfadlaenge(pfad):
        return sum(float(np.linalg.norm(np.asarray(pfad[i + 1], float) - np.asarray(pfad[i], float)))
                   for i in range(len(pfad) - 1))

    def aermel(self, seite):
        """Der Ärmel besteht aus einem Schlauch am Arm (Schulter → Ellbogen → Handgelenk, Ringe quer zum Arm)
        und einer GLOCKE, die vom Handgelenk herabhängt (waagerechte Ringe wie beim Mantel). Erste Fassungen
        ließen die Schlauchringe selbst zum Saum aufgehen und am Ende nach unten kippen: am gebeugten Stabarm
        wurde daraus erst eine Scheibe, dann Wülste am Ellbogen — der weite Ärmel der Vorlage hängt, er folgt
        nicht dem Arm."""
        p = self.p
        pfad, radius = self._aermelpfad(seite)
        name = 'R' if seite > 0 else 'L'
        rohr = Rohr('Aermel_%s' % name, self.farbe('mantel'))
        gewichte = (p['aermel.weite_oben'], p['aermel.weite_mitte'], p['aermel.weite_saum'])
        for t, mix in self.AERMEL:
            f = sum(m * w for m, w in zip(mix, gewichte, strict=True))
            ort, richtung = self._auf_pfad(pfad, t)
            rohr.ring_auf_achse(ort, richtung, radius * f, radius * f)
        teile = [rohr.bauen(dicke=0.008), self._glocke(name, pfad, radius, gewichte, 'Aermelglocke', 1.0, (0.0, 0.2, 0.5, 0.8, 1.0))]
        if p['borte.an'] >= 0.5:
            # Nur das Band am Saum der Glocke (bis 30.09.2026 stand hier (0.0, 0.85): die Borte deckte die
            # ganze Glocke — goldene Kästen an den Händen).
            teile.append(
                self._glocke(name, pfad, radius, gewichte, 'Aermelborte', 1.012, (0.9, 1.0), self.farbe('borte'), 0.004)
            )
        return teile

    def _glocke(self, name, pfad, radius, gewichte, teil, faktor, abschnitte, farbe=None, dicke=0.008):
        """Waagerechte Ringe am Handgelenk nach unten: von der Weite `mitte` zur Weite `saum`. `abschnitte`:
        Anteile der Tiefe (0 = Handgelenk, 1 = Saum), `faktor` gegenüber der Glocke selbst (die Borte liegt
        knapp außen)."""
        p = self.p
        hand = np.asarray(pfad[-1], float)
        tiefe = p['aermel.laenge'] * self._pfadlaenge(pfad) + p['aermel.haengen']
        rohr = Rohr('%s_%s' % (teil, name), farbe or self.farbe('mantel'))
        for s in abschnitte:
            f = (gewichte[1] + (gewichte[2] - gewichte[1]) * s**0.8) * faktor
            # `aermel.tiefe`: der Ärmel der Vorlage ist von vorn weit, von der Seite schmal — ein flacher
            # Trichter
            rohr.ring_waagerecht(
                float(hand[0]), float(hand[1]), radius * f, radius * f * p['aermel.tiefe'], float(hand[2]) + 0.02 - s * tiefe
            )
        return rohr.bauen(dicke=dicke, glaetten=1 if faktor == 1.0 else 0)

    def saumborte(self):
        """Band am Saum des Mantels — mit derselben Öffnung vorn und Wellung wie der Mantel."""
        p = self.p
        rohr = Rohr(
            'Saumborte',
            self.farbe('borte'),
            offen_grad=p['mantel.offen_grad'],
            offen_richtung=self.vorn_grad,
            huelle=self.huelle,
        )
        mx, my, hb, ht = self.m.ring(self.m.z('huefte'))
        z_saum = self.m.boden + p['mantel.saum_hoehe'] * self.m.hoehe
        z_knie = self.m.boden + 0.29 * self.m.hoehe
        f_saum, f_knie = p['mantel.saum_weite'], p['mantel.mitte_weite']
        breite = p['borte.breite']
        for dz in (breite, 0.0):
            z = z_saum + dz
            f = (f_saum + (f_knie - f_saum) * dz / max(z_knie - z_saum, 0.05)) * 1.012
            rohr.ring_waagerecht(
                mx, my, hb * f, ht * f, z, welle=p['mantel.welle'], wellen=9, anpassen=(*self.HUELLE_ROCK, 1.012)
            )
        return rohr.bauen(dicke=0.004, glaetten=0)

    def guertel(self):
        p = self.p
        mx, my, hb, ht = self.m.ring(self.m.z('taille'))
        rohr = Rohr('Guertel', self.farbe('leder'))
        weite = p['mantel.luft'] * p['guertel.weite']
        for dz in (-p['guertel.breite'] / 2, p['guertel.breite'] / 2):
            rohr.ring_waagerecht(mx, my, hb * weite, ht * weite, self.m.z('taille') + dz)
        return rohr.bauen(dicke=0.01, glaetten=0)

    def tasche(self, seite):
        """Lederbeutel am Gürtel, vorn seitlich (Vorlage: Beutel und Fläschchen an der Hüfte)."""
        g = self.p['taschen.groesse']
        mx, my, hb, ht = self.m.ring(self.m.z('taille'))
        z0 = self.m.z('taille')
        rohr = Rohr('Guerteltasche_%s' % ('R' if seite > 0 else 'L'), self.farbe('leder'))
        cx, cy = mx + seite * hb * 0.75, my + self.vorn * ht * 1.05
        for r, dz in ((0.55, 0.0), (1.0, -0.03), (0.85, -0.09), (0.1, -0.115)):
            rohr.ring_waagerecht(cx, cy, 0.045 * r * g, 0.035 * r * g, z0 + dz * g)
        return rohr.bauen(dicke=0.004, deckel_oben=True)

    def bauen(self):
        teile = [self.unterkleid(), self.mantel(), *self.aermel(1), *self.aermel(-1), self.guertel()]
        if self.p['borte.an'] >= 0.5:
            teile.append(self.saumborte())
            if self.p['mantel.offen_grad'] >= 5.0:
                teile += Kostuemfrontborte(self.mantelringe[1:], self.farbe('borte')).bauen()
        if self.p['taschen.an'] >= 0.5:
            teile += [self.tasche(1), self.tasche(-1)]
        return teile
