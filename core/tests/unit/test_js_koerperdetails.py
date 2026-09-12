# -*- coding: utf-8 -*-
u"""Körperdetails: Farben und Längen von Iris, Wimpern und Nägeln.

WARUM (Edgar, 12.09.2026: „bei klick auf das Model … muss ich doch einen
Bereich haben wo ich die Farbe der Fingernägel, die Augenwimpern, die Farbe
der Augen usw einstellen kann? Länge der Augenlider, Fingernägel,
Fußnägel"): Die Rechnung liegt in `gemeinsam/koerperdetails.js` ohne
Three.js und läuft hier in Node an einem kleinen Netz:

1. `aus()` nimmt nur bekannte Felder, kappt Längen auf 0,5..3 und weist
   kaputte Farben ab.
2. `faerben()` setzt die Gruppenfarben (Haut nur, wenn gesetzt; Lippen nur,
   wenn die Gruppe 11 existiert) und den Glanz als Rauheit 1 − Glanz.
3. Ein Wimpernstreifen wird von der Augenseite aus gestreckt: die Wurzel
   bleibt, die Spitze wandert um den Faktor.
4. Ein Fußnagel: die mit der Haut geteilten Wurzelecken bleiben, die freien
   wandern nach außen — und ein zweites `anwenden()` mit anderem Faktor
   rechnet von der gemerkten Basis, nicht vom schon gestreckten Stand.

Sabotage-Gegenprobe gemacht: `_laengs` ohne `(faktor - 1)` → Fälle 3 und 4
rot; `_basisZurueck` weggelassen → Fall 4 (zweites Anwenden) rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'koerperdetails.js')

SKRIPT = """
const { Koerperdetails } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const nah = (was, ist, soll, eps = 1e-5) => {
    if (Math.abs(ist - soll) > eps) throw new Error(was + ': ' + ist + ' statt ' + soll);
};

// 1. aus()
const d = Koerperdetails.aus({ details: { iris: '#FF0000', wimpern: 'rot', naegel_fuss_laenge: 9, fremd: 1 } });
pruefe('iris klein', d.iris, '#ff0000');
pruefe('kaputte farbe', d.wimpern, '#111111');
pruefe('gekappt', d.naegel_fuss_laenge, 3);
pruefe('vorgabe', d.wimpern_laenge, 1);
pruefe('fremd weg', 'fremd' in d, false);
pruefe('istVorgabe', Koerperdetails.istVorgabe(Koerperdetails.aus(null)), true);

pruefe('glanz gekappt', Koerperdetails.aus({ details: { haut_glanz: 7 } }).haut_glanz, 1);
pruefe('haut leer bleibt leer', Koerperdetails.aus({ details: { haut: '' } }).haut, '');

// 2. faerben(): Wimpern, Sklera, Iris, Zunge, Zaehne, zwei Naegel = 7 mit elf
// Materialien; die Haut (0, 1) bleibt ohne Farbe unberuehrt, Lippen (11) fehlen.
const farbe = () => {
    const m = { wert: null, roughness: 0.55, color: { set(v) { m.wert = v; } } };
    return m;
};
const materialien = Array.from({ length: 11 }, farbe);
pruefe('gesetzt', Koerperdetails.faerben(materialien, d), 7);
pruefe('iris material', materialien[6].wert, '#ff0000');
pruefe('haut unberuehrt', materialien[0].wert, null);
nah('haut glanz 0,45 -> rauheit 0,55', materialien[0].roughness, 0.55);
pruefe('einzelmaterial', Koerperdetails.faerben(farbe(), d), 0);
// Mit Haut, Lippen und Glanz: zwoelf Materialien, Haut auf 0 UND 1.
const zwoelf = Array.from({ length: 12 }, farbe);
const voll = Koerperdetails.aus({ details: { haut: '#112233', lippen: '#aa3344', lippen_glanz: 0.25 } });
pruefe('gesetzt voll', Koerperdetails.faerben(zwoelf, voll), 10);
pruefe('haut 0', zwoelf[0].wert, '#112233');
pruefe('haut 1', zwoelf[1].wert, '#112233');
pruefe('lippen', zwoelf[11].wert, '#aa3344');
nah('lippen rauheit', zwoelf[11].roughness, 0.75);

