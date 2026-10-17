# -*- coding: utf-8 -*-
u"""Die „Einstellungen" einer Daz-Garderobenzeile und der Bildnachlader, am Quelltext (16.10.2026).

WARUM (Edgar, 16.10.2026: „es ist ein chaos bei den Assets, die „Einstellungen" verwirren sehr, die oberhalb der Assets sind. Ändere die Farbe der
„Einstellungen" in Gelb, und mache Ordnung darin, ordne sie nach den gleichen Kategorien wie die Assets" — und „bei einigen Eigen Assets fehlen die Icons"):

1. Die Einstellungen eines Stücks stehen als gelber Knopf IN seiner Zeile (`einstellung-knopf`), zugeklappt, und werden erst beim Aufklappen gebaut;
   ihre Gruppen folgen den Kategorien der Garderobe (`_geordnet`, `Genesis9garderobekategorien.ist`); die Farbe ist ein Token (`--einstellung`) in
   beiden Themen.
2. Der Bildnachlader holt ein gescheitertes Bild bis zu dreimal nach (Autoreload des Servers während des Ladens ließ 17 Vorschaubilder kaputt stehen).

Warum Quelltext statt Node: die Module hängen über `state.js` an `three/addons`, das löst der Node-Harness nicht auf. Tests geschrieben, nicht gelaufen.
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


def quelltext(*teile):
    return (Path(settings.BASE_DIR) / 'static').joinpath(*teile).read_text(encoding='utf-8')


class EinstellungenJsTest(SimpleTestCase):
    databases = set()

    def test_1_gelber_knopf_in_der_zeile_zugeklappt_und_erst_beim_aufklappen_gebaut(self):
        regler = quelltext('viewer', 'charakter', 'genesis9', 'genesis9stueckregler.js')
        self.assertIn("knopf.className = 'einstellung-knopf'", regler)
        self.assertIn("knopf.setAttribute('aria-expanded', 'false')", regler)
        self.assertIn("String(auf)", regler)
        self.assertIn('Genesis9stueckregler._geordnet(gruppen)', regler, 'die Gruppen folgen den Kategorien')
        garderobe = quelltext('viewer', 'charakter', 'genesis9', 'genesis9garderobe.js')
        self.assertIn('Genesis9stueckregler.bauen(inst, stueck,', garderobe)
        kategorien = quelltext('viewer', 'charakter', 'genesis9', 'genesis9garderobekategorien.js')
        self.assertIn('static ist(name)', kategorien)

    def test_2_farbe_ist_ein_token_in_beiden_themen(self):
        theme = quelltext('css', 'theme.css')
        self.assertGreaterEqual(theme.count('--einstellung:'), 2, 'dunkel und hell')
        seitenleiste = quelltext('css', 'viewer_seitenleiste.css')
        self.assertIn('.einstellung-knopf', seitenleiste)
        self.assertIn('color: var(--einstellung)', seitenleiste)

    def test_3_bildnachlader_holt_gescheiterte_bilder_nach(self):
        text = quelltext('viewer', 'gemeinsam', 'bildnachlader.js')
        self.assertIn("from '/static/djangobase/js/bildnachlader.js'", text, 'die Logik bleibt in djangoBase')
        self.assertIn('static WIEDERHOLUNGEN = 3', text)
        self.assertIn("bild.addEventListener('error'", text)
        self.assertIn('versuch=', text, 'die Marke umgeht einen zwischengespeicherten Fehlschlag')
        self.assertIn('if (versuch > Bildnachlader.WIEDERHOLUNGEN) return;', text, 'nach der letzten Wiederholung ist Schluss')

    def test_4_die_lagenmaske_laesst_den_einzug_verschweisster_stuecke_in_ruhe(self):
        u"""Daz Mann, Herrenhaar angehakt (Chrome, 16.10.2026): Einzugssumme der Anatomie −651,4 vor, 0,0 nach `Lagenverdeckung.anwenden` — dunkle Krallen am Ansatz."""
        text = quelltext('viewer', 'charakter', 'lagenverdeckung.js')
        self.assertIn("import { Stueckloch } from '../gemeinsam/stueckloch.js';", text)
        self.assertIn('const stoffe = Hautverdeckung.stoffe(inst, true);', text, 'verschweißte Stücke nehmen an der Lagenrechnung nicht teil')
        self.assertIn('if (!voll || Stueckloch.von(netz, anzahl)) continue;', text, 'aufheben setzt ihren Einzug nicht auf null')

    def test_5_jede_stueckmeldung_fuellt_die_objektliste_neu(self):
        u"""Daz Mann: Herrenhaar und JS Pants am Körper, die Liste „Objekte" im Reiter Modell nannte nur die Anatomie."""
        text = quelltext('viewer', 'gemeinsam', 'genesis9kleidung.js')
        melden = text[text.index('static melden('):]
        self.assertLess(melden.index('fn.updateEquippedList?.(inst);'), melden.index('Stueckereignis.melden('), 'die Liste vor der Meldung an die Masken')

    def test_6_der_abstand_der_drapierung_steht_in_millimetern(self):
        u"""War „300 %" für 3 mm: Der Regler hat `einheit: mm`, die Anzeige kannte nur cm und Prozent."""
        text = quelltext('viewer', 'charakter', 'genesis9', 'genesis9stueckregler.js')
        self.assertIn("regler?.einheit === 'mm'", text)
