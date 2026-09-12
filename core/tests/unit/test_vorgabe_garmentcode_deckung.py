# -*- coding: utf-8 -*-
u"""Jeder Viewer, der eine Modellvorgabe anzieht, kennt alle drei Listen.

Eine Vorgabe fuehrt je Verfahren eine Liste: `cloth`, `garments` (MakeHuman)
und seit dem 08.09.2026 `garmentcode`. Die dritte fehlte nacheinander in
jedem Viewer — Theatre und BVH Studio am 11.09.2026 („Female1 laedt nicht
die GarmentCode"), die Ergebnisseite am 12.09.2026 („im unteren 3D
Modellbereich werden keine GarmentCode zum Modell geladen"). Die Figur kam
jedes Mal ohne Fehler und ohne Kleid.

Hier steht deshalb die Deckung fest: Wer `garments` aus der Vorgabe liest,
liest auch `garmentcode`, und zwar ueber die gemeinsamen Klassen
(`gemeinsam/garmentcodestueck.js` laedt, `gemeinsam/garmentcodebindung.js`
bindet) — keine dritte Fassung. Und die Ergebnisseite raeumt die Stuecke
dort weg, wo sie die uebrige Kleidung wegraeumt (Vorgabenwechsel,
Koerperwechsel) und blendet sie mit ihr aus.
"""
import io
import os

from django.conf import settings
from django.test import SimpleTestCase


class DieDeckung(SimpleTestCase):

    WURZEL = str(settings.BASE_DIR)
    VIEWER = os.path.join(WURZEL, 'static', 'viewer')
    THEATRE = os.path.join(WURZEL, 'TheatreJS', 'src')

    #: Wer die Vorgabe anzieht — und in welcher Datei die Stuecke geladen werden.
    ANZIEHER = (
        (os.path.join(THEATRE, 'laden', 'vorgabefigur.js'),
         os.path.join(THEATRE, 'laden', 'vorgabefigur.js')),
        (os.path.join(VIEWER, 'bvh_studio', 'spurzubehoer.js'),
         os.path.join(VIEWER, 'bvh_studio', 'spurzubehoer.js')),
        (os.path.join(VIEWER, 'result_character', 'presets.js'),
         os.path.join(VIEWER, 'result_character', 'garmentcode_stuecke.js')),
    )
    #: Wo gebunden wird (das Theatre bindet im Skinner, nicht beim Laden).
    BINDER = (
        os.path.join(THEATRE, 'studio', 'skinner.js'),
        os.path.join(VIEWER, 'bvh_studio', 'spurzubehoer.js'),
        os.path.join(VIEWER, 'result_character', 'garmentcode_stuecke.js'),
    )

    @staticmethod
    def _quelle(pfad):
        with io.open(pfad, encoding='utf-8') as datei:
            return datei.read()

    def test_wer_garments_liest_liest_auch_garmentcode(self):
        for anzieher, lader in self.ANZIEHER:
            with self.subTest(datei=os.path.basename(anzieher)):
                quelle = self._quelle(anzieher)
                self.assertIn('.garments', quelle)
                self.assertIn('.garmentcode', quelle)
                self.assertIn('Garmentcodestueck', self._quelle(lader))

    def test_gebunden_wird_ueberall_mit_derselben_klasse(self):
        for binder in self.BINDER:
            with self.subTest(datei=os.path.basename(binder)):
                self.assertIn('Garmentcodebindung', self._quelle(binder))

    def test_die_ergebnisseite_raeumt_die_stuecke_mit_der_kleidung_weg(self):
        ordner = os.path.join(self.VIEWER, 'result_character')
        presets = self._quelle(os.path.join(ordner, 'presets.js'))
        # Vorgabenwechsel ohne Koerperwechsel: neben removeAllGarments.
        self.assertEqual(presets.count('GarmentcodeStuecke.entfernen()'), 2)
        # Koerperwechsel: das alte Skelett verschwindet, die Stuecke mit ihm.
        self.assertIn('removeAllGarmentcode', self._quelle(
            os.path.join(ordner, 'mesh_loading.js')))
        # Kleidung ausblenden nimmt die Gruppe mit.
        self.assertIn('GarmentcodeStuecke.sichtbar(state.clothesVisible)',
                      self._quelle(os.path.join(ordner, 'knopfleiste.js')))
