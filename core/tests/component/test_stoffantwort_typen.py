# -*- coding: utf-8 -*-
"""Die Binärtypen der Kleidungs-Antworten — der Vertrag mit Three.js.

DER FEHLER, DEN DIESER TEST FESTNAGELT (gefunden 17.08.2026)
===========================================================
`/api/character/garment/fit/` kodierte **alle** Felder über einen Helfer, der
`skin_weights` hieß und deshalb `float32` schrieb — auch die Dreiecksindizes.
Alle sieben Leser im Frontend lesen sie aber mit `base64ToUint32`
(`kleideranpassung.js`, `garment.js`, `cloth_garments.js`,
`charakter_zubehoer.js`, `prop_garments.js`, `spurzubehoer.js`, `smpl.js`).

Gemessen an der echten Antwort für `accessories/jaldmic_stockings`
(5.402 Punkte, 10.425 Dreiecke):

    als uint32 gelesen:  1110441984, 1152057344, …   (max weit über 5.402)
    gemeint war:          44, 1368, 1364, …

Die Bytes waren die float32-Darstellung derselben Zahlen (44.0 -> 0x42300000).
Three.js bekam damit Indizes weit außerhalb des Netzes — die Kleidung konnte
nicht gezeichnet werden. Kein Fehler im Log, kein Statuscode ≠ 200.

Geprüft wird deshalb nicht „gibt es ein Feld `faces`", sondern: **Ergeben die
Bytes als uint32 gelesen Indizes, die im Netz liegen?**
"""

import base64

import numpy as np
from django.test import TestCase

from core.daten.stoffantwort import Stoffantwort


class StoffantwortTypenTest(TestCase):

    def antwort(self):
        ergebnis = {
            'vertices': np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.]],
                                 dtype=np.float32),
            'faces': np.array([[0, 1, 2]], dtype=np.uint32),
            'normals': np.zeros((3, 3), dtype=np.float32),
            'color': [0.3, 0.4, 0.5],
        }
        return Stoffantwort.aus(ergebnis, None, 'female')

    def test_dreiecke_kommen_als_uint32(self):
        roh = base64.b64decode(self.antwort()['faces'])
        self.assertEqual(len(roh), 3 * 4, '4 Byte je Index')
        self.assertEqual(list(np.frombuffer(roh, dtype=np.uint32)), [0, 1, 2])

    def test_punkte_und_normalen_kommen_als_float32(self):
        antwort = self.antwort()
        for feld, zahl in (('vertices', 9), ('normals', 9)):
            werte = np.frombuffer(base64.b64decode(antwort[feld]),
                                  dtype=np.float32)
            self.assertEqual(len(werte), zahl, feld)

    def test_zaehler_kommen_aus_den_feldern(self):
        antwort = self.antwort()
        self.assertEqual(antwort['vertex_count'], 3)
        self.assertEqual(antwort['face_count'], 1)

    def test_ohne_koerperpunkte_keine_gewichte(self):
        """Kein stilles Nullgewicht: Ohne Körper gibt es keine Zuordnung."""
        antwort = self.antwort()
        self.assertNotIn('skin_indices', antwort)


class AnpassungsantwortTypenTest(TestCase):
    """Dieselbe Prüfung für `Kleidungsanpassung.als_antwort` — dort war der Fehler."""

    def antwort(self):
        from core.daten.anpassungsergebnis import Anpassungsergebnis
        from core.daten.koerperzustand import Koerperzustand
        from core.dienste.kleidungsanpassung import Kleidungsanpassung

        class VorlageAttrappe:
            name = 'Probe'
            source = ''
            vertices = None
            faces = None

        class ReglerAttrappe:
            farbe = (0.3, 0.4, 0.5)

        anpassung = Kleidungsanpassung(
            VorlageAttrappe(),
            Koerperzustand(None, 'female', None, None, 'Female_Caucasian'))
        anpassung.ergebnis = Anpassungsergebnis.aus_dict({
            'vertices': np.zeros((3, 3), dtype=np.float32),
            'faces': np.array([[0, 1, 2]], dtype=np.uint32),
            'normals': np.zeros((3, 3), dtype=np.float32),
        })
        return anpassung.als_antwort('tops/probe', ReglerAttrappe())

    def test_dreiecke_kommen_als_uint32(self):
        roh = base64.b64decode(self.antwort()['faces'])
        self.assertEqual(len(roh), 3 * 4)
        self.assertEqual(list(np.frombuffer(roh, dtype=np.uint32)), [0, 1, 2])

    def test_grosse_indexe_bleiben_lesbar(self):
        """float32 kann ab 2^24 nicht mehr jede ganze Zahl darstellen.

        Ein Netz mit 20 Millionen Punkten ist selten — aber genau daran fällt
        eine falsche Breite auch dann auf, wenn die Zahlen klein aussehen.
        """
        gross = np.array([[16777217, 16777219, 16777221]], dtype=np.uint32)
        kodiert = Stoffantwort.aus(
            {'vertices': np.zeros((3, 3), dtype=np.float32), 'faces': gross,
             'normals': np.zeros((3, 3), dtype=np.float32)},
            None, 'female')['faces']
        gelesen = np.frombuffer(base64.b64decode(kodiert), dtype=np.uint32)
        self.assertEqual(list(gelesen), [16777217, 16777219, 16777221])
