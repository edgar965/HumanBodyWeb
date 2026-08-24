# -*- coding: utf-8 -*-
"""Wächter für `Netzantwort` — die Typen sind der Vertrag mit dem Browser.

WARUM (17.08.2026): Die base64-Kodierung stand sechzehnmal im Projekt. Beim
Zusammenlegen ist der gefährliche Teil nicht das base64, sondern der DATENTYP:
`viewer/gemeinsam/kodierung.js` liest `vertices` als `Float32Array` und `faces`
als `Uint32Array`. Ein Feld, das als float64 herausgeht, ist doppelt so groß und
wird auf der Gegenseite falsch gelesen — jeder zweite Wert wird zum Exponenten
des Nachbarn. Das Modell sieht zerrissen aus, und niemand vermutet einen Typ.

Deshalb prüft dieser Test die Bytes, nicht nur die Schlüssel.
"""

import base64

import numpy as np

from django.test import SimpleTestCase

from core.daten.netzantwort import Netzantwort


class NetzantwortTest(SimpleTestCase):

    def zurueck(self, text, typ):
        return np.frombuffer(base64.b64decode(text), dtype=typ)

    def test_punkte_kommen_als_float32_zurueck(self):
        punkte = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], dtype=np.float64)
        antwort = Netzantwort.aus(punkte)
        self.assertEqual(antwort['vertex_count'], 2)
        werte = self.zurueck(antwort['vertices'], np.float32)
        self.assertEqual(len(werte), 6)
        self.assertEqual(list(werte), [1, 2, 3, 4, 5, 6])

    def test_float64_wird_nicht_durchgelassen(self):
        """Der eigentliche Fehler: doppelte Größe, falsch gelesen."""
        punkte = np.zeros((100, 3), dtype=np.float64)
        roh = base64.b64decode(Netzantwort.aus(punkte)['vertices'])
        self.assertEqual(len(roh), 100 * 3 * 4, '4 Byte je Wert, nicht 8')

    def test_dreiecke_als_uint32(self):
        flaechen = np.array([[0, 1, 2], [2, 3, 0]], dtype=np.int64)
        antwort = Netzantwort.aus(np.zeros((4, 3)), faces=flaechen)
        self.assertEqual(antwort['face_count'], 2)
        self.assertEqual(list(self.zurueck(antwort['faces'], np.uint32)),
                         [0, 1, 2, 2, 3, 0])

    def test_nicht_zusammenhaengendes_feld(self):
        """Nach `faces[:, [0, 2, 1]]` ist das Feld nicht mehr C-zusammenhängend.

        `tobytes()` liefert dort andere Bytes als erwartet, wenn niemand
        `ascontiguousarray` davorsetzt — genau die Umsortierung macht
        `api/netz.py` beim Zerlegen der Vierecke in Dreiecke.
        """
        vierecke = np.array([[0, 1, 2, 3], [4, 5, 6, 7]], dtype=np.uint32)
        gedreht = vierecke[:, [0, 2, 1]]
        self.assertFalse(gedreht.flags['C_CONTIGUOUS'])
        antwort = Netzantwort.aus(np.zeros((8, 3)), faces=gedreht)
        self.assertEqual(list(self.zurueck(antwort['faces'], np.uint32)),
                         [0, 2, 1, 4, 6, 5])

    def test_normalen_und_uvs_optional(self):
        antwort = Netzantwort.aus(np.zeros((2, 3)))
        self.assertNotIn('normals', antwort)
        self.assertNotIn('uvs', antwort)
        self.assertNotIn('faces', antwort)
        self.assertNotIn('face_count', antwort)

    def test_weitere_felder_kommen_mit(self):
        """Zahlenfelder werden kodiert, alles andere geht unverändert durch."""
        antwort = Netzantwort.aus(
            np.zeros((2, 3)),
            skin_weights=np.array([[0.5, 0.5, 0, 0]], dtype=np.float64),
            groups=[{'start': 0, 'count': 6, 'materialIndex': 0}],
            material_names=['HB_Skin'])
        self.assertEqual(list(self.zurueck(antwort['skin_weights'], np.float32)),
                         [0.5, 0.5, 0.0, 0.0])
        self.assertEqual(antwort['groups'][0]['count'], 6)
        self.assertEqual(antwort['material_names'], ['HB_Skin'])

    def test_face_count_zaehlt_dreiecke_nicht_vierecke(self):
        """In zwei der sechzehn Fassungen zählte `face_count` die VIERECKE,
        obwohl `faces` schon zerlegte Dreiecke enthielt."""
        dreiecke = np.zeros((12, 3), dtype=np.uint32)
        self.assertEqual(
            Netzantwort.aus(np.zeros((4, 3)), faces=dreiecke)['face_count'], 12)
