# -*- coding: utf-8 -*-
u"""Gewähltes Stranghaar muss sichtbar sein — auch dunkles (`strangauswahl.js`, 30.09.2026).

Edgar: „G9 Force pixie hair ist nicht auswählbar im 3D View, es wählt immer das ganze
Modell bei Klick". Im Chrome nachgeklickt: Pixie WURDE gewählt, man sah es nur nicht. Die
Auswahlfarbe multiplizierte die Strähnen — Pixie im Mittel [0,062 0,036 0,026] mal
[1,9 1,35 0,7] blieb fast schwarz. Der zweite Klick wählte dann ab (Umschalter).

Geprüft in Node (`strangauswahl.js` + `umfaerbung.js` + `shaderpatch.js` + `bildmittel.js`
in einen Projektordner kopiert, `three` durch eine Attrappe ersetzt — wie
`test_js_umfaerbung.py`):
1. Dunkles UND helles Haar liegen gewählt im Mittel auf der Auswahlfarbe (nicht dunkel).
2. Mit eigener Haarfarbe hellt die Auswahl auf, statt den Farbton zu verschieben.
3. Abwählen stellt die Grundfarbe zurück; das Mittel wird je Netz gemerkt.
4. `_setSubMeshEmissive` benutzt die Klasse — kein fester Faktor mehr.

Sabotage: in `Strangauswahl.setzen` den Faktor durch `ziel.r` ersetzen (ohne Teilen) ->
Fall 1 rot (dunkles Haar bleibt dunkel).
"""
import json
import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from core.projekt_temp import ProjektTemp

VIEWER = Path(settings.BASE_DIR) / 'static' / 'viewer'

DREI = """
export class Color {
    // Ohne Vorgabewerte in der Parameterliste: mit `g = 1` war `g === undefined` nie wahr, und
    // `new Color(0xb84400)` legte 12.076.032 als Rotkanal ab (erster Lauf, 30.09.2026).
    constructor(r, g, b) {
        if (typeof r === 'number' && g === undefined) { this.setHex(r); return; }
        this.r = r ?? 1; this.g = g ?? 1; this.b = b ?? 1;
    }
    setHex(n) { this.r = (n >> 16 & 255) / 255; this.g = (n >> 8 & 255) / 255;
                this.b = (n & 255) / 255; return this; }
    set(hex) { return this.setHex(parseInt(String(hex).replace('#', ''), 16)); }
    copy(c) { this.r = c.r; this.g = c.g; this.b = c.b; return this; }
    setRGB(r, g, b) { this.r = r; this.g = g; this.b = b; return this; }
    getHexString() { return [this.r, this.g, this.b]
        .map(v => Math.round(Math.min(1, v) * 255).toString(16).padStart(2, '0')).join(''); }
}
"""

