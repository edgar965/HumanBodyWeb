# -*- coding: utf-8 -*-
"""JavaScript-Logik `Bvhtext` gegen einen bekannten BVH-Kopf prüfen.

Warum ein Python-Test für JavaScript: Das Projekt hat eine Test-Suite, die über
`manage.py test` läuft — dort soll auch die JS-Logik auftauchen, die ohne Browser
prüfbar ist. `Bvhtext` (static/viewer/bvh_studio/bvhtext.js) ist so ein Fall: Sie
findet den Yposition-Kanal im Kopf einer BVH und ersetzt Werte in den
Bewegungszeilen. Genau das entschied beim Bodenrichten, ob die Korrektur in der
Datei landet oder verloren geht.

Ohne `node` im Pfad bricht der Lauf mit einer Meldung ab (seit dem
30.08.2026) — vorher meldete er grün, ohne gelaufen zu sein.

Geladen wird über `djangobase.testhelfer.Webmodul`: Seit `Serverabruf` in
djangoBase liegt, enthält die Importkette einen absoluten Pfad
(`/static/djangobase/js/serverabruf.js`). Den kann Node nicht auflösen — der
Helfer spiegelt die Kette und biegt solche Pfade um.
"""
import json
import unittest

from ..jsmodul import Jsmodul

BVHTEXT = Jsmodul('bvh_studio', 'bvhtext.js')

#: Kleine, aber vollständige BVH: Wurzel mit 6 Kanälen, ein Gelenk mit 3.
BVH = '\n'.join([
    'HIERARCHY',
    'ROOT Hips',
    '{',
    '  OFFSET 0 0 0',
    '  CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation',
    '  JOINT Spine',
    '  {',
    '    CHANNELS 3 Zrotation Xrotation Yrotation',
    '  }',
    '}',
    'MOTION',
    'Frames: 3',
    'Frame Time: 0.033333',
    '0.0 10.0 0.0 0 0 0 0 0 0',
    '0.0 11.0 0.0 0 0 0 0 0 0',
    '0.0 12.0 0.0 0 0 0 0 0 0',
    '',
])

SKRIPT = """
const {{ Bvhtext }} = await import(MODUL);
const datei = new Bvhtext({bvh});
const kanal = datei.kanal('Yposition');
const geaendert = datei.kanalSetzen(kanal, 3, bild => [1.5, 2.5, 3.5][bild]);
console.log(JSON.stringify({{
    kanal,
    bewegungszeilen: datei.bewegungszeilen(),
    geaendert,
    werte: datei.text().split('\\n')
        .filter(zeile => /^0\\.0/.test(zeile))
        .map(zeile => zeile.split(/\\s+/)[1]),
    unbekannt: datei.kanal('Wposition'),
    ohneMotion: new Bvhtext('HIERARCHY').bewegungszeilen().length,
}}));
"""


class BvhtextTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        skript = SKRIPT.format(bvh=json.dumps(BVH))
        cls.ergebnis = BVHTEXT.laufen(skript)

    def test_yposition_ist_der_zweite_kanal(self):
        self.assertEqual(self.ergebnis['kanal'], 1)

    def test_bewegungszeilen_beginnen_nach_frame_time(self):
        # Zeilen 13, 14, 15 (0-basiert) sind die drei Datenzeilen.
        self.assertEqual(self.ergebnis['bewegungszeilen'], [13, 14, 15])

    def test_werte_werden_ersetzt(self):
        self.assertEqual(self.ergebnis['geaendert'], 3)
        self.assertEqual(self.ergebnis['werte'],
                         ['1.500000', '2.500000', '3.500000'])

    def test_unbekannter_kanal_meldet_minus_eins(self):
        """Sonst würde `kanalSetzen` in die falsche Spalte schreiben."""
        self.assertEqual(self.ergebnis['unbekannt'], -1)

    def test_datei_ohne_motion_hat_keine_bewegungszeilen(self):
        self.assertEqual(self.ergebnis['ohneMotion'], 0)


if __name__ == '__main__':
    unittest.main()
