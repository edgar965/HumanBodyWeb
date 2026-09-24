# -*- coding: utf-8 -*-
u"""Eigene Farbe für Daz-Stücke (24.09.2026) — `Umfaerbung`, `Stueckfarbe`, `Dazeigenschaften`.

Edgar: „kann die Farbe der Haare auch angepasst werden? z.B. Kin Hair? Evtl. auch
die der anderen Assets?" — dann „eine eigene Farbe je Gruppe über die Teil-Auswahl"
und „die Teilnetze auch in den Eigenschaften des Assets".

1. Logik in Node (`umfaerbung.js` + `shaderpatch.js` in einen Projektordner kopiert,
   `three` durch eine Attrappe ersetzt — der Harness löst `three` nicht auf):
   Gruppenfarbe schlägt Stückfarbe; Beschläge (am Gruppennamen, nicht an
   `metalness`) und Glanzschichten färbt nur die Gruppenfarbe; `Bildmittel`
   zählt nur belegte Texel und wird nach dem späten Bildladen nachgezogen; Abschalten lässt das Programm stehen (nur `umfAn` = 0);
   Stranghaar rechnet mit dem Mittel der Punktfarben, nicht mit der Grundfarbe;
   die Netze eines Stücks auf beiden Figurarten (`kennung/n`, `daz_kennung/n`).
2. Der Shadertext: Rechnung HINTER `color_fragment`, Mittel aus der obersten
   Mip-Stufe, Deckel.
3. Verdrahtung: nach jedem Anziehen (Genesis 9 und HumanBody) wird gefärbt,
   die Garderobe gibt `farbe`/`gruppenfarben` beim Neuanziehen weiter, die
   Eigenschaften kennen den Bereich, der Klick merkt die Gruppe.

Sabotage: in `Umfaerbung.netz` `eigene ||` streichen -> Fall 1 rot; in
`genesis9kleidung.js` die `Umfaerbung.stueck`-Zeile entfernen -> Fall 3 rot.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from core.projekt_temp import ProjektTemp

VIEWER = Path(settings.BASE_DIR) / 'static' / 'viewer'

DREI = """
export class Color {
    constructor(r = 1, g = 1, b = 1) { this.r = r; this.g = g; this.b = b; }
    set(hex) { const n = parseInt(hex.slice(1), 16);
        this.r = (n >> 16 & 255) / 255; this.g = (n >> 8 & 255) / 255; this.b = (n & 255) / 255; return this; }
    copy(c) { this.r = c.r; this.g = c.g; this.b = c.b; return this; }
    setRGB(r, g, b) { this.r = r; this.g = g; this.b = b; return this; }
    getHexString() { return [this.r, this.g, this.b]
        .map(v => Math.round(v * 255).toString(16).padStart(2, '0')).join(''); }
}
"""

PROBE = r"""
import { Umfaerbung } from './umfaerbung.js';
import { Shaderpatch } from './shaderpatch.js';
import { Bildmittel } from './bildmittel.js';
import { Color } from './three.js';
const aus = {};
const mat = (gruppe, extra = {}) => ({ isMaterial: true, userData: { gruppe }, color: new Color(0.8, 0.8, 0.8),
                                       metalness: 0, opacity: 1, transparent: false, ...extra });
const netz = (materialien, geometry = null) => ({ material: materialien, geometry,
    traverse(f) { f(this); } });
const haar = mat('kin Hair'), kappe = mat('kin Cap'), knopf = mat('Button'), niete = mat('SmallRivet');
const glanz = mat('Gloss', { transparent: true, opacity: 0.12 });
const shirt = mat('Shirt', { metalness: 1 });     // G9 Base Shirt: Metallkarte, trotzdem Stoff
const inst = { clothMeshes: { 'kin_hair/0': netz([haar, kappe, shirt, niete]), 'kin_hair/1': netz([knopf, glanz]),
                              'daz_kin_hair/0': netz([mat('bangs')]), 'anderes/0': netz([mat('x')]) } };
