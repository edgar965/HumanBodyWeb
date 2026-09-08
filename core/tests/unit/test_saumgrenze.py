# -*- coding: utf-8 -*-
u"""Der Saum muss ueber die Huefte passen — die Baendigung von `shirt.flare`.

Edgar, 08.09.2026, mit Bild: „warum ist dieser Kaputte Bereich bei T-Shirt
mit so vielen Falten?? ich hatte eng anliegend gewaehlt".

Gemessen auf seiner Figur (bust 88,7 · hips 97,9), Knickflaechen im 10-cm-Band
ueber dem Saum: flare 0,70 -> 5,03 %, flare 1,10 (= hips/bust) -> 0,03 %.
Auf `mean_all` kostet die Grenze nichts (8,7 mm Hautabstand mit und ohne).
Rohwerte: `Assets/GarmentCode/test/SMPL_local/messung_flare_grenze.yaml`.
"""
import sys

from django.conf import settings
from django.test import SimpleTestCase

if str(settings.ASSETS_ROOT) not in sys.path:      # pragma: no cover
    sys.path.insert(0, str(settings.ASSETS_ROOT))

from GarmentCode.saumgrenze import Saumgrenze                  # noqa: E402

#: Die Figur aus dem Befund.
FIGUR = {'bust': 88.66, 'hips': 97.88}


class SaumgrenzeTest(SimpleTestCase):

    def test_zu_enger_saum_wird_gehoben(self):
        regler, hinweise = Saumgrenze.baendigen(
            {'shirt.width': 1.0, 'shirt.flare': 0.7}, FIGUR)
        self.assertGreater(regler['shirt.flare'], 1.10)
        self.assertLess(regler['shirt.flare'], 1.11)
        self.assertEqual(len(hinweise), 1)

    def test_weiter_saum_bleibt_unberuehrt(self):
        u"""Nur nach unten begrenzt — wer weit will, bekommt weit."""
        werte = {'shirt.width': 1.0, 'shirt.flare': 1.6}
        regler, hinweise = Saumgrenze.baendigen(werte, FIGUR)
        self.assertEqual(regler['shirt.flare'], 1.6)
        self.assertEqual(hinweise, [])

    def test_width_geht_in_die_rechnung_ein(self):
        u"""Ein weiteres Oberteil braucht weniger Ausstellung.

        `Saumweite = flare * width * bust` — bei width 1,05 reicht ein
        kleinerer flare fuer denselben Umfang.
        """
        eng = Saumgrenze.untergrenze({'shirt.width': 1.0}, FIGUR)
        weit = Saumgrenze.untergrenze({'shirt.width': 1.05}, FIGUR)
        self.assertLess(weit, eng)

    def test_ohne_masse_wird_nicht_geraten(self):
        u"""Fehlen Huefte oder Brust, bleibt der Wert, wie er ist."""
        for masse in ({}, {'bust': 88.0}, {'hips': 97.0}, None):
            regler, hinweise = Saumgrenze.baendigen(
                {'shirt.flare': 0.5}, masse)
            self.assertEqual(regler['shirt.flare'], 0.5, str(masse))
            self.assertEqual(hinweise, [])

    def test_ohne_flare_kein_eingriff(self):
        u"""Wer den Regler nicht stellt, bekommt GarmentCodes Vorgabe."""
        regler, hinweise = Saumgrenze.baendigen({'sleeve.length': 1.0}, FIGUR)
        self.assertNotIn('shirt.flare', regler)
        self.assertEqual(hinweise, [])

    def test_der_hinweis_nennt_beide_werte(self):
        u"""Eine stille Korrektur waere ein Regler, der luegt."""
        _, hinweise = Saumgrenze.baendigen(
            {'shirt.width': 1.0, 'shirt.flare': 0.7}, FIGUR)
        self.assertIn('0.70', hinweise[0])
        self.assertIn('1.10', hinweise[0])
        self.assertIn('98', hinweise[0])

    def test_gegenprobe_ohne_baendigung_bleibt_es_zu_eng(self):
        u"""Sabotage: Ohne den Vergleich kaeme der zu enge Wert durch.

        Die Probe zeigt, dass der Test oben wirklich die Grenze prueft und
        nicht eine Eigenschaft, die ohnehin gilt.
        """
        grenze = Saumgrenze.untergrenze({'shirt.width': 1.0}, FIGUR)
        self.assertGreater(grenze, 0.7,
                           'sonst prueft test_zu_enger_saum_wird_gehoben nichts')
