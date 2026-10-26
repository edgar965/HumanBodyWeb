# -*- coding: utf-8 -*-
u"""`Dazschnittwerte` und `DazschnittGLSL` — Eigen-Einstellungen an Daz-Stücken, nur Wegschneiden (Stufe K2c, 25.10.2026).

WARUM (Edgar, 25.10.2026: „könnte man diese Einstellungen auch an alle existierenden Genesis-Teile anhängen?“): Ausschnitt und Säume an fertigen Daz-Stücken
schneiden nur weg; dieselbe Kante je Punkt (Index, `Dazschnitt.wegflaechen`) und je Pixel (Shader). In Node, ohne Three.js:

1. Vorgabe („wie geliefert“): kein Shader nötig, jede Kante 1 — ein Stück, an dem niemand dreht, bleibt unverändert.
2. Ausschnitt: über der Tiefe fällt weg, darunter bleibt; V ist an der Seite flacher als rund; ein Punkt ohne Kette wird nie geschnitten; gemessen ab dem
   Halsansatz je Umfangswinkel — der Trapezmuskel außerhalb der Breite bleibt (im Chrome: ab der Ebene durch das Halsgelenk fielen 9.018 Dreiecke mehr weg,
   y 1,35–1,40 m, |x| im Median 7,4 cm).
3. Ärmel: die Hand fällt ganz weg, der Oberarm jenseits des Anteils; ein Rumpfpunkt an der Flanke UNTER der Achsel bleibt (`ACHSEL_H`, im Chrome gesehen: ein
   Loch in der Seite bei Ärmel 12 %), einer an der Schulter fällt.
4. Hosenbein, Bund, Saum: Fuß weg, Knie jenseits 40 % weg, Oberschenkel bleibt; Bund tiefer schneidet den Rumpf darüber, nicht das Bein.
5. `ohne`: die `schnitt:`-Werte gehen nicht an den Server; `setzen` schreibt nur in ein getragenes Stück und löscht die Vorgabe.
6. `DazschnittGLSL.patchen`: alle sechs Stellen eingesetzt; fehlt eine, bleibt der Shader unverändert.

Geschrieben 25.10.2026, NICHT gelaufen (Tests nur auf Ansage). Sabotage-Gegenprobe (nicht gefahren): in `kante` den Achsel-Zuschlag weglassen → Fall 3 rot;
in `patchen` `if (!fehlt.length)` weglassen → Fall 6 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

WERTE = Jsmodul('gemeinsam', 'dazschnittwerte.js')
GLSL = Jsmodul('gemeinsam', 'dazschnittglsl.js')

SKRIPT = """
const { Dazschnittwerte: W } = await import(MODUL);
const L = [0.6, 0.5, 0.8];
const vorgabe = W.shaderwerte(W.alle({}));
// 1. Vorgabe
pruefe('nicht noetig', W.noetig(W.alle({})), false);
for (const [k, t, h] of [[1, -0.5, 0.2], [6, -0.5, -0.1], [2, 0.3, 0.2], [8, -0.5, 0.9], [4, 0.5, 1.4], [10, -0.5, 2.2]]) {
    pruefe('vorgabe ' + k, W.kante(k, t, h, 0, 1, vorgabe, L), 1);
}
// 2. Ausschnitt rund 15 % vorn, Breite 180 mm
const rund = W.shaderwerte(W.alle({ 'schnitt:ausschnitt_form': 1, 'schnitt:ausschnitt': 0.15 }));
pruefe('noetig', W.noetig(W.alle({ 'schnitt:ausschnitt_form': 1 })), true);
pruefe('Hals vorn weg', W.kante(6, -0.5, -0.05, 0, 1, rund, L) < 0, true);
pruefe('ueber der Tiefe weg', W.kante(1, -0.5, 0.10, 0, 1, rund, L) < 0, true);
pruefe('unter der Tiefe bleibt', W.kante(1, -0.5, 0.20, 0, 1, rund, L) > 0, true);
const v = W.shaderwerte(W.alle({ 'schnitt:ausschnitt_form': 2, 'schnitt:ausschnitt': 0.15 }));
pruefe('rund an der Seite tiefer als V', W.kante(1, -0.5, 0.10, 0.04, 1, rund, L) < 0 && W.kante(1, -0.5, 0.10, 0.04, 1, v, L) > 0, true);
pruefe('ohne Kette nie', W.kante(0, 0, -0.3, 0, 1, rund, L), 1);
// Trapezmuskel seitlich (x 12 cm, ausserhalb der Breite): ueber der Ebene durch das Halsgelenk (h -0,05), aber unter dem Halsansatz (-0,09) — bleibt
pruefe('Trapez ab Halsansatz bleibt', W.kante(1, -0.5, -0.05, 0.12, 0, rund, L, -0.09) > 0, true);
pruefe('Trapez ab Ebene fiele', W.kante(1, -0.5, -0.05, 0.12, 0, rund, L, 0) < 0, true);
// 3. Ärmel 12 %
const arm = W.shaderwerte(W.alle({ 'schnitt:aermel': 0.12 }));
pruefe('Hand weg', W.kante(8, -0.5, 0.9, 0.3, 0, arm, L), -1);
pruefe('Oberarm jenseits weg', W.kante(2, 0.3, 0.2, 0.2, 0, arm, L) < 0, true);
pruefe('Oberarm diesseits bleibt', W.kante(2, 0.05, 0.15, 0.2, 0, arm, L) > 0, true);
pruefe('Flanke unter der Achsel bleibt', W.kante(1, 0.25, 0.35, 0.15, 0, arm, L) > 0, true);
pruefe('Schulter faellt', W.kante(1, 0.25, 0.10, 0.15, 0, arm, L) < 0, true);
// 4. Hosenbein 40 %, Bund tiefer 0,78, Saum unten 1,2
const hose = W.shaderwerte(W.alle({ 'schnitt:bein': 0.4, 'schnitt:bund': 0.78 }));
pruefe('Fuss weg', W.kante(10, -0.5, 2.2, 0.1, 1, hose, L), -1);
pruefe('Knie weg', W.kante(4, 0.49, 1.45, 0.1, 1, hose, L) < 0, true);
pruefe('Oberschenkel bleibt', W.kante(4, 0.2, 1.2, 0.1, 1, hose, L) > 0, true);
pruefe('Rumpf ueber dem Bund weg', W.kante(1, -0.5, 0.7, 0, 1, hose, L) < 0, true);
pruefe('Bein unter dem Bund bleibt', W.kante(5, 0.1, 1.1, -0.1, 1, hose, L) > 0, true);
const saum = W.shaderwerte(W.alle({ 'schnitt:saum': 1.2 }));
pruefe('Saum: Knie weg', W.kante(4, 0.49, 1.45, 0.1, 1, saum, L) < 0, true);
pruefe('Saum: Arm bleibt', W.kante(2, 0.9, 1.45, 0.3, 0, saum, L), 1);
// 5. ohne, setzen, anzeige
pruefe('ohne', W.ohne({ 'schnitt:saum': 1, 'passform:weite': 2 }), { 'passform:weite': 2 });
pruefe('ohne leer', W.ohne(undefined), {});
const inst = { kleidung: { shirt: { regler: { a: 1 } } } };
pruefe('setzen', W.setzen(inst, 'shirt', 'ausschnitt', 0.2004), true);
pruefe('gerundet', inst.kleidung.shirt.regler['schnitt:ausschnitt'], 0.2);
W.setzen(inst, 'shirt', 'ausschnitt', 0.07);
pruefe('Vorgabe geloescht', 'schnitt:ausschnitt' in inst.kleidung.shirt.regler, false);
pruefe('nicht getragen', W.setzen(inst, 'hose', 'bein', 0.5), false);
pruefe('anzeige aus', W.anzeige({ aus: 1.2, einheit: 'Arm' }, 1.2), 'wie geliefert');
console.log(JSON.stringify({ ok: true }));
"""

PATCH = """
const { DazschnittGLSL } = await import(MODUL);
const voll = () => ({ uniforms: {}, vertexShader: '#include <common>\\n#include <begin_vertex>\\n',
    fragmentShader: '#include <common>\\n#include <clipping_planes_fragment>\\n#include <color_fragment>\\n#include <normal_fragment_maps>\\n' });
