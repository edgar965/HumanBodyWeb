# -*- coding: utf-8 -*-
u"""`Stoffoberflaeche` (`gemeinsam/stoffoberflaeche.js`): die Haut der Figur als
Körper für den Stoffschwung — Stichprobe der Hautpunkte mit Normalen, je Bild
gehäutet und in ein Raster gelegt; ein freier Stoffpunkt hinter seinem
nächsten Hautpunkt wird entlang dessen Normale auf `abstand` davor gesetzt.

WARUM (20.09.2026, Edgar mit Bild: HumanBody im Dancing Queen Dress, der Rock
im Becken): Die Kapseln sind je Knochen eine Kegelkapsel; was die Haut
daneben tut (Gesäß, Bauch, das Becken ohne eigenen Rigify-Knochen), sieht
keine. Gemessen im Browser: Ursula Idle Haut p1 −8 mm, Jump −31 mm; HumanBody
Idle −39 mm ab dem ersten Bild — bei einem Kleid, das in Ruhe nirgends tiefer
als 3,8 mm in der Haut liegt. Das Maß der Probe (`Kleidungsmass.tiefen`) ist
genau „nächster Hautpunkt, seine Normale" — dagegen wird jetzt gerechnet.

Der Körper hier: eine Kugel (Radius 10 cm, 2.000 Punkte, Normalen nach außen)
als ein Knochen.
1. Identisch gehäutet liegen die Weltpunkte auf der Ruhe; ein Stoffpunkt 1 cm
   in der Kugel kommt auf Radius 10 cm + Abstand (auf 2 mm, die Stichprobe ist
   1 cm grob); einer 2 cm davor bleibt, wo er ist; einer 40 cm weit weg auch
   (außer Reichweite); ein gebundener Punkt (Freiheit 0) in der Kugel bleibt drin.
2. Der Knochen um 1 m nach oben verschoben: die Kugel wandert mit, ein
   Stoffpunkt in der verschobenen Kugel wird herausgesetzt, einer an der
   alten Stelle nicht mehr.

3. Gedächtnis (20.09.2026, `hinaus` kostete 24 ms von 62 je Bild): Ruht alles,
   sucht ein Punkt 3 cm vor der Haut kein zweites Mal (`naechster` gezählt), einer
   auf `abstand` schon. Rückt die Kugel 2,5 cm auf ihn zu, wird er gesucht und auf
   10,6 cm vor die neue Mitte gesetzt.

Sabotage-Gegenprobe: in `hinaus` `s >= abstand` durch `true` ersetzen → Fall 1
rot (der Punkt bleibt drin); `haeuten` ohne `W`-Verschiebung → Fall 2 rot; in
`hinaus` die Schranke ohne den Weg (`- 2 * (...)` weg) → Fall 3 rot (der Punkt
bleibt bei 13,0 cm, weil niemand mehr nachsieht).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'stoffoberflaeche.js')

SKRIPT = """
const { Stoffoberflaeche: O } = await import(MODUL);
const N = 2000, R = 0.10, pos = new Float32Array(N * 3), nrm = new Float32Array(N * 3);
const index = new Float32Array(N * 4), gewicht = new Float32Array(N * 4);
for (let i = 0; i < N; i++) {                       // Fibonacci-Kugel
    const y = 1 - 2 * (i + 0.5) / N, r = Math.sqrt(1 - y * y), phi = i * 2.399963;
    const x = r * Math.cos(phi), z = r * Math.sin(phi);
    nrm.set([x, y, z], 3 * i); pos.set([R * x, R * y, R * z], 3 * i);
    gewicht[4 * i] = 1;
}
const o = new O({ n: N, pos, nrm, index, gewicht });
const E = new Float32Array([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]);
const abstand = 0.006;
// --- 1. identisch gehäutet -------------------------------------------------
o.haeuten(E, E);
let ruheAbweichung = 0;
for (let i = 0; i < 3 * N; i++) ruheAbweichung = Math.max(ruheAbweichung, Math.abs(o.welt[i] - pos[i]));
const x = new Float32Array([0.09, 0, 0,   0, 0.12, 0,   0, 0, 0.5,   0.05, 0.05, 0.05]);
const frei = new Float32Array([1, 1, 1, 0]);
o.hinaus(x, frei, 4, abstand);
const rad = (k) => Math.hypot(x[3 * k], x[3 * k + 1], x[3 * k + 2]);
// --- 2. der Knochen 1 m höher ------------------------------------------------
const T = Float32Array.from(E); T[13] = 1.0;
o.haeuten(T, E);
const y2 = new Float32Array([0.09, 1.0, 0,   0.09, 0, 0]);
o.hinaus(y2, new Float32Array([1, 1]), 2, abstand);
console.log(JSON.stringify({
    ruhe_abweichung_mm: +(ruheAbweichung * 1000).toFixed(3),
    drin_cm: +(rad(0) * 100).toFixed(2), davor_cm: +(rad(1) * 100).toFixed(2),
    fern_cm: +(rad(2) * 100).toFixed(2),
    gebunden_cm: +(rad(3) * 100).toFixed(2),
    oben_cm: +(Math.hypot(y2[0], y2[1] - 1.0, y2[2]) * 100).toFixed(2),
    unten_cm: +(Math.hypot(y2[3], y2[4], y2[5]) * 100).toFixed(2),
}));
"""

GEDAECHTNIS = """
const { Stoffoberflaeche: O } = await import(MODUL);
const N = 2000, R = 0.10, pos = new Float32Array(N * 3), nrm = new Float32Array(N * 3);
const index = new Float32Array(N * 4), gewicht = new Float32Array(N * 4);
for (let i = 0; i < N; i++) {
    const y = 1 - 2 * (i + 0.5) / N, r = Math.sqrt(1 - y * y), phi = i * 2.399963;
    nrm.set([r * Math.cos(phi), y, r * Math.sin(phi)], 3 * i);
    pos.set([R * r * Math.cos(phi), R * y, R * r * Math.sin(phi)], 3 * i);
    gewicht[4 * i] = 1;
}
const o = new O({ n: N, pos, nrm, index, gewicht });
const E = new Float32Array([1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]);
const abstand = 0.006, frei = new Float32Array([1, 1]);
const x = new Float32Array([0.13, 0, 0,   0.106, 0, 0]);      // 3 cm davor; genau auf `abstand`
let gesucht = [];
const echt = o.naechster.bind(o);
o.naechster = (px, py, pz) => { gesucht.push(+px.toFixed(3)); return echt(px, py, pz); };
o.haeuten(E, E); o.hinaus(x, frei, 2, abstand);
const erstes = gesucht.length;
gesucht = []; o.haeuten(E, E); o.hinaus(x, frei, 2, abstand);          // nichts bewegt
const ruhe = gesucht.slice();
const T = Float32Array.from(E); T[12] = 0.025;          // die Kugel rückt 2,5 cm auf den Punkt zu
gesucht = []; o.haeuten(T, E); o.hinaus(x, frei, 2, abstand);
console.log(JSON.stringify({ erstes, ruhe_gesucht: ruhe, dann_gesucht: gesucht,
                             punkt_cm: +(x[0] * 100).toFixed(2) }));
