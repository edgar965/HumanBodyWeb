# -*- coding: utf-8 -*-
u"""Eigene Kleider, Stufe K2b und Kragen (25.10.2026 nachts): Stoff an den eigenen Stücken, Socken, Halsansatz, Kragen als Fläche.

Edgar: Stoffregler (Stoffart, Webart, Fäden je cm, Glanz, Glanzsaum, Relief) auch an den eigenen Stücken; Flecken oben an den Schultern; Socken als eigenes
Stück (Sitz 1–4 mm); Kragen mit echter Geometrie, der am Ausschnitt ansetzt und Regler hat. Geprüft in Node (die Module kommen ohne Three.js aus, außer
`Eigenkragengeometrie`/`Eigenkragen`, die hier nicht geladen werden):

1. `Eigenkleidstoff`: eine Stoffart wird zu Zahlen in den Reglern (Index, Prozent, −1 = keine Saumfarbe) und zurück zum Objekt für `Stoffshader.werte`;
   jede Bindung der Auswahl ist eine des Shaders; Relief setzt die Stoffart nicht (wie am Daz-Stück).
2. `Eigenkleidwerte`: Socken sind Art 3 mit Bündchen und Sitz Fuß/Schaft, im Korridor 1–4 mm begrenzt; `shaderwerte` behält alle alten Schlüssel (der
   Rufer der anderen Sitzung liest sie) und bringt `stoff`, `metall`, `relief`, `gestalt` dazu; eine Farbe mit `leer` darf −1 sein.
3. `Eigenkragenlinie.hals` rechnet dieselbe Kante wie `kkHals` im Shader (Mitte vorn, außerhalb der Breite, Stehkragen); `stufe` findet auf einem
   Kunstzylinder (Halbmesser 6 cm) den Ring in allen Fächern im richtigen Abstand.
4. `Koerperkoordinatenpunkte.ansatz`: Rumpfpunkte bekommen die Höhe des untersten Halspunkts ihres Winkels, Beinpunkte 0; `_naegel`: Zehennägel
   bekommen die Kette ihres Fußes (+x = links = 10), schon belegte Punkte bleiben.
5. Shadertext: `EigenkleidGLSL.patchen` ohne `uKkRelief` im Aufruf setzt die Vorgabe 1 (abwärtskompatibel); die Kante zieht den Halsansatz ab;
   `EigenkragenGLSL.patchen` trifft drei Stellen und schiebt nach der Schale (`transformed += kgV` hinter dem Text der Schale).

Im Chrome gemessen (25.10.2026 nachts, DamiraAlt; Werkzeug `ProjektTemp/_wegwerf/eigenkleider/k2b_hilfen.js`): Socken-Abstand an der Silhouette Knöchel
1,81 / 1,89 mm (Schaft 2 mm), Ferse 1,41 mm (Fuß 1,5 mm); Kragenregler 0,5–0,8 ms je Eingabe ohne Neubau, Ausschnittregler mit Kragen 44–81 ms (Neubau
des Kragennetzes, 4.640 Punkte).

NICHT GELAUFEN beim Schreiben (Tests nur auf Ansage). Sabotage-Gegenprobe zum Ausprobieren: in `Eigenkleidstoff.ausStoffart` `relief` mitsetzen → Fall 1
rot; in `Eigenkleidwerte._begrenzen` `f.leer && w < 0 ? -1 :` streichen → Fall 2 rot; in `Eigenkragenlinie.hals` den Übergang (0,35) ändern → Fall 3 rot.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'eigenkleidwerte.js')

SKRIPT = """
const { Eigenkleidwerte } = await import(MODUL);
const { Eigenkleidstoff } = await import(new URL('./eigenkleidstoff.js', MODUL).href);
const { Stoffarten } = await import(new URL('./stoffarten.js', MODUL).href);
const { Eigenkragenlinie } = await import(new URL('./eigenkragenlinie.js', MODUL).href);
const { Koerperkoordinatenpunkte } = await import(new URL('./koerperkoordinatenpunkte.js', MODUL).href);
const { EigenkleidGLSL } = await import(new URL('./eigenkleidglsl.js', MODUL).href);
const { EigenkragenGLSL } = await import(new URL('./eigenkragenglsl.js', MODUL).href);
const r4 = (x) => Math.round(x * 10000) / 10000;

