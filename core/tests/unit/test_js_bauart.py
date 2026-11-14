# -*- coding: utf-8 -*-
"""Bauart je Stück und „Haut gibt nach“ (12.11.2026): `Bauart`, `Starrbindung`, `Hautmaske.verdeckt(… nachgeben)`, `Hauteinzugrechnung`.

Edgar, 12.11.2026: „man könnte doch einen Parameter setzen bis zu dem das mesh eingedrückt werden kann“ und „mach alles, mit deinen
Empfehlungen“ (Konzept `Docu/konzepte/2026-11-12_genesis-zuerst-konzept.md`, Abschnitt 3b). Geprüft in Node mit den echten Modulen:

1. `Hautrechnung` mit `nachgeben` je Stück: Die Maske ist dieselbe wie ohne; die Tiefe eines verdeckten Punkts weit vom Rand ist höchstens die
   des Stücks, mit 20 mm tiefer als die alte Vorgabe 10 mm; liegt ein Punkt unter zwei Stücken, gilt das tiefere; ohne Angabe 10 mm wie bisher.
2. `Starrbindung`: je Insel ein Knochen (der mit der größten Gewichtssumme), Gewicht 1; Nahtkopien an gleicher Stelle gehören zur selben Insel;
   Schuhe, Ersatzstücke und Nicht-Starre gelten nicht.
3. `Bauart`: vom Server gesetzt gewinnt; sonst Stoffschwung → lose, Requisit oder Schuh → starr, sonst anliegend; die Tiefe am Stück schlägt die
   Vorgabe der Bauart.

Sabotage: in `Hautmaske._einStueck` die Bedingung `wert > nachgeben[i]` weglassen (nur das erste Stück zählt) → Fall 1 rot („tieferes Stück
gewinnt“); in `Starrbindung.inseln` den Abgleich gleicher Lage entfernen → Fall 2 rot („Nahtkopie“); in `Bauart.von` die Prüfung von
`userData.stoff` streichen → Fall 3 rot.

Geschrieben am 12.11.2026, nicht gelaufen (Tests nur auf Ansage).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

ZYLINDER = """
function zylinder(radius, y0, y1, ringe, n) {
    const P = [], T = [];
    for (let r = 0; r < ringe; r++) {
        const y = y0 + (y1 - y0) * r / (ringe - 1);
        for (let i = 0; i < n; i++) { const w = 2 * Math.PI * i / n; P.push(radius * Math.cos(w), y, radius * Math.sin(w)); }
    }
    for (let r = 0; r + 1 < ringe; r++) for (let i = 0; i < n; i++) {
        const a = r * n + i, b = r * n + (i + 1) % n, c = (r + 1) * n + i, d = (r + 1) * n + (i + 1) % n;
        T.push(a, c, b, b, c, d);
    }
    return { P: Float32Array.from(P), T: Uint32Array.from(T) };
}
"""

NACHGEBEN = ZYLINDER + """
const dir = MODUL.replace('hautrechnung.js', '');
const { Hautrechnung } = await import(MODUL);
const { Saumband } = await import(dir + 'saumband.js');
const koerper = zylinder(0.10, 0.0, 1.0, 101, 36);
const lang = zylinder(0.102, 0.10, 0.90, 81, 36);          // 80 cm Rohr: die Mitte liegt 40 cm vom Rand, weit jenseits der Rampe
const kurz = zylinder(0.104, 0.40, 0.60, 21, 36);          // darüber ein zweites, kürzeres Stück
const stueck = (s, k, mm) => ({ schluessel: k, punkte: s.P.slice(), dreiecke: s.T.slice(), ...(mm == null ? {} : { nachgeben: mm / 1000 }) });
const tiefe = (r, i) => Math.hypot(r.einzug.werte[3 * i], r.einzug.werte[3 * i + 1], r.einzug.werte[3 * i + 2]);
const mitte = 50 * 36;                                      // Ring 50 (y = 0,5)
const ohne = Hautrechnung.rechnen(koerper.P, koerper.T, [stueck(lang, 'lang', null)]);
const zehn = Hautrechnung.rechnen(koerper.P, koerper.T, [stueck(lang, 'lang', 10)]);
const zwanzig = Hautrechnung.rechnen(koerper.P, koerper.T, [stueck(lang, 'lang', 20)]);
pruefe('Maske gleich', [Array.from(zwanzig.maske).join(''), Array.from(zehn.maske).join('')], [Array.from(ohne.maske).join(''), Array.from(ohne.maske).join('')]);
pruefe('Mitte verdeckt', ohne.maske[mitte], 1);
pruefe('ohne Angabe die alte Vorgabe', +tiefe(ohne, mitte).toFixed(4), +Saumband.TIEFE_M.toFixed(4));
pruefe('10 mm wie ohne Angabe', +tiefe(zehn, mitte).toFixed(5), +tiefe(ohne, mitte).toFixed(5));
pruefe('20 mm tiefer als 10', tiefe(zwanzig, mitte) > tiefe(zehn, mitte) + 0.005, true);
pruefe('20 mm höchstens 20', tiefe(zwanzig, mitte) <= 0.020 + 1e-6, true);
// Zwei Stücke über der Mitte: das tiefere gewinnt, gleich in welcher Reihenfolge.
const a = Hautrechnung.rechnen(koerper.P, koerper.T, [stueck(lang, 'lang', 10), stueck(kurz, 'kurz', 20)]);
const b = Hautrechnung.rechnen(koerper.P, koerper.T, [stueck(kurz, 'kurz', 20), stueck(lang, 'lang', 10)]);
pruefe('tieferes Stück gewinnt', [+tiefe(a, mitte).toFixed(5), +tiefe(b, mitte).toFixed(5)], [+tiefe(zwanzig, mitte).toFixed(5), +tiefe(zwanzig, mitte).toFixed(5)]);
pruefe('Maske mit zwei Stücken gleich', Array.from(a.maske).join(''), Array.from(b.maske).join(''));
console.log(JSON.stringify({ ok: true }));
"""

STARR = """
const { Starrbindung } = await import(MODUL);
// Zwei Quadrate (je zwei Dreiecke) weit auseinander, das zweite mit einer Nahtkopie: Punkt 7 liegt an der Stelle von Punkt 5.
const pos = Float32Array.from([0,0,0, 1,0,0, 1,1,0, 0,1,0,   5,0,0, 6,0,0, 6,1,0, 6,0,0]);
const index = Uint32Array.from([0,1,2, 0,2,3,   4,5,6]);   // Punkt 7 hängt an keinem Dreieck, nur über die Lage an Punkt 5
const si = Float32Array.from([3,4,0,0, 3,4,0,0, 4,3,0,0, 3,0,0,0,   9,8,0,0, 9,8,0,0, 8,9,0,0, 8,0,0,0]);
const sw = Float32Array.from([.6,.4,0,0, .7,.3,0,0, .5,.5,0,0, 1,0,0,0,   .9,.1,0,0, .8,.2,0,0, .6,.4,0,0, 1,0,0,0]);
const attr = (array) => ({ array, count: array.length / 4, needsUpdate: false });
const geo = { index: { array: index }, attributes: { position: { array: pos } }, _a: { skinIndex: attr(si), skinWeight: attr(sw) },
              getAttribute(n) { return this._a[n]; } };