"""


class StoffoberflaecheTest(SimpleTestCase):

    databases = set()

    #: So grob ist die Kugel aus 2.000 Punkten (Punktabstand ~1 cm): Toleranz auf den Radius.
    TOLERANZ_CM = 0.2

    def test_1_ein_punkt_in_der_haut_kommt_vor_die_haut(self):
        a = MODUL.laufen(SKRIPT)
        self.assertLess(a['ruhe_abweichung_mm'], 0.01, a)
        self.assertAlmostEqual(a['drin_cm'], 10.6, delta=self.TOLERANZ_CM,
                               msg='1 cm in der Kugel: liegt nach `hinaus` bei %.2f cm statt 10,6'
                                   % a['drin_cm'])
        self.assertAlmostEqual(a['davor_cm'], 12.0, delta=1e-3, msg='vor der Haut verschoben: %s' % a)
        self.assertAlmostEqual(a['fern_cm'], 50.0, delta=1e-3, msg='außer Reichweite verschoben: %s' % a)
        self.assertAlmostEqual(a['gebunden_cm'], 8.66, delta=0.01, msg='gebundener Punkt verschoben: %s' % a)

    def test_2_die_haut_wandert_mit_dem_knochen(self):
        a = MODUL.laufen(SKRIPT)
        self.assertAlmostEqual(a['oben_cm'], 10.6, delta=self.TOLERANZ_CM, msg=a)
        self.assertAlmostEqual(a['unten_cm'], 9.0, delta=1e-3,
                               msg='an der alten Stelle noch herausgesetzt: %s' % a)

    def test_3_das_gedaechtnis_spart_die_suche_und_verpasst_die_haut_nicht(self):
        a = MODUL.laufen(GEDAECHTNIS)
        self.assertEqual(a['erstes'], 2, 'beim ersten Mal wird jeder Punkt gesucht: %s' % a)
        self.assertEqual(a['ruhe_gesucht'], [0.106],
                         'ruht alles, sucht nur der Punkt auf `abstand` noch einmal: %s' % a)
        self.assertIn(0.13, a['dann_gesucht'], 'die Kugel kam 2,5 cm näher, der Punkt sah nicht nach: %s' % a)
        self.assertAlmostEqual(a['punkt_cm'], 13.1, delta=self.TOLERANZ_CM,
                               msg='3 cm davor, Kugel 2,5 cm näher: liegt bei %.2f cm statt 13,1'
                                   % a['punkt_cm'])
