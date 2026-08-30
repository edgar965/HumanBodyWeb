# -*- coding: utf-8 -*-
"""`Hautgewichte` gegen die alte, kopierte Schleife — Wert für Wert.

WARUM DIESER TEST DER WICHTIGE TEIL DES UMBAUS IST (17.08.2026)
==============================================================
Die Schleife „vier stärkste Knochen, normiert" stand VIERMAL im Browser-Code und
ist jetzt eine Klasse. Prüfen lässt sich das nur rechnend: Skinning sieht in der
Ruhelage RICHTIG aus, egal wie die Gewichte stehen — alle Knochenmatrizen sind
dort die Einheitsmatrix. Falsch wird es erst, wenn ein einzelner Knochen dreht
(siehe „SkinnedMesh Debug Pattern" im Projektgedächtnis). Ein Blick auf die Seite
hätte einen Fehler hier also NICHT gezeigt.

Deshalb steht die alte Fassung hier im Testskript nochmal und wird gegen die neue
Klasse gerechnet — auf Fällen, die weh tun: mehr als vier Einflüsse, unsortierte
Reihenfolge, Summe über und unter 1, ein Punkt ohne jeden Einfluss, ein Punkt
ohne Eintrag im Feld.

Ohne `node` im Pfad bricht der Lauf mit einer Meldung ab (seit dem
30.08.2026) — vorher meldete er grün, ohne gelaufen zu sein.
"""
import unittest

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'hautgewichte.js')

#: Die Fälle, auf die es ankommt — je Punkt eine Liste [Knochen, Gewicht].
SKRIPT = """
const { Hautgewichte } = await import(MODUL);

const daten = { weights: [
    [[3, 0.1], [7, 0.6], [1, 0.2], [9, 0.05], [4, 0.05]],   // fuenf, unsortiert
    [[2, 0.5], [5, 0.5]],                                   // zwei, Summe 1
    [[8, 3.0]],                                             // Summe ueber 1
    [],                                                     // ohne Einfluss
    [[6, 0.0], [7, 0.0]],                                   // Summe 0
    undefined,                                              // kein Eintrag
] };
const punkte = 6;

// --- die ALTE, kopierte Schleife, unveraendert aus animation/netz.js ---
const skinIndices = new Float32Array(punkte * 4);
const skinWeights = new Float32Array(punkte * 4);
for (let v = 0; v < punkte; v++) {
    const infs = daten.weights[v] || [];
    const sorted = infs.slice().sort((a, b) => b[1] - a[1]).slice(0, 4);
    let sum = sorted.reduce((s, e) => s + e[1], 0);
    if (sum < 1e-6) sum = 1;
    for (let i = 0; i < 4; i++) {
        skinIndices[v * 4 + i] = i < sorted.length ? sorted[i][0] : 0;
        skinWeights[v * 4 + i] = i < sorted.length ? sorted[i][1] / sum : 0;
    }
}

const neu = Hautgewichte.vierervektoren(daten, punkte);

// --- und der Ein-Knochen-Fall (Haare am Kopf) ---
const attrs = {};
const geometrie = {
    attributes: { position: { count: 3 } },
    setAttribute: (name, wert) => { attrs[name] = wert; },
};
class Attrappe {
    constructor(feld, breite) { this.array = feld; this.itemSize = breite; }
}
Hautgewichte.anEinenKnochen(geometrie, 42, Attrappe);

console.log(JSON.stringify({
    altIndices: Array.from(skinIndices),
    altGewichte: Array.from(skinWeights),
    neuIndices: Array.from(neu.indices),
    neuGewichte: Array.from(neu.gewichte),
    kopfIndices: Array.from(attrs.skinIndex.array),
    kopfGewichte: Array.from(attrs.skinWeight.array),
    breite: attrs.skinWeight.itemSize,
}));
"""


class HautgewichteTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.e = MODUL.laufen(SKRIPT)

    def test_gleiche_indices_wie_die_alte_schleife(self):
        self.assertEqual(self.e['neuIndices'], self.e['altIndices'])

    def test_gleiche_gewichte_wie_die_alte_schleife(self):
        for i, (alt, neu) in enumerate(zip(self.e['altGewichte'],
                                           self.e['neuGewichte'])):
            self.assertAlmostEqual(alt, neu, places=6,
                                   msg='Stelle %d' % i)

    def test_die_vier_staerksten_in_der_richtigen_reihenfolge(self):
        """Punkt 0 hat fünf Einflüsse — 7 (0,6) muss vorn stehen, 4 wegfallen."""
        self.assertEqual(self.e['neuIndices'][:4], [7.0, 1.0, 3.0, 9.0])

    def test_normiert_auf_summe_eins(self):
        """Punkt 2 hat Gewicht 3,0 — nach dem Normieren genau 1,0."""
        self.assertAlmostEqual(self.e['neuGewichte'][8], 1.0, places=6)

    def test_punkt_ohne_einfluss_bleibt_null_statt_nan(self):
        """Summe 0 würde durch Null teilen; erwartet sind vier Nullen."""
        for stelle in range(12, 16):          # Punkt 3
            self.assertEqual(self.e['neuGewichte'][stelle], 0.0)
        for stelle in range(16, 20):          # Punkt 4, Summe 0
            self.assertEqual(self.e['neuGewichte'][stelle], 0.0)

    def test_fehlender_eintrag_wirft_nicht(self):
        """`weights[5]` ist `undefined` — das darf keine Ausnahme sein."""
        self.assertEqual(self.e['neuIndices'][20:24], [0.0, 0.0, 0.0, 0.0])

    def test_ein_knochen_bekommt_gewicht_eins(self):
        self.assertEqual(self.e['kopfIndices'], [42, 0, 0, 0] * 3)
        self.assertEqual(self.e['kopfGewichte'], [1.0, 0, 0, 0] * 3)
        self.assertEqual(self.e['breite'], 4)


if __name__ == '__main__':
    unittest.main()
