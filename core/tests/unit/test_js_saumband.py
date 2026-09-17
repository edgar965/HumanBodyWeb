# -*- coding: utf-8 -*-
u"""`Saumband`: verdeckte Haut neben der gezeichneten bleibt gezeichnet,
mit dem Abstand versenkt.

WARUM (Edgar, 13.09.2026, Bild vom Ärmel in einer Tanzpose: „Offenbar wird
kein Skin erzeugt unter dem T-Shirt, dann kommt der Ärmel von der anderen
Körperseite durch"): Die Maske reichte an der anliegenden Kante bis zum
Saum, dahinter war keine Haut — wer in die Ärmelöffnung sah, sah die
andere Ärmelwand. Geprüft mit Attrappen:

1. `abstaende`: gezeichnete Punkte 0, verdeckte der Weg AUF DER HAUT zum
   nächsten gezeichneten (Streifen aus Dreiecken: 2, 5, 9, 15 mm), jenseits
   von `BAND_M` `Infinity` — und ein Punkt, der im Raum 2 mm neben einer
   Quelle liegt, aber nur über 40 mm Netzkanten erreichbar ist, bekommt 42;
   ein deckungsgleicher Zwilling ohne eigene Dreiecke den Weg seines Zwillings.
2. `tiefe`: 1 mm + Weg, höchstens `TIEFE_M` — 3, 6, 10, 10 mm; fern 10.
3. `weg`: nur verdeckt UND jenseits des Bands.
4. `Hauteinzug.EINZUG_M` ist `Saumband.TIEFE_M` — eine Quelle.
5. `Hautmaskegeometrie.normalen`: deckungsgleiche Punkte (Naht) teilen
   sich eine Normale — an der Rückenmitte zog der Einzug die Zwillinge
   sonst 1 mm auseinander, ein Spalt über dem Bund.

6. `Hautwege.wege` in double (13.09.2026, Szene eingefroren): Punkt 1 liegt
   bei (11, 5, 3) mm, sein Weg 12,4499 mm rundet in float32 AUF; sein
   Zwilling haengt an einer Kante der Laenge 0. Mit `weg` als Float32Array
   blieb `d < weg[j]` fuer beide wahr, und sie schoben sich endlos
   gegenseitig in die Halde — der Wächter meldet das als Fehler.

Sabotage-Gegenproben: in `Hautwege.wege` die Reichweite nicht anwenden →
der ferne Punkt bekommt einen Weg statt `Infinity` → Fall 1 und 3 rot;
`_naehteVereinen` nicht aufrufen → Fall 5 rot; `weg` als Float32Array →
Fall 6 wirft „Endlosschleife".
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'saumband.js')

SKRIPT = """
const { Saumband: S } = await import(MODUL);
const nah = (was, a, b) => {
    if (Math.abs(a - b) > 1e-7) throw new Error(was + ': ' + a + ' statt ' + b);
};
// Ein Streifen: Punkte 0..6 auf y=0 (x = 0, 2, 5, 9, 15, 45, 400 mm), Punkte
// 7..13 darüber auf y=0,01 (Dreiecke dazwischen); gezeichnet sind 0 und 7.
// Punkt 14 liegt im Raum 2 mm neben Punkt 0, hängt aber nur an Punkt 5 und 12
// (x = 45 mm) — ein Raumabstand sagte 2 mm, der Weg auf der Haut über 40.
// Punkt 15 ist deckungsgleich mit Punkt 1 und hat kein Dreieck: die Naht.
const xs = [0, 0.002, 0.005, 0.009, 0.015, 0.045, 0.4];
const pos = new Float32Array(16 * 3);
xs.forEach((x, i) => { pos[3 * i] = x; pos[3 * (i + 7)] = x; pos[3 * (i + 7) + 1] = 0.01; });
pos[42] = 0.002; pos[43] = -0.04; pos[44] = 0;
pos[45] = 0.002; pos[46] = 0; pos[47] = 0;
const dreiecke = [];
for (let i = 0; i < 6; i++) dreiecke.push(i, i + 1, i + 7, i + 1, i + 8, i + 7);
dreiecke.push(5, 12, 14);
const maske = Uint8Array.from([0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1]);
const d = S.abstaende(pos, maske, Uint32Array.from(dreiecke));
pruefe('gezeichnet', [d[0], d[7]], [0, 0]);
for (const [i, soll] of [[1, 0.002], [2, 0.005], [3, 0.009], [4, 0.015]]) nah('weg ' + i, d[i], soll);
pruefe('fern', d[6], null);            // Infinity wird zu null serialisiert
if (d[6] !== Infinity) throw new Error('fern nicht Infinity: ' + d[6]);
if (!(d[14] > 0.04)) throw new Error('Weg auf der Haut, nicht durch den Raum: ' + d[14]);
nah('naht im graph', d[15], 0.002);
nah('tiefe 2', S.tiefe(d[1]), 0.003); nah('tiefe 5', S.tiefe(d[2]), 0.006);
nah('tiefe 9', S.tiefe(d[3]), 0.010); nah('tiefe 15', S.tiefe(d[4]), 0.010);
nah('tiefe fern', S.tiefe(d[6]), 0.010);
pruefe('weg', Array.from(S.weg(maske, d)), [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0]);
pruefe('leer', Array.from(S.abstaende(new Float32Array(0), new Uint8Array(0), new Uint32Array(0))), []);
// 5. Naht: zwei Dreiecke, geknickt, die gemeinsame Kante mit doppelten Punkten.
const { Hautmaskegeometrie: G } = await import(MODUL.replace('saumband.js', 'hautmaskegeometrie.js'));
const naht = Float32Array.from([0,0,0, 1,0,0, 0,1,0,  1,0,0, 1,1,0.5, 0,1,0]);
const N = G.normalen(naht, Uint32Array.from([0,1,2, 3,4,5]));
for (const [a, b] of [[1, 3], [2, 5]]) for (let k = 0; k < 3; k++) nah('naht ' + a + '/' + b, N[3 * a + k], N[3 * b + k]);
if (Math.abs(N[3 * 1 + 2] - 1) < 1e-6) throw new Error('Naht: Zwilling sieht nur seinen halben Fächer');
// 6. Zwillinge an einem Weg, den float32 aufrundet: Quelle 0, Punkt 1 bei
// (11, 5, 3) mm, Punkt 2 deckungsgleich mit 1, Punkt 3 fuer die Dreiecke.
const { Hautwege: W } = await import(MODUL.replace('saumband.js', 'hautwege.js'));
const rund = Float32Array.from([0,0,0, 0.011,0.005,0.003, 0.011,0.005,0.003, 0,0.02,0]);
const wege = W.wege(rund, Uint32Array.from([0,1,3, 0,2,3]), [0], 0.15);
if (Math.fround(wege[1]) <= wege[1]) throw new Error('Probe greift nicht: float32 rundet hier nicht auf');
if (wege[1] !== wege[2]) throw new Error('Zwillinge mit verschiedenem Weg: ' + wege[1] + ' / ' + wege[2]);
console.log(JSON.stringify({ ok: true }));
"""


class SaumbandJsTest(SimpleTestCase):

    def test_band_neben_der_gezeichneten_haut(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))

    def test_einzug_und_index_haengen_am_band(self):
        u"""Eine Quelle für die Tiefe; die vier Verwender kürzen den Index
        mit `weg` aus `Hauteinzug.setzen`, nicht mehr mit der Maske."""
        viewer = MODUL.VIEWER
        einzug = (viewer / 'gemeinsam' / 'hauteinzug.js').read_text(encoding='utf-8')
        self.assertIn('static EINZUG_M = Saumband.TIEFE_M;', einzug)
        self.assertIn('stand.weg = Saumband.weg(maske, abstaende);', einzug)
        for ordner, name in (('scene', 'hautverdeckung.js'), ('gemeinsam', 'figurhaut.js')):
            quelle = (viewer / ordner / name).read_text(encoding='utf-8')
            self.assertIn('Hautmaske.indexOhne(voll.index, voll.gruppen, einzug.weg)', quelle, name)
            self.assertNotIn('Hautmaske.indexOhne(voll.index, voll.gruppen, maske)', quelle, name)
        lagen = (viewer / 'scene' / 'lagenverdeckung.js').read_text(encoding='utf-8')
        self.assertIn('Hautmaske.indexOhne(voll.index, voll.gruppen, einzug.weg || maske)', lagen)
