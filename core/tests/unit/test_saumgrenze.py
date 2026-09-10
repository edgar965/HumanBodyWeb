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


#: Dieselbe Figur, aber mit den Laengenmassen — erst damit ist die Saumhoehe
#: bekannt. Zahlen aus `GarmentcodeDienst.masse('female')`, 09.09.2026.
FIGUR_VOLL = {
    'bust': 88.38, 'waist': 61.84, 'hips': 97.43,
    'height': 167.99, 'head_l': 25.81, 'waist_line': 32.31,
    'hips_line': 25.00, 'vert_bust_line': 18.93,
}


class DerSaumZaehltDortWoErSitzt(SimpleTestCase):
    u"""Korrektur vom 09.09.2026 (Edgar, mit Bild von unten: „das sind doch
    mindestens 5 cm zwischen brust und t-shirt!").

    Die Grenze rechnete gegen die Huefte, auch wenn das Shirt an der Taille
    endet. Damit wurde JEDES T-Shirt hueftweit — gemessen 35–44 mm Luft
    unter der Brust, und (97,4 − 61,8) / 2pi ist genau 5,7 cm.
    """

    def test_ein_shirt_bis_zur_taille_misst_an_der_taille(self):
        umfang = Saumgrenze.saumumfang(
            {'shirt.length': 1.0}, FIGUR_VOLL)
        self.assertAlmostEqual(umfang, FIGUR_VOLL['waist'], places=1)

    def test_ein_sehr_langes_shirt_misst_weiter_an_der_huefte(self):
        u"""Der alte Fall bleibt richtig — dort war die Grenze nie falsch."""
        umfang = Saumgrenze.saumumfang({'shirt.length': 2.0}, FIGUR_VOLL)
        self.assertAlmostEqual(umfang, FIGUR_VOLL['hips'], places=1)

    def test_die_saumhoehe_folgt_der_formel_aus_tee_py(self):
        u"""`length = design['length'] * body['waist_line']`, ab Schulter."""
        hoehe = Saumgrenze.saumhoehe({'shirt.length': 1.0}, FIGUR_VOLL)
        erwartet = (FIGUR_VOLL['height'] - FIGUR_VOLL['head_l']
                    - FIGUR_VOLL['waist_line'])
        self.assertAlmostEqual(hoehe, erwartet, places=3)

    def test_taillenshirt_darf_jetzt_tailliert_sein(self):
        u"""Der Kern des Befunds: 0,7 wurde auf 1,05 gehoben und machte das
        Shirt hueftweit. Jetzt bleibt der Wert stehen."""
        regler, hinweise = Saumgrenze.baendigen(
            {'shirt.width': 1.05, 'shirt.flare': 0.7, 'shirt.length': 1.0},
            FIGUR_VOLL)
        self.assertEqual(regler['shirt.flare'], 0.7)
        self.assertEqual(hinweise, [])

    def test_beim_langen_shirt_greift_die_grenze_weiter(self):
        regler, hinweise = Saumgrenze.baendigen(
            {'shirt.width': 1.05, 'shirt.flare': 0.7, 'shirt.length': 2.0},
            FIGUR_VOLL)
        self.assertGreater(regler['shirt.flare'], 1.0)
        self.assertEqual(len(hinweise), 1)

    def test_ein_croptop_misst_am_brustkorb(self):
        u"""Ueber der Taille ist der Koerper wieder weiter — dort darf der
        Saum nicht enger werden als der Brustkorb."""
        umfang = Saumgrenze.saumumfang({'shirt.length': 0.6}, FIGUR_VOLL)
        self.assertGreater(umfang, FIGUR_VOLL['waist'])
        self.assertLess(umfang, FIGUR_VOLL['bust'])

    def test_ohne_laengenregler_gilt_die_vorgabe_eins(self):
        u"""Kein Sonderfall: `default.yaml` sagt 1,0, und das heisst Taille."""
        self.assertAlmostEqual(
            Saumgrenze.saumumfang({}, FIGUR_VOLL),
            Saumgrenze.saumumfang({'shirt.length': 1.0}, FIGUR_VOLL),
            places=3)

    def test_ohne_laengenmasse_bleibt_es_bei_der_huefte(self):
        u"""Rueckwaertskompatibel: Die alten Aufrufer geben nur bust/hips."""
        self.assertAlmostEqual(Saumgrenze.saumumfang({}, FIGUR),
                               FIGUR['hips'], places=3)

    def test_der_hinweis_nennt_die_saumhoehe(self):
        u"""Vorher stand dort immer „Hüfte" — auch bei einem Taillenshirt,
        und dann sucht man den Fehler an der falschen Stelle."""
        _, hinweise = Saumgrenze.baendigen(
            {'shirt.width': 1.05, 'shirt.flare': 0.7, 'shirt.length': 2.0},
            FIGUR_VOLL)
        self.assertIn('über dem Boden', hinweise[0])

    def test_gegenprobe_die_alte_rechnung_haette_gehoben(self):
        u"""Sabotage: Mit `hips` statt Saumumfang kaeme 0,7 nicht durch —
        das belegt, dass der Test oben die Aenderung prueft."""
        alt = FIGUR_VOLL['hips'] / (FIGUR_VOLL['bust'] * 1.05)
        self.assertGreater(alt, 0.7)
        neu = Saumgrenze.untergrenze(
            {'shirt.width': 1.05, 'shirt.length': 1.0}, FIGUR_VOLL)
        self.assertLess(neu, 0.7)


