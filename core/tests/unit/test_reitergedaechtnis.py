# -*- coding: utf-8 -*-
u"""Die letzten Einstellungen stehen beim naechsten Aufruf.

AUFTRAG (Edgar, 09.09.2026): „merke dir die letzten Einstellungen auf allen
Tabs, z.B. GarmentCode, so dass sie beim naechsten Aufruf angeklickt sind."

Die REGELN (welches Feld gemerkt werden darf) pruefen
`test_js_gedaechtniswahl` in node. Hier steht die Verdrahtung — die
haeufigere halbe Sache: ein Modul, das da ist, aber niemand ruft. Genau
dieser Fehler steckte am selben Tag in `szene_dialoge.js`
(`GarmentcodeAblage` war importiert, aber der Dateiweg baute die Figur
selbst).

Gemessen im Browser (09.09.2026): Reiter GarmentCode, Vorlage „hose", drei
Regler von Hand, ein Preset angehakt — nach `location.reload()` stand alles
wieder: Reiter offen, Vorlage gesetzt, sieben Reglerwerte im Modul UND an
den Schiebern, das Haekchen an. Und im Serverlog KEIN Bau: Der Start soll
nichts drapieren.
"""
import io

from django.conf import settings
from django.test import SimpleTestCase


def _quelle(pfad):
    return io.open(settings.BASE_DIR / 'static' / 'viewer' / pfad,
                   encoding='utf-8').read()


class ReitergedaechtnisTest(SimpleTestCase):

    databases = []

    def test_der_start_holt_die_einstellungen(self):
        quelle = _quelle('scene/szenenaufbau.js')
        self.assertIn('Reitergedaechtnis.starten()', quelle)
        self.assertIn('Reitergedaechtnis.letzterReiter()', quelle)
        # In der Startsequenz, nicht im Verdrahten: Die Reiterfreigabe haengt
        # daran, dass eine Figur steht.
        self.assertIn('_reitergedaechtnis()', quelle)
        self.assertIn('Reiterfreigabe.frei(', quelle)

    def test_der_reiter_wird_beim_umschalten_gemerkt(self):
        quelle = _quelle('scene/properties.js')
        self.assertIn('Reitergedaechtnis.reiterMerken(', quelle)
        # Neben `Figurmerker`, nicht statt ihm: der eine liegt im
        # sessionStorage (diese Sitzung), der andere im localStorage.
        self.assertIn('Figurmerker.tabMerken(', quelle)

    def test_die_ablage_ist_der_localstorage(self):
        u"""`sessionStorage` waere beim naechsten Fenster leer."""
        quelle = _quelle('scene/reitergedaechtnis.js')
        self.assertIn('localStorage.getItem(', quelle)
        self.assertIn('localStorage.setItem(', quelle)
        # Mit Punkt: ein ZUGRIFF. Im Kommentar steht das Wort mit Absicht —
        # dort wird begruendet, warum `Figurmerker` die andere Ablage nimmt.
        self.assertNotIn('sessionStorage.', quelle)

    def test_jeder_zugriff_ist_umschlossen(self):
        u"""Im privaten Fenster wirft schon das Lesen."""
        quelle = _quelle('scene/reitergedaechtnis.js')
        self.assertEqual(quelle.count('try {'), quelle.count('} catch'))
        self.assertGreaterEqual(quelle.count('try {'), 2)

    def test_die_kennung_ist_nur_die_id(self):
        u"""Kein `data-pfad` — sonst zwei Buchfuehrungen fuer eine Zahl.

        Die GarmentCode-Regler fuehrt `garmentcodeRegler` in `this.werte`,
        und genau die gehen an den Server. Ein zweiter Satz aus dem DOM
        laeuft auseinander, sobald ein Preset oder ein Vorlagenwechsel nur
        eine Seite anfasst.
        """
        quelle = _quelle('scene/reitergedaechtnis.js')
        rumpf = quelle.split('static kennung(feld) {')[1].split('}')[0]
        self.assertIn('feld.id', rumpf)
        self.assertNotIn('data-pfad', rumpf)
        self.assertNotIn('dataset', rumpf)

    def test_garmentcode_haengt_am_gedaechtnis(self):
        quelle = _quelle('scene/garmentcode_regler.js')
        self.assertIn('Garmentcodegedaechtnis.anwenden(this, vorlage)', quelle)
        self.assertIn('Garmentcodegedaechtnis.merken(this)', quelle)
        # Gemerkt wird bei Hand-Aenderung UND bei einem Preset.
        for name in ('vonHand(pfad) {', 'mehrereSetzen(werte) {'):
            rumpf = quelle.split(name)[1].split('\n    }')[0]
            self.assertIn('merken()', rumpf, name)

    def test_das_wiederherstellen_baut_nicht(self):
        u"""Beim Seitenstart gibt es keinen Schnitt, auf den ein Bau zeigt."""
        quelle = _quelle('scene/garmentcode_gedaechtnis.js')
        rumpf = quelle.split('static anwenden(')[1]
        self.assertNotIn('GarmentcodeLive', rumpf)
        self.assertNotIn('mehrereSetzen', rumpf)

    def test_nur_pfade_dieser_vorlage_werden_gesetzt(self):
        u"""`sleeve.cuff.cuff_len` gibt es bei einem Rock nicht."""
        quelle = _quelle('scene/garmentcode_gedaechtnis.js')
        self.assertIn('in regler.vorgaben', quelle)

    def test_die_haekchen_kommen_mit(self):
        u"""„Angeklickt" ist woertlich gemeint."""
        self.assertIn('garmentcodePreset.anhaken(',
                      _quelle('scene/garmentcode_gedaechtnis.js'))
        preset = _quelle('scene/garmentcode_preset.js')
        self.assertIn('anhaken(namen) {', preset)
        self.assertIn('aktiveListe() {', preset)
