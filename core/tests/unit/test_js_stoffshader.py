# -*- coding: utf-8 -*-
u"""Stoff im Shader (25.10.2026): `Stoffarten`, `Stoffshader`, `StoffshaderGLSL`, Verdrahtung in `Stoffwerte` und `Stueckstoff`.

Edgar: „beim Regler: Stoff gibt es noch mehr Optionen, siehe die Optionen bei einigen Garments, z.B. die Anzahl der Fäden, Glanz, stoffart
usw. Durchforste alles und baue ein“. Geprüft in Node (die drei Module kommen ohne Three.js aus):

1. Jede Stoffart trägt alle Felder in ihrem Bereich, ihre Bindung kennt der Shader, `werte` liefert eine KOPIE (eine Wahl darf die Tabelle
   nicht verändern, wenn danach ein Regler gezogen wird) und setzt Metall auf 0.
2. `Stoffshader.werte`: Bindung → Nummer, Dichte = uvMeter · 100 · Fäden je cm, „Wie geliefert“ (glatt) → Art 0, fehlende Felder →
   Vorgabe (Glanz 1, Saum 0), Saumfarbe sRGB → linear wie Threes `Color.set` (#ff8000 → 1 / 0,216 / 0), leer = wie der Stoff.
3. `setzen` hängt den Eingriff erst an, wenn er etwas ändert (kein neues Programm für ein unberührtes Stück), danach bleibt es DERSELBE
   Eingriff mit denselben Uniform-Objekten (Three hält sie je Material fest); kein Eingriff an Nicht-Standard-Materialien.
4. `StoffshaderGLSL.einsetzen` trifft vier Stellen; die Einbindungen bleiben stehen; `USE_SHEEN` nur, wo es nicht schon definiert ist.
5. In Python: Die vier Stellen gibt es im Physical-Shader der eingebundenen Three-Fassung; `Stoffwerte` ersetzt die Normalkarte nicht mehr
   (die gebackenen Falten stehen darin), `Genesis9texturen.holen` ruft `stoffnach`, die Garderobe gibt `stoff` beim Neuanziehen weiter.

Im Chrome gemessen (25.10.2026, Mann1, Basic Wear T-Shirt, Nahansicht 0,4 m, 200 × 200 Bildpunkte, Stoff 0,08 grau ohne Bild): mittlere
Nachbardifferenz ohne Bindung 0,44; Leinwand 1,06, Köper 1,25, Satin 1,95, Narbung 6,48, Jersey 9,89 (Struktur 0,6); Köper bei 80 Fäden je cm
0,44 (ausgeblendet). Glanz 0 / 1 / 2: Helligkeit 114,9 / 126,6 / 136,8.

NICHT GELAUFEN beim Schreiben (Tests nur auf Ansage). Sabotage-Gegenprobe zum Ausprobieren: in `Stoffarten.werte` `{ ...a.gewebe }` durch
`a.gewebe` ersetzen → Fall 1 rot; in `Stoffshader.setzen` die Zeile mit `noetig` streichen → Fall 3 rot.
"""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'stoffshader.js')
VIEWER = Path(settings.BASE_DIR) / 'static' / 'viewer'
THREE = Path(settings.BASE_DIR) / 'static' / 'vendor' / 'three' / 'build' / 'three.module.js'