class EineHebungOhneWirkungWirdNichtGemeldet(SimpleTestCase):
    u"""Edgar, 09.09.2026, im Protokoll gesehen: „Ausstellung von 0.70 auf
    0.70 gehoben".

    Formal stimmte es — die Grenze lag bei 0,7004, der Regler bei 0,70, und
    gerundet wurde daraus wieder 0,70. Eine Meldung, die eine Aenderung
    ankuendigt und keine vornimmt, schickt jeden auf die falsche Faehrte.
    Seither wird erst gerundet und dann verglichen.
    """

    def _figur_mit_grenze(self, ziel):
        u"""Eine Figur bauen, deren Untergrenze moeglichst genau `ziel` ist.

        `untergrenze` ist `saumumfang / (bust * width)`. Bei width 1,0 und
        einem Saum auf Taillenhoehe genuegt es, `waist` passend zu setzen.
        """
        figur = dict(FIGUR_VOLL)
        figur['waist'] = ziel * figur['bust']
        return figur

    def test_gleicher_wert_nach_dem_runden_meldet_nichts(self):
        figur = self._figur_mit_grenze(0.7004)
        regler = {'shirt.flare': 0.70, 'shirt.width': 1.0,
                  'shirt.length': 1.0}
        gebaendigt, hinweise = Saumgrenze.baendigen(regler, figur)
        self.assertEqual(hinweise, [])
        self.assertEqual(gebaendigt['shirt.flare'], 0.70)

    def test_eine_echte_hebung_wird_weiter_gemeldet(self):
        u"""Gegenprobe — sonst pruefte der Test oben nur, dass nie etwas
        passiert."""
        figur = self._figur_mit_grenze(0.85)
        regler = {'shirt.flare': 0.70, 'shirt.width': 1.0,
                  'shirt.length': 1.0}
        gebaendigt, hinweise = Saumgrenze.baendigen(regler, figur)
        self.assertEqual(len(hinweise), 1)
        self.assertGreater(gebaendigt['shirt.flare'], 0.70)

    def test_der_regler_bleibt_unveraendert_wenn_nichts_gemeldet_wird(self):
        figur = self._figur_mit_grenze(0.7004)
        regler = {'shirt.flare': 0.70, 'shirt.width': 1.0,
                  'shirt.length': 1.0}
        gebaendigt, _ = Saumgrenze.baendigen(regler, figur)
        self.assertIs(gebaendigt, regler)
