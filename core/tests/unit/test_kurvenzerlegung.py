# -*- coding: utf-8 -*-
u"""`Kurvenzerlegung`: dieselben Punkte, ohne 12.402 Integrale.

WARUM (08.09.2026, Edgar: „nach erzeugung eines 2D Modells sollen die Regler
in Echtzeit das 2D Modell anpassen"): Ein Kleid-Schnitt brauchte 950 ms im
warmen Dauerprozess. Das Profil zeigte `Edge.linearize` mit 1,42 s von
1,66 s — darunter 12.402 `scipy.integrate.quad` und 260.946 Ableitungen,
nur um neun Punkte gleichmaessig auf einer Bezierkurve zu verteilen.

Die Zerlegung tabelliert die Bogenlaenge EINMAL je Kante und interpoliert.
Gemessen (`ProjektTemp/kurven_gegenprobe2.py`, warmer Prozess):

    Kleid      866 ms -> 225 ms   T-Shirt   758 -> 169
    Hemd       785 ms -> 198 ms   Jumpsuit 1174 -> 431

Geprueft wird hier die RECHNUNG, nicht die Anbindung: Sie braucht kein
GarmentCode und kein Python 3.10, nur eine Kurve mit bekannter Bogenlaenge.

DIE GERADE IST DER SCHARFE FALL. Auf ihr faellt jede Verwechslung von
Bogenlaenge und Parameter sofort auf: Gleichmaessig nach Bogenlaenge ist
dort dasselbe wie gleichmaessig in t, und beides muss exakt
`0.1, 0.2, ... 0.9` ergeben.
"""
import math

from django.test import SimpleTestCase


class Kurve:
    u"""Eine Attrappe mit `point(t)` — mehr braucht `teilstellen` nicht."""

    def __init__(self, funktion):
        self.funktion = funktion
        self.aufrufe = 0

    def point(self, t):
        self.aufrufe += 1
        return self.funktion(t)


def _zerlegung():
    u"""Die Klasse aus dem GarmentCode-Paket."""
    from GarmentCode.kurvenzerlegung import Kurvenzerlegung
    return Kurvenzerlegung


class KurvenzerlegungTest(SimpleTestCase):

    databases = set()

    def test_gerade_trifft_exakt(self):
        u"""Auf einer Geraden sind Bogenlaenge und Parameter dasselbe."""
        Z = _zerlegung()
        gerade = Kurve(lambda t: complex(3.0 * t, 4.0 * t))   # Laenge 5
        stellen = Z.teilstellen(gerade, 9)
        self.assertEqual(len(stellen), 9)
        for soll, ist in zip([0.1 * i for i in range(1, 10)], stellen):
            self.assertAlmostEqual(soll, ist, places=9)

    def test_gleichmaessig_nach_bogenlaenge_nicht_nach_parameter(self):
        u"""Der ganze Zweck: gleiche ABSTAENDE, nicht gleiche t-Schritte.

        Die Kurve `t -> t**3` laeuft anfangs langsam und dann schnell. Wer
        einfach `linspace` in t nimmt, bekommt am Anfang enge und am Ende
        weite Abstaende — genau der Fehler, den diese Klasse vermeidet.
        """
        Z = _zerlegung()
        kurve = Kurve(lambda t: complex(t ** 3, 0.0))
        stellen = Z.teilstellen(kurve, 9)
        punkte = [s ** 3 for s in stellen]
        abstaende = [b - a for a, b in zip([0.0] + punkte, punkte + [1.0])]
        self.assertAlmostEqual(max(abstaende), min(abstaende), places=3,
                               msg='Abstaende sind nicht gleichmaessig: %s'
                                   % abstaende)
        # Und die Gegenprobe: in t waeren sie es NICHT.
        gleich_t = [0.1 * i for i in range(1, 10)]
        roh = [s ** 3 for s in gleich_t]
        roh_abst = [b - a for a, b in zip([0.0] + roh, roh + [1.0])]
        self.assertGreater(max(roh_abst) - min(roh_abst), 0.1,
                           'Die Kurve ist zu brav fuer diesen Test')

    def test_viertelkreis_gegen_die_analytische_loesung(self):
        u"""Auf dem Kreis ist die Bogenlaenge bekannt: s(t) = r * Winkel."""
        Z = _zerlegung()
        kreis = Kurve(lambda t: complex(math.cos(t * math.pi / 2),
                                        math.sin(t * math.pi / 2)))
        stellen = Z.teilstellen(kreis, 9)
        # Gleiche Bogenlaenge heisst auf dem Kreis gleicher Winkel, und der
        # Winkel ist hier linear in t.
        for soll, ist in zip([0.1 * i for i in range(1, 10)], stellen):
            self.assertAlmostEqual(soll, ist, places=4)

    def test_entartete_kante_faellt_nicht_um(self):
        u"""Anfang = Ende: Gesamtlaenge null, keine Division durch null."""
        Z = _zerlegung()
        punkt = Kurve(lambda t: complex(1.0, 2.0))
        stellen = Z.teilstellen(punkt, 9)
        self.assertEqual(len(stellen), 9)
        for soll, ist in zip([0.1 * i for i in range(1, 10)], stellen):
            self.assertAlmostEqual(soll, ist, places=9)

    def test_anzahl_und_raender(self):
        u"""Ohne Anfang und Ende — wie beim Upstream."""
        for n in (1, 4, 9, 20):
            stellen = _zerlegung().teilstellen(
                Kurve(lambda t: complex(t, 0.0)), n)
            self.assertEqual(len(stellen), n)
            self.assertGreater(min(stellen), 0.0)
            self.assertLess(max(stellen), 1.0)

    def test_aufwand_haengt_nicht_an_der_punktzahl(self):
        u"""EINMAL tabellieren, dann interpolieren — das ist der Gewinn.

        Der Upstream loest je Punkt eine Nullstellensuche; hier kostet der
        zehnte Punkt nichts mehr. Gemessen an den `point`-Aufrufen: Sie
        muessen fuer 9 und fuer 90 Punkte gleich bleiben.
        """
        Z = _zerlegung()
        wenig = Kurve(lambda t: complex(t, t * t))
        viel = Kurve(lambda t: complex(t, t * t))
        Z.teilstellen(wenig, 9)
        Z.teilstellen(viel, 90)
        self.assertEqual(wenig.aufrufe, viel.aufrufe)
        self.assertEqual(wenig.aufrufe, Z.STUETZEN)
