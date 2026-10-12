# -*- coding: utf-8 -*-
u"""Blender-Import: die Haut der Figur hinter die Kleidung legen (10.10.2026, Rainy: Haut am Schritt bis 62 mm vor der Hose).

Edgar: „die Haut geht durch die Hose". Gemessen (`ProjektTemp/_wegwerf/blendimport_massstab/rainy_schritt_sicht.py`): von 1.917 nach vorn gerichteten
Hautpunkten am Becken lagen 664 vor der vordersten Hosenfläche; `Blendimportunterkleid` legt sie 3 mm dahinter.

1. Ein Hautpunkt VOR der vordersten Kleiderfläche seiner Spalte geht `LUFT_M` hinter sie — nur in z.
2. Ein Hautpunkt hinter der Fläche bleibt; ohne Kleidung in der Spalte bleibt er; liegt die Fläche mehr als `MAX_M` hinter ihm (Rücken eines Hemds
   über nackter Haut), bleibt er auch.
3. Hat ein Kleid zwei Wände (Vorder- und Rückseite), gilt die vorderste.
4. Der Kasten nimmt nur die Vorderseite am Becken (`kasten`).
5. Der Bericht trennt „davor" (bis `MAX_M`) von „weit".
6. `Blendimportlauf._unterkleid` ist wiederholbar: der Regler eines früheren Laufs (Endung `_unterkleid`) liegt nicht unter der neuen Rechnung, und
   Regler der Nachformung bleiben.

Sabotage: in `verschiebung` `ueber > 0.0` zu `ueber > -1.0` → Fall 2 rot; `MAX_M` auf 1.0 → Fall 2 (Rücken) rot; in `vorderste` `np.maximum.at` zu
`np.minimum.at` → Fall 3 rot. Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage; Gegenprobe an echten Daten:
`ProjektTemp/_wegwerf/blendimport_massstab/unterkleid_offline.py` und `unterkleid_probe.py`.
"""

from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportunterkleid import Blendimportunterkleid as U


def platte(z, halb=1.0):
    u"""Ein Quadrat aus zwei Dreiecken bei `z`, von x, y = −halb … +halb."""
    p = np.array([[-halb, -halb, z], [halb, -halb, z], [halb, halb, z], [-halb, halb, z]], dtype=np.float64)
    return p, np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int64)


class Unterkleid(SimpleTestCase):

    def test_1_haut_vor_dem_stoff_geht_dahinter(self):
        huelle = U.zu_huelle([platte(0.0)])
        haut = np.array([[0.1, 0.2, 0.020]])
        v = U.verschiebung(haut, huelle, np.array([True]))
        self.assertTrue(np.allclose(v[0], [0.0, 0.0, -0.020 - U.LUFT_M]), v)

    def test_2_haut_hinter_dem_stoff_ohne_stoff_und_weit_dahinter_bleibt(self):
        huelle = U.zu_huelle([platte(0.0, halb=0.5)])
        haut = np.array([[0.0, 0.0, -0.010],        # hinter der Fläche
                         [0.9, 0.0, 0.020],         # ohne Stoff in der Spalte
                         [0.1, 0.1, U.MAX_M + 0.05]])        # die Fläche liegt weiter als `MAX_M` dahinter: ein Rücken
        v = U.verschiebung(haut, huelle, np.ones(3, dtype=bool))
        self.assertTrue(np.allclose(v, 0.0), v)

    def test_3_bei_zwei_waenden_gilt_die_vorderste(self):
        vorn, hinten = platte(0.0), platte(-0.004)
        huelle = U.zu_huelle([vorn, hinten])
        self.assertTrue(np.allclose(U.vorderste(huelle, np.array([[0.0, 0.0, 0.05]]), np.array([True])), 0.0))

    def test_4_der_kasten_nimmt_nur_die_vorderseite_am_becken(self):
        punkte = np.array([[0.0, 0.85, 0.08],      # Becken, vorn
                           [0.0, 0.85, -0.08],     # Becken, hinten
                           [0.0, 1.40, 0.08],      # Brust
                           [0.30, 0.85, 0.08]])    # zu weit seitlich
        # „Vorn“ heißt: z über dem Median ALLER Punkte — eine Figur hat Vorder- und Rückseite, darum vier Punkte hinten dazu (sonst liegt der Median auf 0,08).
        hinten = np.tile([0.0, 0.85, -0.08], (4, 1))
        # Höhe 1,75 m, Sohle 0: der Kasten läuft von 0,70 m bis 1,12 m
        gewaehlt = U.kasten(np.vstack([punkte, hinten]), 0.0, 1.75)
        self.assertEqual(gewaehlt.tolist(), [True, False, False, False] + [False] * 4)

    def test_5_der_bericht_trennt_davor_und_weit(self):
        huelle = U.zu_huelle([platte(0.0)])
        haut = np.array([[0.0, 0.0, 0.030], [0.1, 0.0, -0.01], [0.2, 0.0, U.MAX_M + 0.1]])
        bericht = U.sicht(haut, huelle, np.ones(3, dtype=bool))
        self.assertEqual((bericht['davor'], bericht['weit'], bericht['mit_kleidung']), (1, 1, 3))
        self.assertEqual(bericht['davor_max_mm'], 30.0)