const netz = { geometry: geo, userData: {} };
const r = Starrbindung.anwenden(netz);
pruefe('zwei Inseln', r.inseln, 2);
pruefe('Insel 1 an Knochen 3', [si[0], si[4], si[8], si[12]], [3, 3, 3, 3]);
pruefe('Insel 2 an Knochen 9, Nahtkopie mit', [si[16], si[20], si[24], si[28]], [9, 9, 9, 9]);
pruefe('Gewicht 1, Rest 0', [sw[0], sw[1], sw[28], sw[29]], [1, 0, 1, 0]);
pruefe('neu hochgeladen', [geo._a.skinIndex.needsUpdate, geo._a.skinWeight.needsUpdate], [true, true]);
// Zwei Inseln, die sich berühren (Laserwaffe aus vielen Teilen), sind EIN starres Teil; weit auseinander bleiben sie zwei.
const nah = Starrbindung.gruppen(Int32Array.from([0, 0, 1, 1]), Float32Array.from([0,0,0, 0.1,0,0, 0.11,0,0, 0.2,0,0]));
const fern = Starrbindung.gruppen(Int32Array.from([0, 0, 1, 1]), Float32Array.from([0,0,0, 0.1,0,0, 0.3,0,0, 0.4,0,0]));
pruefe('berührende Inseln eine Gruppe', nah[0] === nah[2], true);
pruefe('ferne Inseln zwei Gruppen', fern[0] === fern[2], false);
pruefe('gilt nur für starr', [Starrbindung.gilt({ userData: {} }, 'starr'), Starrbindung.gilt({ userData: {} }, 'anliegend'),
    Starrbindung.gilt({ userData: { schuh: true } }, 'starr'), Starrbindung.gilt({ userData: { hautTiefe: 0.02 } }, 'starr'),
    Starrbindung.gilt({ userData: { ersetzt: ['augen'] } }, 'starr')], [true, false, false, false, false]);
