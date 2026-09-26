# -*- coding: utf-8 -*-
u"""Die Stücknamen der Daz-Garderobe lesen sich nicht wie gesperrt.

WARUM (Edgar, 19.09.2026, Szene → Assets → Genesis 9): „die meisten genesis
kleider sind ausgegraut". Kein Stück war gesperrt (70 von 70 `zeigbar`) —
der Name stand als `<label>` in `.slider-row`, und `scene_config.html` färbt
diese Labels `--text-muted` (#888), wie die Reglertitel. Genau das Grau, das
auch ein gesperrtes Stück (`gedaempft`) trägt. Seither trägt der Name
`stueckname`, `animationsbaum.css` gibt ihm `--text`; gedämpft bleibt nur,
was nicht zeigbar ist.

Textprüfung an den drei beteiligten Dateien — die Kopplung steht sonst
nirgends: Fällt die Regel in der Vorlage, braucht es die Klasse nicht mehr;
fällt die Klasse oder die CSS-Regel, sind die Namen wieder grau.
"""
import re

from django.conf import settings
from django.test import SimpleTestCase

STATIK = settings.BASE_DIR / 'static'
VORLAGEN = settings.BASE_DIR / 'templates'


class GarderobeStueckname(SimpleTestCase):
    databases = set()

    def _lesen(self, pfad):
        return pfad.read_text(encoding='utf-8')

    def test_die_vorlage_daempft_labels_in_reglerzeilen(self):
        """Der Grund für die Klasse: ohne diese Regel wäre sie überflüssig."""
        css = self._lesen(VORLAGEN / 'scene_config.html')
        regel = re.search(r'\.slider-row label\s*\{[^}]*color:\s*var\(--text-muted\)', css)
        self.assertIsNotNone(regel, '`.slider-row label` färbt nicht mehr gedämpft — '
                                    '`stueckname` in genesis9garderobe.js prüfen')

    def test_der_stueckname_traegt_die_klasse_und_gedaempft_nur_ungezeigt(self):
        js = self._lesen(STATIK / 'viewer' / 'charakter' / 'genesis9' / 'genesis9garderobe.js')
        label = re.search(r'<label for="\$\{kennung\}" class="([^"]*)"', js)
        self.assertIsNotNone(label)
        self.assertTrue(label.group(1).startswith('stueckname'), label.group(1))
        self.assertIn("stueck.zeigbar ? '' : ' gedaempft'", label.group(1))

    def test_das_css_gibt_dem_stuecknamen_die_textfarbe(self):
        css = self._lesen(STATIK / 'css' / 'animationsbaum.css')
        regel = re.search(r'\.slider-row label\.stueckname\s*\{[^}]*color:\s*var\(--text\)', css)
        self.assertIsNotNone(regel)