aus.netze = Umfaerbung.netze(inst, 'kin_hair').map(n => n.schluessel);
aus.gesetzt = Umfaerbung.stueck(inst, 'kin_hair', { farbe: '#ff0080', gruppenfarben: { 'kin Cap': '#00ff00', Button: '#0000ff' } });
aus.haar = Umfaerbung.farbe(haar); aus.kappe = Umfaerbung.farbe(kappe);
aus.knopf = Umfaerbung.farbe(knopf); aus.glanz = Umfaerbung.farbe(glanz);
aus.shirt = Umfaerbung.farbe(shirt); aus.niete = Umfaerbung.farbe(niete);
// Bildmittel: leere Atlasflaechen (durchsichtig oder schwarz) zaehlen nicht mit.
const px = [255, 0, 0, 255,   0, 0, 0, 255,   9, 9, 9, 255,   0, 255, 0, 0];
aus.bildmittel = Bildmittel.ausPixeln(px).map(v => +v.toFixed(3));
aus.bildmittelLeer = Bildmittel.ausPixeln([0, 0, 0, 0]).map(v => +v.toFixed(3));
// Das Bild kommt nach dem Faerben: beim Zeichnen gemessen, danach nicht mehr.
const spaet = mat('Late');
Umfaerbung.setzen(spaet, '#ffffff');
const e = Shaderpatch.eingriff(spaet, 'umfaerbung');
spaet.map = { image: 'bild', userData: { bildmittel: { bild: 'bild', farbe: [0.5, 0.25, 0] } } };
spaet.onBeforeRender();
aus.spaet = [e.uniforms.umfBildDa.value, e.uniforms.umfBild.value.r, e.uniforms.umfBild.value.g];
aus.anderes = Shaderpatch.hat(inst.clothMeshes['anderes/0'].material[0], 'umfaerbung');
aus.ohneFarbeKeinEingriff = Umfaerbung.setzen(mat('y'), '');
Umfaerbung.stueck(inst, 'kin_hair', { farbe: '', gruppenfarben: {} });
aus.aus = [Umfaerbung.farbe(haar), Shaderpatch.hat(haar, 'umfaerbung')];
const n = 4, farben = { count: n, getX: i => [0.2, 0.4, 0.2, 0.4][i], getY: () => 0.1, getZ: () => 0 };
const strang = mat('Strands', { vertexColors: true, color: new Color(1, 1, 1) });
Umfaerbung.netz(netz([strang], { attributes: { color: farben }, userData: {} }), '#ffffff');
const u = Shaderpatch.eingriff(strang, 'umfaerbung').uniforms;
aus.strang = [u.umfMitGrund.value, +u.umfMittel.value.r.toFixed(3), +u.umfMittel.value.g.toFixed(3)];
aus.grund = Shaderpatch.eingriff(haar, 'umfaerbung').uniforms.umfMitGrund.value;
const frag = Umfaerbung.fragment('#include <common>\nvoid main(){\n#include <map_fragment>\n#include <color_fragment>\n}');
aus.frag = frag;
console.log(JSON.stringify(aus));
"""


def quelltext(*teile):
    return VIEWER.joinpath(*teile).read_text(encoding='utf-8')


class UmfaerbungTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not shutil.which('node'):
            raise RuntimeError('node ist nicht im Pfad — ohne node kein Ergebnis (jsmodul.py).')
        ordner = Path(ProjektTemp.ordner(prefix='umfaerbung_'))
        try:
            for name in ('umfaerbung.js', 'shaderpatch.js', 'bildmittel.js'):
                text = quelltext('gemeinsam', name).replace("from 'three'", "from './three.js'")
                (ordner / name).write_text(text, encoding='utf-8')
            (ordner / 'three.js').write_text(DREI, encoding='utf-8')
            (ordner / 'probe.mjs').write_text(PROBE, encoding='utf-8')
            lauf = subprocess.run(['node', str(ordner / 'probe.mjs')], capture_output=True,
                                  text=True, encoding='utf-8', timeout=60)
        finally:
            shutil.rmtree(ordner, ignore_errors=True)
        if lauf.returncode:
            raise AssertionError(lauf.stderr)
        cls.aus = json.loads(lauf.stdout.strip().splitlines()[-1])

    def test_1_gruppenfarbe_schlaegt_stueckfarbe(self):
        a = self.aus
        self.assertEqual(a['netze'], ['kin_hair/0', 'kin_hair/1', 'daz_kin_hair/0'])
        self.assertEqual(a['haar'], '#ff0080')
        self.assertEqual(a['kappe'], '#00ff00')
        self.assertEqual(a['knopf'], '#0000ff', 'Beschlag nur mit eigener Gruppenfarbe')
        self.assertEqual(a['niete'], '', 'SmallRivet ist Beschlag')
        self.assertEqual(a['shirt'], '#ff0080', 'Metallkarte macht kein Metall')
        self.assertEqual(a['glanz'], '', 'die Glanzschicht faerbt die Stueckfarbe nicht')
        self.assertFalse(a['anderes'], 'fremdes Stueck unberuehrt')
        self.assertFalse(a['ohneFarbeKeinEingriff'], 'ohne Farbe kein Shadereingriff')
        self.assertEqual(a['gesetzt'], 5)

    def test_1b_bildmittel_nur_belegte_texel(self):
        self.assertEqual(self.aus['bildmittel'], [1.0, 0.0, 0.0], 'Schwarz und Durchsichtiges zaehlen nicht')
        self.assertEqual(self.aus['bildmittelLeer'], [0.0, 0.0, 0.0], 'nichts belegt: alle')
        self.assertEqual(self.aus['spaet'], [1, 0.5, 0.25])

    def test_2_aus_laesst_das_programm_stehen(self):
        self.assertEqual(self.aus['aus'], ['', True])

    def test_3_stranghaar_rechnet_mit_punktfarben(self):
        self.assertEqual(self.aus['strang'], [0, 0.3, 0.1])
        self.assertEqual(self.aus['grund'], 1)

    def test_4_shadertext(self):
        frag = self.aus['frag']
        self.assertIn('uniform float umfAn;', frag)
        self.assertLess(frag.index('#include <color_fragment>'), frag.index('if (umfAn > 0.5)'))
        self.assertIn('umfBildDa > 0.5 ? umfBild : textureLod(map, vec2(0.5), 16.0).rgb', frag)
        self.assertIn('mix(vec3(1.0), diffuse, umfMitGrund) * umfMittel', frag)
        self.assertIn('min(umfH / umfM, 4.0)', frag)

    def test_5_verdrahtung(self):
        self.assertIn('Umfaerbung.stueck(inst, kennung, inst.kleidung[kennung]);',
                      quelltext('gemeinsam', 'genesis9kleidung.js'))
        self.assertIn('Umfaerbung.stueck(inst, kennung, inst.dazKleidung[kennung]);',
                      quelltext('scene', 'genesis9', 'dazkleidung.js'))
        self.assertIn('material.userData.gruppe = gruppe.name;', quelltext('gemeinsam', 'genesis9strang.js'))
        garderobe = quelltext('scene', 'genesis9', 'genesis9garderobe.js')
        self.assertIn("farbe: felder.farbe?.wert ?? (bisher.farbe || ''),", garderobe)
        self.assertIn('gruppenfarben: { ...(bisher.gruppenfarben || {}) },', garderobe)
        self.assertIn('Dazeigenschaften.zeigen(teilnetz)', quelltext('scene', 'properties.js'))
        self.assertRegex(quelltext('scene', 'interaction.js'),
                         r'state\._getroffeneGruppe = \{ key: hitTarget\.key,')
        vorlage = (Path(settings.BASE_DIR) / 'templates' / 'scene_config.html').read_text(encoding='utf-8')
        self.assertIn('id="prop-daz-section"', vorlage)
        self.assertIn('id="prop-daz-teile"', vorlage)
        self.assertIn("css/stueckfarbe.css", vorlage)
        stueckfarbe = quelltext('scene', 'genesis9', 'stueckfarbe.js')
        self.assertTrue(re.search(r'static gruppe\(inst, kennung, gruppe, hex\)', stueckfarbe))

    def test_6_farbdialog_statt_farbfeld_in_der_zeile(self):
        u"""24.09.2026, Edgar mit Bild: „Farben nicht auswählbar" — das Farbfeld stand
        abgeschnitten hinter der Variantenauswahl. Jetzt Knopf + Dialog."""
        stueckfarbe = quelltext('scene', 'genesis9', 'stueckfarbe.js')
        self.assertNotIn("type = 'color'", stueckfarbe, 'kein Farbfeld mehr in der Zeile')
        self.assertIn('Stueckfarbdialog.oeffnen({ inst, kennung, gruppe,', stueckfarbe)
        dialog = quelltext('scene', 'genesis9', 'stueckfarbdialog.js')
        self.assertEqual(dialog.count("['#"), 30, 'Palette mit 30 Farben')
        for teil in ("static hexNormal(text)", "if (e.key === 'Escape') zu();",
                     'Stueckfarbe.gruppe(z.inst, z.kennung, z.ziel, hex);'):
            self.assertIn(teil, dialog)
        css = (Path(settings.BASE_DIR) / 'static' / 'css' / 'stueckfarbe.css').read_text(encoding='utf-8')
        self.assertIn('.slider-row:has(> .hb-stueckfarbe) > .hb-dehnt { min-width: 0; }', css,
                      'die Variantenauswahl gibt den Platz her')
        self.assertIn('pointer-events: none', css, 'Hintergrund frei, Figur sichtbar')