// 1. Stoff als Zahlen
const denim = Eigenkleidstoff.ausStoffart('denim');
pruefe('Denim Index', Eigenkleidstoff.STOFFARTEN[denim.stoffart], 'denim');
pruefe('Denim Köper', Eigenkleidstoff.GEWEBE[denim.gewebe], 'koeper');
pruefe('Relief bleibt', 'relief' in denim, false);
pruefe('Saumfarbe keine', denim.glanzsaum_farbe, -1);
const s = Eigenkleidstoff.stoff({ ...denim, relief: 100 });
pruefe('zurück', [s.stoffart, s.gewebe.art, s.gewebe.faeden, r4(s.gewebe.staerke), r4(s.glanz), r4(s.rauheit), s.saumfarbe], ['denim', 'koeper', 4, 0.6, 0.5, 0.9, '']);
pruefe('ohne Gewebe', Eigenkleidstoff.stoff({ gewebe: 0 }).gewebe, { art: 'glatt', faeden: 0, staerke: 0 });
pruefe('Farbe', Eigenkleidstoff.hex(0xff8000), '#ff8000');
const wahl = Stoffarten.gewebewahl().map(e => e[0]);
for (const g of Eigenkleidstoff.GEWEBE.slice(1)) pruefe('Bindung ' + g, wahl.includes(g), true);
pruefe('unbekannt', Eigenkleidstoff.ausStoffart('blech'), null);

// 2. Socken und Schnittstelle
pruefe('Socke Nummer', Eigenkleidwerte.ARTEN.socke.nummer, 3);
const inst = { regler: {} };
const w0 = Eigenkleidwerte.shaderwerte('socke', Eigenkleidwerte.alle(inst, 'socke'));
pruefe('Socke Vorgabe', [w0.saum[0], r4(w0.sitz[0]), r4(w0.sitz[1])], [0.8, 0.0015, 0.002]);
Eigenkleidwerte.setzen(inst, 'socke', 'sitz_fuss', 9);
pruefe('Korridor', inst.regler['kleid:socke:sitz_fuss'], 4);
Eigenkleidwerte.setzen(inst, 'socke', 'glanzsaum_farbe', -1);
pruefe('leere Farbe', Eigenkleidwerte.wert(inst, 'socke', 'glanzsaum_farbe'), -1);
const wo = Eigenkleidwerte.shaderwerte('oberteil', Eigenkleidwerte.alle({ regler: {} }, 'oberteil'));
for (const k of ['saum', 'sitz', 'hals', 'kragen', 'band', 'bruecke', 'falten', 'rauheit', 'farbe', 'stoff', 'metall', 'relief', 'gestalt']) pruefe('Schlüssel ' + k, k in wo, true);
pruefe('Kragen aus', wo.gestalt.map(r4), [0, 0.038, 0.014, 0.003]);
pruefe('Relief 1', wo.relief, 1);

