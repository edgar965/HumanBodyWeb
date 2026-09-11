# -*- coding: utf-8 -*-
u"""Der Haar-Abschnitt im Eigenschaften-Reiter geht beim Haarklick auf.

WARUM (Edgar, 10.09.2026): „wenn ich das Haar anklicke, werden mir nicht die
Eigenschaften des Haars angezeigt, sondern Tab Modell". Der Reiter war der
richtige („Modell" ist die Beschriftung des Eigenschaften-Reiters seit dem
09.09.2026) — der Abschnitt darin blieb zu: Die Vorlage versteckt ihn seit
dem 17.08.2026 per Klasse `hb-versteckt`, und beide Stellen, die ihn zeigen
wollten, setzten nur `style.display`. Eine Klasse mit dreifacher Spezifität
schlägt ein geleertes Inline-Attribut.

Geprüft am Quelltext, weil es im Testlauf keinen DOM gibt.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul


def _lies(*teile):
    return Jsmodul(*teile).pfad.read_text(encoding='utf-8')


class DerHaarabschnittGehtAufTest(SimpleTestCase):

    databases = []

    def test_hair_js_schaltet_die_klasse(self):
        quelle = _lies('scene', 'hair.js')
        stelle = quelle.index('function _syncPropHairControls')
        self.assertIn("classList.toggle('hb-versteckt', !haar)", quelle[stelle:])

    def test_properties_js_schaltet_die_klasse(self):
        quelle = _lies('scene', 'properties.js')
        stelle = quelle.index("getElementById('prop-hair-section')")
        self.assertIn("classList.toggle('hb-versteckt', !isHair)",
                      quelle[stelle:stelle + 400])

    def test_die_vorlage_versteckt_ihn_wirklich(self):
        u"""Die Gegenprobe: Ohne die Klasse in der Vorlage wäre der Test
        oben eine Vorsichtsmaßnahme ohne Anlass."""
        from django.conf import settings
        vorlage = (settings.BASE_DIR / 'templates' / 'scene_config.html')
        text = vorlage.read_text(encoding='utf-8')
        self.assertIn('class="prop-section hb-versteckt" id="prop-hair-section"', text)