SKRIPT = """
const { Stoffshader } = await import(MODUL);
const { Stoffarten } = await import(new URL('./stoffarten.js', MODUL).href);
const { StoffshaderGLSL } = await import(new URL('./stoffshaderglsl.js', MODUL).href);
const { Shaderpatch } = await import(new URL('./shaderpatch.js', MODUL).href);
const r3 = (x) => Math.round(x * 1000) / 1000;

// 1. Tabelle
for (const [name, a] of Object.entries(Stoffarten.ARTEN)) {
    for (const f of ['rauheit', 'glanz', 'saum', 'saumstreuung']) {
        pruefe(name + ' ' + f + ' im Bereich', typeof a[f] === 'number' && a[f] >= 0 && a[f] <= (f === 'glanz' ? 2 : 1), true);
    }
    pruefe(name + ' Bindung bekannt', Stoffshader.ARTEN[a.gewebe.art] > 0, true);
    pruefe(name + ' Fäden', a.gewebe.faeden > 0, true);
}
const w = Stoffarten.werte('denim');
w.gewebe.faeden = 99;
pruefe('Kopie', Stoffarten.ARTEN.denim.gewebe.faeden, 4);
pruefe('Metall 0', w.metall, 0);
pruefe('unbekannt', Stoffarten.werte('blech'), null);
pruefe('Wahl ohne glatt, mit Narbung', Stoffarten.gewebewahl().map(e => e[0]), ['leinwand', 'koeper', 'jersey', 'satin', 'narbung']);

// 2. Uniforms
const u = Stoffshader.uniforms();
Stoffshader.werte(u, Stoffarten.werte('denim'), 1.085);
pruefe('Köper', u.stoffArt.value, 2);
pruefe('Dichte', r3(u.stoffDichte.value), r3(1.085 * 100 * 4));
pruefe('Glanz Denim', u.stoffSpiegel.value, 0.5);
Stoffshader.werte(u, { gewebe: { art: 'glatt', faeden: 0, staerke: 0 } }, 1);
pruefe('wie geliefert', [u.stoffArt.value, u.stoffStaerke.value, u.stoffSpiegel.value, u.stoffSaum.value], [0, 0, 1, 0]);
Stoffshader.werte(u, { saum: 1, saumfarbe: '#ff8000' }, 0);
pruefe('Saumfarbe linear', [u.stoffSaumEigen.value, r3(u.stoffSaumFarbe.value.r), r3(u.stoffSaumFarbe.value.g), r3(u.stoffSaumFarbe.value.b)], [1, 1, 0.216, 0]);
Stoffshader.werte(u, { saum: 1, saumfarbe: '' }, 0);
pruefe('wie der Stoff', u.stoffSaumEigen.value, 0);
pruefe('ohne Maß 1 m je UV', Stoffshader.dichte(0, 5), 500);

// 3. Anhängen erst bei Bedarf, danach dieselben Uniforms
const mat = () => ({ isMaterial: true, isMeshStandardMaterial: true, userData: {} });
const m = mat();
pruefe('unberührt: kein Eingriff', [Stoffshader.setzen(m, { rauheit: 0.5 }, 1), Shaderpatch.hat(m, 'stoffshader')], [false, false]);
Stoffshader.setzen(m, Stoffarten.werte('seide'), 1);
const erst = Stoffshader.stand(m);
Stoffshader.setzen(m, { glanz: 1 }, 1);
pruefe('derselbe Eingriff', Stoffshader.stand(m) === erst, true);
pruefe('zurück auf neutral', [erst.stoffArt.value, erst.stoffSpiegel.value, erst.stoffSaum.value], [0, 1, 0]);
pruefe('kein Standard-Material', Stoffshader.setzen({ isMaterial: true, userData: {} }, Stoffarten.werte('seide'), 1), false);

// 4. Shadertext
const shader = { uniforms: {}, vertexShader: 'a\\n#include <uv_vertex>\\nb',
    fragmentShader: '#define STANDARD\\n#include <common>\\n#include <normal_fragment_maps>\\n#include <clearcoat_normal_fragment_begin>\\n'
        + '#include <lights_physical_fragment>\\n#include <lights_fragment_begin>' };
const stellen = Stoffshader.patchen(shader, Stoffshader.uniforms());
pruefe('vier Stellen', stellen, 4);
for (const inc of ['uv_vertex']) pruefe('bleibt ' + inc, shader.vertexShader.includes('#include <' + inc + '>'), true);
for (const inc of ['common', 'clearcoat_normal_fragment_begin', 'lights_fragment_begin', 'normal_fragment_maps']) {
    pruefe('bleibt ' + inc, shader.fragmentShader.includes('#include <' + inc + '>'), true);
}
pruefe('Bindung nach den Normalkarten', shader.fragmentShader.indexOf('stoffSicht') > shader.fragmentShader.indexOf('#include <normal_fragment_maps>'), true);
pruefe('Saum nach lights_physical_fragment', shader.fragmentShader.indexOf('material.sheenColor =') > shader.fragmentShader.indexOf('#include <lights_physical_fragment>'), true);
pruefe('USE_SHEEN nur bedingt', /#ifndef USE_SHEEN\\s+#define USE_SHEEN\\s+#endif/.test(shader.fragmentShader), true);
pruefe('Uniforms am Shader', Object.keys(shader.uniforms).filter(k => k.startsWith('stoff')).length, 8);
console.log('ok');
"""


class StoffshaderTest(SimpleTestCase):

    def test_stoffarten_uniforms_eingriff_und_shadertext(self):
        self.assertIn('ok', MODUL.laufen(SKRIPT))

    def test_stellen_gibt_es_im_physical_shader_der_three_fassung(self):
        text = THREE.read_text(encoding='utf-8')
        fragment = re.search(r'const fragment\$\d+ = "#define STANDARD\\n#ifdef PHYSICAL.*?";', text)
        self.assertIsNotNone(fragment, 'Physical-Fragment-Shader nicht gefunden')
        for stelle in ('#include <common>', '#include <clearcoat_normal_fragment_begin>', '#include <lights_physical_fragment>',
                       '#include <lights_fragment_begin>', '#ifdef USE_SHEEN\\n\\tuniform vec3 sheenColor;'):
            self.assertIn(stelle, fragment.group(0), stelle)
        self.assertIn("'attribute vec2 uv;'", text, 'uv ist im Vertex-Vorspann nicht mehr unbedingt deklariert')

    def test_verdrahtung(self):
        stoffwerte = (VIEWER / 'gemeinsam' / 'stoffwerte.js').read_text(encoding='utf-8')
        self.assertNotIn('material.normalMap =', stoffwerte, 'das Gewebe ersetzt wieder die Normalkarte (und mit ihr die Falten)')
        self.assertIn('Stoffshader.setzen(material, stoff', stoffwerte)
        self.assertIn('daten.stoffnach =', stoffwerte)
        texturen = (VIEWER / 'gemeinsam' / 'genesis9texturen.js').read_text(encoding='utf-8')
        self.assertIn('material.userData?.stoffnach?.()', texturen)
        garderobe = (VIEWER / 'charakter' / 'genesis9' / 'genesis9garderobe.js').read_text(encoding='utf-8')
        self.assertIn('stoff: bisher.stoff', garderobe, 'ein Variantenwechsel verlöre die Stoffwerte')
        stueck = (VIEWER / 'charakter' / 'genesis9' / 'stueckstoff.js').read_text(encoding='utf-8')
        for feld in ('stoffart', 'glanz', 'saum', 'saumstreuung', 'saumfarbe', 'relief', 'faeden', 'staerke'):
            self.assertIn(f"'{feld}'", stueck, feld)
