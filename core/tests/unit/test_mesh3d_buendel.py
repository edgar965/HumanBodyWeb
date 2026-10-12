# -*- coding: utf-8 -*-
"""Die Jobseite „Mesh-3D“ lädt ihre Module als EIN Bündel (12.10.2026).

Edgar: „40–50 s Wartezeit im Browser für das Modell ist viel zu lange, ich brauche 5–10 s“. Gemessen im Messtab: 232 Einzelmodule kalt 6,5 s bis die Bühne angelegt war, als Bündel 0,96 s.
Quelltext gelesen, nichts gestartet, kein esbuild-Lauf. Nicht gelaufen — läuft nur auf Ansage.

    BuendelTest   der Einstieg ist eingetragen, die Vorlage nimmt ihre Importe aus EINER Adresse, und `main.js` führt alles, was die Vorlage braucht
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.modulbuendel import Modulbuendel
from core.templatetags import szenenskript


class BuendelTest(SimpleTestCase):
    databases = set()

    def _vorlage(self):
        return (Path(settings.BASE_DIR) / 'templates' / 'mesh3d_auftrag.html').read_text(encoding='utf-8')

    def test_1_der_einstieg_ist_eingetragen_und_vorhanden(self):
        self.assertIn('mesh3d', Modulbuendel.EINSTIEGE)
        self.assertTrue((Path(Modulbuendel.wurzel()) / Modulbuendel.EINSTIEGE['mesh3d']).is_file())
        self.assertEqual(szenenskript.EINZELN_MESH3D, Modulbuendel.EINSTIEGE['mesh3d'])

    def test_2_die_vorlage_importiert_nur_aus_dem_buendel(self):
        text = self._vorlage()
        # Ein Modul, das einmal im Bündel und einmal einzeln geladen würde, hätte zwei Zustände.
        for name in ('mesh3dseite.js', 'auftragloeschen.js', 'seitenreiter.js'):
            self.assertNotIn(name, text, name)
        adressen = re.findall(r'from "\{% (\w+) %\}"', text)
        self.assertGreaterEqual(len(adressen), 2)
        self.assertEqual(set(adressen), {'mesh3dskript'})

    def test_3_main_fuehrt_alles_was_die_vorlage_braucht(self):
        text = (Path(Modulbuendel.wurzel()) / Modulbuendel.EINSTIEGE['mesh3d']).read_text(encoding='utf-8')
        for name in ('Mesh3dseite', 'Auftragloeschen', 'Seitenreiter'):
            self.assertRegex(text, r'export \{ %s \} from' % name)
