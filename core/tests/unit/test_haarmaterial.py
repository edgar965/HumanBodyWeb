# -*- coding: utf-8 -*-
u"""Haar ist kein Metall — und die Frisur-Dateien sagen es nicht selbst.

WARUM (Edgar, 10.09.2026): „warum ist das Haar der Female1 jetzt plötzlich
grau?" Im Browser gemessen: `metalness = 1` bei `roughness = 1`. Ein
vollmetallisches Material hat keine diffuse Reflexion, die Szene hat keine
Umgebungskarte — übrig bleibt flaches Grau, gleich welche Farbe daraufliegt
(„Silken Black" #272727 und „Dark Brown" #503827 sahen identisch aus).

DIE URSACHE STECKT IN DEN DATEN, und der zweite Test hält genau das fest:
Alle Frisur-GLBs führen `materials: null`. Für diesen Fall schreibt die
glTF-Spezifikation ein Standardmaterial mit `metallicFactor 1.0` vor. Bekäme
eine Frisur eines Tages ein echtes Material, wäre der Grund für die
Korrektur entfallen — dann soll dieser Test daran erinnern, statt sie stumm
weiterlaufen zu lassen.
"""
import json
import struct

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul


class DasHaarmaterialIstDielektrischTest(SimpleTestCase):

    databases = []

    def setUp(self):
        self.quelle = Jsmodul('character_core.js').pfad.read_text(
            encoding='utf-8')

    def test_die_metallstaerke_wird_gesetzt(self):
        self.assertIn('m.metalness = HAAR_METALL', self.quelle)
        self.assertIn('const HAAR_METALL = 0.0', self.quelle)

    def test_auch_ohne_bekannte_farbe(self):
        u"""Der frühere `if (!rgb) return;` ließ genau den Fall metallisch,
        in dem eine Frisur ohne Farbeintrag geladen wird."""
        stelle = self.quelle.index('export function applyHairColor')
        rumpf = self.quelle[stelle:stelle + 900]
        self.assertNotIn('if (!rgb) return;', rumpf)
        self.assertLess(rumpf.index('m.metalness'), rumpf.index('if (color)'),
                        u'Die Metallstärke muss vor der Farbe kommen — sie '
                        u'gilt auch ohne sie')


class DieFrisurdateienFuehrenKeinMaterialTest(SimpleTestCase):
    u"""Die Gegenprobe an den echten Daten (nur lesend)."""

    databases = []

    def test_jede_frisur_ueberlaesst_das_material_der_spezifikation(self):
        ordner = settings.HUMANBODY_ROOT / 'data' / 'humanBody' / 'hairstyles'
        dateien = sorted(ordner.glob('*.glb'))
        self.assertTrue(dateien, u'Keine Frisur gefunden: %s' % ordner)
        for pfad in dateien:
            with open(pfad, 'rb') as datei:
                datei.read(12)
                laenge, _art = struct.unpack('<II', datei.read(8))
                kopf = json.loads(datei.read(laenge).decode('utf-8'))
            self.assertIsNone(kopf.get('materials'), pfad.name)
