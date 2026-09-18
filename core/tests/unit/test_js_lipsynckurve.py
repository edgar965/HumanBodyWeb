# -*- coding: utf-8 -*-
u"""`Lipsynckurve` und `Lipsyncformen` (`gemeinsam/`): Rhubarbs Mundformen
mit Zeiten -> Reglerstellung je Bild (18.09.2026, Edgar: „mach Lipsync").

Drei Cues (X 0–0,2 · D 0,2–0,5 · A 0,5–0,8): davor und danach Ruhe; mitten
im D-Cue der volle `Vis AA`; 30 ms nach dem Wechsel D -> A die Haelfte von
beidem (Uebergang 60 ms); MB-Lab-Tabelle liefert Mundeinheiten statt Visemes;
`addieren` deckelt auf 1.

Sabotage-Gegenproben: `u` fest auf 1 (kein Uebergang) -> Fall 2 rot (AA 0
statt 0,5); `stelle` mit `t <= c.end` -> Fall 1 rot (0,8 faellt in A statt X).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'lipsynckurve.js')

SKRIPT = """
const { Lipsynckurve: K, Lipsyncformen: F } = await import(MODUL);
const cues = [{ start: 0, end: 0.2, form: 'X' }, { start: 0.2, end: 0.5, form: 'D' },
              { start: 0.5, end: 0.8, form: 'A' }];
const g9 = F.tabelle('genesis9'), mb = F.tabelle('modell');
const mitte = K.gewichte(cues, 0.35, g9);
const wechsel = K.gewichte(cues, 0.53, g9);
const summe = K.addieren({ facs_ctrl_vAA: 0.8 },
                         { facs_ctrl_vAA: 0.7, facs_ctrl_vM: 0.2 });
console.log(JSON.stringify({
    vorher: K.form(cues, -0.1), ruhe: K.form(cues, 0.1), d: K.form(cues, 0.499),
    a: K.form(cues, 0.5), danach: K.form(cues, 0.8),
    mitteAA: mitte.facs_ctrl_vAA, mitteAnzahl: Object.keys(mitte).length,
    wechselAA: wechsel.facs_ctrl_vAA, wechselM: wechsel.facs_ctrl_vM,
    ausserhalb: Object.keys(K.gewichte(cues, 0.9, g9)).length,
    mblab: K.gewichte(cues, 0.35, mb), formen: Object.keys(g9).sort().join(''),
    summe,
}));
"""


class LipsynckurveTest(SimpleTestCase):

    databases = set()

    def test_1_form_an_der_zeit(self):
        aus = MODUL.laufen(SKRIPT)
        self.assertEqual(
            [aus['vorher'], aus['ruhe'], aus['d'], aus['a'], aus['danach']],
            ['X', 'X', 'D', 'A', 'X'])
        self.assertEqual(aus['ausserhalb'], 0)
        self.assertEqual(aus['formen'], 'ABCDEFGHX')

    def test_2_uebergang_und_tabellen(self):
        aus = MODUL.laufen(SKRIPT)
        self.assertAlmostEqual(aus['mitteAA'], 1.0, places=6)
        self.assertEqual(aus['mitteAnzahl'], 1)
        self.assertAlmostEqual(aus['wechselAA'], 0.5, places=6)
        self.assertAlmostEqual(aus['wechselM'], 0.5, places=6)
        self.assertIn('mouthOpen', aus['mblab'])
        self.assertNotIn('facs_ctrl_vAA', aus['mblab'])
        self.assertAlmostEqual(aus['summe']['facs_ctrl_vAA'], 1.0, places=6)
        self.assertAlmostEqual(aus['summe']['facs_ctrl_vM'], 0.2, places=6)
