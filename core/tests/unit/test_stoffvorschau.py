# -*- coding: utf-8 -*-
u"""`Stoffvorschau`: der Stoff folgt dem Koerper, ohne neue Simulation.

WARUM (08.09.2026, Edgar: „vielleicht zweistufig - erst der schnelle
MakeHuman nachbau, dann das «echte» genaue Bauen?"): Eine Drapierung kostet
gemessen 24,5 s. Nach EINER Simulation steht aber fest, wo jeder Stoffpunkt
relativ zum Koerper liegt — diese Lage haelt die Klasse fest und rechnet sie
bei jedem Reglerzug nach. Gemessen 8,4 ms je Zug bei 11.387 Stoffpunkten.

DIE DREI FALLEN, DIE HIER WIRKLICH ZUGESCHLAGEN HABEN
=====================================================
1. `CharacterState.compute()` gibt bei jedem Aufruf DENSELBEN Puffer
   zurueck. Mit `np.asarray` (das nicht kopiert) zeigte der gespeicherte
   Grundkoerper auf das Feld, das der naechste Reglerzug ueberschreibt —
   jede Bilanz meldete 0,0 mm.
2. Drei Koordinatensysteme: Szene (m, Z oben), Stoff (cm, Y oben), Koerper
   der Drapierung (m, Y oben). Ohne Umrechnung projizierte jeder Stoffpunkt
   auf ein weit entferntes Dreieck — die Vorschau lief, war schnell, und
   bewegte nichts.
3. Beides faellt NICHT durch eine Ausnahme auf, sondern nur dadurch, dass
   sich der Stoff nicht bewegt. Deshalb pruefen die Tests unten die
   BEWEGUNG, nicht die Abwesenheit von Fehlern.
"""
import numpy as np
from django.test import SimpleTestCase

from ._kunstkoerper import Kunstkoerper


