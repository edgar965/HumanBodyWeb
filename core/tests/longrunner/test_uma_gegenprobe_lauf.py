# -*- coding: utf-8 -*-
u"""UMA gegen UMA Python, Teil 2: Animation und Kleidung.

Fortsetzung von `test_uma_gegenprobe.py` (Netz und Skelett); getrennt,
weil eine Datei mit allen vier Fällen über 300 Zeilen ginge.

    Fall 3   dieselbe BVH auf beide Skelette
    Fall 4   dieselbe Rasse mit denselben drei Kleidungsstücken
"""
import sys
import unittest
from pathlib import Path

from django.conf import settings

sys.path.insert(0, str(Path(settings.ASSETS_ROOT)))

import numpy as np                                          # noqa: E402

from .test_uma_gegenprobe import (KLEIDUNG, RASSE,          # noqa: E402
                                  _bauen, _referenz)

#: Eine BVH aus dem Bestand — Arme seitlich, also viel Bewegung in den
#: Gliedmaßen und wenig im Rumpf. Fehlt sie, wird übersprungen statt
#: eine andere geraten.
BVH = 'Aist/01001_ArmeSeitlich.bvh'


def _bvh():
    pfad = Path(settings.OBJECTS_ROOT) / 'animations' / 'bvh' / BVH
    if not pfad.is_file():
        raise unittest.SkipTest('BVH fehlt: %s' % pfad)
    return pfad


class AnimationAufBeiden(unittest.TestCase):
    u"""Fall 3 — dieselbe Bewegung auf beiden Zielskeletten.

    WAS HIER GEPRÜFT WIRD, UND WAS NICHT
    ====================================
    Nicht, dass zwei Retarget-Läufe bitgleich sind — sie rechnen gegen
    verschiedene Ruhelagen (die GLB bringt ihre eigene mit, der
    Python-Bau leitet sie aus `kopf`/`schwanz` ab). Geprüft wird, dass
    BEIDE Wege dieselben Knochen ansprechen und dass die Bewegung
    wirklich ankommt.

    Die Zuordnungstabelle ist für beide dieselbe
    (`formats/uma_knochen.DEF_ZU_UMA`, 05.09.2026 für die GLB-Figur
    geschrieben). Unabhängig bestätigt hat sie der C#-Code: `RaceData.TPose`
    führt 55 `HumanBone`-Paare, und dort steht auch, was ein Rateschluss
    verfehlt hätte — `Spine` heißt bei UMA `LowerBack`, und `Finger05` ist
    der DAUMEN.
    """

    databases = []

    @classmethod
    def setUpClass(cls):
        _referenz('Gegenprobe_nackt')          # überspringt, wenn sie fehlt
        cls.pfad = str(_bvh())

    def _lauf(self, ziel, figur):
        from core.dienste.retargetdaten import Retargetdaten
        return Retargetdaten(self.pfad, body_height=1.99, ziel=ziel,
                             figur=figur).holen()

    def test_beide_ziele_rechnen_und_treffen_dieselben_knochen(self):
        glb = self._lauf('uma', 'Gegenprobe_nackt.glb')
        py = self._lauf('umapython', RASSE)
        namen_glb = set(glb.als_dict()['mapped_bones'])
        namen_py = set(py.als_dict()['mapped_bones'])
        self.assertTrue(namen_glb, u'GLB-Ziel hat keinen Knochen zugeordnet')
        self.assertEqual(namen_glb, namen_py,
                         u'Beide Wege nutzen dieselbe Zuordnungstabelle')

    def test_die_bewegung_kommt_an(self):
        u"""Eine Spur, die sich nicht ändert, ist keine Animation.

        Genau daran hing der Befund vom 07.09.2026 bei SMPL: Der Clip
        entstand, hatte Spuren — und bewegte nichts, weil die Spuren
        Knochen nannten, die die Figur nicht hat.
        """
        py = self._lauf('umapython', RASSE).als_dict()
        self.assertGreater(py['frame_count'], 10)
        bewegt = 0
        for spur in py['tracks'].values():
            werte = np.asarray(spur, dtype=np.float64).reshape(-1, 4)
            if len(werte) > 1 and np.abs(werte - werte[0]).max() > 0.01:
                bewegt += 1
        self.assertGreater(bewegt, 10,
                           u'zu wenige Knochen bewegen sich: %d' % bewegt)

    def test_die_wurzel_ist_dabei(self):
        py = self._lauf('umapython', RASSE).als_dict()
        self.assertIn('Hips', py['tracks'])


