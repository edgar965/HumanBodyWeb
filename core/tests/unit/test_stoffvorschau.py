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


def _wuerfel(n=6):
    u"""Ein geschlossener Quader 1 m, Y oben — je Seite `n` x `n` Felder.

    UNTERTEILT, nicht mit 12 Dreiecken: `DreiecksProjektion` fragt den
    KD-Baum nach `KANDIDATEN = 32` Nachbarn. Ein Netz mit weniger Dreiecken
    laeuft dort aus dem Feld (IndexError). Koerpernetze haben 17.288
    Dreiecke; ein zu grobes Testnetz prueft also einen Fall, den es nicht
    gibt.
    """
    punkte, dreiecke = [], []
    # Sechs Seiten, jede als Gitter. `achse` ist die feste Richtung.
    seiten = [(0, -.5), (0, .5), (1, 0.), (1, 1.), (2, -.5), (2, .5)]
    for achse, wert in seiten:
        ab = len(punkte)
        frei = [i for i in range(3) if i != achse]
        for a in range(n + 1):
            for b in range(n + 1):
                p = [0.0, 0.0, 0.0]
                p[achse] = wert
                p[frei[0]] = -.5 + a / n if frei[0] != 1 else a / n
                p[frei[1]] = -.5 + b / n if frei[1] != 1 else b / n
                punkte.append(p)
        for a in range(n):
            for b in range(n):
                i = ab + a * (n + 1) + b
                j = i + (n + 1)
                dreiecke.append([i, j, i + 1])
                dreiecke.append([i + 1, j, j + 1])
    return np.asarray(punkte, dtype=float), np.asarray(dreiecke, dtype=int)


def _vorschau():
    from GarmentCode.stoffvorschau import Stoffvorschau
    return Stoffvorschau


class StoffvorschauTest(SimpleTestCase):

    databases = set()

    def test_stoff_folgt_dem_koerper(self):
        u"""Der Kern: Koerper wird breiter, der Stoff geht mit."""
        S = _vorschau()
        punkte, dreiecke = _wuerfel()
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
        S = _vorschau()
        punkte, dreiecke = _wuerfel()
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
        S = _vorschau()
        punkte, dreiecke = _wuerfel()
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
        S = _vorschau()
        zoben = np.array([[1., 2., 3.], [-4., 5., -6.]])
        yoben = S.nach_yoben(zoben)
        # (x, y, z) -> (x, z, -y)
        self.assertTrue(np.allclose(yoben, [[1., 3., -2.], [-4., -6., -5.]]))
        self.assertTrue(np.allclose(S.nach_zoben(yoben), zoben))

    def test_aus_drapierung_rechnet_zentimeter_um(self):
        u"""Der Stoff kommt in cm, der Koerper in m mit Z oben."""
        S = _vorschau()
        punkte, dreiecke = _wuerfel()
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
        S = _vorschau()
        punkte, dreiecke = _wuerfel()
        nah = S(punkte, dreiecke, np.array([[.52, .3, 0.], [.52, .6, .2]]))
        self.assertTrue(nah.sitzt()['sitzt'])
        self.assertLess(nah.sitzt()['median_mm'], 50.0)

        # Derselbe Stoff, aber in Zentimetern gelesen: 100x zu gross.
        falsch = S(punkte, dreiecke, np.array([[52., 30., 0.], [52., 60., 20.]]))
        self.assertFalse(falsch.sitzt()['sitzt'])
        self.assertGreater(falsch.sitzt()['median_mm'], 1000.0)

    def test_falsche_punktzahl_wird_gemeldet(self):
        u"""Ein Koerper anderer Bauart passt nicht — und das muss knallen."""
        S = _vorschau()
        punkte, dreiecke = _wuerfel()
        v = S(punkte, dreiecke, np.array([[.52, .3, 0.]]))
        with self.assertRaises(ValueError):
            v.punkte(np.zeros((5, 3)))

    def test_quads_werden_geteilt(self):
        u"""Die Netze des Projekts kommen teils als Vierecke."""
        S = _vorschau()
        punkte, dreiecke = _wuerfel()
        # Aus je zwei Dreiecken wieder ein Viereck bauen — so kommen die
        # Netze des Projekts (`netz.faces`) teilweise an.
        quads = np.array([[d1[0], d1[1], d2[1], d2[2]]
                          for d1, d2 in zip(dreiecke[0::2], dreiecke[1::2])],
                         dtype=int)
        v = S(punkte, quads, np.array([[0., .5, .52]]))
        self.assertEqual(v.projektion.dreiecke.shape[1], 3)
        self.assertEqual(len(v.projektion.dreiecke), 2 * len(quads))
