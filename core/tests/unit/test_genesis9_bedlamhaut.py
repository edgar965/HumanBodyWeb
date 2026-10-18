# -*- coding: utf-8 -*-
u"""BEDLAM-Häute auf Genesis 9 (`G9bedlamhaut`, `G9bedlamabbildung`, 17.10.2026) — Kunstbilder, keine Texturen, keine Abbildung. Geschrieben, nicht gelaufen.

Edgar, 17.10.2026: „mach alles was offen ist" (Tabelle 12 in `genesis9-alter.md`).

1. Die aufgemalte Unterwäsche der Fotos (olivgrün bei den Frauen: Farbe (123, 117, 77); grau bei den Männern) wird aus den Körperkacheln genommen und mit Haut aus der Umgebung gefüllt; Haut weit
   weg davon bleibt, wie sie war; ohne solche Pixel kommt dasselbe Bild zurück.
2. Die Kopfkachel behält ihr Foto (Augen, Zähne, Haar sehen „grau" aus): `_bauen` ruft die Retusche nur für andere Kacheln — als Quelltext geprüft.
3. Schlüssel: nur `skin_<f|m>_<gruppe>_<nr>_ALB`; der Präfix `bedlam:` kennzeichnet den Hautsatz; ein fremder Schlüssel ergibt `{}`.
4. Ohne Abbildung oder Ordner gibt es keine Hautsätze in der Auswahl.
5. Der Haken im Hautkatalog: ein eingetragener Anbieter erscheint in `hautpresets()` und liefert `haut(preset)` für seine Kennungen; ein anderer Preset bleibt beim alten Weg.
6. Der Dateiname einer fertigen Kachel trägt die Fassung (`f<Fassung>_<Kachel>.jpg`), der der Abbildung ebenso (`artefakte-benennen.md`).

Sabotage-Gegenprobe (nicht gefahren): in `ohne_unterwaesche` die Grau-Bedingung streichen → Fall 1 (grau) rot; die Schlüsselprüfung streichen → Fall 3 rot; `anbieten` nicht in `haut` abfragen → Fall 5 rot.
"""
from pathlib import Path
from unittest import mock

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase
from Genesis9.hautpresets import G9hautpresets

from core.dienste.g9bedlamabbildung import G9bedlamabbildung
from core.dienste.g9bedlamhaut import G9bedlamhaut

HAUT = (230, 180, 150)
OLIV = (123, 117, 77)
GRAU = (110, 110, 110)


def bild(farbe, groesse=64):
    b = np.zeros((groesse, groesse, 3), dtype=np.uint8)
    b[:] = HAUT
    b[24:40, 24:40] = farbe
    return b


class UnterwaescheTest(SimpleTestCase):
    databases = set()

    def pruefen(self, farbe):
        aus = G9bedlamhaut.ohne_unterwaesche(bild(farbe))
        mitte = aus[32, 32].astype(int)
        self.assertLess(abs(int(mitte[0]) - HAUT[0]), 25, 'rot in der Mitte des Flecks wieder Haut: %s' % mitte)
        self.assertLess(abs(int(mitte[2]) - HAUT[2]), 25, 'blau in der Mitte des Flecks wieder Haut: %s' % mitte)
        self.assertEqual(aus[2, 2].tolist(), list(HAUT), 'Haut weit weg bleibt unverändert')

    def test_1_olivgruen_wird_haut(self):
        self.pruefen(OLIV)

    def test_1b_grau_wird_haut(self):
        self.pruefen(GRAU)

    def test_1c_ohne_unterwaesche_dasselbe_bild(self):
        glatt = np.full((32, 32, 3), HAUT, dtype=np.uint8)
        self.assertIs(G9bedlamhaut.ohne_unterwaesche(glatt), glatt)

    def test_2_kopfkachel_ohne_retusche(self):
        quelle = Path(settings.BASE_DIR) / 'core' / 'dienste' / 'g9bedlamhaut.py'
        text = quelle.read_text(encoding='utf-8')
        self.assertIn('if kachel != cls.KOPFKACHEL:', text)
        self.assertEqual(G9bedlamhaut.KOPFKACHEL, 1001)


class SchluesselTest(SimpleTestCase):
    databases = set()

    def test_3_schluessel_praefix_und_fremde(self):
        self.assertTrue(G9bedlamhaut.gehoert('bedlam:skin_f_white_01_ALB'))
        self.assertFalse(G9bedlamhaut.gehoert('G9 Feminine Skin 01 MAT'))
        self.assertTrue(G9bedlamhaut._SCHLUESSEL.match('skin_m_seasian_12_ALB'))
        self.assertFalse(G9bedlamhaut._SCHLUESSEL.match('../../etc/passwd'))
        self.assertFalse(G9bedlamhaut._SCHLUESSEL.match('skin_f_white_01_ALB.png'))
        self.assertEqual(G9bedlamhaut._geschlecht('skin_m_white_01_ALB'), 'male')
        self.assertEqual(G9bedlamhaut._geschlecht('skin_f_white_01_ALB'), 'female')
        with mock.patch.object(G9bedlamhaut, 'verfuegbar', return_value=True):
            self.assertEqual(G9bedlamhaut.bilder('bedlam:../../geheim'), {}, 'kein Dateiname aus der Anfrage')

    def test_4_ohne_abbildung_keine_haeute(self):
        with mock.patch.object(G9bedlamabbildung, 'vorhanden', return_value=False):
            self.assertEqual(G9bedlamhaut.praesets(), [])
            self.assertEqual(G9bedlamhaut.bilder('bedlam:skin_f_white_01_ALB'), {})

    def test_6_fassung_im_dateinamen(self):
        self.assertIn('v%d' % G9bedlamabbildung.FASSUNG, G9bedlamabbildung.pfad().name)
        self.assertIn(str(G9bedlamabbildung.SEITE), G9bedlamabbildung.pfad().name)
        text = (Path(settings.BASE_DIR) / 'core' / 'dienste' / 'g9bedlamhaut.py').read_text(encoding='utf-8')
        self.assertIn("'f%d_%d.jpg' % (cls.FASSUNG, k)", text)


class AnbieterTest(SimpleTestCase):
    databases = set()

    def test_5_anbieter_im_hautkatalog(self):
        class Probe:
            @staticmethod
            def praesets():
                return [{'id': 'probe:eins', 'name': 'Probe', 'geschlecht': '', 'vorschau': False}]

            @staticmethod
            def gehoert(preset):
                return str(preset).startswith('probe:')

            @staticmethod
            def bilder(preset):
                return {'Head': {'albedo': 'x.jpg'}}

        G9hautpresets.anbieten(Probe)
        G9hautpresets.anbieten(Probe)                       # Wiederholung ist harmlos
        try:
            self.assertEqual(G9hautpresets.ANBIETER.count(Probe), 1)
            self.assertEqual(G9hautpresets.haut('probe:eins'), {'Head': {'albedo': 'x.jpg'}})
            with mock.patch.object(G9hautpresets, 'presetordner') as ordner:
                ordner.return_value = Path('gibt_es_nicht')
                with mock.patch('Genesis9.hautwahl.G9hautwahl.katalog', return_value={}):
                    self.assertIn('probe:eins', [e['id'] for e in G9hautpresets.hautpresets()])
            self.assertEqual(G9hautpresets.haut('G9 gibt es nicht MAT'), {}, 'ein anderer Preset bleibt beim alten Weg')
        finally:
            G9hautpresets.ANBIETER.remove(Probe)
