# -*- coding: utf-8 -*-
u"""Zu welchem Körperpunkt gehört ein Kleidungspunkt?

WARUM DIESER TEST (Befund `doppelcode`, 30.08.2026)
===================================================
``Kleidungswerkzeuge.knochenindizes`` und ``knochengewichte`` trugen dieselben
vierzehn Zeilen und unterschieden sich in EINEM Buchstaben — ``si[nearest]``
gegen ``sw[nearest]``. Genau das macht die Doppelung teuer: Wer die Zuordnung an
einer Stelle nachbessert, bekommt Indizes und Gewichte aus zwei verschiedenen
Rechnungen. Das Kleidungsstück hängt dann an den richtigen Knochen mit den
falschen Anteilen.

DAS SIEHT MAN NICHT AN DER FIGUR. In der Ruhelage sind alle Knochenmatrizen die
Einheitsmatrix — ein Kleidungsstück mit vertauschten Gewichten steht dort
korrekt da. Falsch wird es erst in Bewegung, und dann sieht es nach einem
Verzerrungsfehler aus, nicht nach vertauschten Zahlen (siehe „SkinnedMesh Debug
Pattern" im Projektgedächtnis).

Deshalb wird hier gerechnet, nicht angesehen: Beide Methoden müssen DIESELBE
Zuordnung benutzen, und der Zwei-Schritt-Weg über einen fremden Körper muss die
Kette einhalten.

DER ZWEI-SCHRITT-WEG: Wurde das Stück gegen einen fremden Körper gerechnet (etwa
den von MakeHuman), wird erst dessen nächster Punkt gesucht und dieser auf den
nächsten Rigify-Punkt abgebildet. Ein Schritt weniger bindet bei abweichendem
Armwinkel den Ärmel an den Rumpf — und auch das fällt erst in Bewegung auf.
"""
import unittest

import numpy as np

from core.dienste.kleidungswerkzeuge import Kleidungswerkzeuge


class KleiderzuordnungTest(unittest.TestCase):
    u"""Die gemeinsame Zuordnung — ohne Datenbank, ohne Produktivdaten."""

    #: Liest nur NumPy-Felder aus dem Testfall (Regel ``testlauf-blockiert-server``).
    databases = []

    def test_naechster_punkt_wird_getroffen(self):
        koerper = np.array([[0., 0., 0.], [1., 0., 0.], [2., 0., 0.]])
        kleid = np.array([[1.9, 0., 0.], [0.1, 0., 0.], [1.4, 0., 0.]])
        zu = Kleidungswerkzeuge._zuordnung(kleid, koerper)
        self.assertEqual(list(zu), [2, 0, 1])

    def test_gleich_viele_punkte_wie_kleidungspunkte(self):
        koerper = np.random.RandomState(7).rand(50, 3)
        kleid = np.random.RandomState(8).rand(17, 3)
        self.assertEqual(len(Kleidungswerkzeuge._zuordnung(kleid, koerper)), 17)

    def test_fremder_koerper_geht_ueber_zwei_schritte(self):
        u"""Kleid → fremder Körper → Rigify-Körper, nicht Kleid → Rigify."""
        # Der fremde Koerper liegt um 10 versetzt: Wer ihn ueberspringt, findet
        # fuer JEDEN Kleidungspunkt denselben Rigify-Punkt.
        fremd = np.array([[10., 0., 0.], [11., 0., 0.], [12., 0., 0.],
                          [13., 0., 0.]])
        rigify = np.array([[10.1, 0., 0.], [12.1, 0., 0.]])
        kleid = np.array([[10.2, 0., 0.], [12.9, 0., 0.]])

        ueber_fremd = Kleidungswerkzeuge._zuordnung(kleid, rigify, ref_body=fremd)
        # Kleid[0] -> fremd[0] (10.0) -> rigify[0] (10.1) = 0
        # Kleid[1] -> fremd[3] (13.0) -> rigify[1] (12.1) = 1
        self.assertEqual(list(ueber_fremd), [0, 1])

    def test_gleich_grosser_referenzkoerper_wird_uebergangen(self):
        u"""Hat der fremde Körper dieselbe Punktzahl, ist er derselbe Körper.

        Dann wäre der Umweg reine Rechenzeit — und würde bei identischen
        Punkten ohnehin dasselbe ergeben."""
        koerper = np.array([[0., 0., 0.], [5., 0., 0.]])
        kleid = np.array([[4.9, 0., 0.]])
        mit = Kleidungswerkzeuge._zuordnung(kleid, koerper, ref_body=koerper)
        ohne = Kleidungswerkzeuge._zuordnung(kleid, koerper)
        self.assertEqual(list(mit), list(ohne))

    def test_indizes_und_gewichte_teilen_die_zuordnung(self):
        u"""Der eigentliche Befund: EIN Weg für beide Antworten.

        Statt der echten Gewichtstabelle (Produktivdaten in
        ``HumanBody/data``) steht hier eine Attrappe: Wichtig ist nicht, welche
        Zahlen herauskommen, sondern dass beide Methoden denselben Index
        nachschlagen."""
        koerper = np.array([[0., 0., 0.], [1., 0., 0.], [2., 0., 0.]])
        kleid = np.array([[1.9, 0., 0.], [0.1, 0., 0.]])
        erwartet = list(Kleidungswerkzeuge._zuordnung(kleid, koerper))

        si = np.array([[10, 11, 12, 13], [20, 21, 22, 23], [30, 31, 32, 33]])
        sw = np.array([[.1, .2, .3, .4], [.5, .6, .7, .8], [.9, 1., 1.1, 1.2]])

        from core.dienste import kleidungswerkzeuge as modul
        echt = modul.Skingewichte.arrays
        modul.Skingewichte.arrays = staticmethod(lambda geschlecht='female': (si, sw))
        try:
            i_roh = Kleidungswerkzeuge.knochenindizes(kleid, koerper)
            w_roh = Kleidungswerkzeuge.knochengewichte(kleid, koerper)
        finally:
            modul.Skingewichte.arrays = echt

        indizes = np.frombuffer(i_roh, dtype=np.float32).reshape(-1, 4)
        gewichte = np.frombuffer(w_roh, dtype=np.float32).reshape(-1, 4)
        self.assertEqual(len(indizes), len(kleid))
        np.testing.assert_allclose(indizes, si[erwartet].astype(np.float32))
        np.testing.assert_allclose(gewichte, sw[erwartet].astype(np.float32))

    def test_ausgabe_ist_float32(self):
        u"""Three.js liest beide Felder als Float32 — auch die Indizes.

        Ein Uint32-Puffer käme dort als andere Zahl an, ohne Fehler: Das
        Kleidungsstück hinge an zufälligen Knochen."""
        koerper = np.array([[0., 0., 0.], [1., 0., 0.]])
        kleid = np.array([[0.9, 0., 0.]])
        si = np.array([[1, 2, 3, 4], [5, 6, 7, 8]])
        sw = np.array([[.25, .25, .25, .25], [.4, .3, .2, .1]])

        from core.dienste import kleidungswerkzeuge as modul
        echt = modul.Skingewichte.arrays
        modul.Skingewichte.arrays = staticmethod(lambda geschlecht='female': (si, sw))
        try:
            roh = Kleidungswerkzeuge.knochenindizes(kleid, koerper)
        finally:
            modul.Skingewichte.arrays = echt
        self.assertEqual(len(roh), 4 * 4)      # vier Werte a vier Byte
        np.testing.assert_allclose(np.frombuffer(roh, dtype=np.float32),
                                   [5., 6., 7., 8.])
