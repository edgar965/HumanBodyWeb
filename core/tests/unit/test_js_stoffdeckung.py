"""Stoffdeckung — wie viel eines Stoffs man nicht durchschaut (19.10.2026), geprüft in Node an einer Kunstkarte.

Gemessen im Chrome (Damira0): `g9_base_bikini` trägt eine Alphakarte mit 100 % deckenden Texeln samt `alphaTest` 0,02 und galt nach dem Material allein als
durchbrochen — das Genital wurde unter ihm nicht verdeckt. Die Spitze `mh_punkduck_strappy_lace_thong` deckt 0 %. `Stoffdeckung.anteil` zählt die
Dreiecke, deren UV-Mitte auf einem deckenden Texel liegt; `durchbrochen` braucht DOM und Textur und ist hier nicht geprüft.

1. Karte 2 × 2, links deckend (Grün 255), rechts frei (0): ein Dreieck links und eines rechts → Anteil 0,5.
2. `flipY`: oben deckend, unten frei — ein Dreieck bei v = 0,1 liegt mit `flipY` (v = 0 unten) auf der freien, ohne auf der deckenden Zeile.
3. UV außerhalb 0 … 1 wiederholt sich (u = 1,25 wie u = 0,25).
4. Ohne Dreiecke: Anteil 1 (nichts zu durchschauen).

Sabotage (gedacht, nicht gefahren): `flipY` ignorieren → Fall 2 rot. Geschrieben 19.10.2026, gelaufen auf Ansage: grün.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'stoffdeckung.js')


class StoffdeckungTest(SimpleTestCase):
    databases = set()

    def test_anteil_deckender_dreiecke(self):
        skript = """
const { Stoffdeckung: S } = await import(MODUL);
const fehler = [];
const pruefe = (name, ist, soll) => { if (JSON.stringify(ist) !== JSON.stringify(soll)) fehler.push(`${name}: ${JSON.stringify(ist)} statt ${JSON.stringify(soll)}`); };
const dreieck = (u, v) => [u - 0.01, v - 0.01, u + 0.01, v - 0.01, u, v + 0.01];
// 1. links deckend, rechts frei (Zeilen von oben: [255, 0], [255, 0])
const links = Uint8Array.from([255, 0, 255, 0]);
pruefe('links/rechts', S.anteil(Float32Array.from([...dreieck(0.25, 0.5), ...dreieck(0.75, 0.5)]), Uint32Array.from([0, 1, 2, 3, 4, 5]), links, 2), 0.5);
// 2. oben deckend, unten frei
const oben = Uint8Array.from([255, 255, 0, 0]), unten = Float32Array.from(dreieck(0.5, 0.1)), ein = Uint32Array.from([0, 1, 2]);
pruefe('flipY', [S.anteil(unten, ein, oben, 2, true), S.anteil(unten, ein, oben, 2, false)], [0, 1]);
// 3. Wiederholung
pruefe('Wiederholung', S.anteil(Float32Array.from(dreieck(1.25, 0.5)), ein, links, 2), 1);
// 4. ohne Dreiecke
pruefe('leer', S.anteil(new Float32Array(0), new Uint32Array(0), links, 2), 1);
console.log(JSON.stringify({ ok: !fehler.length, fehler }));
"""
        ausgabe = MODUL.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
