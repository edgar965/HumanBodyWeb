# -*- coding: utf-8 -*-
"""Blender-Import: eine .blend OHNE Skelett sagt es im Klartext (08.10.2026).

Edgar startete den Import von „Beautiful Asian girl 5.0.blend" und fragte, ob er läuft. Er lief nicht: nach 8 s endete der
Schritt „Lesen" mit „Kein Körper: kein Netz an einer Armatur ist mindestens 1.0 m hoch". Gemessen (`blend_inhalt.py`, Blender 5.2.2):
die Datei hat 15 Netze und 0 Armaturen (ein Character-Creator-Modell ohne Rig) — der Exporter nimmt nur Netze mit
Armatur-Modifikator, das Inventar war leer, und die Meldung klang nach einem Maßproblem.

1. Ohne Netz an einer Armatur, aber mit Netzen ohne: „Das Modell hat kein Skelett: 15 Netze (…), 0 Armaturen".
2. Ohne irgendein Netz im Inventar (alte Inventare ohne `ohne_armatur`): die bisherige Meldung bleibt.
3. Mit Körper wie bisher: kein Fehler, die Rollen kommen heraus.

Sabotage-Gegenprobe: in `koerper` die Bedingung `not self.netze and self.ohne_armatur` streichen → Fall 1 rot.

Nicht gelaufen (Stand 08.10.2026) — läuft nur auf Ansage.
"""

from django.test import SimpleTestCase

from core.dienste.blendimportrollen import Blendimportrollen


def _netz(name, hoch, gewichte):
    return {'name': name, 'datei': name + '.glb', 'punkte': 1000, 'min': [0, 0, 0], 'max': [0.5, 0.5, hoch], 'gewichte': gewichte, 'materialien': []}


class OhneSkelettTest(SimpleTestCase):
    databases = set()

    def test_1_ohne_armatur_steht_im_klartext_warum(self):
        inventar = {'netze': [], 'armaturen': 0, 'ohne_armatur': [' bra', 'body', 'boot', 'eyelashes', 'hair1']}
        with self.assertRaises(ValueError) as fehler:
            Blendimportrollen(inventar).zuordnen()
        text = str(fehler.exception)
        self.assertIn('kein Skelett', text)
        self.assertIn('5 Netze', text)
        self.assertIn('0 Armaturen', text)
        self.assertIn('body', text)
        self.assertIn('…', text, 'mehr als vier Netze werden gekürzt')

    def test_2_alte_inventare_ohne_die_angabe_behalten_die_bisherige_meldung(self):
        with self.assertRaises(ValueError) as fehler:
            Blendimportrollen({'netze': []}).zuordnen()
        self.assertIn('Kein Körper', str(fehler.exception))

    def test_3_mit_koerper_kommt_keine_fehlermeldung(self):
        inventar = {'netze': [_netz('body', 1.7, {'spine': 1.0, 'head': 1.0})], 'armaturen': 1, 'ohne_armatur': ['bra']}
        rollen = Blendimportrollen(inventar).zuordnen()
        self.assertEqual([r['rolle'] for r in rollen], ['koerper'])
