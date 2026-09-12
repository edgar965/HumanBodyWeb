# -*- coding: utf-8 -*-
u"""Klipquelle: ein Clip für alle Ansichten der Ergebnisseite.

Edgar (12.09.2026): „schon wieder unterschiedliche Rigs oben und unten" und
„nach dem Play startet das Video oben mit einem anderen Rig, erst nach
einigen Sekunden ändert sich das Rig, und startet auch das untere Video".

Gemessen davor: zwei Retarget-Abrufe je Seite (Skelettfenster 1,601 m,
Figur 1,678 m — zwei Ablagen, zwei Maßstäbe), 3,5 s nebeneinander. Jetzt
holt die Figur, und das Skelettfenster wartet auf DENSELBEN Clip.

Was hier in Node läuft (reine Logik, ohne DOM und three.js):
`holen` vor `melden` wartet und bekommt den gemeldeten Clip; `holen` nach
`melden` bekommt ihn sofort; `scheitern` weist die Wartenden ab, ein
späterer Clip erreicht sie nicht mehr; `beiWechsel` sieht nur weitere Clips,
nicht den ersten.

Dazu das Drahtformat der Figurseite: `bvh_animation.js` meldet, `index.js`
lässt niemand ewig warten. Die Spielerseite (`rigstart.js`, `bvh_player.js`,
`bedienung.js`, `humanbodyrig.js`) prüft `test_js_rigstart.py`.
Sabotage-Gegenprobe: `melden` ohne das Leeren der Warter lässt „nur einmal"
rot werden.
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

STATIK = Path(settings.BASE_DIR) / 'static'

MODUL = Jsmodul('gemeinsam', 'klipquelle.js')

SKRIPT = """
const { Klipquelle } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const eins = { name: 'eins' }, zwei = { name: 'zwei' };

// holen VOR melden wartet — und bekommt genau den gemeldeten Clip
Klipquelle.leeren();
pruefe('anfangs nichts', Klipquelle.gemeldet, false);
let angekommen = null;
const warter = Klipquelle.holen().then(k => { angekommen = k; });
await new Promise(r => setTimeout(r, 5));
pruefe('wartet noch', angekommen, null);
Klipquelle.melden(eins);
await warter;
pruefe('erster Clip', angekommen, eins);
pruefe('gemeldet', Klipquelle.gemeldet, true);

// holen NACH melden: sofort derselbe
pruefe('sofort', await Klipquelle.holen(), eins);

// beiWechsel sieht nur weitere Clips; die Warter werden nur einmal bedient
const gesehen = [];
Klipquelle.beiWechsel(k => gesehen.push(k.name));
Klipquelle.melden(zwei);
pruefe('Wechsel', gesehen, ['zwei']);
pruefe('nur einmal', angekommen, eins);
pruefe('jetzt der zweite', await Klipquelle.holen(), zwei);

// scheitern weist die Wartenden ab; ein späterer Clip erreicht sie nicht
Klipquelle.leeren();
let fehler = null;
const abgelehnt = Klipquelle.holen().catch(e => { fehler = e.message; });
Klipquelle.scheitern(new Error('keine Figur'));
await abgelehnt;
pruefe('abgelehnt', fehler, 'keine Figur');
Klipquelle.melden(eins);
pruefe('bleibt abgelehnt', fehler, 'keine Figur');
console.log(JSON.stringify({ok: true}));
"""


class KlipquelleTest(SimpleTestCase):

    databases = set()

    def test_ein_clip_fuer_alle_wartenden(self):
        self.assertEqual(MODUL.laufen(SKRIPT), {'ok': True})


class DasDrahtformat(SimpleTestCase):
    u"""Wer meldet, wer holt, wer nimmt das Versprechen an."""

    databases = set()

    def quelle(self, *teile):
        return STATIK.joinpath(*teile).read_text(encoding='utf-8')

    def test_die_figur_meldet_ihren_clip_und_ihr_scheitern(self):
        text = self.quelle('viewer', 'result_character', 'bvh_animation.js')
        self.assertIn('Klipquelle.melden(clip)', text)
        self.assertIn('Klipquelle.scheitern(err)', text)

    def test_der_einstieg_laesst_niemanden_ewig_warten(self):
        text = self.quelle('viewer', 'result_character', 'index.js')
        self.assertIn('if (!Klipquelle.gemeldet)', text)
        self.assertIn('Klipquelle.scheitern(', text)
