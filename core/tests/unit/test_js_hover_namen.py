# -*- coding: utf-8 -*-
u"""Das Schild der Schwebeanzeige nennt Stück und Modell, nicht die Daz-Geometrie
(20.09.2026, Edgar: „der hover text bei Genesis Kleidern ist falsch, der zeigt
geometry (genesis) anstelle der Genesis asset namen. Auch bei der genesis figur
soll der name des Modells angezeigt werden").

Die Regel `Genesis9kleidung.beschriftung` läuft in Node (sie hängt an nichts);
der Rest sind Textzusicherungen an den drei Stellen, weil die Module Three
importieren: `anziehen` holt den Katalognamen (Szene und BVH-Studio teilen das
Modul), `Dazkleidung` desgleichen, und `Schwebeanzeige._ziele` meldet Körper
und Anhänge einer Genesis-Figur mit dem Modellnamen.

Im Browser geprüft (Ursula1): Hand → „Ursula1 (Genesis 9)", Jeans → „Angie
Jeans (Genesis 9)", Niete → „Angie Jeans · BL Rivet (Genesis 9)".
Sabotage-Gegenprobe: `teilname !== 'geometry'` weg → Fall 1 rot.
"""
import re

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

STATIK = settings.BASE_DIR / 'static' / 'viewer'


def _beschriftung_quelle():
    quelle = (STATIK / 'gemeinsam' / 'genesis9kleidung.js').read_text(encoding='utf-8')
    treffer = re.search(r"static beschriftung\((.*?)\) \{(.*?)\n    \}", quelle, re.S)
    return 'function beschriftung(%s) {%s\n}' % (treffer.group(1), treffer.group(2))


class HoverNamenTest(SimpleTestCase):
    databases = set()

    def test_1_die_beschriftung(self):
        skript = _beschriftung_quelle() + """
const aus = {
    eins: beschriftung('Angie Jeans', 'geometry', 1),
    geometry: beschriftung('Dancing Queen Dress', 'geometry', 3),
    teil: beschriftung('Angie Jeans', 'BL Rivet', 7),
    daz: beschriftung('Dancing Queen Dress', 'Dress', 3, 'Daz'),
    ohne: beschriftung('G9 Base Shirt', null, 1),
};
console.log(JSON.stringify(aus));
"""
        self.assertEqual(Jsmodul('gemeinsam', 'genesis9kleidung.js').laufen(skript), {
            'eins': 'Angie Jeans (Genesis 9)',
            'geometry': 'Dancing Queen Dress (Genesis 9)',
            'teil': 'Angie Jeans · BL Rivet (Genesis 9)',
            'daz': 'Dancing Queen Dress · Dress (Daz)',
            'ohne': 'G9 Base Shirt (Genesis 9)',
        })

    def test_2_die_stuecke_tragen_den_katalognamen(self):
        kleidung = (STATIK / 'gemeinsam' / 'genesis9kleidung.js').read_text(encoding='utf-8')
        self.assertIn("const name = await Genesis9kleidung.anzeigename(kennung);", kleidung)
        self.assertIn("netz.userData.beschriftung = Genesis9kleidung.beschriftung(name, teil.name, daten.teile.length);",
                      kleidung)
        daz = (STATIK / 'scene' / 'genesis9' / 'dazkleidung.js').read_text(encoding='utf-8')
        self.assertIn("Genesis9kleidung.beschriftung(name, teil.name, daten.teile.length, 'Daz')", daz)
        self.assertNotIn("`${kennung} (Daz)`", daz)

    def test_3_die_figur_meldet_den_modellnamen(self):
        schwebe = (STATIK / 'scene' / 'schwebeanzeige.js').read_text(encoding='utf-8')
        self.assertIn("figur.quelle === 'genesis9' && figur.bodyMesh", schwebe)
        self.assertIn("`${figur.presetName || figur.name || id} (Genesis 9)`", schwebe)
        self.assertIn("Object.values(figur.anhangNetze || {})", schwebe)
        self.assertIn("(treffer.figur || treffer.knochen)", schwebe)