const s = voll();
pruefe('alle Stellen', DazschnittGLSL.patchen(s, { uDkHals: { value: [] } }), []);
pruefe('Attribut', s.vertexShader.includes('attribute vec4 dkKoord'), true);
pruefe('Schnitt', s.fragmentShader.includes('if ( dkF < 0.0 ) discard;'), true);
pruefe('Achsel eingesetzt', /ACHSEL_H|ACHSEL_STEIGUNG/.test(s.fragmentShader), false);
pruefe('Uniforms', 'uDkHals' in s.uniforms, true);
const t = voll(); t.fragmentShader = t.fragmentShader.replace('#include <normal_fragment_maps>', '');
const vorher = t.fragmentShader;
pruefe('fehlt', DazschnittGLSL.patchen(t, {}), ['normal_fragment_maps']);
pruefe('unveraendert', t.fragmentShader, vorher);
console.log(JSON.stringify({ ok: true }));
"""


class DazschnittwerteTest(SimpleTestCase):
    databases = set()

    def test_vorgabe_ausschnitt_aermel_hose_und_ablage(self):
        self.assertEqual(WERTE.laufen(SKRIPT), {'ok': True})

    def test_shader_eingriff_ganz_oder_gar_nicht(self):
        self.assertEqual(GLSL.laufen(PATCH), {'ok': True})