// Kleines Netz: Haut-Dreieck (0,1,2), Sklera links (3,4,5), ein Wimpern-
// streifen (6..9, zwei Dreiecke, Wurzel bei y=0 nahe der Sklera), ein
// Fussnagel (Wurzel 1,2 = Haut, Spitze 10,11).
const p = new Float32Array([
    0,0,0,  1,0,0,  0,1,0,          // 0-2 Haut
    -1,0,0, -1,0.1,0, -1.1,0,0,     // 3-5 Sklera links
    -1,0.2,0, -0.9,0.2,0, -1,1.2,0, -0.9,1.2,0,   // 6-9 Wimpern: Wurzel y=0.2 (nahe Auge), Spitze y=1.2
    1.5,0,0, 1.5,1,0,               // 10-11 Nagelspitze
]);
const index = Uint32Array.from([
    0,1,2,            // Haut
    3,4,5,            // Sklera
    6,7,8, 7,9,8,     // Wimpern
    1,2,10, 2,11,10,  // Nagel Fuss (1,2 Haut)
]);
const gruppen = [
    { start: 0, count: 3, materialIndex: 0 }, { start: 3, count: 3, materialIndex: 4 },
    { start: 6, count: 6, materialIndex: 2 }, { start: 12, count: 6, materialIndex: 10 },
];
const plan = Koerperdetails.plan(index, gruppen, p);
pruefe('ein streifen', plan.wimpern.length, 1);
pruefe('ein nagel', plan.naegelFuss.length, 1);
pruefe('nagelwurzel', plan.naegelFuss[0].wurzel.sort(), [1, 2]);
pruefe('nagelfrei', plan.naegelFuss[0].frei.sort(), [10, 11]);

// 3. Wimpern: Faktor 2 — Wurzel (6,7) bleibt, Spitze (8,9) von y 1.2 auf 2.2
const q = p.slice();
Koerperdetails.strecken(q, plan, { ...Koerperdetails.VORGABE, wimpern_laenge: 2 });
nah('wurzel bleibt', q[3 * 6 + 1], 0.2);
nah('spitze doppelt', q[3 * 8 + 1], 2.2);
nah('haut unberuehrt', q[3 * 0], 0);

// 4. Nagel ueber anwenden(): Basis gemerkt, zweiter Faktor rechnet neu
const geo = { index: { array: index }, groups: gruppen, userData: {},
              attributes: { position: { array: p.slice(), needsUpdate: false } } };
const netz = { geometry: geo, material: materialien };
Koerperdetails.anwenden(netz, { ...Koerperdetails.VORGABE, naegel_fuss_laenge: 2 });
const a = geo.attributes.position.array;
nah('wurzel 1 bleibt', a[3 * 1], 1);
// Wurzelschwerpunkt (0.5,0.5), Spitzenschwerpunkt (1.5,0.5): Achse +x, Spitze +1 weiter
nah('spitze x', a[3 * 10], 2.5);
pruefe('needsUpdate', geo.attributes.position.needsUpdate, true);
Koerperdetails.anwenden(netz, { ...Koerperdetails.VORGABE, naegel_fuss_laenge: 1.5 });
nah('zweiter faktor von der basis', geo.attributes.position.array[3 * 10], 2.0);
Koerperdetails.anwenden(netz, Koerperdetails.aus(null));
nah('zurueck auf basis', geo.attributes.position.array[3 * 10], 1.5);
// Frischer Puffer als neue Basis
const frisch = p.slice(); frisch[3 * 10] = 3.0;
Koerperdetails.anwenden(netz, { ...Koerperdetails.VORGABE, naegel_fuss_laenge: 2 }, frisch);
nah('frische basis', frisch[3 * 10], 5.5);
console.log(JSON.stringify({ ok: true, bewegt: Koerperdetails.strecken(p.slice(), plan, { ...Koerperdetails.VORGABE, wimpern_laenge: 2, naegel_fuss_laenge: 2 }) }));
"""


class KoerperdetailsTest(SimpleTestCase):

    def test_farben_und_laengen(self):
        aus = MODUL.laufen(SKRIPT)
        self.assertTrue(aus['ok'])
        # Spitze des Streifens (2) + freie Nagelecken (2); Wurzeln bleiben.
        self.assertEqual(aus['bewegt'], 4)
