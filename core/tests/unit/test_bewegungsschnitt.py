# -*- coding: utf-8 -*-
"""`Bewegungsschnitt` — eine Bewegung auf n Bilder zu 30 je Sekunde nach ihren Zeiten (01.11.2026, Edgar zu `Königin1_render.mp4`: „warum läuft das video so langsm?“).

Kunstbewegungen: je Bild ein Knochen mit der Bildnummer als Quaternion-x und eine Wurzellage mit der Bildnummer als x — so verrät das geschriebene Bild, aus welchem Bild der
Quelle es stammt. DanceKurz kam mit 1004 Bildern zu 60 je Sekunde; der alte Schnitt nahm die ersten n Bilder und gab ihnen 30er-Zeiten (halbe Geschwindigkeit).

Geschrieben am 01.11.2026, nicht gelaufen; keine Sabotage-Gegenprobe.
"""

import json
from pathlib import Path

import numpy as np
from django.test import SimpleTestCase

from core.dienste.bewegungsschnitt import Bewegungsschnitt

from ._pruefablage import Pruefablage


class BewegungsschnittTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _bewegung(anzahl, fps, zeiten=True):
        d = {'name': 'kunst', 'frame_count': anzahl,
             'tracks': {'hip': [w for i in range(anzahl) for w in (float(i), 0.0, 0.0, 1.0)]},
             'position_track': {'bone': 'hip', 'values': [w for i in range(anzahl) for w in (float(i), 0.0, 0.0)]}}
        if zeiten:
            d['times'] = [i / fps for i in range(anzahl)]
        return d

    def test_zeiten_aus_times_sonst_dreissig_je_sekunde(self):
        np.testing.assert_allclose(Bewegungsschnitt.zeiten(self._bewegung(5, 60)), np.arange(5) / 60)
        np.testing.assert_allclose(Bewegungsschnitt.zeiten(self._bewegung(5, 60, zeiten=False)), np.arange(5) / 30)
        falsch = dict(self._bewegung(5, 60), times=[0.0, 0.1])            # Zeiten passen nicht zur Bildzahl
        np.testing.assert_allclose(Bewegungsschnitt.zeiten(falsch), np.arange(5) / 30)

    def test_bilder_bis_zum_ende_der_bewegung(self):
        tanz = self._bewegung(1004, 60)                                   # DanceKurz: 16,73 s
        self.assertEqual(Bewegungsschnitt.bilder(tanz, float('inf')), 502)
        self.assertEqual(Bewegungsschnitt.bilder(tanz, 1.0), 30)
        self.assertEqual(Bewegungsschnitt.bilder(tanz, 0.0), 2)           # mindestens zwei Bilder
        self.assertEqual(Bewegungsschnitt.bilder(self._bewegung(10, 30), 60.0), 10)

    def test_auswahl_sechzig_nimmt_jedes_zweite(self):
        np.testing.assert_array_equal(Bewegungsschnitt.auswahl(self._bewegung(1004, 60), 502), np.arange(502) * 2)

    def test_auswahl_dreissig_bleibt_gleich(self):
        np.testing.assert_array_equal(Bewegungsschnitt.auswahl(self._bewegung(40, 30), 40), np.arange(40))

    def test_auswahl_nimmt_den_naechsten_zeitpunkt(self):
        j = Bewegungsschnitt.auswahl(self._bewegung(50, 24), 10)          # 24 je Sekunde: t = i / 30 liegt zwischen zwei Bildern
        soll = [int(np.argmin(np.abs(np.arange(50) / 24 - i / 30))) for i in range(10)]
        np.testing.assert_array_equal(j, soll)

    def test_schreiben_nimmt_die_bilder_der_auswahl(self):
        d = self._bewegung(120, 60)
        with Pruefablage.ordner('bewegungsschnitt_') as ordner:
            ziel = Path(ordner) / 'neu' / 'bewegung.json'                 # der Ordner fehlt noch
            Bewegungsschnitt.schreiben(d, ziel, 30)
            neu = json.loads(ziel.read_text(encoding='utf-8'))
        self.assertEqual(neu['frame_count'], 30)
        self.assertAlmostEqual(neu['duration'], 1.0)
        np.testing.assert_allclose(neu['times'], np.arange(30) / 30, atol=1e-6)
        q = np.asarray(neu['tracks']['hip']).reshape(-1, 4)
        np.testing.assert_array_equal(q[:, 0], np.arange(30) * 2)
        lage = np.asarray(neu['position_track']['values']).reshape(-1, 3)
        np.testing.assert_array_equal(lage[:, 0], np.arange(30) * 2)
        self.assertEqual(neu['position_track']['bone'], 'hip')
        self.assertEqual(neu['name'], 'kunst')                            # übrige Felder bleiben
        self.assertEqual(len(d['times']), 120)                            # die Quelle bleibt unverändert

    def test_schreiben_ohne_wurzellage(self):
        d = self._bewegung(10, 30)
        del d['position_track']
        with Pruefablage.ordner('bewegungsschnitt_') as ordner:
            ziel = Path(ordner) / 'bewegung.json'
            Bewegungsschnitt.schreiben(d, ziel, 5)
            neu = json.loads(ziel.read_text(encoding='utf-8'))
        self.assertNotIn('position_track', neu)
        self.assertEqual(len(neu['tracks']['hip']), 20)
