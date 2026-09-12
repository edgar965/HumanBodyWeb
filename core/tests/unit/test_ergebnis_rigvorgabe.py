# -*- coding: utf-8 -*-
u"""Die Ergebnisseite zeigt das HumanBody-Rig auf allen Ansichten — als VORGABE.

WARUM (12.09.2026, Edgar zum dritten Mal: „oben ist ein anderes Rig zu sehen
als unten. Das Rig in den oberen Bereichen ist wahrscheinlich CMU oder SMPL,
ohne Gesicht und Hand"): Das DEF-Rig gab es oben nur hinter dem Knopf „Rig",
und unten stand der Schalter der 3D-Figur auf aus. Wer die Seite öffnete,
sah oben das BVH-Skelett (SMPL-X: 54 Gelenke, kein Gesicht) und unten die
Figur mit ihrem Rig — zwei Skelette.

Geprüft wird am Quelltext, dass die Vorgabe an ALLEN vier Stellen steht:
der Spieler schaltet das Rig nach dem Laden selbst ein, der Knopf zeigt
den Stand, die Figur startet mit sichtbarem Rig und baut den Helfer, sobald
ihr Skelett da ist — nicht erst beim Kippen.
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

STATIK = Path(settings.BASE_DIR) / 'static'
SPIELER = STATIK / 'js' / 'bvh_player.js'
BEDIENUNG = STATIK / 'js' / 'bvh_player' / 'bedienung.js'
FIGUR = STATIK / 'viewer' / 'result_character'


def lesen(pfad):
    return pfad.read_text(encoding='utf-8')


class DieRigvorgabe(SimpleTestCase):

    def test_der_spieler_schaltet_das_rig_nach_dem_laden_selbst_ein(self):
        js = lesen(SPIELER)
        self.assertIn('async rigVorgeben()', js)
        start = js.index('async starten(')
        self.assertIn('await this.rigVorgeben();', js[start:])
        # nach dem Skelett, nicht davor: ohne Wurzel gibt es keinen Anker
        self.assertLess(js.index('await this.skelett.laden(bvhUrl)', start),
                        js.index('await this.rigVorgeben();', start))
        self.assertIn('this.bedienung.rigStandZeigen(this.rigGewuenscht)', js)

    def test_der_knopf_zeigt_den_stand(self):
        self.assertIn("classList.toggle('active', !!an)", lesen(BEDIENUNG))

    def test_die_figur_startet_mit_sichtbarem_rig(self):
        self.assertIn('rigVisible: true', lesen(FIGUR / 'state.js'))
        leiste = lesen(FIGUR / 'knopfleiste.js')
        rig = leiste.index("text: 'Rig'")
        self.assertIn('an: true', leiste[rig:leiste.index('kippen', rig)])

    def test_der_helfer_entsteht_mit_dem_skelett(self):
        js = lesen(FIGUR / 'mesh_loading.js')
        skelett = js.index('state.rigifySkeleton = buildRigifySkeleton(')
        self.assertIn('if (state.rigVisible && !state.skeletonHelper)',
                      js[skelett:skelett + 600])
        self.assertIn("import { Skelettanzeige }", js)
