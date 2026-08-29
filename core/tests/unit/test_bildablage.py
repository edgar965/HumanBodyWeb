# -*- coding: utf-8 -*-
u"""`Bildablage` — die drei Fälle einer Data-URL, und wohin die Datei kommt.

WARUM ES DIESE TESTS ERST JETZT GIBT (29.08.2026, Befund `doppelcode`)
======================================================================
`Fotoabgleich.projektion_sichern` und `Fotoauftraege.bild_sichern` trugen
dieselben zehn Zeilen: Data-URL zerlegen, zwei Fehlerfälle beantworten,
Datei ablegen. Sie liegen jetzt in `Bildablage.sichern_aus_dataurl`.

Für den Prüfling gab es keinen einzigen Fall — auch nicht für
`bytes_aus_dataurl`, dessen Kopf ausdrücklich DREI Rückgaben unterscheidet:

    b''    — es kam gar kein Bild mit   -> 400 „No image data"
    None   — base64 kaputt              -> 400 „Invalid base64"
    bytes  — in Ordnung

Die beiden leeren Fälle sehen in Python gleich falsch aus (`not roh` ist für
beide wahr), und wer sie zusammenzieht, bekommt für ein kaputtes Bild die
Meldung „kein Bild" — die auf einen ganz anderen Fehler zeigt.

GESCHRIEBEN WIRD IN EIN WEGWERF-VERZEICHNIS: `Bildablage` legt unter
`BASE_DIR/media/photo_analysis/` ab. Ein Test, der dorthin schreibt, hinterlässt
Dateien in den Produktivdaten — genau die Sorte Rest, von der am 28.08.2026
1.374 Stück in `media/scene_objects/` gefunden wurden.
"""
import base64
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from core.dienste.bildablage import Bildablage

#: Ein winziges gültiges JPEG-Fragment — der Inhalt ist gleichgültig, nur
#: dass es dieselben Bytes zurückgibt.
ROH = b'\xff\xd8\xff\xe0 Testbild'
DATAURL = 'data:image/jpeg;base64,' + base64.b64encode(ROH).decode()


class BytesAusDataurlTest(SimpleTestCase):
    """Die drei Rückgaben — einzeln festgenagelt."""

    def test_gueltige_dataurl_gibt_die_bytes(self):
        self.assertEqual(ROH, Bildablage.bytes_aus_dataurl(DATAURL))

    def test_auch_ohne_vorspann(self):
        u"""Manche Aufrufer schicken nur den Base64-Teil."""
        self.assertEqual(ROH, Bildablage.bytes_aus_dataurl(
            base64.b64encode(ROH).decode()))

    def test_leer_ist_nicht_kaputt(self):
        u"""`b''` und `None` sind ZWEI Fälle, keiner davon der andere."""
        self.assertEqual(b'', Bildablage.bytes_aus_dataurl(''))
        self.assertEqual(b'', Bildablage.bytes_aus_dataurl(None))

    def test_kaputte_base64_gibt_none(self):
        u"""`None` gibt es nur bei einer Laengen- oder Fuellzeichen-Panne."""
        self.assertIsNone(Bildablage.bytes_aus_dataurl('data:,QQ'))
        self.assertIsNone(Bildablage.bytes_aus_dataurl('data:,AAAAA'))

    def test_fremdzeichen_werden_still_verschluckt(self):
        u"""GEMESSEN, nicht vermutet (29.08.2026): `base64.b64decode` ohne
        `validate=True` wirft fremde Zeichen weg, statt zu werfen.

            b64decode('%%%')  -> b''      (kein Fehler)
            b64decode('QQ')   -> wirft    (Incorrect padding)

        Ein Bild aus lauter Fremdzeichen kommt also als „No image data" an,
        nicht als „Invalid base64". Beides ist eine 400 mit einem ehrlichen
        Text — aber wer den Fehlertext liest, um die Ursache zu suchen, wird
        in die falsche Richtung geschickt. Deshalb steht es hier fest."""
        self.assertEqual(b'', Bildablage.bytes_aus_dataurl('data:,%%%'))


class SichernAusDataurlTest(SimpleTestCase):
    u"""Der Weg, den beide Endpunkte gehen — in einem Wegwerf-Verzeichnis."""

    def setUp(self):
        # `dir=` ist Pflicht: sonst System-Temp auf C: (Befund `lehren-treue`).
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        self.ordner = tempfile.mkdtemp(prefix='bildablage_', dir=str(basis))
        self.addCleanup(shutil.rmtree, self.ordner, True)

    def _ablage(self, unterordner='pruefung'):
        return Bildablage(unterordner)

    def test_gueltiges_bild_landet_auf_der_platte(self):
        with override_settings(BASE_DIR=self.ordner):
            pfad, fehler = self._ablage().sichern_aus_dataurl('abc', DATAURL)
        self.assertIsNone(fehler)
        self.assertEqual('media/photo_analysis/pruefung/abc.jpg', pfad)
        voll = os.path.join(self.ordner, *pfad.split('/'))
        self.assertTrue(os.path.isfile(voll), 'Datei nicht geschrieben')
        with open(voll, 'rb') as datei:
            self.assertEqual(ROH, datei.read())

    def test_kein_bild_meldet_kein_bild(self):
        with override_settings(BASE_DIR=self.ordner):
            pfad, fehler = self._ablage().sichern_aus_dataurl('abc', '')
        self.assertIsNone(pfad)
        self.assertEqual('No image data', fehler)

    def test_kaputtes_bild_meldet_kaputt(self):
        u"""Der Unterschied, auf den es ankommt: NICHT „No image data"."""
        with override_settings(BASE_DIR=self.ordner):
            pfad, fehler = self._ablage().sichern_aus_dataurl('abc', 'data:,QQ')
        self.assertIsNone(pfad)
        self.assertEqual('Invalid base64', fehler)

    def test_im_fehlerfall_entsteht_keine_datei(self):
        u"""Eine leere `.jpg` wäre schlimmer als keine: Sie sieht aus wie ein
        Ergebnis und lässt sich später nicht mehr von einem echten Bild
        unterscheiden."""
        with override_settings(BASE_DIR=self.ordner):
            self._ablage().sichern_aus_dataurl('leer', '')
            self._ablage().sichern_aus_dataurl('kaputt', 'data:,QQ')
        ordner = os.path.join(self.ordner, 'media', 'photo_analysis', 'pruefung')
        vorhanden = os.listdir(ordner) if os.path.isdir(ordner) else []
        self.assertEqual([], vorhanden, 'Datei trotz Fehler geschrieben')

    def test_der_unterordner_steht_im_pfad(self):
        u"""Die beiden Endpunkte unterscheiden sich NUR darin."""
        with override_settings(BASE_DIR=self.ordner):
            a, _ = Bildablage('silhouettes').sichern_aus_dataurl('x', DATAURL)
            b, _ = Bildablage('screenshots').sichern_aus_dataurl('x', DATAURL)
        self.assertEqual('media/photo_analysis/silhouettes/x.jpg', a)
        self.assertEqual('media/photo_analysis/screenshots/x.jpg', b)


if __name__ == '__main__':          # pragma: no cover
    unittest.main()