class StoffvorschauTest(SimpleTestCase):

    databases = set()

    def test_stoff_folgt_dem_koerper(self):
        u"""Der Kern: Koerper wird breiter, der Stoff geht mit."""
        S = StoffvorschauTest._vorschau()
        punkte, dreiecke = Kunstkoerper.wuerfel()
        # Stoff dicht ueber der Seitenflaeche x = +0.5
        stoff = np.array([[.52, .3, 0.], [.52, .6, .2], [.52, .5, -.2]])
        v = S(punkte, dreiecke, stoff)

        breiter = punkte.copy()
        breiter[:, 0] *= 2.0                   # Wuerfel doppelt so breit
        neu = v.punkte(breiter)
        self.assertGreater(float(np.abs(neu - stoff).max()), 0.4,
                           'Der Stoff ist dem Koerper nicht gefolgt')
        # Und er bleibt AUSSEN: x muss mitgewachsen sein, nicht schrumpfen.
        self.assertGreater(float(neu[:, 0].min()), 0.9)

    def test_unveraenderter_koerper_laesst_den_stoff_stehen(self):
        u"""Die Gegenprobe: ohne Verformung darf sich nichts bewegen."""
        S = StoffvorschauTest._vorschau()
        punkte, dreiecke = Kunstkoerper.wuerfel()
        stoff = np.array([[.52, .3, 0.], [.52, .6, .2]])
        v = S(punkte, dreiecke, stoff)
        gleich = v.punkte(punkte.copy())
        self.assertLess(float(np.abs(gleich - stoff).max()), 1e-9)

    def test_grundkoerper_wird_kopiert(self):
        u"""Falle 1: Ein wandernder Puffer darf die Bindung nicht mitziehen.

        Genau so ist es passiert: `compute()` liefert immer dasselbe Feld.
        Wer es nur ansieht statt zu kopieren, bindet an einen Bezug, der
        sich mitveraendert — und misst danach immer 0,0 mm.
        """
        S = StoffvorschauTest._vorschau()
        punkte, dreiecke = Kunstkoerper.wuerfel()
        stoff = np.array([[.52, .3, 0.]])
        v = S(punkte, dreiecke, stoff)
        punkte[:, 0] *= 5.0                    # der Aufrufer schreibt weiter
        self.assertLess(float(np.abs(v.grundkoerper[:, 0]).max()), 0.51,
                        'Die Bindung haengt am Puffer des Aufrufers')
        stoff[0, 0] = 99.0
        self.assertLess(float(v.stoff.max()), 1.0,
                        'Das Stoffnetz haengt am Puffer des Aufrufers')

    def test_achsen_hin_und_zurueck(self):
        u"""Falle 2: Z oben <-> Y oben, und die Umkehrung muss treffen."""
        S = StoffvorschauTest._vorschau()
        zoben = np.array([[1., 2., 3.], [-4., 5., -6.]])
        yoben = S.nach_yoben(zoben)
        # (x, y, z) -> (x, z, -y)
        self.assertTrue(np.allclose(yoben, [[1., 3., -2.], [-4., -6., -5.]]))
        self.assertTrue(np.allclose(S.nach_zoben(yoben), zoben))

    def test_aus_drapierung_rechnet_zentimeter_um(self):
        u"""Der Stoff kommt in cm, der Koerper in m mit Z oben."""
        S = StoffvorschauTest._vorschau()
        punkte, dreiecke = Kunstkoerper.wuerfel()
        koerper_zoben = S.nach_zoben(punkte)          # so kaeme er aus der Szene
        stoff_cm = np.array([[52., 30., 0.]])         # dieselbe Stelle in cm
        v = S.aus_drapierung(koerper_zoben, dreiecke, stoff_cm)
        self.assertTrue(np.allclose(v.stoff, [[.52, .30, 0.]]))
        # Und der Koerper liegt wieder Y oben, wie das Stoffnetz.
        self.assertTrue(np.allclose(v.grundkoerper, punkte))

    def test_sitzt_erkennt_zwei_netze_in_verschiedenen_systemen(self):
        u"""Die Probe, die den stillen Fehler haette fangen muessen.

        Sitzt der Stoff am Koerper, sind es Millimeter. Liegt er wegen
        falscher Einheit meterweit daneben, meldet `sitzt()` das — statt
        eine Vorschau zu liefern, die nur nichts bewegt.
        """
        S = StoffvorschauTest._vorschau()
        punkte, dreiecke = Kunstkoerper.wuerfel()
        nah = S(punkte, dreiecke, np.array([[.52, .3, 0.], [.52, .6, .2]]))
        self.assertTrue(nah.sitzt()['sitzt'])
        self.assertLess(nah.sitzt()['median_mm'], 50.0)

        # Derselbe Stoff, aber in Zentimetern gelesen: 100x zu gross.
        falsch = S(punkte, dreiecke, np.array([[52., 30., 0.], [52., 60., 20.]]))
        self.assertFalse(falsch.sitzt()['sitzt'])
        self.assertGreater(falsch.sitzt()['median_mm'], 1000.0)

    def test_falsche_punktzahl_wird_gemeldet(self):
        u"""Ein Koerper anderer Bauart passt nicht — und das muss knallen."""
        S = StoffvorschauTest._vorschau()
        punkte, dreiecke = Kunstkoerper.wuerfel()
        v = S(punkte, dreiecke, np.array([[.52, .3, 0.]]))
        with self.assertRaises(ValueError):
            v.punkte(np.zeros((5, 3)))

    def test_quads_werden_geteilt(self):
        u"""Die Netze des Projekts kommen teils als Vierecke."""
        S = StoffvorschauTest._vorschau()
        punkte, dreiecke = Kunstkoerper.wuerfel()
        # Aus je zwei Dreiecken wieder ein Viereck bauen — so kommen die
        # Netze des Projekts (`netz.faces`) teilweise an.
        quads = np.array([[d1[0], d1[1], d2[1], d2[2]]
                          for d1, d2 in zip(dreiecke[0::2], dreiecke[1::2])],
                         dtype=int)
        v = S(punkte, quads, np.array([[0., .5, .52]]))
        self.assertEqual(v.projektion.dreiecke.shape[1], 3)
        self.assertEqual(len(v.projektion.dreiecke), 2 * len(quads))

    @staticmethod
    def _vorschau():
        from GarmentCode.stoffvorschau import Stoffvorschau
        return Stoffvorschau