// 3. Kante wie im Shader
const w = { form: 0, tiefe: 0.07, hinten: 0.02, breite: 0.18, laenge: 0.56, steh: 0.025 };
pruefe('vorn Mitte', r4(Eigenkragenlinie.hals(0.1, 0, 1, w)), r4((0.1 - 0.07) * 0.56));
pruefe('hinten Mitte', r4(Eigenkragenlinie.hals(0.1, 0, -1, w)), r4((0.1 - 0.02) * 0.56));
pruefe('außerhalb', r4(Eigenkragenlinie.hals(0.1, 0.2, 1, w)), r4(0.1 * 0.56));
pruefe('Stehkragen', r4(Eigenkragenlinie.hals(0.1, 0, 1, { ...w, form: 4 })), r4(0.1 * 0.56 + 0.025));
const ringe = 20, je = 256, pos = [], koord = [], dreiecke = [];          // 256 Spalten: 512 Schnittpunkte je Ring > 240 Fächer
for (let i = 0; i < ringe; i++) for (let k = 0; k < je; k++) {
    const phi = 2 * Math.PI * (k + 0.5) / je, y = 1.4 - 0.005 * i;        // halber Schritt: kein Punkt genau auf x = 0 (dort griffe die Ausschnittform)
    pos.push(0.06 * Math.sin(phi), y, 0.06 * Math.cos(phi));
    koord.push(1, -0.5, (1.4 - y) / 0.56 - 0.05, (k + 0.5) / je);
}
for (let i = 0; i + 1 < ringe; i++) for (let k = 0; k < je; k++) {
    const a = i * je + k, b = i * je + (k + 1) % je, c = a + je, d = b + je;
    dreiecke.push(a, b, c, b, d, c);
}
const ww = { ...w, breite: 0.001 };
const f = Eigenkragenlinie.feld(Float32Array.from(pos), Float32Array.from(koord), null, Uint32Array.from(dreiecke), ww);
const linie = Eigenkragenlinie.stufe(Float32Array.from(pos), Uint32Array.from(dreiecke), f, 0, { cx: 0, cz: 0 });
pruefe('Ring gefunden', linie !== null, true);
pruefe('alle Fächer', linie.besetzt, Eigenkragenlinie.FAECHER);
const p = Eigenkragenlinie.wert(Float32Array.from(pos), 3, linie.punkte[0]);
pruefe('Abstand 6 cm', r4(Math.hypot(p[0], p[2])) <= 0.06 && r4(Math.hypot(p[0], p[2])) > 0.059, true);
pruefe('Höhe am Ansatz', r4(p[1]), r4(1.4 - 0.05 * 0.56));

// 4. Halsansatz und Zehennägel
const n = 6, kk = { kette: Uint8Array.from([6, 6, 1, 1, 4, 6]), anteil: new Float32Array(n), hoehe: Float32Array.from([-0.03, -0.05, -0.02, 0.1, 1.2, -0.09]),
    winkel: Float32Array.from([0.01, 0.02, 0.014, 0.5, 0.3, 0.5]) };
const ansatz = Koerperkoordinatenpunkte.ansatz(kk);
pruefe('Bein ohne Ansatz', ansatz[4], 0);
pruefe('vorn höher als hinten', ansatz[2] > ansatz[3], true);
pruefe('hinten am Halspunkt', ansatz[3] < -0.05, true);
const aus = { kette: Uint8Array.from([0, 0, 4]), anteil: new Float32Array(3), hoehe: new Float32Array(3), winkel: new Float32Array(3) };
Koerperkoordinatenpunkte._naegel(aus, Float32Array.from([0.1, 0, 0, -0.1, 0, 0, 0.1, 0, 0]), Uint32Array.from([0, 1, 2]), [{ start: 0, count: 3, materialIndex: 0 }],
    [{ userData: { gruppe: 'Toenails' } }]);
pruefe('Nägel', Array.from(aus.kette), [10, 11, 4]);

// 5. Shadertext
const roh = () => ({ uniforms: {}, vertexShader: '#include <common>\\n#include <morphnormal_vertex>\\n#include <morphtarget_vertex>\\n',
    fragmentShader: '#include <common>\\n#include <clipping_planes_fragment>\\n#include <color_fragment>\\n#include <normal_fragment_maps>\\n' });
const sh = roh();
pruefe('alle Stellen', EigenkleidGLSL.patchen(sh, { uKkArt: { value: 3 } }), []);
pruefe('Relief Vorgabe', sh.uniforms.uKkRelief.value, 1);
pruefe('Rufer gewinnt', sh.uniforms.uKkArt.value, 3);
pruefe('Ansatz in der Kante', sh.fragmentShader.includes('h - vKkAnsatz'), true);
const kr = roh();
pruefe('Kragen drei Stellen', EigenkragenGLSL.patchen(kr, { uKgGestalt: { value: [2, 0.04, 0.01, 0.003] } }), []);
pruefe('erst Schale, dann Kragen', kr.vertexShader.indexOf('transformed += kgV') > kr.vertexShader.indexOf('kkSitz'), true);
console.log('ok');
"""


class EigenkleidK2bTest(SimpleTestCase):

    def test_stoff_socken_kante_ansatz_und_shadertext(self):
        self.assertIn('ok', MODUL.laufen(SKRIPT))