PROBE = r"""
import { Strangauswahl } from './strangauswahl.js';
import { Umfaerbung } from './umfaerbung.js';
import { Color } from './three.js';
const aus = {};
const strang = (farbe) => {
    const n = 200;
    const attr = { count: n, version: 1, getX: () => farbe[0], getY: () => farbe[1], getZ: () => farbe[2] };
    const mat = { isMaterial: true, userData: {}, color: new Color(1, 1, 1), vertexColors: true,
                  wireframe: true, opacity: 1, transparent: false, metalness: 0 };
    return { netz: { geometry: { attributes: { color: attr }, userData: {} }, userData: {} }, mat };
};
const gezeigt = (s, farbe) => [s.mat.color.r * farbe[0], s.mat.color.g * farbe[1], s.mat.color.b * farbe[2]];

// 1. Dunkel (Pixie) und hell (Blond): gewählt im Mittel auf der Auswahlfarbe.
const dunkel = [0.062, 0.036, 0.026], hell = [0.8, 0.6, 0.3];
const a = strang(dunkel), b = strang(hell);
Strangauswahl.setzen(a.netz, a.mat, Strangauswahl.AUSWAHL);
Strangauswahl.setzen(b.netz, b.mat, Strangauswahl.AUSWAHL);
aus.dunkel = gezeigt(a, dunkel).map(v => +v.toFixed(3));
aus.hell = gezeigt(b, hell).map(v => +v.toFixed(3));
const z = Strangauswahl.AUSWAHL;
aus.ziel = [z.r, z.g, z.b].map(v => +v.toFixed(3));

// 2. Mit eigener Farbe: grau aufhellen (die Umfärbung legt den Farbton fest).
const c = strang(dunkel);
Umfaerbung.netz({ material: [c.mat], geometry: c.netz.geometry, traverse(f) { f(this); } }, '#a0461e');
Strangauswahl.setzen(c.netz, c.mat, Strangauswahl.AUSWAHL);
aus.umgefaerbt = [c.mat.color.r, c.mat.color.g, c.mat.color.b];

// 3. Abwählen stellt zurück; das Mittel ist gemerkt.
Strangauswahl.setzen(a.netz, a.mat, null);
aus.zurueck = [a.mat.color.r, a.mat.color.g, a.mat.color.b];
aus.gemerkt = !!a.netz.userData._strangmittel;
console.log(JSON.stringify(aus));
"""


def quelltext(*teile):
    return VIEWER.joinpath(*teile).read_text(encoding='utf-8')


class StrangauswahlTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not shutil.which('node'):
            raise RuntimeError('node ist nicht im Pfad — ohne node kein Ergebnis (jsmodul.py).')
        ordner = Path(ProjektTemp.ordner(prefix='strangauswahl_'))
        try:
            quellen = {'strangauswahl.js': ('charakter', 'strangauswahl.js'),
                       'umfaerbung.js': ('gemeinsam', 'umfaerbung.js'),
                       'shaderpatch.js': ('gemeinsam', 'shaderpatch.js'),
                       'bildmittel.js': ('gemeinsam', 'bildmittel.js')}
            for ziel, teile in quellen.items():
                text = (quelltext(*teile).replace("from 'three'", "from './three.js'")
                        .replace("from '../gemeinsam/umfaerbung.js'", "from './umfaerbung.js'"))
                (ordner / ziel).write_text(text, encoding='utf-8')
            (ordner / 'three.js').write_text(DREI, encoding='utf-8')
            (ordner / 'probe.mjs').write_text(PROBE, encoding='utf-8')
            lauf = subprocess.run(['node', str(ordner / 'probe.mjs')], capture_output=True,
                                  text=True, encoding='utf-8', timeout=60)
        finally:
            shutil.rmtree(ordner, ignore_errors=True)
        if lauf.returncode:
            raise AssertionError(lauf.stderr)
        cls.aus = json.loads(lauf.stdout.strip().splitlines()[-1])

    def test_1_dunkles_und_helles_haar_zeigen_die_auswahlfarbe(self):
        u"""Vorher blieb Pixie gewählt bei [0,118 0,049 0,018] — unsichtbar."""
        for name in ('dunkel', 'hell'):
            for kanal, (ist, soll) in enumerate(zip(self.aus[name], self.aus['ziel'], strict=True)):
                self.assertAlmostEqual(ist, soll, places=2, msg='%s Kanal %d' % (name, kanal))

    def test_2_mit_eigener_farbe_wird_aufgehellt(self):
        r, g, b = self.aus['umgefaerbt']
        self.assertEqual(r, g)
        self.assertEqual(g, b)
        self.assertGreater(r, 1.5)

    def test_3_abwaehlen_stellt_zurueck(self):
        self.assertEqual(self.aus['zurueck'], [1, 1, 1])
        self.assertTrue(self.aus['gemerkt'])

    def test_4_die_auswahl_benutzt_die_klasse(self):
        text = quelltext('charakter', 'teilnetz_auswahl.js')
        self.assertIn('Strangauswahl.setzen', text)
        self.assertNotIn('STRANG_AUSWAHL', text, 'der feste Faktor ist zurück')