class UnterkleidOhneLoch(SimpleTestCase):
    u"""Das Daz-Stück ersetzt die Haut im Loch (11.10.2026): deren Punkte dürfen den Regler nicht bestimmen. Gemessen an „cute girl" (Import 08:45): mit den Lochpunkten schob der Regler die Haut
    bis 33,9 mm zurück (im Loch bis 32 mm) und kippte die Haut rund um den Ring (Knick über die Naht Median 22° statt 9,8°); ohne sie genügten 6,6 mm, mit Nachformung 0,4 sogar 3,6 mm.

    7. `ohne` nimmt Punkte aus der Maske — und `None` lässt sie, wie sie ist; eine zu lange Ausnahmemaske schadet nicht.
    8. Ein ausgenommener Punkt vor dem Stoff bleibt stehen, der daneben geht dahinter.
    9. `formen` reicht `ausnehmen` an die Rechnung und legt den Regler unter der gewünschten Endung ab (der des Imports bleibt unberührt).

    Sabotage (im Kopf, nicht gelaufen): in `ohne` das `~` weglassen → Fall 7 und 8 rot; in `formen` `endung or self.ENDUNG` durch `self.ENDUNG` ersetzen → Fall 9 rot.
    """

    def test_7_ohne_nimmt_punkte_aus_der_maske(self):
        maske = np.array([True, True, False, True])
        self.assertEqual(U.ohne(maske, np.array([False, True, True, False])).tolist(), [True, False, False, True])
        self.assertIs(U.ohne(maske, None), maske)
        self.assertEqual(U.ohne(maske, np.array([True, True, True, True, True, True])).tolist(), [False, False, False, False])

    def test_8_ein_ausgenommener_punkt_vor_dem_stoff_bleibt_stehen(self):
        huelle = U.zu_huelle([platte(0.0)])
        haut = np.array([[0.1, 0.1, 0.020], [-0.1, 0.1, 0.020]])
        maske = U.ohne(np.ones(2, dtype=bool), np.array([False, True]))
        v = U.verschiebung(haut, huelle, maske)
        self.assertTrue(np.allclose(v[0], [0.0, 0.0, -0.020 - U.LUFT_M]))
        self.assertTrue(np.allclose(v[1], 0.0), 'der Punkt im Loch bleibt, obwohl er vor dem Stoff steht')

    def test_9_formen_reicht_die_ausnahme_weiter_und_legt_unter_eigener_endung_ab(self):
        job = mock.Mock()
        job.ergebnis = {'rest': {'regler': 'eigen:k'}}
        u = U(mock.Mock(), job, {'netze': []}, [], 'k')
        ausnehmen = np.array([False, True])
        with mock.patch.object(U, 'feld', return_value=(np.full((2, 3), 0.01), {'vorher': {'davor': 5}})) as feld, \
                mock.patch('Genesis9.eigenmorphe.G9eigenmorphe.vorhanden', return_value=True), \
                mock.patch('Genesis9.eigenmorphe.G9eigenmorphe.ablegen', side_effect=lambda name, *_: 'eigen:' + name) as ablegen:
            bericht = u.formen({'eigen:k_scham': 0.4}, ausnehmen=ausnehmen, endung='_unterkleid_daz')
        feld.assert_called_once_with({'eigen:k_scham': 0.4}, ausnehmen)
        self.assertEqual(ablegen.call_args[0][0], 'k_unterkleid_daz')
        self.assertEqual(bericht['regler'], {'eigen:k_unterkleid_daz': 1.0})


class UnterkleidLauf(SimpleTestCase):

    def test_6_der_lauf_ist_wiederholbar(self):
        from core.dienste.blendimportlauf import Blendimportlauf

        lauf = Blendimportlauf.__new__(Blendimportlauf)
        lauf.stand = {'rollen': [], 'quelle': {'name': 'x'}}
        lauf.ablage, lauf.melden = mock.Mock(), None
        lauf.inventar = lambda: {'netze': []}
        with mock.patch('core.dienste.blendimportunterkleid.Blendimportunterkleid.formen') as formen:
            formen.return_value = {'vorher': {}, 'regler': {'eigen:k_unterkleid': 1.0}}
            frueher = {'regler': {'eigen:k_scham': 1.0, 'eigen:k_unterkleid': 1.0}, 'unterkleid': {'alt': True}}
            neu = lauf._unterkleid(job=None, bericht=frueher)
            formen.assert_called_once_with({'eigen:k_scham': 1.0})          # ohne den eigenen Regler von früher
            self.assertEqual(neu['regler'], {'eigen:k_scham': 1.0, 'eigen:k_unterkleid': 1.0})
            self.assertNotIn('alt', neu['unterkleid'])
            formen.return_value = {'aus': 'keine Haut vor der Kleidung'}   # nichts mehr nötig: der alte Regler verschwindet
            neu = lauf._unterkleid(job=None, bericht=frueher)
            self.assertEqual(neu['regler'], {'eigen:k_scham': 1.0})
