# -*- coding: utf-8 -*-
"""`Lippenhaut`: die Lippenfarbe läuft im Hautshader glatt aus.

WARUM (Edgar, 13.09.2026, Bild aus der Szene: „die Lippen sind fehlerhaft"):
Je Dreieck gefärbt war der Lippenrand ein Zickzack. Jetzt trägt jeder
Punkt seinen Abstand zum Lippenrand (Attribut `lippe`), und der Shader der
Haut mischt daraus je Bildpunkt. Geprüft mit Attrappen statt Three.js —
Materialien mit `color.clone/copy`, eine Geometrie mit `attributes.position`:

1. Das Attribut hat je Punkt einen Wert: Saumpunkte ihren Abstand,
   Lippenpunkte INNEN, alle anderen AUSSEN.
2. Der Eingriff hängt an Haut UND Censor (Gruppen 0 und 1), nicht an den
   Lippen; der Shader bekommt Attribut, Varying, Uniforms und die Mischung
   von Farbe und Rauheit.
3. `nachziehen` holt Farbe und Rauheit des Lippenmaterials in die Uniforms —
   auch an einem Klon des Hautmaterials (Weichgewebe klont alle).
4. Ohne Saum oder ohne Lippenmaterial passiert nichts (0).

Dazu das Drahtformat: `Lippenbau` spaltet mit Saum NICHT mehr ab und ruft
`Lippenhaut.anlegen`; `Detailfarben.faerben` zieht nach; der Server liefert
`lippen` als `{punkte, saum}`.

Sabotage-Gegenprobe: `werte[i] = Lippenhaut.INNEN` weg → Fall 1 rot.
"""

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'lippenhaut.js')

SKRIPT = """
const { Lippenhaut: L } = await import(MODUL);
const { Shaderpatch } = await import(new URL('./shaderpatch.js', MODUL).href);
class Farbe {
    constructor(h) { this.h = h; }
    clone() { return new Farbe(this.h); }
    copy(o) { this.h = o.h; return this; }
}
class Attribut { constructor(werte, n) { this.array = werte; this.count = werte.length / n; } }
const material = (h, r) => ({ color: new Farbe(h), roughness: r, clone() { return material(this.color.h, this.roughness); } });
const netz = () => ({
    geometry: { attributes: { position: new Attribut(new Float32Array(18), 3) }, gesetzt: {},
                setAttribute(name, a) { this.gesetzt[name] = a; this.attributes[name] = a; } },
    material: [material('haut', 0.55), material('haut', 0.55), material('wimper', 0.8)],
});
const n = netz(); n.material[11] = material('#b5707a', 0.4);
const lippen = { punkte: [1, 2, 3], saum: { punkte: [2, 3, 4], abstand: [2.5, 0.3, -1.5] } };
pruefe('saumpunkte', L.anlegen(n, lippen), 3);
pruefe('attribut', Array.from(n.geometry.gesetzt.lippe.array).map(w => Math.round(w * 100) / 100), [-10, 10, 2.5, 0.3, -1.5, -10]);
pruefe('eingriff an haut und censor', [0, 1, 2].map(g => Shaderpatch.hat(n.material[g], 'lippen')), [true, true, false]);
const shader = { uniforms: {}, vertexShader: 'void main() {\\n#include <begin_vertex>\\n}',
                 fragmentShader: 'void main() {\\n#include <color_fragment>\\n#include <roughnessmap_fragment>\\n}' };
n.material[0].onBeforeCompile(shader);
pruefe('uniform farbe', shader.uniforms.lippenFarbe.value.h, '#b5707a');
pruefe('uniform rauheit', shader.uniforms.lippenRauheit.value, 0.4);
pruefe('vertex', [shader.vertexShader.includes('attribute float lippe;'), shader.vertexShader.includes('vLippe = lippe;')], [true, true]);
pruefe('fragment', [shader.fragmentShader.includes('smoothstep(-0.70, 0.70, vLippe)'),
                    shader.fragmentShader.includes('mix(diffuseColor.rgb, lippenFarbe, lippenAnteil)'),
                    shader.fragmentShader.includes('mix(roughnessFactor, lippenRauheit, lippenAnteil)')], [true, true, true]);
// nachziehen — auch am Klon
n.material[11].color.h = '#e60022'; n.material[11].roughness = 0.2;
const klon = n.material.map(m => (Shaderpatch.hat(m, 'lippen') ? Shaderpatch.klonen(m) : m));
pruefe('nachziehen klon', L.nachziehen(klon), 2);
pruefe('uniform nach klon', [shader.uniforms.lippenFarbe.value.h, shader.uniforms.lippenRauheit.value], ['#e60022', 0.2]);
// nichts zu tun
pruefe('ohne saum', L.anlegen(netz(), { punkte: [1] }), 0);
const ohneLippe = netz(); pruefe('ohne lippenmaterial', L.anlegen(ohneLippe, lippen), 0);
pruefe('nachziehen ohne eingriff', L.nachziehen(netz().material), 0);
console.log(JSON.stringify({ ok: true }));
"""


class LippenhautTest(SimpleTestCase):
    def test_attribut_eingriff_und_nachziehen(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))


class DasLippenDrahtformat(SimpleTestCase):
    def quelle(self, *teile):
        return Path(settings.BASE_DIR).joinpath(*teile).read_text(encoding='utf-8')

    def test_lippenbau_ruft_die_lippenhaut_statt_abzuspalten(self):
        text = self.quelle('static', 'viewer', 'gemeinsam', 'lippenbau.js')
        self.assertIn("import { Lippenhaut } from './lippenhaut.js';", text)
        anlegen = text.index('geo.userData.lippensaum = Lippenhaut.anlegen(netz, lippen);')
        abspalten = text.index('Lippengruppe.abspalten(geo.index.array, geo.groups, punkte)')
        self.assertLess(anlegen, abspalten)
        self.assertIn('if (geo.userData.lippensaum) { geo.userData.lippen = 0; return 0; }', text)

    def test_detailfarben_zieht_die_uniforms_nach(self):
        text = self.quelle('static', 'viewer', 'gemeinsam', 'detailfarben.js')
        self.assertIn("import { Lippenhaut } from './lippenhaut.js';", text)
        self.assertIn('Lippenhaut.nachziehen(materialien);', text)

    def test_der_server_liefert_punkte_und_saum(self):
        text = self.quelle('core', 'api', 'netzanfrage.py')
        self.assertEqual(text.count('Lippenmaske.lippen(self.geschlecht'), 2)
        self.assertNotIn('Lippenmaske.indizes(', text)