console.log(JSON.stringify({ ok: true }));
"""

BAUART = """
const { Bauart } = await import(MODUL);
const n = (u) => ({ userData: u });
pruefe('vom Server', Bauart.von(n({ bauart: 'lose', art: 'requisit' })), 'lose');
pruefe('Stoffschwung lose', Bauart.von(n({ stoff: { frei: [] } })), 'lose');
pruefe('Requisit starr', Bauart.von(n({ art: 'requisit' })), 'starr');
pruefe('Schuh starr', Bauart.von(n({ schuh: true })), 'starr');
pruefe('Ersatzstück anliegend', Bauart.von(n({ hautTiefe: 0.02, art: 'kleidung' })), 'anliegend');
pruefe('sonst anliegend', Bauart.von(n({ art: 'kleidung' })), 'anliegend');
pruefe('Tiefe der Bauart', [Bauart.nachgebenM(n({ schuh: true })), Bauart.nachgebenM(n({ art: 'kleidung' }))], [0.02, 0.03]);
pruefe('Tiefe am Stück', Bauart.nachgebenM(n({ art: 'kleidung', nachgebenMm: 4 })), 0.004);
pruefe('null ist keine Angabe', [Bauart.nachgebenM(n({ schuh: true, nachgebenMm: null })), Bauart.nachgebenM(n({ art: 'kleidung', nachgebenMm: 0 }))], [0.02, 0]);
const netz = n({});
Bauart.eintragen(netz, { bauart: 'starr', nachgeben_mm: 30, schuh: false });
pruefe('eintragen', [netz.userData.bauart, netz.userData.nachgebenMm, netz.userData.schuh], ['starr', 30, false]);
Bauart.eintragen(netz, { bauart: 'quatsch' });
pruefe('Unbekanntes verworfen', [netz.userData.bauart, netz.userData.nachgebenMm], [null, null]);
console.log(JSON.stringify({ ok: true }));
"""


class BauartTest(SimpleTestCase):

    def test_1_haut_gibt_bis_zur_tiefe_des_stuecks_nach(self):
        self.assertTrue(Jsmodul('gemeinsam', 'hautrechnung.js').laufen(NACHGEBEN).get('ok'))

    def test_2_starre_stuecke_haengen_je_insel_an_einem_knochen(self):
        self.assertTrue(Jsmodul('gemeinsam', 'starrbindung.js').laufen(STARR).get('ok'))

    def test_3_die_bauart_eines_netzes(self):
        self.assertTrue(Jsmodul('gemeinsam', 'bauart.js').laufen(BAUART).get('ok'))
