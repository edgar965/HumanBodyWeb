# -*- coding: utf-8 -*-
"""GarmentCode-Stuecke folgen dem neuen Skelett einer Genesis-9-Figur.

Edgar, 19.09.2026, mit Bild: „Hose (genesis) animiert nicht, und Garment Code
auch nicht". Im Browser gemessen: nach `inst.neuFormen()` hing `gc_oberteil`
noch am alten Skelett (`netz.skeleton === altesSkelett`, die Jeans am neuen)
— `_kleiderBinden` bindet nur Stuecke mit `hautgewichte` um, und `nachbinden`
uebersprang jedes gehaeutete Stueck. Seither meldet das Modell ein
`Skelettereignis`, die Szene bindet nach, und ein gehaeutetes Stueck mit
fremdem Skelett gilt als nicht gebunden.
"""

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'skelettereignis.js')

SKRIPT = """
const { Skelettereignis } = await import(MODUL);
if (Skelettereignis.NAME !== 'figur-skelett') throw new Error('Name');
// Ohne Dokument (Node, Worker): melden ist kein Fehler, nur wirkungslos.
if (Skelettereignis.melden({}) !== false) throw new Error('ohne document muss melden false liefern');
console.log(JSON.stringify({ ok: true }));
"""


def _quelle(*teile):
    pfad = settings.BASE_DIR / 'static' / 'viewer'
    for teil in teile:
        pfad = pfad / teil
    return pfad.read_text(encoding='utf-8')


class GarmentcodeNachbindungTest(SimpleTestCase):
    databases = set()

    def test_das_ereignis_laeuft_in_node(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_das_modell_meldet_nach_dem_umbinden(self):
        quelle = _quelle('gemeinsam', 'genesis9modell.js')
        rumpf = quelle.split('_kleiderBinden() {')[1].split('\n    }')[0]
        self.assertIn('Skelettereignis.melden(this)', rumpf)
        self.assertIn("import { Skelettereignis } from './skelettereignis.js';", quelle)

    def test_die_szene_hoert_zu_und_bindet_nach(self):
        quelle = _quelle('scene', 'garmentcode_nachbindung.js')
        self.assertIn('Skelettereignis.hoeren(', quelle)
        self.assertIn('GarmentcodeAnziehen.nachbinden(inst)', quelle)
        self.assertIn('GarmentcodeNachbindung.einhaengen();', quelle)
        # Eingehaengt, wo auch der HumanBody-Weg steht — sonst hoert niemand.
        self.assertIn("import './garmentcode_nachbindung.js';", _quelle('scene', 'skeleton.js'))

    def test_ein_stueck_am_alten_skelett_wird_neu_gebunden(self):
        quelle = _quelle('scene', 'garmentcode_anziehen.js')
        rumpf = quelle.split('static nachbinden(figur) {')[1].split('\n    }')[0]
        self.assertIn('netz.isSkinnedMesh && netz.skeleton === skelett', rumpf)
        self.assertNotIn('netz.isSkinnedMesh ||', rumpf)
        # Das Skelett der Figur ist das des Koerpers — nie das eines Stuecks,
        # das noch am alten haengt.
        skelett = quelle.split('static _skelett(figur) {')[1].split('\n    }')[0]
        self.assertIn('figur?.bodyMesh?.skeleton || figur?.skelett?.skeleton', skelett)
        self.assertIn('!o.userData?.gcRig', skelett)

    def test_die_masken_rechnen_einmal_je_umbau(self):
        """Ein Umbau holt Koerper und jedes Daz-Stueck einzeln; jede Ankunft
        meldet. Ohne Ruhezeit liefe die Maske je Meldung (auf Stufe 2 je
        Lauf zweistellige Sekunden)."""
        for ordner, name, klasse in (('gemeinsam', 'hautverdeckung.js', 'Hautverdeckung'),
                                     ('scene', 'lagenverdeckung.js', 'Lagenverdeckung')):
            quelle = _quelle(ordner, name)
            self.assertIn('static RUHE_MS = 400;', quelle, name)
            self.assertIn('clearTimeout(%s._ausstehend.get(inst))' % klasse, quelle, name)
            self.assertIn('}, %s.RUHE_MS));' % klasse, quelle, name)
            self.assertNotIn('}, 0);', quelle.split('Stueckereignis.hoeren(')[1], name)

    def test_daz_stuecke_melden_nur_mit_garmentcode_stueck(self):
        quelle = _quelle('gemeinsam', 'genesis9kleidung.js')
        self.assertIn("schluessel.startsWith('gc_')", quelle)
        self.assertIn('Genesis9kleidung.melden(inst, kennung, true)', quelle)
        self.assertIn('Genesis9kleidung.melden(inst, kennung, false)', quelle)
