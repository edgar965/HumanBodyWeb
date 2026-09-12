# -*- coding: utf-8 -*-
u"""Rigstart: das HumanBody-Rig kommt beim Seitenstart, mit dem Clip der Figur.

Edgar (12.09.2026): „nach dem Play startet das Video oben mit einem anderen
Rig, erst nach einigen Sekunden ändert sich das Rig, und startet auch das
untere Video" — „gleich nach dem Wechsel in den Result soll das richtige Rig
der Animation geladen werden".

Das Drahtformat der Spielerseite: `rigstart.js` beginnt sofort, holt den Clip
aus der `Klipquelle` und sperrt das Abspielen (`bereitschaft(false)`), bis
das Rig da ist; `bvh_player.js` ruft es beim Start und zeigt kein BVH-Skelett,
solange das Rig aussteht; `humanbodyrig.js` nimmt das Versprechen an und
übernimmt weitere Clips; `bedienung.js` sperrt Knopf und Leertaste.

Diese Dateien setzen auf dem Rig-Knopf der Parallelsitzung auf
(`humanbodyrig.js`) und werden mit ihm committet.
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

STATIK = Path(settings.BASE_DIR) / 'static'


class DasDrahtformat(SimpleTestCase):

    databases = set()

    def quelle(self, *teile):
        return STATIK.joinpath(*teile).read_text(encoding='utf-8')

    def test_der_spieler_holt_das_rig_beim_start_mit_dem_clip_der_figur(self):
        rigstart = self.quelle('js', 'bvh_player', 'rigstart.js')
        self.assertIn('Klipquelle.holen()', rigstart)
        self.assertIn('bereitschaft(false)', rigstart)
        spieler = self.quelle('js', 'bvh_player.js')
        self.assertIn('this.rigstart.beginnen()', spieler)
        self.assertIn('!this.rigstart.ausstehend', spieler)

    def test_das_rig_nimmt_das_versprechen_an(self):
        text = self.quelle('js', 'bvh_player', 'humanbodyrig.js')
        self.assertIn('static async laden(szene, jobId, klipVersprechen = null)', text)
        self.assertIn('klipUebernehmen(klip)', text)

    def test_abspielen_ist_gesperrt_solange_das_rig_laedt(self):
        text = self.quelle('js', 'bvh_player', 'bedienung.js')
        self.assertIn('bereitschaft(an)', text)
        self.assertIn('if (!this.bereit) return;', text)