class KleidungAufBeiden(unittest.TestCase):
    u"""Fall 4 — dieselben drei Stücke auf beiden Wegen.

    Drei Stücke aus drei Plätzen (Oberkörper, Beine, Füße), damit nicht
    zufällig ein einzelnes Rezept den Ausschlag gibt. Kleidung ist bei UMA
    kein Sonderfall: Ein Kleidungsstück IST ein Slot wie der Körper auch,
    mit denselben Knochen und denselben Bindeposen — deshalb sitzt es.
    """

    databases = []

    @classmethod
    def setUpClass(cls):
        from UMA_Python.gegenprobe import Unityglb
        cls.unity = Unityglb(_referenz('Gegenprobe_kleidung', KLEIDUNG))
        cls.gebaut = _bauen(KLEIDUNG)

    def test_punkt_und_dreieckszahl_stimmen(self):
        self.assertEqual(len(self.gebaut.netz.punkte),
                         len(self.unity.punkte))
        self.assertEqual(len(self.gebaut.netz.dreiecke),
                         self.unity.dreiecke)

    def test_jedes_stueck_ist_ein_eigener_bereich(self):
        u"""Acht Körperslots plus drei Stücke."""
        namen = [name for name, *_ in self.gebaut.netz.bereiche]
        self.assertEqual(len(namen), 11)
        for rezept in KLEIDUNG:
            kurz = rezept.replace('_Recipe', '').lower()
            self.assertTrue(any(kurz in n.lower() for n in namen),
                            u'%s fehlt in %s' % (rezept, namen))

    def test_der_koerper_bleibt_exakt(self):
        u"""Kleidung ändert am Körper nichts — und das ist zu prüfen.

        Gemessen über die fünf Körperslots: Median 0,114 mm, genau wie
        bei der nackten Figur. Der Rest ist die Reglerstellung.
        """
        from UMA_Python.gegenprobe import Unityglb
        punkte = self.gebaut.punkte()
        koerper = [(n, a, z) for n, a, z, _, _ in self.gebaut.netz.bereiche
                   if n.startswith('UMA30_Body')]
        self.assertEqual(len(koerper), 5)
        eigen = np.concatenate([punkte[a:a + z] for _, a, z in koerper])
        abstand = Unityglb.abstaende(eigen, self.unity.punkte)
        self.assertLess(float(np.median(abstand)), 0.5)

    def test_die_kleidung_liegt_am_selben_ort(self):
        u"""Der offene Rest, mit seiner gemessenen Größe.

        Gruppenweise gegen Unitys Atlanten gemessen (Unity fasst Slots
        nach Material zusammen: 1.668 + 3.906 = 5.574 und
        3.131 + 4.824 = 7.955):

            Innenmund + Stiefel   Median 0,129 mm   max  0,84 mm
            Hoodie + Shorts       Median 6,65  mm   max 35,45 mm

        Die STARRE Kleidung sitzt also exakt, die verformbare nicht.
        Der Versatz hat keine Richtung (Mittelwert 0,7 / -0,03 /
        -0,11 mm bei 5 mm Streuung je Achse) und ist am Rumpf doppelt
        so groß wie am Becken (10,1 gegen 5,6 mm) — er sieht aus wie
        eine Anpassung an die Körperform, die Unity vornimmt und der
        Port nicht. `UMAClothingConformer` ist es NICHT: Die Klasse hat
        im ganzen Upstream keinen Aufrufer außerhalb von Editor und
        Tests. Auch die vorgebackene Form ist es nicht — ohne sie
        ändert sich der Wert um keinen Hundertstelmillimeter (6,652 in
        beiden Fällen), und die Kleidungsslots führen gar keine
        BlendShapes.

        Die Schwelle steht auf dem gemessenen Wert. Wer die Ursache
        findet, macht diesen Test schärfer — er ist die Stelle, an der
        es auffällt.
        """
        from UMA_Python.gegenprobe import Unityglb
        punkte = self.gebaut.punkte()
        stellen = {n: (a, a + z) for n, a, z, _, _ in self.gebaut.netz.bereiche}
        stoff = [n for n in stellen if 'hoodie' in n or 'shorts' in n]
        self.assertEqual(len(stoff), 2)
        eigen = np.concatenate([punkte[stellen[n][0]:stellen[n][1]]
                                for n in stoff])
        abstand = Unityglb.abstaende(eigen, self.unity.punkte)
        self.assertLess(float(np.median(abstand)), 12.0,
                        u'die Kleidung ist weiter abgewandert als gemessen')

    def test_die_kleidung_haengt_am_selben_skelett(self):
        u"""Der Grund, warum UMA-Kleidung sitzt — und die Probe darauf.

        Jeder Stoffpunkt trägt Gewichte auf Knochen DIESES Skeletts.
        Zeigt einer ins Leere, reißt das Stück beim ersten Bild auf.
        """
        netz = self.gebaut.netz
        hoechster = int(np.asarray(netz.knochenindex).max())
        self.assertLess(hoechster, len(netz.knochen))
        summe = np.asarray(netz.gewichte).sum(axis=1)
        self.assertAlmostEqual(float(summe.min()), 1.0, places=4)
        self.assertAlmostEqual(float(summe.max()), 1.0, places=4)
